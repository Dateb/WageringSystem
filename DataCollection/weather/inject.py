from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.weather.fetch import WeatherFetcher
from Persistence.RaceCardPersistence import RaceCardsPersistence


class WeatherInjector:

    def __init__(self, weather_fetcher: WeatherFetcher):
        self.weather_fetcher = weather_fetcher

    def inject_weather_of_race(self, race_card: WritableRaceCard) -> bool:
        if "weather" not in race_card.raw_race_card["race"]:
            weather = self.weather_fetcher.fetch_weather_of_race(race_card)
            race_card.raw_race_card["race"]["weather"] = weather["data"][0]

            return True

        return False


def main():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="race_cards")

    weather_fetcher = WeatherFetcher()
    weather_injector = WeatherInjector(weather_fetcher)

    race_card_file_names = race_cards_persistence.race_card_file_names

    for race_card_file_name in reversed(race_card_file_names):
        race_cards = race_cards_persistence.load_race_card_files_writable([race_card_file_name])

        previous_day = list(race_cards.keys())[0].split(' ')[0]
        print(previous_day)
        for race_date, race_card in race_cards.items():
            if weather_injector.inject_weather_of_race(race_card):
                race_day = race_date.split(' ')[0]
                if race_day != previous_day:
                    previous_day = race_day
                    race_cards_persistence.save(list(race_cards.values()))


if __name__ == '__main__':
    main()
    print('finished')
