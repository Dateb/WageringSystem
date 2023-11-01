import json
from datetime import datetime, time
from typing import Dict, Tuple, List

import websocket

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


class MarketRetriever:

    def __init__(self):
        self.scraper = get_scraper()
        self.today_markets_url = self.get_markets_url()
        self.today_markets_raw = self.scraper.request_data(self.today_markets_url)

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
                        base_market_id = market_data["id"]

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
                            if market["marketType"] == "PLACE":
                                place_market_id = market["id"]

                        if place_market_id:
                            return Market(event_id, place_market_id)
                        else:
                            return None


class ExchangeOddsRequester:

    def __init__(self, customer_id: str, markets: List[Market]):
        websocket.enableTrace(False)
        self.web_socket = websocket.WebSocket()
        self.scraper = get_scraper()

        self.customer_id = customer_id
        self.markets = markets

        for market in markets:
            market_data = self.get_market_data(market)
            market.horse_number_by_exchange_id = self.extract_number_by_internal_id(market_data)

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

    def open_race_connection(self) -> RawMarketOffer:
        self.web_socket.connect(
            url="wss://exch.piwi247.com/customer/ws/multiple-market-prices/585/e95aa9c5-7a6e-40cd-8060-4de2f796e09d/websocket",
            cookie=f"BIAB_CUSTOMER={self.customer_id}",
        )
        self.web_socket.recv()

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
        print(opening_request)
        self.web_socket.send(opening_request)

        message = self.web_socket.recv()

        opening_odds_message = json.loads(json.loads(message[2:-1]))

        market = self.get_market_from_message(opening_odds_message)
        odds_by_horse_number = self.get_odds_by_horse_number_from_message(market, opening_odds_message)

        return RawMarketOffer(market, odds_by_horse_number)

    def close_race_connection(self):
        self.web_socket.close()

    def poll_raw_market_offer(self) -> RawMarketOffer:
        message = self.web_socket.recv()

        if message == "h":
            return None

        message = json.loads(json.loads(message[2:-1]))

        if "rc" not in message:
            return None

        market = self.get_market_from_message(message)
        odds_by_horse_number = self.get_odds_by_horse_number_from_message(market, message)

        return RawMarketOffer(market, odds_by_horse_number)

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


if __name__ == "__main__":
    ex_odds_requester = ExchangeOddsRequester(
        event_id="32009638",
        market_id="1.208384078"
    )
    odds = ex_odds_requester.get_odds_by_horse_number_from_message()
    print(odds)
