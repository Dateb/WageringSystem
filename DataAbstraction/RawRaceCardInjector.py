from datetime import datetime, timedelta, date
from typing import List

from DataAbstraction.WinTimesFactory import WinTimesFactory
from DataCollection.FormGuide import FormGuide
from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from Persistence.JSONPersistence import JSONPersistence
from Persistence.RaceCardPersistence import RaceCardsPersistence
from util.speed_calculator import race_card_track_to_win_time_track


class RawRaceCardInjector:

    def __init__(self, race_card: WritableRaceCard):
        self.__race_card = race_card
        self.__persistence = JSONPersistence("win_times_contextualized")
        self.__win_times = self.__persistence.load()
        self.__win_times_factory = WinTimesFactory()

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card


def main():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="race_cards")

    for race_cards in race_cards_persistence:
        print(list(race_cards.keys())[0])
        for date_time in race_cards:
            injector = RawRaceCardInjector(race_cards[date_time])

        race_cards_persistence.save(list(race_cards.values()))


if __name__ == '__main__':
    main()
    print('finished')
