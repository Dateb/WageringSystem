from typing import List

from DataAbstraction.FormGuide import FormGuide
from DataAbstraction.RaceCard import RaceCard


class RawRaceCardInjector:

    def __init__(self, race_card: RaceCard):
        self.__race_card = race_card

    def inject_form_guides(self, form_guides: List[FormGuide]):
        for form_guide in form_guides:
            horse_data = self.__race_card.get_data_of_subject(form_guide.subject_id)
            horse_data["formGuide"] = form_guide.raw_formguide

    @property
    def raw_race_card(self):
        return self.__race_card.raw_race_card
