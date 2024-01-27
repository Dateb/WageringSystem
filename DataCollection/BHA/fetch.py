import re
from datetime import timedelta
from typing import Dict

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper
from DataCollection.collect_util import distance_to_meters
from Persistence.RaceCardPersistence import RaceCardsPersistence

scraper = get_scraper()

header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'Alt-Used': 'www.britishhorseracing.com',
    'Authorization': "",
    'Connection': 'keep-alive',
    'Cookie': '_ga_C2J05ZNW25=GS1.1.1701868160.5.1.1701869752.48.0.0; _ga=GA1.1.707870863.1694911425; bha-ie-test=true; __cf_bm=BE8kV0BrMcG2mesOMTZ7FYsdZhxpHxbuyowfDrCTNRU-1701869200-0-AXe1VwkrfW2s8kEyZKnH5lvfloVyDU+So+s1F49DbcDkHd9Ou4WwbBDiYK8Ov5y+ZYXln3GWbEs0ocNMbYZyDHE=',
    'Host': 'www.britishhorseracing.com',
    'Referer': 'https://www.britishhorseracing.com/racing/results/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'TE': 'trailers',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
}


class BHAInjector:

    def __init__(self):
        self.race_series_ids_per_year_month = {}
        self.races_data = {}
        self.current_race_date = None
        self.race_cards_loader = RaceCardsPersistence("race_cards")

    def get_horse_attributes(self, horse_data: dict) -> dict:
        horse_attributes = {
            "finishTime": horse_data["positionFinishTime"],
            "resultBtnDistancePFO": horse_data["resultBtnDistancePFO"],
            "resultFinishDNF": horse_data["resultFinishDNF"],
            "jockeyId": horse_data["jockeyId"],
            "trainerId": horse_data["trainerId"],
            "ownerId": horse_data["ownerId"],
            "ratingFlat": horse_data["ratingFlat"],
            "ratingAWT": horse_data["ratingAWT"],
            "ratingChase": horse_data["ratingChase"],
            "ratingHurdle": horse_data["ratingHurdle"],
            "HRO": horse_data["HRO"],
            "nonRunnerDeclaredReason": horse_data["nonRunnerDeclaredReason"],
            "nonRunnerDeclaredDate": horse_data["nonRunnerDeclaredDate"],
            "nonRunnerDeclaredTime": horse_data["nonRunnerDeclaredTime"]
        }

        return horse_attributes

    def inject(self, race_card: RaceCard) -> None:
        race_card_data = self.fetch(race_card)
        self.inject_race_card_data(race_card, race_card_data)

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

        race_dict = self.get_race_dict(race_card, race_series_id)
        race_id = race_dict["raceId"]
        division_sequence = race_dict["divisionSequence"]

        race_card_url = f"https://www.britishhorseracing.com/feeds/v3/races/{race_card_year}/{race_id}/{division_sequence}/results"
        race_card_data = scraper.request_data_with_header(race_card_url, header, avg_wait_seconds=5.0)

        return race_card_data

    def inject_race_card_data(self, race_card: RaceCard, race_card_data: Dict) -> None:
        race_series_id = self.get_race_series_id(race_card)
        race_dict = self.get_race_dict(race_card, race_series_id)

        race_card.raw_race_card["race"]["adjusted_distance"] = distance_to_meters(race_dict["distanceChangeText"])

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

    def get_race_dict(self, race_card: RaceCard, race_series_id: str) -> dict:
        race_time = (race_card.datetime - timedelta(hours=1)).time()

        return self.races_data[race_series_id][str(race_time)]

    def save_race_series_of_year_month(self, year: int, month: int) -> None:
        race_series_per_month_url = f"https://www.britishhorseracing.com/feeds/v3/fixtures?fields=courseId,courseName,fixtureDate,fixtureType,fixtureSession,abandonedReasonCode,highlightTitle&month={month}&order=desc&page=1&per_page=1000&resultsAvailable=true&year={year}"
        race_series_of_month_data = scraper.request_data_with_header(race_series_per_month_url, header)

        year_month_key = f"{year}_{month}"
        self.race_series_ids_per_year_month[year_month_key] = {}

        for race_series in race_series_of_month_data["data"]:
            if 'courseName' in race_series:
                race_series_key = f"{race_series['courseName']}_{race_series['fixtureDate']}"
                self.race_series_ids_per_year_month[year_month_key][race_series_key] = race_series["fixtureId"]

    def save_races_of_race_series(self, year: int, race_series_id: str):
        self.races_data[race_series_id] = {}

        races_of_race_series_url = f"https://www.britishhorseracing.com/feeds/v3/fixtures/{year}/{race_series_id}/races"
        races_of_race_series_data = scraper.request_data_with_header(races_of_race_series_url, header, avg_wait_seconds=0.5)

        for race in races_of_race_series_data["data"]:
            self.races_data[race_series_id][race['raceTime']] = {
                "raceId": race['raceId'],
                "divisionSequence": race['divisionSequence'],
                "distanceChangeText": race['distanceChangeText']
            }

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


def main():
    bha_fetcher = BHAInjector()


if __name__ == '__main__':
    main()
    print("finished")
