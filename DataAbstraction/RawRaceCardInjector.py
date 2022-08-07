from datetime import datetime, timedelta
from typing import List

from DataCollection.FormGuide import FormGuide
from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from Persistence.JSONPersistence import JSONPersistence
from Persistence.RaceCardPersistence import RaceCardsPersistence


class RawRaceCardInjector:

    def __init__(self, race_card: WritableRaceCard):
        self.__race_card = race_card
        self.__win_times = JSONPersistence("win_times_contextualized").load()

    def inject_form_tables(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            horse_data = self.__race_card.get_data_of_subject(form_guide.subject_id)
            horse_data["formTable"] = form_guide.form_table

    def inject_win_times_to_form_table(self, form_table: List[dict]):
        for past_form in form_table:
            self.__inject_win_time_to_past_form(past_form)

    def __inject_win_time_to_past_form(self, past_form: dict):
        past_form["winTimeSeconds"] = -1
        past_form["raceDistance"] = -1
        past_form["categoryLetter"] = -1
        if past_form["country"] == "GB":
            date = datetime.utcfromtimestamp(past_form["date"])
            date += timedelta(hours=2)
            date = date.strftime('%Y-%m-%d')
            if date in self.__win_times:
                win_times_of_date = self.__win_times[date]
                track_name = past_form["trackName"]
                if track_name in win_times_of_date:
                    race_number = str(past_form["raceNumber"])
                    if race_number in win_times_of_date[track_name]:
                        past_form["winTimeSeconds"] = win_times_of_date[track_name][race_number]["win_time"]
                        past_form["raceDistance"] = win_times_of_date[track_name][race_number]["distance"]
                        past_form["categoryLetter"] = win_times_of_date[track_name][race_number]["class"]
            else:
                print(f"Date {date} has no recorded win times.")

    def update_win_times(self):
        for horse in self.__race_card.horses:
            form_table = self.__race_card.raw_race_card["runners"]["data"][str(horse.horse_id)]["formTable"]
            self.inject_win_times_to_form_table(form_table)

    def inject_past_race_card(self, subject_id: str, past_race_card: WritableRaceCard):
        horse_data = self.__race_card.get_data_of_subject(subject_id)
        if "pastRaces" not in horse_data:
            horse_data["pastRaces"] = []

        horse_data["pastRaces"].append(past_race_card.raw_race_card)

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card


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
