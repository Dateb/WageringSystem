from typing import List

from DataAbstraction.FormGuide import FormGuide
from DataAbstraction.RaceCard import RaceCard


class RawRaceCardInjector:

    def __init__(self, race_card: RaceCard):
        self.__race_card = race_card

    def inject_form_tables(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            horse_data = self.__race_card.get_data_of_subject(form_guide.subject_id)
            horse_data["formTable"] = form_guide.form_table

    def inject_past_race_card(self, subject_id: str, past_race_card: RaceCard):
        horse_data = self.__race_card.get_data_of_subject(subject_id)
        if "pastRaces" not in horse_data:
            horse_data["pastRaces"] = []

        horse_data["pastRaces"].append(past_race_card.raw_race_card)

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card
