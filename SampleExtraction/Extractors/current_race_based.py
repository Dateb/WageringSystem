from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class Age(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Age"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return horse.age


class CurrentOdds(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Odds_Feature"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.current_win_odds


class CurrentDistance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Distance"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return float(race_card.distance)


class CurrentRaceClass(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Race_Class"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if race_card.race_class.isnumeric():
            return int(race_card.race_class)


class CurrentGoing(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Going"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return race_card.going


class HasTrainerMultipleHorses(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Has_Trainer_Multiple_Horses"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        trainer_names = [
            other_horse.trainer_name for other_horse in race_card.horses if other_horse.trainer_name == horse.trainer_name
        ]

        return int(len(trainer_names) > 1)

