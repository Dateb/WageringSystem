import json
from typing import Dict

import websocket

from DataCollection.Scraper import get_scraper


class ExchangeOddsRequester:

    def __init__(self, event_id: str, market_id: str):
        websocket.enableTrace(True)
        self.web_socket = websocket.WebSocket()
        self.scraper = get_scraper()

        self.event_id = event_id
        self.market_id = market_id

        self.current_odds_data = self.get_current_odds_data()
        self.market_data = self.get_market_data()

        self.current_odds = self.get_odds_from_exchange()

    def get_odds_from_exchange(self) -> Dict[str, float]:
        odds_by_internal_id = self.extract_odds_by_internal_id(self.current_odds_data)
        number_by_internal_id = self.extract_number_by_internal_id(self.market_data)

        exchange_odds = {
            number_by_internal_id[internal_id]: odds_by_internal_id[internal_id] for internal_id in number_by_internal_id
        }

        return exchange_odds

    def get_current_odds_data(self) -> dict:
        self.web_socket.connect(url="wss://exch.piwi247.com/customer/ws/market-prices/223/hsosmrv2/websocket")
        self.web_socket.recv()

        request = '["{\\"eventId\\":\\"'
        request += self.event_id
        request += '\\",\\"marketId\\":\\"'
        request += self.market_id
        request += '\\",\\"applicationType\\":\\"WEB\\"}"]'
        self.web_socket.send(request)

        raw_odds_message = self.web_socket.recv()
        self.web_socket.close()

        current_odds_data = json.loads(json.loads(raw_odds_message[2:-1]))

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


if __name__ == "__main__":
    ex_odds_requester = ExchangeOddsRequester(
        event_id="32009638",
        market_id="1.208384078"
    )
    odds = ex_odds_requester.get_odds_from_exchange()
    print(odds)
