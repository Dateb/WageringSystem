from DataCollection.BHA.fetch import BHAInjector
from Persistence.RaceCardPersistence import RaceDataPersistence


def main():
    race_cards_persistence = RaceDataPersistence(data_dir_name="raw_race_cards_dev")

    injector = BHAInjector()

    race_card_file_names = race_cards_persistence.race_data_file_names

    for raw_races in race_cards_persistence:
        race_cards = race_cards_persistence.raw_races_to_race_cards(raw_races, race_cards_persistence.create_writable_race_card)
        print(f"Currently at {list(race_cards.keys())[0]}")

        # previous_day = list(race_cards.keys())[0].split(' ')[0]
        # print(previous_day)
        for race_date, race_card in race_cards.items():
            if race_card.country == "GB":
                if not race_card.race_class:
                    injection_successful = injector.inject(race_card)
                    if injection_successful:
                        print(f"Repaired race card: {race_card.race_id}")
                        race_cards_persistence.save(list(race_cards.values()))
                    else:
                        print(f"Could not repair race card: {race_card.race_id}")


if __name__ == '__main__':
    main()
    print('finished')