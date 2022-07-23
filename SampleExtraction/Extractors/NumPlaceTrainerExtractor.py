from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class NumPlaceTrainerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Num_Place_Trainer"

    def get_value(self, horse: Horse) -> str:
        trainer = horse.raw_data["trainer"]
        trainer_stats = trainer["stats"]
        if trainer_stats is not False:
            return trainer_stats["numPlace"]

        return self.PLACEHOLDER_VALUE
