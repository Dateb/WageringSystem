from datetime import date, timedelta
from DataCollection.DayCollector import DayCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Persistence.RaceCardPersistence import RaceCardsPersistence


class TrainDataCollector:

    __TIME_OF_A_DAY = timedelta(days=1)

    def __init__(self, file_name: str):
        self.__race_cards_persistence = RaceCardsPersistence(file_name)

        initial_race_cards = self.__race_cards_persistence.load_every_month_non_writable()
        self.collected_days = {initial_race_cards[datetime].date for datetime in initial_race_cards}

        self.__race_cards_collector = FullRaceCardsCollector()
        self.__day_collector = DayCollector()

    def collect(self, query_date: date):
        newest_train_date = query_date
        if len(self.collected_days) > 0:
            newest_train_date = max(self.collected_days)

        if newest_train_date > query_date:
            self.collect_forward_until_newest_date(query_date, newest_train_date)

        self.__collect_backwards_from_query_date(query_date)

    def collect_forward_until_newest_date(self, query_date: date, newest_date: date):
        print(f"Forward collecting to date: {newest_date}")
        scraping_date = query_date
        while scraping_date != newest_date:
            if scraping_date not in self.collected_days:
                self.collect_day(scraping_date)
            scraping_date += self.__TIME_OF_A_DAY

    def __collect_backwards_from_query_date(self, query_date: date):
        print(f"Backward collecting from date: {query_date}")
        scraping_date = query_date
        while True:
            if scraping_date not in self.collected_days:
                self.collect_day(scraping_date)
            scraping_date -= self.__TIME_OF_A_DAY

    def collect_day(self, race_date: date):
        print(f"Currently collecting:{race_date}")
        race_ids = self.__day_collector.get_closed_race_ids_of_day(race_date)
        new_race_cards = self.__race_cards_collector.collect_race_cards_from_race_ids(race_ids)
        self.collected_days.add(race_date)

        if len(race_ids) > 0:
            self.__race_cards_persistence.save(new_race_cards)


def main():
    train_data_collector = TrainDataCollector(file_name="race_cards")

    query_date = date(
        year=2015,
        month=3,
        day=1,
    )

    train_data_collector.collect(query_date)
    #train_data_collector.collect_day(query_date)


if __name__ == '__main__':
    main()


