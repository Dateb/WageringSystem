import math
import random
import time
from abc import abstractmethod, ABC
from datetime import date

import requests
from bs4 import BeautifulSoup

from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.Scraper import get_scraper
from DataCollection.current_races.fetch import TodayRaceCardsFetcher, TomorrowRaceCardsFetcher
from Persistence.RaceCardPersistence import RaceCardsPersistence


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
        self.session = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        self.base_time_form_url = "https://www.timeform.com/horse-racing"

        self.current_track_name = ""
        self.current_date = None

        self.login()

    def login(self):
        cookies = {
            "__RequestVerificationToken_L2hvcnNlLXJhY2luZw2": "owJ64-4957DPl9614pDtfNekriUcqG98dgHYazcBqdxeKbT-TKgfmNFE2EtpXFPtk8Y6_MBj3Ho3V15Fa3l_P3VjVK01",
            "_hjSessionUser_1506705": "eyJpZCI6Ijc4ODJkMjA2LTVkOTUtNWJhZC1hMzk4LWU5ZjJlNjRlMTA3YSIsImNyZWF0ZWQiOjE2NjM4ODc0NzE3MzMsImV4aXN0aW5nIjp0cnVlfQ=="
        }

        url = "https://www.timeform.com/horse-racing/account/sign-in?returnUrl=/horse-racing/"
        login_doc = self.session.get(url, headers=self.headers, cookies=cookies).text

        login_soup = BeautifulSoup(login_doc, 'html.parser')

        login_token = login_soup.find("form", {"id": "signinform"}).find("input", {"name": "__RequestVerificationToken"})["value"]

        login_url = "https://www.timeform.com/horse-racing/account/handlelogin?returnUrl=/horse-racing/"
        login_payload = {
            "__RequestVerificationToken": login_token,
            "EmailAddress": "daniel.tebart@googlemail.com",
            "Password": "titctsat49_",
            "RememberMe": "false"
        }

        print(login_token)
        self.session.post(login_url, login_payload, headers=self.headers, cookies=cookies)

    def get_time_form_attributes(self, race_card: WritableRaceCard):
        time_form_attributes = {
            "race": {},
            "horses": {},
            "result": {},
        }
        time_form_soup = self.get_time_form_soup(race_card)
        if time_form_soup is not None:
            time_form_attributes["result"]["winTimeSeconds"] = self.get_win_time(time_form_soup)
            time_form_attributes["race"]["distance"] = self.get_distance(time_form_soup)

            for horse_row in self.get_horse_rows(time_form_soup):
                horse_number = self.get_horse_number(horse_row)

                if horse_number:
                    time_form_attributes["horses"][horse_number] = {
                        "equipCode": self.get_equip_code(horse_row),
                        "rating": self.get_rating(horse_row),
                        "bsp_win": self.get_bsp_win(horse_row),
                        "bsp_place": self.get_bsp_place(horse_row),
                        "lengths_behind": self.get_lengths_behind(horse_row)
                    }
        else:
            raise ValueError

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
        response = self.session.get(time_form_url, headers=self.headers)

        if response.history:
            return None

        if response.status_code == 404:
            return None

        #TODO: Reuse it from scraper
        lowest_waiting_time = 12 * 0.8
        highest_waiting_time = 12 * 1.2
        waiting_time = random.uniform(lowest_waiting_time, highest_waiting_time)
        time.sleep(waiting_time)

        while not response.status_code == 200:
            response = self.session.get(time_form_url, headers=self.headers)
            time.sleep(4)

        return BeautifulSoup(response.text, 'html.parser')

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
        if track_name == "newmarket" and day_of_race.month in [6, 7, 8] and day_of_race.year >= 2013:
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
    def get_bsp_win(self, horse_row: BeautifulSoup) -> float:
        pass

    @abstractmethod
    def get_bsp_place(self, horse_row: BeautifulSoup) -> float:
        pass

    @abstractmethod
    def get_lengths_behind(self, time_form_soup: BeautifulSoup) -> float:
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
        horse_number = horse_row.find("a", {"class": "rp-horse"}).text.split(".")[0]

        if horse_number.isnumeric():
            return int(horse_number)
        return None

    def get_lengths_behind(self, horse_row: BeautifulSoup) -> float:
        final_position = horse_row.find("span", {"class": "rp-entry-number"}).text

        lengths_behind_text = horse_row.find("td", {"class": "rp-result-btn"}).text

        if not lengths_behind_text and final_position.isnumeric() and int(final_position) == 1:
            return 0.0

        if lengths_behind_text == "dh":
            return 0.0

        if lengths_behind_text == "ns":
            return 0.05

        if lengths_behind_text == "sh":
            return 0.1

        if lengths_behind_text == "hd":
            return 0.2

        if lengths_behind_text == "nk":
            return 0.3

        if lengths_behind_text == "ds":
            return -2.0

        if lengths_behind_text == "a":
            return -3.0

        lengths_behind_text = lengths_behind_text.replace("¼", ".25")
        lengths_behind_text = lengths_behind_text.replace("½", ".5")
        lengths_behind_text = lengths_behind_text.replace("¾", ".75")

        if not lengths_behind_text:
            return -1.0

        lengths_behind = float(lengths_behind_text)

        return lengths_behind

    def get_equip_code(self, horse_row: BeautifulSoup) -> str:
        return horse_row.find_all("td", {"class": "rp-ageequip-hide"})[2].text[1:-1]

    def get_rating(self, horse_row: BeautifulSoup) -> int:
        rating = horse_row.find_all("td", {"class": "rp-ageequip-hide"})[3].text[1:-1]
        if not rating:
            rating = -1
        return int(rating)

    def get_bsp_win(self, horse_row: BeautifulSoup) -> float:
        bsp_win = horse_row.find("td", {"title": "Betfair Win SP", "class": "rp-result-bsp-show"}).text

        if not bsp_win:
            return 0

        return float(bsp_win)

    def get_bsp_place(self, horse_row: BeautifulSoup) -> float:
        bsp_place = horse_row.find("td", {"title": "Betfair Place SP", "class": "rp-result-sp"}).text

        start_of_bsp_place_pos = bsp_place.find("(") + 1
        end_of_bsp_place_pos = bsp_place.find(")")

        bsp_place = bsp_place[start_of_bsp_place_pos:end_of_bsp_place_pos]

        if not bsp_place:
            return 0

        return float(bsp_place)

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

    def get_bsp_win(self, horse_row: BeautifulSoup) -> float:
        return 0

    def get_bsp_place(self, horse_row: BeautifulSoup) -> float:
        return 0

    def get_win_time(self, time_form_soup: BeautifulSoup) -> float:
        return -1


def main():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="race_cards")

    time_form_fetcher = ResultTimeformFetcher()
    dummy_race_card = list(race_cards_persistence.load_first_month_writable().values())[0]
    time_form_attributes = time_form_fetcher.get_time_form_attributes(dummy_race_card)
    print(time_form_attributes)


if __name__ == '__main__':
    main()
    print('finished')
