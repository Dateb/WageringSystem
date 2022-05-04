from datetime import date, timedelta

from typing import List

from DataCollection.Scraper import get_scraper


class DayCollector:

    def __init__(self):
        self.__scraper = get_scraper()

    def get_race_ids_of_day(self, day: date) -> List[str]:
        race_ids = []
        api_url = f"https://www.racebets.de/ajax/events/calendar/date/{str(day)}?_=1651490197128"
        calendar_data = self.__scraper.request_data(api_url)

        race_series_list = self.__get_race_series_from_calendar_data(calendar_data)
        for race_series in race_series_list:
            race_ids += self.__get_race_ids_from_race_series(race_series)

        return race_ids

    def __get_race_series_from_calendar_data(self, calendar_data: dict) -> List[dict]:
        race_series_list = []
        del calendar_data["calendarDates"]
        for race_series_key in calendar_data:
            race_series = calendar_data[race_series_key]
            if race_series["country"] == "GB" and race_series["raceType"] in ["G", "J"] and not race_series["specialBetsEvent"]:
                race_series_list.append(race_series)

        return race_series_list

    def __get_race_ids_from_race_series(self, race_series: dict) -> List[str]:
        return [race["idRace"] for race in race_series["relatedRaces"] if race["raceStatus"] == "OPN"]


def main():
    day_collector = DayCollector()
    start_date = date(2019, 4, 13)
    end_date = date(2019, 4, 16)
    print(day_collector.get_race_ids_from_date_interval(start_date, end_date))


if __name__ == '__main__':
    main()
