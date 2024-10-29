from copy import deepcopy

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.feature_sources import FeatureSource, FeatureValueGroup
from SampleExtraction.feature_sources.value_calculators import TrainerCalculator


class HasWon(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.has_won)


class Age(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int(horse.age)


class Gender(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        if horse.gender is None:
            return ""

        return horse.gender


class Origin(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return horse.origin


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
        return rating

    def get_placeholder_rating(self, race_card: RaceCard) -> float:
        race_type = race_card.race_type_detail
        if race_type in ["STC", "HCH"]:
            race_type = "HRD"

        if race_type in ["NHF"]:
            race_type = "FLT"

        return self.MIDDLE_RATINGS_PER_CLASS[race_type][int(race_card.race_class)] / 150


class PostPosition(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return str(horse.post_position)


class TrainerChangeEarningsRateDiff(FeatureExtractor):

    def __init__(self, previous_trainer_source: FeatureSource, performance_source: FeatureSource, trainer_performance_value: FeatureValueGroup):
        super().__init__()
        self.previous_trainer_source = previous_trainer_source
        self.performance_source = performance_source
        self.horse_trainer = FeatureValueGroup(["subject_id"], TrainerCalculator())
        self.trainer_performance_value = trainer_performance_value

        self.previous_trainer_source.register_feature_value_group(self.horse_trainer)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_trainer = self.previous_trainer_source.get_feature_value(race_card, horse, self.horse_trainer)

        if previous_trainer is not None and previous_trainer.id != horse.trainer.id:
            prev_horse = deepcopy(horse)
            prev_horse.trainer = previous_trainer
            prev_horse.trainer_id = previous_trainer.id

            current_trainer_value = self.performance_source.get_feature_value(
                race_card,
                horse,
                self.trainer_performance_value
            )

            prev_trainer_value = self.performance_source.get_feature_value(
                race_card,
                prev_horse,
                self.trainer_performance_value
            )

            if current_trainer_value is not None and prev_trainer_value is not None:
                return current_trainer_value - prev_trainer_value

        return 0.0
