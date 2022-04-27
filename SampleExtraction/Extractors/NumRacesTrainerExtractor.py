from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class NumRacesTrainerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Num_Races_Trainer"

    def get_value(self, horse: Horse) -> str:
        trainer = horse.raw_data["trainer"]
        trainer_stats = trainer["stats"]
        if trainer_stats is not False:
            return trainer_stats["numRaces"]

        return "0"
