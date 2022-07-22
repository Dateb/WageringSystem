import math
import re
from datetime import datetime, timedelta
from typing import List

from DataCollection.Scraper import get_scraper
from bs4 import BeautifulSoup

from Persistence.JSONPersistence import JSONPersistence


class WinTimeFactory:

    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_results_url = "https://t.attheraces.com/results"
        self.__soup = None

    def get_win_times_of_date(self, date: str):
        self.__soup = self.__get_soup_from_date(date)
        track_names = self.__get_track_names()

        return self.__get_win_times_of_tracks(track_names)

    def __get_soup_from_date(self, date: str) -> BeautifulSoup:
        win_times_url = f"{self.__base_results_url}/{date}"
        result_doc = self.__scraper.request_html(win_times_url)

        return BeautifulSoup(result_doc, 'html.parser')

    def __get_track_names(self) -> List[str]:
        track_titles = [header.text for header in self.__soup.find_all("h2") if "h6" in header["class"]]
        track_names = [re.search('\r\n                (.+?) Results', track_title).group(1) for track_title in track_titles]
        gb_track_names = [track_name for track_name in track_names if "(" not in track_name]

        return gb_track_names

    def __get_win_times_of_tracks(self, track_names: List[str]) -> dict:
        win_times = {}
        for track_name in track_names:
            win_times[track_name] = {}
            there_are_win_times_left = True
            race_number = 1
            while there_are_win_times_left:
                article = self.__find_article_of_race(track_name, race_number)
                if article is None:
                    there_are_win_times_left = False
                else:
                    win_times[track_name][race_number] = {}

                    win_time_text = self.__find_win_time_text(article)
                    win_times[track_name][race_number]["win_time"] = self.__win_time_text_to_seconds(win_time_text)

                    distance_text = self.__find_distance_text(article)
                    print(distance_text)
                    win_times[track_name][race_number]["distance"] = self.__distance_text_to_meters(distance_text)

                    class_text = self.__find_class_text(article)
                    win_times[track_name][race_number]["class"] = class_text

                    race_number += 1

        return win_times

    def __find_article_of_race(self, track_name: str, race_number: int):
        for link in self.__soup.find_all('a', href=True):
            if self.__link_corresponds_to_race(link, track_name, race_number):
                return link.findParent("article")

    def __find_win_time_text(self, article) -> str:
        win_time_bold_elem = [bold_elem for bold_elem in article.find_all("b") if "Win Time" in bold_elem.text]
        if not win_time_bold_elem:
            return "0m -1s"
        win_time_div = win_time_bold_elem[0].findParent("div")
        win_time_start_idx = self.__find_win_time_start_idx(win_time_div.text)
        win_time_end_idx = win_time_div.text.find("s") + 1

        return win_time_div.text[win_time_start_idx:win_time_end_idx]

    def __find_distance_text(self, article) -> str:
        distance_span_elem = [span_elem for span_elem in article.find_all("span") if len(span_elem.text) > 1
                              and (span_elem.text[-1] == "f" or span_elem.text[-1] == "m")
                              and (span_elem.text[-2].isdigit() or span_elem.text[-2] == "½")]
        if not distance_span_elem:
            return "0f"
        return distance_span_elem[0].text

    def __find_class_text(self, article) -> str:
        class_span_elem = [span_elem for span_elem in article.find_all("span") if "Class " in span_elem.text]
        if not class_span_elem:
            return "-1"
        class_begin_idx = class_span_elem[0].text.rindex("Class")

        return class_span_elem[0].text[class_begin_idx + len("Class") + 1]

    def __distance_text_to_meters(self, distance_text: str) -> int:
        distance_text = distance_text.replace("½", ".5")
        distance_split = distance_text.split(sep=" ")
        if len(distance_split) > 1:
            miles = distance_split[0][:-1]
            furlongs = distance_split[1][:-1]
        else:
            unit = distance_split[0][-1]
            if unit == "m":
                miles = distance_split[0][:-1]
                furlongs = "0"
            else:
                miles = "0"
                furlongs = distance_split[0][:-1]
        return math.floor(float(miles) * 1609.34 + float(furlongs) * 201.168)

    def __link_corresponds_to_race(self, link, track_name: str, race_number: int) -> bool:
        track_name = track_name.replace(" ", "-")
        if f"/racecard/{track_name}" not in link['href']:
            return False

        if "button" in link["class"]:
            return False

        link_number = int(link.findPrevious().text)

        return link_number == race_number

    def __find_win_time_start_idx(self, div_text: str) -> int:
        for i, c in enumerate(div_text):
            if c.isdigit():
                return i

    def __win_time_text_to_seconds(self, win_time_text: str) -> float:
        return self.__get_minutes_of_win_time(win_time_text) * 60 + self.__get_seconds_of_win_time(win_time_text)

    def __get_minutes_of_win_time(self, win_time_text: str) -> int:
        start_idx = 0
        end_idx = win_time_text.find("m")

        return int(win_time_text[start_idx:end_idx])

    def __get_seconds_of_win_time(self, win_time_text: str) -> float:
        start_idx = win_time_text.find(" ") + 1
        end_idx = len(win_time_text) - 1

        return float(win_time_text[start_idx:end_idx])


def main():
    persistence = JSONPersistence("win_times_contextualized")
    win_time_factory = WinTimeFactory()

    win_times = persistence.load()
    base = datetime.strptime('2022-06-07', "%Y-%m-%d").date()
    dates = [base - timedelta(days=x) for x in range(6000)]
    for date in dates:
        date = str(date)
        print(date)
        if date not in win_times:
            win_times[date] = win_time_factory.get_win_times_of_date(date)
            persistence.save(win_times)


if __name__ == '__main__':
    main()
    print("finished")
