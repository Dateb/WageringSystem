from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import scratched_rate_source


class HorseScratchedRate(FeatureExtractor):

    scratched_rate_source.average_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return scratched_rate_source.get_average_of_name(str(horse.subject_id))


class JockeyScratchedRate(FeatureExtractor):

    scratched_rate_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return scratched_rate_source.get_average_of_name(str(horse.jockey_name))


class TrainerScratchedRate(FeatureExtractor):

    scratched_rate_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return scratched_rate_source.get_average_of_name(str(horse.trainer_name))
