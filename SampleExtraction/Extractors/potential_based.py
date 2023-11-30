from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.init import best_class_place_source


class BestClassPlace(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        best_class_place = best_class_place_source.get_previous_of_name(str(horse.subject_id))

        if best_class_place is None:
            return self.PLACEHOLDER_VALUE

        if race_card.race_class in ["A", "B"]:
            return self.PLACEHOLDER_VALUE

        race_class_difference = int(race_card.race_class) - best_class_place

        return race_class_difference


class HorseTopFinish(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_final_positions = [past_form.final_position for past_form in horse.form_table.past_forms if past_form.final_position != -1]

        if not past_final_positions:
            return self.PLACEHOLDER_VALUE

        return min(past_final_positions)


class MaxPastRatingExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_ratings = [past_form.rating for past_form in horse.form_table.past_forms if past_form.rating != -1]

        if not past_ratings:
            return self.PLACEHOLDER_VALUE

        return max(past_ratings)
