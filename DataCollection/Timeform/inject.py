from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.Timeform.fetch import TimeFormFetcher, ResultTimeformFetcher
from Persistence.RaceCardPersistence import RaceCardsPersistence


class TimeFormInjector:

    def __init__(self, time_form_collector: TimeFormFetcher):
        self.time_form_collector = time_form_collector

    def inject_time_form_attributes(self, race_card: WritableRaceCard) -> None:
        time_form_attributes = self.time_form_collector.get_time_form_attributes(race_card)
        print(time_form_attributes)

        if time_form_attributes is not None:
            self.write_race_results(race_card, time_form_attributes)
            self.write_race_attributes(race_card, time_form_attributes)
            self.write_horse_attributes(race_card, time_form_attributes)

    def write_race_results(self, race_card: WritableRaceCard, time_form_attributes: dict):
        if race_card.has_results:
            raw_result = race_card.raw_race_card["result"]

            for result_attribute in time_form_attributes["result"]:
                old_value = None
                if result_attribute in raw_result:
                    old_value = raw_result[result_attribute]

                new_value = time_form_attributes["result"][result_attribute]
                raw_result[result_attribute] = new_value

                if old_value != new_value:
                    print(f"Changed attribute {result_attribute}: {old_value} -> {new_value}")

    def write_race_attributes(self, race_card: WritableRaceCard, time_form_attributes: dict):
        raw_race = race_card.raw_race_card["race"]
        for race_attribute in time_form_attributes["race"]:
            new_value = time_form_attributes["race"][race_attribute]
            raw_race[race_attribute] = new_value

        raw_race["timeFormInjected"] = True

    def write_horse_attributes(self, race_card: WritableRaceCard, time_form_attributes: dict):
        for horse_name in time_form_attributes["horses"]:
            horse = race_card.get_horse_by_name(horse_name)

            if horse is None:
                print(f"Horse name not found: {horse_name}, try to find horse by jockey...")
                jockey_name = time_form_attributes["horses"][horse_name]["util"]["jockey_name"]
                horse = race_card.get_horse_by_jockey(jockey_name)
                if horse is None:
                    raise ValueError

            for horse_attribute in time_form_attributes["horses"][horse_name]["to_inject"]:
                horse.raw_data[horse_attribute] = time_form_attributes["horses"][horse_name]["to_inject"][horse_attribute]


def main():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="race_cards")

    time_form_fetcher = ResultTimeformFetcher()
    time_form_injector = TimeFormInjector(time_form_fetcher)
    for race_cards in race_cards_persistence:
        is_injection_executed = False
        print(list(race_cards.keys())[0])
        for race_card in race_cards.values():
            raw_race = race_card.raw_race_card["race"]
            if "timeFormInjected" not in raw_race or not raw_race["timeFormInjected"]:
                is_injection_executed = True
                if time_form_fetcher.has_race_series_changed(race_card):
                    race_cards_persistence.save(list(race_cards.values()))
                time_form_injector.inject_time_form_attributes(race_card)

        if is_injection_executed:
            race_cards_persistence.save(list(race_cards.values()))


def reset_injection_flag():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="race_cards")

    for race_cards in race_cards_persistence:
        print(list(race_cards.keys())[0])
        for race_card in race_cards.values():
            raw_race = race_card.raw_race_card["race"]
            if "timeFormInjected" in raw_race or not raw_race["timeFormInjected"]:
                raw_race["timeFormInjected"] = False

        race_cards_persistence.save(list(race_cards.values()))


if __name__ == '__main__':
    main()
    # reset_injection_flag()
    print('finished')
