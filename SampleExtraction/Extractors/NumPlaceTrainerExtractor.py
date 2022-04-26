from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class NumPlaceTrainerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Num_Place_Trainer"

    def get_value(self, horse_id: str, horse_data: dict) -> str:
        trainer = horse_data[horse_id]["trainer"]
        trainer_stats = trainer["stats"]
        if trainer_stats is not False:
            return trainer_stats["numPlace"]

        return "0"
