from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class Age(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Age"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return horse.age


class Gender(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Gender"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if horse.gender == "G":
            return 0
        elif horse.gender == "M":
            return 1
        elif horse.gender == "C":
            return 2


class CurrentOdds(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Odds_Feature"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.current_win_odds


class CurrentRating(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Rating"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if not horse.rating:
            return self.PLACEHOLDER_VALUE
        return float(horse.rating)


class HasBlinker(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Has_Blinker"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.has_blinkers)


class DoesHeadToHead(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Does_Head_To_Head"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.horse_id in race_card.head_to_head_horses)