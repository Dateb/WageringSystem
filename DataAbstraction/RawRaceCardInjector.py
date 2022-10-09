from datetime import datetime, timedelta, date
from typing import List

from DataAbstraction.WinTimesFactory import WinTimesFactory
from DataCollection.FormGuide import FormGuide
from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from Persistence.JSONPersistence import JSONPersistence
from Persistence.RaceCardPersistence import RaceCardsPersistence


class RawRaceCardInjector:

    def __init__(self, race_card: WritableRaceCard):
        self.__race_card = race_card
        self.__persistence = JSONPersistence("win_times_contextualized")
        self.__win_times = self.__persistence.load()
        self.__win_times_factory = WinTimesFactory()

    def inject_form_tables(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            horse_data = self.__race_card.get_data_of_subject(form_guide.subject_id)
            horse_data["formTable"] = form_guide.form_table
            self.inject_win_times_to_form_table(horse_data["formTable"])

    def inject_win_times_to_form_table(self, form_table: List[dict]):
        for past_form in form_table:
            self.__inject_win_time_to_past_form(past_form)

    def inject_win_time_to_race_card(self):
        result = self.__race_card.raw_race_card["result"]
        result["winTimeSeconds"] = -1
        race_date = str(self.__race_card.date)

        self.__load_win_info_of_race_date(race_date)

        track_name = past_form_track_to_win_time_track(self.__race_card.track_name)
        race_number = self.__race_card.race_number
        win_time_info = self.get_win_time_info(race_date, track_name, race_number)
        if win_time_info is not None:
            result["winTimeSeconds"] = win_time_info["win_time"]

    def inject_horse_distance_to_race_card(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            if form_guide.current_race_form:
                current_race_form = form_guide.current_race_form
                horse_name_of_form = current_race_form["name"]
                horse_data = self.__race_card.get_data_of_horse_name(horse_name_of_form)

                horse_data["horseDistance"] = -1

                if "horseDistance" in current_race_form:
                    horse_data["horseDistance"] = current_race_form["horseDistance"]

                if "finalPosition" in current_race_form and current_race_form["finalPosition"] == 1:
                    horse_data["horseDistance"] = 0

    def __inject_win_time_to_past_form(self, past_form: dict):
        past_form["winTimeSeconds"] = -1
        past_form["raceDistance"] = -1
        past_form["categoryLetter"] = -1
        if past_form["country"] == "GB":
            race_date = datetime.utcfromtimestamp(past_form["date"])
            race_date += timedelta(hours=2)
            race_date = race_date.strftime('%Y-%m-%d')

            self.__load_win_info_of_race_date(race_date)

            win_time_info = self.get_win_time_info(race_date, past_form["trackName"], past_form["raceNumber"])

            if win_time_info is not None:
                past_form["winTimeSeconds"] = win_time_info["win_time"]
                past_form["raceDistance"] = win_time_info["distance"]
                past_form["categoryLetter"] = win_time_info["class"]

    def get_win_time_info(self, race_date: str, track_name: str, race_number: int) -> dict:
        win_time_info_of_date = self.__win_times[race_date]
        track_name = past_form_track_to_win_time_track(track_name)
        if track_name in win_time_info_of_date:
            race_number = str(race_number)
            if race_number in win_time_info_of_date[track_name]:
                return win_time_info_of_date[track_name][race_number]

        else:
            print(f"track name not found: {track_name}, date: {date}")

    def __load_win_info_of_race_date(self, race_date: str):
        if race_date not in self.__win_times:
            print(f"Date {race_date} has no recorded win times.")
            self.__win_times[race_date] = self.__win_times_factory.get_win_times_of_date(race_date)
            self.__persistence.save(self.__win_times)

    def update_win_times(self):
        for horse in self.__race_card.horses:
            form_table = self.__race_card.raw_race_card["runners"]["data"][str(horse.horse_id)]["formTable"]
            self.inject_win_times_to_form_table(form_table)

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card


def past_form_track_to_win_time_track(track_name: str) -> str:
    if track_name == "Epsom":
        return "Epsom Downs"
    if track_name == "Bangor":
        return "Bangor-On-Dee"
    if track_name == "Royal Ascot":
        return "Ascot"
    if track_name == "Chelmsford":
        return "Chelmsford City"
    if track_name == "Glorious Goodwood":
        return "Goodwood"
    if track_name == "Perth Hunt":
        return "Perth"
    if track_name == "Ascot Champions Day":
        return "Ascot"
    if track_name == "Newcastle PMU":
        return "Newcastle"
    if track_name == "Newmarket PMU":
        return "Newmarket"
    if track_name == "Chelmsford City PMU":
        return "Chelmsford City"
    if track_name == "Chelmsford PMU":
        return "Chelmsford City"
    if track_name == "Kempton PMU":
        return "Kempton"
    return track_name


def main():
    race_cards_persistence = RaceCardsPersistence(data_dir_name="train_race_cards")

    for race_cards in race_cards_persistence:
        print(list(race_cards.keys())[0])
        for date_time in race_cards:
            injector = RawRaceCardInjector(race_cards[date_time])
            injector.update_win_times()

        race_cards_persistence.save(list(race_cards.values()))


if __name__ == '__main__':
    main()
    print('finished')
