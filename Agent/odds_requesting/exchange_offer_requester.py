import json
from datetime import datetime, time
from time import sleep
from typing import Dict, Tuple, List

import websocket
from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException

from Agent.odds_requesting.offer_requester import OfferRequester
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper
from Model.Betting.bet import BetOffer


class Market:

    def __init__(self, event_id: str, market_id: str):
        self.event_id = event_id
        self.market_id = market_id
        self.horse_number_by_exchange_id = {}


class RawMarketOffer:

    def __init__(self, market: Market, odds_by_horse_number: Dict[str, float]):
        self.market = market
        self.odds_by_horse_number = odds_by_horse_number


class RaceCardMarketMap:
    def __init__(self):
        self.race_card_to_market = {}
        self.market_to_race_card = {}

    def add(self, race_card: RaceCard, market: Market):
        self.race_card_to_market[race_card] = market
        self.market_to_race_card[market] = race_card

    def delete(self, race_card: RaceCard):
        market_of_race_card = self.get_market(race_card)
        del self.race_card_to_market[race_card]
        del self.market_to_race_card[market_of_race_card]

    def get_race_card(self, market: Market) -> RaceCard:
        return self.market_to_race_card[market]

    def get_market(self, race_card: RaceCard) -> Market:
        return self.race_card_to_market[race_card]

    def get_race_cards(self) -> List[RaceCard]:
        return list(self.market_to_race_card.values())

    def get_markets(self) -> List[Market]:
        return list(self.race_card_to_market.values())


class MarketRetriever:

    def __init__(self, market_type: str):
        self.scraper = get_scraper()
        self.today_markets_url = self.get_markets_url()
        self.today_markets_raw = self.scraper.request_data(self.today_markets_url)
        self.market_type = market_type

    def get_markets_url(self) -> str:
        time_range = "TODAY"

        current_time = datetime.now().time()

        if time(20, 0) <= current_time or current_time <= time(2, 0):
            time_range = "TOMORROW"

        return f"https://exch.piwi247.com/customer/api/horse-racing/7/all?timeRange={time_range}"

    def get_market(self, country: str, track_name: str, race_number: int) -> Market:
        for country_data in self.today_markets_raw:
            if country in country_data["name"]:
                events_raw = country_data["events"]
                for event_data in events_raw:
                    if track_name in event_data["name"]:
                        market_data = event_data["markets"][race_number - 1]
                        event_id = event_data["id"]

                        start_time_timestamp = int(market_data["startTime"]) / 1000
                        start_time = datetime.utcfromtimestamp(start_time_timestamp)

                        start_time_minute = str(start_time.minute)
                        if len(start_time_minute) == 1:
                            start_time_minute = f"0{start_time_minute}"
                        market_list_url = f"https://exch.piwi247.com/customer/api/race/{event_id}.{start_time.hour}{start_time_minute}"

                        print(market_list_url)
                        market_list_data = self.scraper.request_data(market_list_url)

                        markets = market_list_data["children"]

                        place_market_id = ""
                        for market in markets:
                            if market["marketType"] == self.market_type:
                                place_market_id = market["id"]

                        if place_market_id:
                            return Market(event_id, place_market_id)
                        else:
                            return None


class ExchangeOfferRequester(OfferRequester):

    def __init__(self, customer_id: str, market_type: str, upcoming_race_cards: Dict[str, RaceCard]):
        super().__init__(upcoming_race_cards)
        self.customer_id = customer_id
        self.market_type = market_type

        self.race_card_market_map = RaceCardMarketMap()
        self.scratched_horses = {race_card: [] for race_card in upcoming_race_cards.values()}

        self.init_race_card_market_map()
        self.markets = self.race_card_market_map.get_markets()

        websocket.enableTrace(False)
        self.web_socket = websocket.WebSocket()
        self.scraper = get_scraper()

        for market in self.markets:
            market_data = self.get_market_data(market)
            market.horse_number_by_exchange_id = self.extract_number_by_internal_id(market_data)

        self.open_race_connection()
        self.market_opening_request_timer = 0

    def init_race_card_market_map(self) -> None:
        market_retriever = MarketRetriever(self.market_type)
        for race_card in self.upcoming_race_cards.values():
            market = market_retriever.get_market(
                country=race_card.country,
                track_name=race_card.track_name,
                race_number=race_card.race_number,
            )

            if market is not None:
                self.race_card_market_map.add(race_card, market)

    def get_bet_offers(self) -> List[BetOffer]:
        raw_market_offer = self.poll_raw_market_offer()
        if raw_market_offer is not None:
            return self.raw_market_offer_to_bet_offers(raw_market_offer)

        return []

    def raw_market_offer_to_bet_offers(self, raw_market_offer: RawMarketOffer) -> List[BetOffer]:
        race_card = self.race_card_market_map.get_race_card(raw_market_offer.market)

        bet_offers = []

        for horse_number, odds in raw_market_offer.odds_by_horse_number.items():
            if odds > 0:
                horse = race_card.get_horse_by_number(int(horse_number))

                if horse is None:
                    print(f"Horse nr. not found: {horse_number}, at race: {race_card.race_id}")
                else:
                    new_offer = BetOffer(
                        race_card=race_card,
                        horse=horse,
                        odds=odds,
                        scratched_horses=self.scratched_horses[race_card],
                        event_datetime=datetime.now(),
                        adjustment_factor=1.0,
                    )

                    bet_offers.append(new_offer)

        return bet_offers

    def get_odds_by_horse_number_from_message(self, market: Market, message) -> Dict[str, float]:
        odds_by_internal_id = self.extract_odds_by_internal_id(message)

        exchange_odds = {
            market.horse_number_by_exchange_id[internal_id]: odds_by_internal_id[internal_id]
            for internal_id in odds_by_internal_id
        }

        return exchange_odds

    def get_market_from_message(self, message) -> Market:
        for market in self.markets:
            if market.market_id == message["id"]:
                return market

    def open_race_connection(self) -> None:
        self.web_socket.connect(
            url="wss://exch.piwi247.com/customer/ws/multiple-market-prices/585/e95aa9c5-7a6e-40cd-8060-4de2f796e09d/websocket",
            cookie=f"BIAB_CUSTOMER={self.customer_id}",
        )
        self.web_socket.recv()

        self.send_market_opening_request()

    def send_market_opening_request(self) -> None:
        opening_request = '["['

        for market in self.markets:
            opening_request += '{\\"marketId\\":\\"'
            opening_request += market.market_id
            opening_request += '\\",\\"eventId\\":\\"'
            opening_request += market.event_id
            opening_request += '\\",\\"applicationType\\":\\"WEB\\"}'

            if market != self.markets[-1]:
                opening_request += ","

        opening_request += ']"]'
        self.web_socket.send(opening_request)

    def close_race_connection(self):
        self.web_socket.close()

    def poll_raw_market_offer(self) -> RawMarketOffer:
        self.market_opening_request_timer += 1

        if self.market_opening_request_timer > 600:
            self.market_opening_request_timer = 0
            self.send_market_opening_request()

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

                self.close_race_connection()
                self.open_race_connection()

            except WebSocketTimeoutException as error:
                print("Websocket timed out. Trying to reconnect...")

                self.close_race_connection()
                self.open_race_connection()

        if message == "h":
            return None

        message = json.loads(json.loads(message[2:-1]))

        if "rc" not in message:
            return None

        market = self.get_market_from_message(message)
        odds_by_horse_number = self.get_odds_by_horse_number_from_message(market, message)

        # scratched_horses = self.get_scratched_horses(message)
        #
        # if scratched_horses:
        #     self.scratched_horses[self.race_card_market_map.get_race_card(market)] = scratched_horses

        return RawMarketOffer(market, odds_by_horse_number)

    def get_scratched_horses(self, message: dict) -> List[str]:
        scratched_horses = []
        if "marketDefinition" in message:
            market_definition = message["marketDefinition"]
            if "runners" in market_definition:
                for runner in market_definition["runners"]:
                    if runner["status"] == "REMOVED":
                        scratched_horses.append(runner["name"])

        return scratched_horses

    def extract_odds_by_internal_id(self, current_odds_data: dict) -> dict:
        odds_by_internal_id = {}
        for horse_data in current_odds_data["rc"]:
            odds_by_internal_id[horse_data["id"]] = horse_data["bdatb"][0]["odds"]

        return odds_by_internal_id

    def get_market_data(self, market: Market) -> dict:
        return self.scraper.request_data(
            url=f"https://exch.piwi247.com/customer/api/market/{market.market_id}"
        )

    def extract_number_by_internal_id(self, market_data: dict) -> dict:
        number_by_internal_id = {}
        for horse_data in market_data["runners"]:
            number_by_internal_id[horse_data["selectionId"]] = horse_data["metadata"]["CLOTH_NUMBER_ALPHA"]

        return number_by_internal_id

    def delete_markets(self, deleted_race_card: RaceCard) -> None:
        self.race_card_market_map.delete(deleted_race_card)

        self.markets = self.race_card_market_map.get_markets()

        self.close_race_connection()
        self.open_race_connection()


if __name__ == "__main__":
    ex_odds_requester = ExchangeOfferRequester(
        event_id="32009638",
        market_id="1.208384078"
    )
    odds = ex_odds_requester.get_odds_by_horse_number_from_message()
    print(odds)
