import json
from collections import OrderedDict
from time import sleep
from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning import simulate_conf
from Persistence.RaceCardPersistence import RaceDataPersistence
import requests


class WeatherFetcher:

    API_KEY: str = "6ad7d44b0c7d06cdfb08ec29ec908a43"

    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        with open("../../data/locations.json", "r") as f:
            self.locations = json.load(f)

    def get_weather_data(self, race_cards: List[RaceCard]):
        weather_data = {str(race_card.date): {} for race_card in race_cards}
        for race_card in race_cards:
            weather_data[str(race_card.date)][race_card.track_name] = {}

        request_counter = 0
        for race_card in race_cards:
            weather_attributes = self.fetch_weather_attributes(race_card)
            weather_data[str(race_card.date)][race_card.track_name][str(race_card.race_number)] = weather_attributes
            request_counter += 1
            print(f"requested {request_counter} times...")

        return weather_data

    def fetch_weather_attributes(self, race_card: RaceCard) -> dict:
        post_time = race_card.date_raw
        latitude = self.locations[race_card.track_name]["latitude"]
        longitude = self.locations[race_card.track_name]["longitude"]

        weather_api_url = self.base_url + f"?lat={latitude}&lon={longitude}&dt={post_time}&appid={self.API_KEY}"

        response = requests.get(weather_api_url)
        sleep(0.5)
        if response.status_code != 200:
            raise Exception()

        return response.json()

def main():
    race_cards_persistence = RaceDataPersistence(data_dir_name=simulate_conf.DEV_RACE_CARDS_FOLDER_NAME)
    weather_persistence = RaceDataPersistence(data_dir_name="weather")

    for raw_races in race_cards_persistence:
        current_race_data_file_name = race_cards_persistence.race_data_file_names[race_cards_persistence.iter_idx - 1]
        weather_data = weather_persistence.load_race_data(current_race_data_file_name)

        race_cards = race_cards_persistence.raw_races_to_race_cards(raw_races, race_cards_persistence.create_race_card)
        race_keys_with_weather = []
        for race_key, race_card in race_cards.items():
            if str(race_card.date) in weather_data:
                if race_card.track_name in weather_data[str(race_card.date)]:
                    if str(race_card.race_number) in weather_data[str(race_card.date)][race_card.track_name]:
                        race_keys_with_weather.append(race_key)

        for race_key in race_keys_with_weather:
            race_cards.pop(race_key)

        race_cards = list(OrderedDict(sorted(race_cards.items())).values())
        weather_fetcher = WeatherFetcher()

        while race_cards:
            current_day = race_cards[0].datetime.day
            race_cards_of_day = [race_card for race_card in race_cards if race_card.datetime.day == current_day]

            weather_data = weather_fetcher.get_weather_data(race_cards_of_day)

            weather_persistence.save_date_based_dict(weather_data)
            race_cards = [race_card for race_card in race_cards if race_card not in race_cards_of_day]
            print(f"Finished day: {current_day}, remaining requests: {len(race_cards)}")

            if not race_cards:
                return 0


if __name__ == '__main__':
    main()
    print('finished')
