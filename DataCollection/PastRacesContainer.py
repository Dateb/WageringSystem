from DataAbstraction.FormGuideFactory import FormGuideFactory
from DataAbstraction.RaceCardFactory import RaceCardFactory
from DataAbstraction.RaceCard import RaceCard


class PastRacesContainer:

    def __init__(self, raw_past_races: dict):
        self.__raw_past_races = raw_past_races
        self.__race_card_factory = RaceCardFactory()
        self.__form_guide_factory = FormGuideFactory()

    def load_past_races(self, race_card: RaceCard):
        race_id = race_card.race_id
        for subject_id in race_card.subject_ids:
            past_race_key = self.__get_past_race_key(race_id, subject_id, 1)
            self.__raw_past_races[past_race_key] = self.__get_past_race(race_id, subject_id)

    def __get_past_race(self, race_id: str, subject_id: str) -> dict:
        if subject_id == 0:
            return {"ERROR": "no_past_race"}

        form_guide = self.__form_guide_factory.run(subject_id)
        past_race_ids = form_guide.past_race_ids

        if len(past_race_ids) == 0:
            return {"ERROR": "no_past_race"}

        if int(race_id) in past_race_ids:
            idx_current_race = past_race_ids.index(int(race_id))
        else:
            idx_current_race = -1
        idx_past_race = idx_current_race + 1

        if idx_past_race >= len(past_race_ids):
            return {"ERROR": "no_past_race"}

        past_race_id = past_race_ids[idx_past_race]

        return self.__race_card_factory.run(past_race_id).raw_race

    def get_past_race(self, race_id: str, subject_id: str, n_races_ago: int) -> RaceCard:
        past_race_key = self.__get_past_race_key(race_id, subject_id, n_races_ago)
        raw_race_data = self.__raw_past_races[past_race_key]

        return RaceCard(race_id, raw_race_data)

    def is_past_race_computed(self, race_id: str, subject_id: str, n_races_ago: int) -> bool:
        past_race_key = self.__get_past_race_key(race_id, subject_id, n_races_ago)
        return past_race_key in self.__raw_past_races

    def is_past_race_available(self, race_id: str, subject_id: str, n_races_ago: int) -> bool:
        past_race_key = self.__get_past_race_key(race_id, subject_id, n_races_ago)
        if "ERROR" in self.__raw_past_races[past_race_key]:
            return False

        return True

    def __get_past_race_key(self, race_id: str, subject_id: str, n_races_ago: int):
        return f"(\'{race_id}\', {subject_id}, {n_races_ago})"

    @property
    def raw_past_races(self):
        return self.__raw_past_races

