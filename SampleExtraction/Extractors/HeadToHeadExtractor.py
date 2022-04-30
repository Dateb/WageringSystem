from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class HeadToHeadExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Does_Head_To_Head"

    def get_value(self, horse: Horse) -> int:
        return int(horse.horse_id in horse.get_race(0).head_to_head_horses)
