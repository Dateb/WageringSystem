import json
from datetime import datetime, timedelta
from typing import Dict, Tuple

import numpy as np
import websocket
from numpy import ndarray

from DataCollection.Scraper import get_scraper


class ExchangeOddsRequester:

    def __init__(self, customer_id: str, event_id: str, market_id: str):
        self.web_socket = websocket.WebSocket()
        self.scraper = get_scraper()

        self.customer_id = customer_id
        self.event_id = event_id
        self.market_id = market_id

        self.market_data = self.get_market_data()
        self.horse_number_by_exchange_id = self.extract_number_by_internal_id(self.market_data)

        self.current_odds_data = {}
        self.current_odds = {}
        self.open_race_connection()

    def get_odds_from_exchange(self) -> ndarray:
        self.open_race_connection()
        self.close_race_connection()
        odds_by_internal_id = self.extract_odds_by_internal_id(self.current_odds_data)

        exchange_odds = np.zeros(shape=(len(self.horse_number_by_exchange_id)))
        for internal_id in self.horse_number_by_exchange_id:
            horse_number = int(self.horse_number_by_exchange_id[internal_id])
            exchange_odds[horse_number - 1] = odds_by_internal_id[internal_id]

        return exchange_odds

    def open_race_connection(self):
        self.web_socket.connect(
            url="wss://exch.piwi247.com/customer/ws/market-prices/485/vewdhysm/websocket",
            cookie=f"BIAB_CUSTOMER={self.customer_id}",
        )
        self.web_socket.recv()

        request = '["{\\"eventId\\":\\"'
        request += self.event_id
        request += '\\",\\"marketId\\":\\"'
        request += self.market_id
        request += '\\",\\"applicationType\\":\\"WEB\\"}"]'
        self.web_socket.send(request)
        self.current_odds_data = self.get_current_odds_data()

    def close_race_connection(self):
        self.web_socket.close()

    def get_current_odds_data(self) -> dict:
        message = self.web_socket.recv()

        if message == "h":
            return self.current_odds_data

        print(message)
        current_odds_data = json.loads(json.loads(message[2:-1]))

        return current_odds_data

    def extract_odds_by_internal_id(self, current_odds_data: dict) -> dict:
        odds_by_internal_id = {}
        for horse_data in current_odds_data["rc"]:
            odds_by_internal_id[horse_data["id"]] = horse_data["bdatb"][0]["odds"]

        return odds_by_internal_id

    def get_market_data(self) -> dict:
        return self.scraper.request_data(
            url=f"https://exch.piwi247.com/customer/api/market/{self.market_id}?showGroups=true"
        )

    def extract_number_by_internal_id(self, market_data: dict) -> dict:
        number_by_internal_id = {}
        for horse_data in market_data["runners"]:
            number_by_internal_id[horse_data["selectionId"]] = horse_data["metadata"]["CLOTH_NUMBER_ALPHA"]

        return number_by_internal_id


class MarketRetriever:

    def __init__(self):
        self.scraper = get_scraper()

        self.markets_url = "https://exch.piwi247.com/customer/api/horse-racing/7/all?timeRange=TODAY"
        self.markets_raw = self.scraper.request_data(self.markets_url)
        self.events_raw = self.get_events()

        if self.events_raw is None:
            self.markets_url = "https://exch.piwi247.com/customer/api/horse-racing/7/all?timeRange=TOMORROW"
            self.markets_raw = self.scraper.request_data(self.markets_url)
            self.events_raw = self.get_events()

        if self.events_raw is None:
            print("Cannot find events today or tomorrow in GB")

    def get_events(self) -> dict:
        for country_data in self.markets_raw:
            if "GB" in country_data["name"]:
                return country_data["events"]

    def get_event_and_market_id(self, track_name: str, start_time: int) -> Tuple[str, str]:
        for event_data in self.events_raw:
            if track_name in event_data["name"]:
                for market_data in event_data["markets"]:
                    if market_data["startTime"] / 1000 == start_time:
                        event_id = event_data["id"]

                        date_time_obj = datetime.fromtimestamp(start_time) - timedelta(hours=2)
                        market_request_time_substr = f"{str(date_time_obj.hour).rjust(2, '0')}{str(date_time_obj.minute).rjust(2, '0')}"
                        markets_of_race_url = f"https://exch.piwi247.com/customer/api/race/{event_id}.{market_request_time_substr}"
                        markets_of_race_raw = self.scraper.request_data(markets_of_race_url)

                        for market_raw in markets_of_race_raw["children"]:
                            if market_raw["name"] == "To Be Placed":
                                place_market_id = market_raw["id"]

                                return event_id, place_market_id


if __name__ == "__main__":
    ex_odds_requester = ExchangeOddsRequester(
        event_id="32009638",
        market_id="1.208384078"
    )
    odds = ex_odds_requester.get_odds_from_exchange()
    print(odds)
