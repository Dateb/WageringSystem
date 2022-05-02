from typing import List

from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.RawRaceCard import RawRaceCard
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence


class PastRacesCollector:
    def __init__(self, raw_race_cards: List[RawRaceCard], initial_past_races: dict):
        self.__past_races = initial_past_races
        self.__raw_race_cards = raw_race_cards
        self.__raw_race_card_factory = RawRaceCardFactory()
        self.__form_guide_factory = FormGuideFactory()
        self.__is_done = False

    def collect(self, n_past_races: int = 100):
        n_new_past_races = 0
        for i, raw_race_card in enumerate(self.__raw_race_cards):
            race_id = raw_race_card.race_id
            for horse_id in raw_race_card.horses:
                if not raw_race_card.is_horse_scratched(horse_id):
                    subject_id = raw_race_card.get_subject_id_of_horse(horse_id)
                    past_race_key = str((race_id, subject_id, 1))
                    if past_race_key not in self.__past_races:
                        self.__past_races[past_race_key] = self.__create_past_race(race_id, subject_id)
                        n_new_past_races += 1

                    if n_new_past_races >= n_past_races:
                        print(f"race: {i + 1}/{len(self.__raw_race_cards)}")
                        return 0

        self.__is_done = True

    def __create_past_race(self, race_id: str, subject_id: str) -> dict:
        print(race_id)
        print(subject_id)

        if subject_id == 0:
            return {"ERROR": "no_past_race"}

        form_guide = self.__form_guide_factory.run(subject_id)
        past_race_ids = form_guide.past_race_ids

        if len(past_race_ids) == 0:
            return {"ERROR": "no_past_race"}

        print(past_race_ids)

        if int(race_id) in past_race_ids:
            idx_current_race = past_race_ids.index(int(race_id))
        else:
            idx_current_race = -1
        idx_past_race = idx_current_race + 1

        if idx_past_race >= len(past_race_ids):
            return {"ERROR": "no_past_race"}

        past_race_id = past_race_ids[idx_past_race]

        return self.__raw_race_card_factory.run(past_race_id).raw_race_data

    @property
    def past_races(self) -> dict:
        return self.__past_races

    @property
    def is_done(self):
        return self.__is_done


def scrape_race_histories(raw_race_cards):
    persistence = PastRacesContainerPersistence()
    initial_past_races = persistence.load().raw_past_races
    race_histories_collector = PastRacesCollector(raw_race_cards, initial_past_races)
    race_histories_collector.collect()
    persistence.save(race_histories_collector.past_races)

    return not race_histories_collector.is_done


def main():
    raw_race_cards = RawRaceCardsPersistence("raw_race_cards").load()

    while scrape_race_histories(raw_race_cards):
        pass

    print("Collected past races of every horse!")


if __name__ == '__main__':
    main()
