from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class HasWon(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.has_won)


class Age(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int(horse.age) / 10


class Gender(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return horse.gender


class CurrentRating(FeatureExtractor):

    MIDDLE_RATINGS_PER_CLASS = {
        "FLT": {
            1: 123,
            2: 98,
            3: 85.5,
            4: 75.5,
            5: 65.5,
            6: 55.5,
            7: 22.5
        },
        "HRD": {
            1: 87.5,
            2: 70,
            3: 60,
            4: 50,
            5: 42.5,
            6: 87.5
        }
    }

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if not horse.rating:
            return self.PLACEHOLDER_VALUE
        rating = int(float(horse.rating))
        if rating in [-1, 0]:
            return self.PLACEHOLDER_VALUE
        return rating / 150

    def get_placeholder_rating(self, race_card: RaceCard) -> float:
        race_type = race_card.race_type_detail
        if race_type in ["STC", "HCH"]:
            race_type = "HRD"

        if race_type in ["NHF"]:
            race_type = "FLT"

        return self.MIDDLE_RATINGS_PER_CLASS[race_type][int(race_card.race_class)] / 150


class DoesHeadToHead(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.horse_id in race_card.head_to_head_horses)