from datetime import datetime, timedelta
from typing import List

from DataAbstraction.FormGuide import FormGuide
from DataAbstraction.WritableRaceCard import WritableRaceCard
from Persistence.JSONPersistence import JSONPersistence
from Persistence.RaceCardPersistence import RaceCardsPersistence


class RawRaceCardInjector:

    def __init__(self, race_card: WritableRaceCard):
        self.__race_card = race_card

    def inject_form_tables(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            horse_data = self.__race_card.get_data_of_subject(form_guide.subject_id)
            horse_data["formTable"] = form_guide.form_table

    def inject_win_time(self, win_times: dict):
        for horse in self.__race_card.horses:
            form_table = self.__race_card.raw_race_card["runners"]["data"][str(horse.horse_id)]["formTable"]
            for past_race in form_table:
                past_race["winTimeSeconds"] = -1
                past_race["raceDistance"] = -1
                past_race["categoryLetter"] = -1
                if past_race["country"] == "GB":
                    date = datetime.utcfromtimestamp(past_race["date"])
                    date += timedelta(hours=2)
                    date = date.strftime('%Y-%m-%d')
                    if date in win_times:
                        win_times_of_date = win_times[date]
                        track_name = past_race["trackName"]
                        if track_name in win_times_of_date:
                            race_number = str(past_race["raceNumber"])
                            if race_number in win_times_of_date[track_name]:
                                past_race["winTimeSeconds"] = win_times_of_date[track_name][race_number]["win_time"]
                                past_race["raceDistance"] = win_times_of_date[track_name][race_number]["distance"]
                                past_race["categoryLetter"] = win_times_of_date[track_name][race_number]["class"]

                    else:
                        print(f"Date {date} has no recorded win times.")

    def inject_past_race_card(self, subject_id: str, past_race_card: WritableRaceCard):
        horse_data = self.__race_card.get_data_of_subject(subject_id)
        if "pastRaces" not in horse_data:
            horse_data["pastRaces"] = []

        horse_data["pastRaces"].append(past_race_card.raw_race_card)

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card


def main():
    race_cards_persistence = RaceCardsPersistence(file_name="train_race_cards")

    win_times = JSONPersistence("win_times_contextualized").load()

    counter = 0
    for race_cards in race_cards_persistence:
        print(counter)
        counter += 1
        for date_time in race_cards:
            injector = RawRaceCardInjector(race_cards[date_time])
            injector.inject_win_time(win_times)

        race_cards_persistence.save(list(race_cards.values()))


if __name__ == '__main__':
    main()
    print('finished')
