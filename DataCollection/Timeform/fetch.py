import math
from abc import abstractmethod, ABC
from datetime import date

from bs4 import BeautifulSoup

from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.Scraper import get_scraper
from DataCollection.current_races.fetch import TodayRaceCardsFetcher


class TimeFormFetcher(ABC):

    time_form_track_name_code = {
        "ascot": 1,
        "ayr": 2,
        "bangor-on-dee": 3,
        "bath": 4,
        "beverley": 5,
        "brighton": 6,
        "carlisle": 7,
        "cartmel": 8,
        "catterick-bridge": 9,
        "cheltenham": 10,
        "chepstow": 11,
        "chester": 12,
        "exeter": 13,
        "doncaster": 14,
        "musselburgh": 15,
        "epsom-downs": 16,
        "fakenham": 17,
        "fontwell-park": 19,
        "goodwood": 20,
        "hamilton-park": 21,
        "haydock-park": 22,
        "hereford": 23,
        "hexham": 24,
        "huntingdon": 25,
        "kelso": 26,
        "kempton-park": 27,
        "chelmsford-city": 28,
        "leicester": 29,
        "lingfield-park": 30,
        "aintree": 31,
        "ludlow": 32,
        "market-rasen": 33,
        "newbury": 34,
        "newcastle": 35,
        "newmarket": 36,
        "newton-abbot": 37,
        "nottingham": 38,
        "perth": 39,
        "plumpton": 40,
        "pontefract": 41,
        "redcar": 42,
        "ripon": 43,
        "salisbury": 44,
        "sandown-park": 45,
        "sedgefield": 46,
        "southwell": 47,
        "stratford-on-avon": 48,
        "taunton": 49,
        "ffos-las": 50,
        "thirsk": 51,
        "towcester": 52,
        "uttoxeter": 53,
        "warwick": 54,
        "wetherby": 55,
        "wincanton": 56,
        "windsor": 57,
        "wolverhampton": 58,
        "worcester": 59,
        "yarmouth": 61,
        "york": 62,
    }

    def __init__(self):
        self.scraper = get_scraper()
        self.base_time_form_url = "https://www.timeform.com/horse-racing"
        self.current_track_name = ""
        self.current_date = None

    def get_time_form_attributes(self, race_card: WritableRaceCard):
        time_form_attributes = {
            "race": {},
            "horses": {},
            "result": {},
        }
        time_form_soup = self.get_time_form_soup(race_card)
        time_form_attributes["result"]["winTimeSeconds"] = self.get_win_time(time_form_soup)
        time_form_attributes["race"]["distance"] = self.get_distance(time_form_soup)

        for horse_row in self.get_horse_rows(time_form_soup):
            horse_number = self.get_horse_number(horse_row)
            equip_code = self.get_equip_code(horse_row)
            rating = self.get_rating(horse_row)

            time_form_attributes["horses"][horse_number] = {
                "equipCode": equip_code,
                "rating": rating,
            }

        return time_form_attributes

    def get_time_form_soup(self, race_card: WritableRaceCard):
        time_form_url = self.base_time_form_url
        track_name = self.track_name_to_timeform_name(race_card.track_name)

        if self.has_race_series_changed(race_card):
            self.current_track_name = track_name
            self.current_date = race_card.date

        time_form_url += f"/{track_name}"
        time_form_url += f"/{race_card.date}"
        time_form_url += f"/{race_card.datetime.hour}{race_card.datetime.minute}"
        time_form_url += f"/{self.get_code_of_track_name(track_name, race_card.date)}"
        time_form_url += f"/{race_card.race_number}"

        print(time_form_url)

        result_doc = self.scraper.request_html(time_form_url)

        return BeautifulSoup(result_doc, 'html.parser')

    def win_time_to_seconds(self, win_time: str) -> float:
        if not win_time:
            return -1
        return self.get_minutes_of_win_time(win_time) * 60 + self.get_seconds_of_win_time(win_time)

    def get_minutes_of_win_time(self, win_time: str) -> int:
        start_idx = 0
        end_idx = win_time.find("m")

        if end_idx == -1:
            return 0

        return int(win_time[start_idx:end_idx])

    def get_seconds_of_win_time(self, win_time: str) -> float:
        start_idx = win_time.find(" ") + 1
        end_idx = len(win_time) - 1

        return float(win_time[start_idx:end_idx])

    def get_distance(self, time_form_soup) -> int:
        distance = time_form_soup.find("span", {"title": "Distance expressed in miles, furlongs and yards"}).text
        return self.distance_to_meters(distance)

    def distance_to_meters(self, distance: str) -> int:
        distance_amount_per_unit = {
            "m": 0,
            "f": 0,
            "y": 0,
        }

        distance_split = distance.split(sep=" ")

        for distance_unit in distance_split:
            unit = distance_unit[-1]
            distance_amount = distance_unit[:-1]
            if distance_amount.isnumeric() and unit in distance_amount_per_unit:
                distance_amount_per_unit[unit] = float(distance_amount)

        distance_in_metres = distance_amount_per_unit["m"] * 1609.34 + distance_amount_per_unit["f"] * 201.168 \
                             + distance_amount_per_unit["y"] * 0.9144

        return math.floor(distance_in_metres)

    def get_code_of_track_name(self, track_name: str, day_of_race: date) -> int:
        track_code = self.time_form_track_name_code[track_name]
        if track_name == "newmarket" and day_of_race.month in [6, 7, 8] and day_of_race.year in [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]:
            track_code = 60
        return track_code

    def track_name_to_timeform_name(self, track_name: str) -> str:
        if "PMU" in track_name:
            track_name = track_name[:-4]
        if track_name == "Lingfield":
            track_name = "Lingfield-Park"
        if track_name == "Kempton" or track_name == "Kempton PMU":
            track_name = "Kempton-Park"
        if track_name == "Haydock":
            track_name = "Haydock-Park"
        if track_name == "Sandown":
            track_name = "Sandown-Park"
        if track_name == "Fontwell":
            track_name = "Fontwell-Park"
        if track_name in ["Catterick", "Catterrick"]:
            track_name = "Catterick-Bridge"
        if track_name in ["Chelmsford City", "Chelmsford", "Chelmsford PMU"]:
            track_name = "chelmsford-city"
        if track_name == "Market Rasen":
            track_name = "market-rasen"
        if track_name == "Ffos Las":
            track_name = "ffos-las"
        if track_name == "Bangor":
            track_name = "Bangor-On-Dee"
        if track_name == "Newton Abbot":
            track_name = "newton-abbot"
        if track_name == "Stratford":
            track_name = "Stratford-On-Avon"
        if track_name == "Epsom":
            track_name = "epsom-downs"
        if track_name == "Hamilton":
            track_name = "Hamilton-Park"
        if track_name in ["Royal Ascot", "Ascot Champions Day"]:
            track_name = "Ascot"
        if track_name == "Carlise":
            track_name = "Carlisle"
        if track_name == "Glorious Goodwood":
            track_name = "Goodwood"
        return track_name.lower()

    def has_race_series_changed(self, race_card: WritableRaceCard):
        track_name = self.track_name_to_timeform_name(race_card.track_name)
        return track_name != self.current_track_name or race_card.date != self.current_date

    @abstractmethod
    def get_horse_rows(self, time_form_soup: BeautifulSoup):
        pass

    @abstractmethod
    def get_horse_number(self, horse_row: BeautifulSoup):
        pass

    @abstractmethod
    def get_equip_code(self, horse_row: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def get_rating(self, horse_row: BeautifulSoup) -> int:
        pass

    @abstractmethod
    def get_win_time(self, time_form_soup: BeautifulSoup) -> float:
        pass


class ResultTimeformFetcher(TimeFormFetcher):

    def __init__(self):
        super().__init__()
        self.base_time_form_url = f"{self.base_time_form_url}/result"

    def get_horse_rows(self, time_form_soup: BeautifulSoup):
        return time_form_soup.find_all("tbody", {"class": "rp-table-row"})

    def get_horse_number(self, horse_row: BeautifulSoup) -> int:
        return int(horse_row.find("a", {"class": "rp-horse"}).text.split(".")[0])

    def get_equip_code(self, horse_row: BeautifulSoup) -> str:
        return horse_row.find_all("td", {"class": "rp-ageequip-hide"})[2].text[1:-1]

    def get_rating(self, horse_row: BeautifulSoup) -> int:
        rating = horse_row.find_all("td", {"class": "rp-ageequip-hide"})[3].text[1:-1]
        if not rating:
            rating = -1
        return int(rating)

    def get_win_time(self, time_form_soup: BeautifulSoup) -> float:
        time_text_elem = time_form_soup.select_one('span:-soup-contains("Time:")')
        if not time_text_elem:
            return -1
        win_time = time_text_elem.find_next_sibling(text=True).text
        end_of_time_pos = win_time.find("\r")
        win_time = win_time[:end_of_time_pos]
        return self.win_time_to_seconds(win_time)


class RaceCardTimeformFetcher(TimeFormFetcher):

    def __init__(self):
        super().__init__()
        self.base_time_form_url = f"{self.base_time_form_url}/racecards"

    def get_horse_rows(self, time_form_soup: BeautifulSoup):
        return time_form_soup.find_all("tbody", {"class": "rp-table-row"})

    def get_horse_number(self, horse_row: BeautifulSoup) -> int:
        return int(horse_row.find("span", {"class": "rp-entry-number"}).text)

    def get_equip_code(self, horse_row: BeautifulSoup) -> str:
        equip_cell = horse_row.find("td", {"class": "rp-td-horse-equipment"}).find("span")

        equip_text = ""
        if equip_cell:
            equip_text = equip_cell.text

        return equip_text[1:-1]

    def get_rating(self, horse_row: BeautifulSoup) -> int:
        rating_cell = horse_row.find("td", {"class": "rp-td-horse-or"}).find("span")

        rating_text = ""
        if rating_cell:
            rating_text = rating_cell.text

        if not rating_text:
            rating = -1
        else:
            rating = int(rating_text[1:-1])
        return rating

    def get_win_time(self, time_form_soup: BeautifulSoup) -> float:
        return -1


def main():
    time_form_fetcher = RaceCardTimeformFetcher()

    today_race_card = TodayRaceCardsFetcher().fetch_race_cards()[0]
    soup = time_form_fetcher.get_time_form_attributes(today_race_card)
    print(soup)


if __name__ == '__main__':
    main()
    print('finished')
