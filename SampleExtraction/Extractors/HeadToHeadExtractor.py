from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class HeadToHeadExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Does_Head_To_Head"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.horse_id in race_card.head_to_head_horses)
