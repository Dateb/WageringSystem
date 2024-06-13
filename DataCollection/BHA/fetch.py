import re
from datetime import timedelta
from typing import Dict

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper
from DataCollection.collect_util import distance_to_meters
from Persistence.RaceCardPersistence import RaceDataPersistence

scraper = get_scraper()

header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'Authorization': "",
    'Connection': 'keep-alive',
    'Host': 'api09.horseracing.software',
    'Origin': 'https://www.britishhorseracing.com',
    'Referer': 'https://www.britishhorseracing.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'TE': 'trailers',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
}


class BHAInjector:

    def __init__(self):
        self.race_series_ids_per_year_month = {}
        self.races_data = {}
        self.current_race_date = None
        self.current_race_idx = 0

    def get_horse_attributes(self, horse_data: dict) -> dict:
        horse_attributes = {
            "finishTime": horse_data["positionFinishTime"],
            "resultBtnDistancePFO": horse_data["resultBtnDistancePFO"],
            "resultFinishDNF": horse_data["DNFReason"],
            "jockeyId": horse_data["jockeyId"],
            "trainerId": horse_data["trainerId"],
            "ownerId": horse_data["ownerId"],
            "ratingFlat": horse_data["ratingFlat"],
            "ratingAWT": horse_data["ratingAwt"],
            "ratingChase": horse_data["ratingChase"],
            "ratingHurdle": horse_data["ratingHurdle"],
            "HRO": horse_data["HRO"],
            "nonRunnerDeclaredReason": horse_data["nonRunnerDeclaredReason"],
            "nonRunnerDeclaredDate": horse_data["nonRunnerDeclaredDate"],
            "nonRunnerDeclaredTime": horse_data["nonRunnerDeclaredTime"]
        }

        return horse_attributes

    def inject(self, race_card: RaceCard) -> bool:
        injection_successful = False
        print(f"{race_card.race_id}/{self.current_race_idx}")

        race_card_data = self.fetch(race_card)
        if race_card_data:
            self.inject_race_card_data(race_card, race_card_data)
            injection_successful = True

        self.current_race_idx += 1
        return injection_successful

    def fetch(self, race_card: RaceCard) -> Dict:
        race_card_month = race_card.datetime.month
        race_card_year = race_card.datetime.year

        race_series_ids_key = f"{race_card_year}_{race_card_month}"

        if race_series_ids_key not in self.race_series_ids_per_year_month:
            self.save_race_series_of_year_month(race_card_year, race_card_month)

        race_series_id = self.get_race_series_id(race_card)

        if race_series_id is None:
            placeholder_data = {"data": []}
            return placeholder_data

        if race_series_id not in self.races_data:
            self.save_races_of_race_series(race_card_year, race_series_id)
            self.current_race_idx = 0

        if self.current_race_idx >= len(self.races_data[race_series_id]):
            return {}

        race_dict = self.races_data[race_series_id][self.current_race_idx]

        if race_dict["raceTime"][0:2] != str(race_card.datetime.hour - 1) or race_dict["raceTime"][3:5] != str(race_card.datetime.minute).zfill(2):
            print(race_dict)
            if race_dict["winnerName"] != race_card.winner_name.split()[0]:
                print("Race card not matching. Trying next one...")
                self.current_race_idx += 1
                return self.fetch(race_card)

        race_id = race_dict["raceId"]
        division_sequence = race_dict["divisionSequence"]

        race_card_url = f"https://api09.horseracing.software/bha/v1/races/{race_card_year}/{race_id}/{division_sequence}/results"
        race_card_data = scraper.request_data_with_header(race_card_url, header, avg_wait_seconds=3.0)

        return race_card_data

    def inject_race_card_data(self, race_card: RaceCard, race_card_data: Dict) -> None:
        race_series_id = self.get_race_series_id(race_card)
        print(f"{race_card.race_id}")

        race_dict = self.races_data[race_series_id][self.current_race_idx]

        race_card.raw_race_card["race"]["adjusted_distance"] = distance_to_meters(race_dict["distanceChangeText"])
        race_card.raw_race_card["race"]["categoryLetter"] = self.extract_race_class(race_dict)

        for horse_data in race_card_data["data"]:
            horse = self.get_horse(race_card, horse_data)

            if horse is not None:
                horse_raw_data = horse.raw_data

                horse_attributes = self.get_horse_attributes(horse_data)

                for attribute in horse_attributes:
                    horse_raw_data[attribute] = horse_attributes[attribute]

    def get_horse(self, race_card: RaceCard, horse_data: Dict) -> Horse:
        horse_name_bha = self.get_horse_name(horse_data["racehorseName"])

        horse = race_card.get_horse_by_horse_name(horse_name_bha)

        if horse is None:
            if horse_data["jockeyName"] is not None:
                horse = race_card.get_horse_by_jockey(horse_data["jockeyName"])

        if horse is None:
            print(horse_data)
            horse = race_card.get_horse_by_number(int(horse_data["clothNumber"]))

        if horse is None:
            print(f"Horse not found: {horse_name_bha}")

        return horse

    def get_horse_name(self, horse_raw_name: str):
        # Define a regular expression pattern to match the name
        pattern = r'^\d+\.\s*|\s*\([A-Z]+\)$'

        # Remove the prefix and suffix
        horse_name = re.sub(pattern, '', horse_raw_name)

        # Remove any leading/trailing whitespaces
        horse_name = horse_name.strip()

        return horse_name

    def get_race_series_id(self, race_card: RaceCard) -> str:
        year_month_key = f"{race_card.datetime.year}_{race_card.datetime.month}"

        course_name = self.track_name_to_course_name(race_card.track_name)
        race_date = str(race_card.date)

        race_series_key = f"{course_name}_{race_date}"

        if race_series_key not in self.race_series_ids_per_year_month[year_month_key]:
            return None

        return self.race_series_ids_per_year_month[year_month_key][race_series_key]

    def save_race_series_of_year_month(self, year: int, month: int) -> None:
        race_series_per_month_url = f"https://api09.horseracing.software/bha/v1/fixtures/?fields=courseId,courseName,fixtureDate,fixtureType,fixtureSession,abandonedReasonCode,highlightTitle&month={month}&order=desc&page=1&per_page=250&resultsAvailable=1&year={year}"
        race_series_of_month_data = scraper.request_data_with_header(race_series_per_month_url, header)

        year_month_key = f"{year}_{month}"
        self.race_series_ids_per_year_month[year_month_key] = {}

        for race_series in race_series_of_month_data["data"]:
            if 'courseName' in race_series:
                race_series_key = f"{race_series['courseName']}_{race_series['fixtureDate']}"
                self.race_series_ids_per_year_month[year_month_key][race_series_key] = race_series["fixtureId"]

    def save_races_of_race_series(self, year: int, race_series_id: str):
        races_of_race_series_url = f"https://api09.horseracing.software/bha/v1/fixtures/{year}/{race_series_id}/races"
        races_of_race_series_data = scraper.request_data_with_header(races_of_race_series_url, header, avg_wait_seconds=0.5)

        races = [race for race in races_of_race_series_data["data"] if "EMIRATES" not in race["raceName"]]

        self.races_data[race_series_id] = [
            {
            "raceId": race['raceId'],
            "divisionSequence": race['divisionSequence'],
            "distanceChangeText": race['distanceChangeText'],
            "prizeAmount": race["prizeAmount"],
            "raceTime": race["raceTime"],
            "raceName": race["raceName"],
            "winnerName": self.get_winner_name(race)
            }
            for race in races
        ]

    def get_winner_name(self, race: dict) -> str:
        if not race["winnersDetails"]:
            return ""

        return race["winnersDetails"][0]["racehorseName"].split()[0]

    def track_name_to_course_name(self, track_name: str) -> str:
        if track_name == "Lingfield":
            return "Lingfield Park"
        if track_name == "Sandown":
            return "Sandown Park"
        if track_name == "Kempton":
            return "Kempton Park"
        if track_name == "Chelmsford":
            return "Chelmsford City"
        if track_name == "Catterick":
            return "Catterick Bridge"
        if track_name == "Haydock":
            return "Haydock Park"
        if track_name == "Bangor":
            return "Bangor-on-Dee"
        if track_name == "Stratford":
            return "Stratford-on-Avon"
        if track_name == "Fontwell":
            return "Fontwell Park"
        if track_name == "Hamilton":
            return "Hamilton Park"
        if track_name == "Epsom":
            return "Epsom Downs"
        if track_name == "Yarmouth":
            return "Great Yarmouth"

        return track_name

    def extract_race_class(self, race_dict: dict) -> str:
        pattern = r'(?i)\(CLASS (\d+)(?: [A-Z]+)*\)'
        race_name = race_dict['raceName']
        print(race_name)
        match = re.search(pattern, race_name)

        if match:
            class_number = match.group(1)
            print(class_number)
        else:
            return "0"

        return class_number


def main():
    bha_fetcher = BHAInjector()


if __name__ == '__main__':
    main()
    print("finished")
