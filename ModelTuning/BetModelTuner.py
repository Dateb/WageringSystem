import pickle
from math import floor
from random import sample
from typing import Dict

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from Model.BetModel import BetModel
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BET_MODEL_PATH = "../data/bet_model.dat"


class BetModelTuner:

    def __init__(self, race_cards: Dict[str, RaceCard]):
        self.race_cards = race_cards
        self.feature_manager = FeatureManager()

        n_container_race_cards = floor(len(race_cards) * 0.1)
        print(n_container_race_cards)
        container_race_card_keys = sample(list(self.race_cards.keys()), k=n_container_race_cards)
        container_race_cards = [race_cards.pop(race_card_key) for race_card_key in container_race_card_keys]

        self.feature_manager.set_features(list(race_cards.values()))
        self.feature_manager.fit_enabled_container(container_race_cards)

        sample_encoder = SampleEncoder(self.feature_manager.features)
        self.samples = sample_encoder.transform(list(race_cards.values()))
        self.sample_split_generator = SampleSplitGenerator(self.samples)

    def get_tuned_bet_model(self) -> BetModel:
        configuration_tuner = BetModelConfigurationTuner(
            race_cards=self.race_cards,
            samples=self.samples,
            feature_manager=self.feature_manager,
            sample_split_generator=self.sample_split_generator,
        )
        bet_model = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=5)

        return bet_model


def main():
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_every_month_non_writable()
    print(len(race_cards))

    tuning_pipeline = BetModelTuner(race_cards)
    bet_model = tuning_pipeline.get_tuned_bet_model()

    persistence = RaceCardsPersistence("test_race_cards")
    test_race_cards = persistence.load_every_month_non_writable()

    feature_manager = FeatureManager(features=bet_model.features)
    feature_manager.set_features(list(test_race_cards.values()))

    sample_encoder = SampleEncoder(bet_model.features)
    test_samples = sample_encoder.transform(list(test_race_cards.values()))

    fund_history_summaries = [
        bet_model.fund_history_summary(
            race_cards=test_race_cards,
            samples=test_samples,
            name="Gradient Boosted Trees Estimators"
        )
    ]

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__BET_MODEL_PATH, "wb") as f:
        pickle.dump(bet_model, f)


if __name__ == '__main__':
    main()
    print("finished")
