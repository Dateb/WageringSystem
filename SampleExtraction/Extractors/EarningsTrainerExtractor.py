from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class EarningsTrainerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Earnings_Trainer"

    def get_value(self, horse: Horse) -> str:
        trainer = horse.raw_data["trainer"]
        trainer_stats = trainer["stats"]
        if trainer_stats is not False:
            return trainer_stats["earnings"]

        return self.PLACEHOLDER_VALUE
