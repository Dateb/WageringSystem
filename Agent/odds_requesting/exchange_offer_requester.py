import json
from datetime import datetime, time
from time import sleep
from typing import Dict, Tuple, List

import requests
import websocket
from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException

from Agent.odds_requesting.offer_requester import OfferRequester
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper
from Model.Betting.bet import BetOffer, LiveResult


class Market:

    def __init__(self, race_card: RaceCard, today_markets_raw: dict):
        self.scraper = get_scraper()
        self.type = "WIN"

        self.event_id = ""
        self.market_id = ""

        self.set_event_and_market_id(
            country=race_card.country,
            track_name=race_card.track_name,
            race_number=race_card.race_number,
            today_markets_raw=today_markets_raw,
        )

        self.race_card = race_card
        self.horse_number_by_exchange_id = {}

    def set_event_and_market_id(self, country: str, track_name: str, race_number: int, today_markets_raw: dict) -> None:
        for country_data in today_markets_raw:
            if country in country_data["name"]:
                events_raw = country_data["events"]
                for event_data in events_raw:
                    if track_name in event_data["name"]:
                        market_data = event_data["markets"][race_number - 1]
                        self.event_id = event_data["id"]

                        start_time_timestamp = int(market_data["startTime"]) / 1000
                        start_time = datetime.utcfromtimestamp(start_time_timestamp)

                        start_time_minute = str(start_time.minute)
                        if len(start_time_minute) == 1:
                            start_time_minute = f"0{start_time_minute}"
                        market_list_url = f"https://exch.piwi247.com/customer/api/race/{self.event_id}.{start_time.hour}{start_time_minute}"

                        print(market_list_url)
                        market_list_data = self.scraper.request_data(market_list_url)

                        markets = market_list_data["children"]

                        for market in markets:
                            if market["marketType"] == self.type:
                                self.market_id = market["id"]


class MarketOffer:

    def __init__(self, market: Market, horse_number: str, odds: float):
        self.market = market
        self.horse_number = horse_number
        self.odds = odds

    def to_bet_offer(self) -> BetOffer:
        offer_odds = self.odds
        if offer_odds < 0:
            offer_odds = 0

        race_card = self.market.race_card
        horse = race_card.get_horse_by_number(int(self.horse_number))

        if horse is None:
            print(f"Horse nr. not found: {self.horse_number}, at race: {race_card.race_id}")
        else:
            live_result = LiveResult(
                offer_odds=offer_odds,
                starting_odds=0.0,
                has_won=horse.has_won,
                adjustment_factor=1.0,
                win=0,
                loss=0,
            )
            return BetOffer(
                is_success=False,
                country=race_card.country,
                race_class=race_card.race_class,
                horse_number=horse.number,
                live_result=live_result,
                scratched_horse_numbers=[],
                race_datetime=race_card.datetime,
                offer_datetime=datetime.now(),
                n_horses=race_card.n_horses,
                n_winners=1
            )


class ExchangeConnection:

    def __init__(self):
        self.session_id = "0e78ced5-020b-49e6-8d99-c272c49ffa39"
        self.customer_id = self.get_customer_id()
        self.scraper = get_scraper()

        websocket.enableTrace(False)
        self.web_socket = websocket.WebSocket()

    def get_today_markets_raw(self) -> dict:
        time_range = "TODAY"

        current_time = datetime.now().time()

        if time(20, 0) <= current_time or current_time <= time(2, 0):
            time_range = "TOMORROW"

        today_markets_raw_url = f"https://exch.piwi247.com/customer/api/horse-racing/7/all?timeRange={time_range}"
        return self.scraper.request_data(today_markets_raw_url)

    def get_market_data(self, market_id: str) -> dict:
        return self.scraper.request_data(
            url=f"https://exch.piwi247.com/customer/api/market/{market_id}"
        )

    def get_customer_id(self) -> str:
        login_response = requests.post(
            "https://api.piwi247.com/api/users/login",
            data={
                "email": "daniel.tebart@googlemail.com",
                "password": "Ds*#de!@6846",
                "loginType": 1,
                "remember": False
            },
            cookies={
                "BIAB_AN": self.session_id
            }
        )

        login_response_data = login_response.json()["data"]
        return login_response_data["token"]["orbit"]["access_token"]

    def send_market_opening_request(self, markets: List[Market]) -> None:
        opening_request = '["['

        for market in markets:
            opening_request += '{\\"marketId\\":\\"'
            opening_request += market.market_id
            opening_request += '\\",\\"eventId\\":\\"'
            opening_request += market.event_id
            opening_request += '\\",\\"applicationType\\":\\"WEB\\"}'

            if market != markets[-1]:
                opening_request += ","

        opening_request += ']"]'
        self.web_socket.send(opening_request)

    def open_race_connection(self, markets: List[Market]) -> None:
        try:
            self.web_socket.connect(
                url="wss://exch.piwi247.com/customer/ws/multiple-market-prices/585/e95aa9c5-7a6e-40cd-8060-4de2f796e09d/websocket",
                cookie=f"BIAB_CUSTOMER={self.customer_id}",
            )
        except ValueError:
            raise Exception("Could open socket connection of exchange. Probably invalid customer id.")

        self.web_socket.recv()

        self.send_market_opening_request(markets)

    def close_race_connection(self) -> None:
        self.web_socket.close()

    def reopen(self, markets: List[Market]) -> None:
        self.close_race_connection()
        self.open_race_connection(markets)

    def receive_message(self, markets: List[Market]) -> dict:
        while True:
            try:
                # TODO: Error websocket._exceptions.WebSocketTimeoutException: Connection timed out while receiving (see textdump for full stacktrace)
                message = self.web_socket.recv()
                sleep(0.1)

                break
            except OSError as error:
                print(f"Encountered error during odds receipt: {error}")
                sleep(60)
            except WebSocketConnectionClosedException as error:
                print("Websocket was closed. Trying to reconnect...")

                self.reopen(markets)

            except WebSocketTimeoutException as error:
                print("Websocket timed out. Trying to reconnect...")

                self.reopen(markets)

        if message == "h":
            return None

        # TODO: Line below should catch this error: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        return json.loads(json.loads(message[2:-1]))

    def submit_bets(self, bets_data: dict) -> None:
        url = "https://exch.piwi247.com/customer/api/placeBets"
        payload = bets_data

        cookies = {
            "BIAB_AN": self.session_id,
            "BIAB_COMPETITION_TIME_FILTER": "ALL",
            "BIAB_CUSTOMER": self.customer_id,
            "BIAB_HORSE_RACING_PERIOD": "AFTER_TOMORROW",
            "BIAB_LANGUAGE": "en",
            "BIAB_LOGIN_POP_UP_SHOWN": "true",
            "BIAB_SHOW_TOOLTIPS": "false",
            "BIAB_TZ": "-120",
            "COLLAPSE-LEFT_PANEL_COLLAPSE_GROUP-SPORT_COLLAPSE": "true",
            "COLLAPSE-SPORT_INNER_COLLAPSE-SPORT_INNER_COLLAPSE_MORE-1": "false",
            "CSRF-TOKEN": "c54bb77a-8154-4950-a65d-56d7970f0b38",
            "EXCHANGE_TYPE": "sportsGames",
            "PROFITANDLOSS_BETTYPE": "Sports",
            "PROFITANDLOSS_SPORTNAME": "allSports",
        }

        response = self.scraper.post_payload(
            url=url,
            payload=payload,
            headers=
            {
                'Accept': 'application/json, text/plain, */*',
                'access-control-allow-credentials': "true",
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Host': "exch.piwi247.com",
                'Origin': "https://exch.piwi247.com",
                'Referer': "https://exch.piwi247.com/customer/sport/7/market/1.228271247",
                "x-device": "DESKTOP",
                "X-CSRF-TOKEN": "c54bb77a-8154-4950-a65d-56d7970f0b38"
            },
            cookies=cookies
        )


class Exchange:

    def __init__(self, market_type: str, upcoming_race_cards: Dict[str, RaceCard]):
        self.exchange_connection = ExchangeConnection()
        self.market_type = market_type

        today_markets_raw = self.exchange_connection.get_today_markets_raw()
        self.markets = [
            Market(race_card, today_markets_raw) for race_card in upcoming_race_cards.values()
        ]
        self.markets = [market for market in self.markets if (market.event_id and market.event_id)]

        self.scratched_horses = {race_card: [] for race_card in upcoming_race_cards.values()}

        for market in self.markets:
            market_data = self.exchange_connection.get_market_data(market.market_id)
            market.horse_number_by_exchange_id = self.extract_number_by_internal_id(market_data)

        self.exchange_connection.open_race_connection(self.markets)
        self.market_opening_request_timer = 0
        self.bets_data = {}

    def get_bet_offers(self) -> List[BetOffer]:
        market_offers = self.poll_market_offers()

        bet_offers = [market_offer.to_bet_offer() for market_offer in market_offers]

        return bet_offers

    def poll_market_offers(self) -> List[MarketOffer]:
        self.market_opening_request_timer += 1

        if self.market_opening_request_timer > 600:
            self.market_opening_request_timer = 0
            self.exchange_connection.send_market_opening_request(self.markets)

        message = self.exchange_connection.receive_message(self.markets)

        if message is None:
            return []

        if "rc" not in message:
            return []

        market = self.get_market(message)

        # scratched_horses = self.get_scratched_horses(message)
        #
        # if scratched_horses:
        #     self.scratched_horses[self.race_card_market_map.get_race_card(market)] = scratched_horses

        return self.get_market_offers(market, message)

    def get_market(self, message) -> Market:
        for market in self.markets:
            if market.market_id == message["id"]:
                return market

    def get_market_offers(self, market: Market, message: dict) -> List[MarketOffer]:
        market_offers = []
        for horse_data in message["rc"]:
            horse_id = horse_data["id"]
            horse_number = market.horse_number_by_exchange_id[horse_id]
            odds = horse_data["bdatb"][0]["odds"]

            market_offers.append(MarketOffer(market, horse_number, odds))

        return market_offers

    def get_scratched_horses(self, message: dict) -> List[str]:
        scratched_horses = []
        if "marketDefinition" in message:
            market_definition = message["marketDefinition"]
            if "runners" in market_definition:
                for runner in market_definition["runners"]:
                    if runner["status"] == "REMOVED":
                        scratched_horses.append(runner["name"])

        return scratched_horses

    def extract_number_by_internal_id(self, market_data: dict) -> dict:
        number_by_internal_id = {}
        for horse_data in market_data["runners"]:
            number_by_internal_id[horse_data["selectionId"]] = horse_data["metadata"]["CLOTH_NUMBER_ALPHA"]

        return number_by_internal_id

    def delete_market_of_race_card(self, deleted_race_card: RaceCard) -> None:
        for market in self.markets:
            if market.race_card.race_id == deleted_race_card.race_id:
                self.markets.remove(market)

    def reset_connection(self) -> None:
        self.exchange_connection = ExchangeConnection()
        self.exchange_connection.reopen(self.markets)

    def add_bet(self, market: Market, horse_exchange_id: int, odds: float) -> None:
        if market.market_id not in self.bets_data:
            self.bets_data[market.market_id] = []

        self.bets_data[market.market_id].append(
            {
                    "selectionId": horse_exchange_id,
                    "handicap": 0,
                    "price": str(odds),
                    "size": "6",
                    "side": "BACK",
                    "betType": "EXCHANGE",
                    "netPLBetslipEnabled": False,
                    "netPLMarketPageEnabled": False,
                    "quickStakesEnabled": True,
                    "confirmBetsEnabled": False,
                    "applicationType": "WEB",
                    "mobile": False,
                    "isEachWay": False,
                    "eachWayData": {},
                    "page": "market",
                    "persistenceType": "LAPSE",
                    "placedUsingEnterKey": False
                }
        )

    def submit_bets(self):
        self.exchange_connection.submit_bets(self.bets_data)
        self.bets_data = {}


if __name__ == "__main__":
    exchange_connection = ExchangeConnection()

    bets_data = {
        "1.228287890": [
            {
                "selectionId": 67859761,
                "handicap": 0,
                "price": "500",
                "size": "6",
                "side": "BACK",
                "betType": "EXCHANGE",
                "netPLBetslipEnabled": False,
                "netPLMarketPageEnabled": False,
                "quickStakesEnabled": True,
                "confirmBetsEnabled": False,
                "applicationType": "WEB",
                "mobile": False,
                "isEachWay": False,
                "eachWayData": {},
                "page": "market",
                "persistenceType": "LAPSE",
                "placedUsingEnterKey": False
            },
            {
                "selectionId": 67452409,
                "handicap": 0,
                "price": "1000",
                "size": "6",
                "side": "BACK",
                "betType": "EXCHANGE",
                "netPLBetslipEnabled": False,
                "netPLMarketPageEnabled": False,
                "quickStakesEnabled": True,
                "confirmBetsEnabled": False,
                "applicationType": "WEB",
                "mobile": False,
                "isEachWay": False,
                "eachWayData": {},
                "page": "market",
                "persistenceType": "LAPSE",
                "placedUsingEnterKey": False
            }
        ],
        "1.228287793": [
            {
                "selectionId": 10088209,
                "handicap": 0,
                "price": "50.0",
                "size": "6",
                "side": "BACK",
                "betType": "EXCHANGE",
                "netPLBetslipEnabled": False,
                "netPLMarketPageEnabled": False,
                "quickStakesEnabled": True,
                "confirmBetsEnabled": False,
                "applicationType": "WEB",
                "mobile": False,
                "isEachWay": False,
                "eachWayData": {},
                "page": "market",
                "persistenceType": "LAPSE",
                "placedUsingEnterKey": False
            }
        ]
    }

    exchange_connection.submit_bets(bets_data)
