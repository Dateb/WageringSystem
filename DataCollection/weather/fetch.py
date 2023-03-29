import json
from time import sleep

from DataAbstraction.Present.RaceCard import RaceCard
from Persistence.RaceCardPersistence import RaceCardsPersistence
import requests


class WeatherFetcher:

    API_KEY: str = "6ad7d44b0c7d06cdfb08ec29ec908a43"

    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        with open("../../data/locations.json", "r") as f:
            self.locations = json.load(f)

    def fetch_weather_of_race(self, race_card: RaceCard) -> dict:
        post_time = race_card.date_raw
        latitude = self.locations[race_card.track_name]["latitude"]
        longitude = self.locations[race_card.track_name]["longitude"]

        weather_api_url = self.base_url + f"?lat={latitude}&lon={longitude}&dt={post_time}&appid={self.API_KEY}"

        response = requests.get(weather_api_url)
        sleep(1)
        if response.status_code == 200:
            return response.json()

        raise Exception()


def main():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="race_cards")

    weather_fetcher = WeatherFetcher()
    dummy_race_card = list(race_cards_persistence.load_first_month_writable().values())[0]
    time_form_attributes = weather_fetcher.fetch_weather_of_race(dummy_race_card)
    print(time_form_attributes)


if __name__ == '__main__':
    main()
    print('finished')
