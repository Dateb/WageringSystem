from typing import List

from tqdm import tqdm
from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.RaceHistory import RaceHistory
from DataCollection.RawRaceCard import RawRaceCard
from Persistence.RaceHistoryPersistence import RaceHistoryPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence


class RaceHistoryCollector:
    def __init__(self, raw_race_cards: List[RawRaceCard], initial_race_histories: List[RaceHistory] = None):
        self.__race_histories = [] if initial_race_histories is None else initial_race_histories
        self.__discovered_subject_ids = [race_history.subject_id for race_history in self.__race_histories] + ["0"]
        self.__raw_race_cards = raw_race_cards
        self.__form_guide_factory = FormGuideFactory()
        self.__is_done = False

    def collect(self, n_subjects: int = 10):
        n_new_subjects = 0
        for i in range(len(self.__raw_race_cards)):
            raw_race_card = self.__raw_race_cards[i]
            new_subject_ids = [subject_id for subject_id in raw_race_card.subject_ids
                               if str(subject_id) not in self.__discovered_subject_ids]

            if len(new_subject_ids) > 0:
                print(f"race: {i + 1}/{len(self.__raw_race_cards)}")

            self.__race_histories += [self.__create_race_history(subject_id) for subject_id in new_subject_ids]
            self.__discovered_subject_ids += new_subject_ids
            n_new_subjects += len(new_subject_ids)
            if n_new_subjects >= n_subjects:
                return 0

        self.__is_done = True

    def __create_race_history(self, subject_id: str) -> RaceHistory:
        form_guide = self.__form_guide_factory.run(subject_id)
        past_race_ids = form_guide.gb_past_race_ids

        new_race_history = RaceHistory(subject_id, past_race_ids)
        return new_race_history

    @property
    def race_histories(self):
        return self.__race_histories

    @property
    def is_done(self):
        return self.__is_done


def scrape_race_histories(raw_race_cards):
    persistence = RaceHistoryPersistence()
    initial_race_histories = persistence.load()
    race_histories_collector = RaceHistoryCollector(raw_race_cards, initial_race_histories)
    race_histories_collector.collect()
    persistence.save(race_histories_collector.race_histories)

    return not race_histories_collector.is_done


def main():
    raw_race_cards = RawRaceCardsPersistence().load()

    while scrape_race_histories(raw_race_cards):
        pass

    print("Collected race histories of every race!")


if __name__ == '__main__':
    main()
