from datetime import datetime, timedelta
from typing import List

from pytz import timezone

from DataAbstraction.FormGuide import FormGuide
from DataAbstraction.RaceCard import RaceCard
from DataAbstraction.WinTimeFactory import WinTimeFactory


class RawRaceCardInjector:

    def __init__(self, race_card: RaceCard):
        self.__race_card = race_card

    def inject_form_tables(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            horse_data = self.__race_card.get_data_of_subject(form_guide.subject_id)
            horse_data["formTable"] = form_guide.form_table

    def inject_win_time(self):
        for horse in self.__race_card.horses:
            form_table = self.__race_card.form_table_of_horse(horse)
            for past_race in form_table:
                if past_race["country"] == "GB":
                    print(past_race["idRace"])
                    date = datetime.utcfromtimestamp(past_race["date"])
                    date += timedelta(hours=2)
                    date = date.strftime('%Y-%m-%d')
                    win_time_factory = WinTimeFactory(date, past_race["trackName"], int(past_race["raceNumber"]))
                    past_race["win_time"] = win_time_factory.__get_win_times_of_tracks()
                else:
                    past_race["win_time"] = -1

    def inject_past_race_card(self, subject_id: str, past_race_card: RaceCard):
        horse_data = self.__race_card.get_data_of_subject(subject_id)
        if "pastRaces" not in horse_data:
            horse_data["pastRaces"] = []

        horse_data["pastRaces"].append(past_race_card.raw_race_card)

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card
