from datetime import date, timedelta

from typing import List

from DataCollection.Scraper import get_scraper


class DayCollector:

    def __init__(self):
        self.__scraper = get_scraper()

    def get_closed_race_ids_of_day(self, day: date) -> List[str]:
        races = self.__get_races_of_day(day)

        race_ids = [race["idRace"] for race in races if race["raceStatus"] in ["FNL", "TMP"]]

        return race_ids

    def get_open_race_ids_of_day(self, day: date) -> List[str]:
        races = self.__get_races_of_day(day)
        print(races)

        race_ids = [race["idRace"] for race in races if race["raceStatus"] == "OPN"]

        return race_ids

    def get_race_ids_of_tomorrow(self) -> List[str]:
        tomorrow = date.today() + timedelta(days=1)
        races = self.__get_races_of_day(tomorrow)

        return [race["idRace"] for race in races]

    def __get_races_of_day(self, day: date) -> List[dict]:
        race_series_list = self.__get_race_series_of_day(day)
        races = []
        for race_series in race_series_list:
            races += race_series["relatedRaces"]

        return races

    def __get_race_series_of_day(self, day: date) -> List[dict]:
        api_url = f"https://www.racebets.de/ajax/events/calendar/date/{str(day)}?_=1651490197128"
        calendar_data = self.__scraper.request_data(api_url)

        return self.__get_race_series_from_calendar_data(calendar_data)

    def __get_race_series_from_calendar_data(self, calendar_data: dict) -> List[dict]:
        race_series_list = []
        del calendar_data["calendarDates"]
        for race_series_key in calendar_data:
            race_series = calendar_data[race_series_key]
            if race_series["country"] == "GB" and race_series["raceType"] in ["G", "J"] and not race_series["specialBetsEvent"] and "PMU" not in race_series["title"]\
                    and race_series["title"] != "Down Royal":
                race_series_list.append(race_series)

        return race_series_list


def main():
    day_collector = DayCollector()
    start_date = date(2022, 5, 5)

    closed_race_ids = day_collector.get_closed_race_ids_of_day(start_date)
    open_race_ids = day_collector.get_open_race_ids_of_day(start_date)
    print(closed_race_ids)
    print(len(closed_race_ids))
    print(open_race_ids)
    print(len(open_race_ids))


if __name__ == '__main__':
    main()
