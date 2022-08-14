import pickle
from typing import List, Dict

from DataAbstraction.Present.RaceCard import RaceCard
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

BET_MODEL_PATH: str = "../data/bet_model.dat"
TEST_FUND_HISTORY_SUMMARIES_PATH: str = "../data/fund_history_summaries.dat"


class Tester:

    def __init__(self, test_race_cards: Dict[str, RaceCard]):
        self.test_race_cards = test_race_cards
        with open(BET_MODEL_PATH, "rb") as f:
            self.bet_model = pickle.load(f)

        self.feature_manager = FeatureManager(features=self.bet_model.features)
        self.feature_manager.set_features(list(self.test_race_cards.values()))

        sample_encoder = SampleEncoder(self.feature_manager.features)
        self.test_samples = sample_encoder.transform(list(self.test_race_cards.values()))

    def run(self, name: str) -> List[FundHistorySummary]:
        return [self.bet_model.fund_history_summary(self.test_race_cards, self.test_samples, name)]


def main():
    persistence = RaceCardsPersistence("test_race_cards")
    test_race_cards = persistence.load_every_month_non_writable()

    tester = Tester(test_race_cards)
    fund_history_summaries = tester.run("GBT test set")

    with open(TEST_FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)


if __name__ == '__main__':
    main()
    print("finished")
