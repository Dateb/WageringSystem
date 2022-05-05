import os

import requests
import time
import random
from requests import Session
from requests_ip_rotator import ApiGateway


class Scraper:
    __HOMEPAGE_URL: str = "https://www.racebets.de"

    __session: Session
    cookie_token_key: str = 'XSRF-TOKEN'
    header_token_key: str = 'X-XSRF-TOKEN'

    def __init__(self, n_request_tries=5):
        self.__n_request_tries = n_request_tries

        self.__gateway = ApiGateway(
            self.__HOMEPAGE_URL,
            access_key_id="AKIAQYYVWP3QQYTJIDWN",#os.environ.get("AWS_ACCESS_KEY_ID"),
            access_key_secret="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",#os.environ.get("AWS_ACCESS_KEY_SECRET"),
        )
        self.__session = requests.Session()

        self.__headers = {
            self.header_token_key: self.__get_api_token(
                "https://www.racebets.de/de/pferdewetten/race/details/id/4347262"
            ),
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        self.__gateway.start()
        self.__session.mount("https://www.racebets.de", self.__gateway)

    def __get_api_token(self, url: str) -> str:
        self.__get_cookies(url)
        header_token = self.__session.cookies[self.cookie_token_key].replace('%3B', ';')
        return header_token

    def __get_cookies(self, url: str) -> dict:
        headers = {
            'Cookie': 'CONSENT=YES+cb.20210418-17-p0.it+FX+917; ',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        return self.__session.get(url, headers=headers).cookies.get_dict()

    def request_data(self, url: str) -> dict:
        result = {}
        for _ in range(self.__n_request_tries):
            response = self.__session.get(url=url, headers=self.__headers)
            self.__wait_random_amount_of_seconds(1.0)
            if response.status_code == 200:
                result = response.json()
                return result

        return result

    def __wait_random_amount_of_seconds(self, average_seconds_to_wait: float):
        lowest_waiting_time = average_seconds_to_wait * 0.9
        highest_waiting_time = average_seconds_to_wait * 1.1
        waiting_time = random.uniform(lowest_waiting_time, highest_waiting_time)
        time.sleep(waiting_time)

    def start(self):
        self.__gateway.start()

    def stop(self):
        self.__gateway.shutdown()


__scraper = Scraper()


def get_scraper() -> Scraper:
    return __scraper


def main():
    for i in range(10):
        response = __scraper.request_data(url="https://www.racebets.de/ajax/races/details/id/2272776?_=1650443717416")
        print(response)
    __scraper.stop()


if __name__ == '__main__':
    main()
