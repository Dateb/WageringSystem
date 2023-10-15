import json
from typing import Dict, Tuple

import websocket

from DataCollection.Scraper import get_scraper


class MarketRetriever:

    def __init__(self):
        self.scraper = get_scraper()
        self.today_markets_url = "https://exch.piwi247.com/customer/api/horse-racing/7/all?timeRange=TODAY"
        self.today_markets_raw = self.scraper.request_data(self.today_markets_url)

    def get_event_and_market_id(self, country: str, track_name: str, race_number: int) -> Tuple[str, str]:
        print(country)

        print(self.today_markets_raw)
        for country_data in self.today_markets_raw:
            print(country_data)
            if country in country_data["name"]:
                events_raw = country_data["events"]
                for event_data in events_raw:
                    print(event_data)
                    if track_name in event_data["name"]:
                        market_data = event_data["markets"][race_number - 1]
                        event_id = event_data["id"]

                        market_id_parts = market_data["id"].split(".")

                        market_id = f"{market_id_parts[0]}.{str(int(market_id_parts[1]) + 1)}"

                        return event_id, market_id


class ExchangeOddsRequester:

    def __init__(self, customer_id: str, event_id: str, market_id: str):
        websocket.enableTrace(True)
        self.web_socket = websocket.WebSocket()
        self.scraper = get_scraper()

        self.customer_id = customer_id
        self.event_id = event_id
        self.market_id = market_id

        self.market_data = self.get_market_data()
        print(self.market_data)
        self.horse_number_by_exchange_id = self.extract_number_by_internal_id(self.market_data)

        self.current_odds_data = {}
        self.current_odds = {}
        self.open_race_connection()

    def get_odds_from_exchange(self) -> Dict[str, float]:
        self.open_race_connection()
        self.close_race_connection()
        odds_by_internal_id = self.extract_odds_by_internal_id(self.current_odds_data)

        exchange_odds = {
            self.horse_number_by_exchange_id[internal_id]: odds_by_internal_id[internal_id]
            for internal_id in self.horse_number_by_exchange_id
        }

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

        current_odds_data = json.loads(json.loads(message[2:-1]))

        return current_odds_data

    def extract_odds_by_internal_id(self, current_odds_data: dict) -> dict:
        odds_by_internal_id = {}
        for horse_data in current_odds_data["rc"]:
            odds_by_internal_id[horse_data["id"]] = horse_data["bdatb"][0]["odds"]

        return odds_by_internal_id

    def get_market_data(self) -> dict:
        return self.scraper.request_data(
            url=f"https://exch.piwi247.com/customer/api/market/{self.market_id}"
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
    odds = ex_odds_requester.get_odds_from_exchange()
    print(odds)
