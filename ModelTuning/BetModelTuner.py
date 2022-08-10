import pickle
from typing import Dict

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from ModelTuning.BetModel import BetModel
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSplitter import RaceCardsSplitter
from SampleExtraction.SampleEncoder import SampleEncoder

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BEST_MODEL_PATH = "../data/best_ranker.dat"


class BetModelTuner:

    def __init__(self, race_cards: Dict[str, RaceCard]):
        self.feature_manager = FeatureManager()

        race_cards_splitter = RaceCardsSplitter()
        self.train_race_cards, self.validation_race_cards = race_cards_splitter.split_race_cards(race_cards)

        self.feature_manager.fit_enabled_container(list(self.train_race_cards.values()))
        self.feature_manager.set_features(list(race_cards.values()))

        sample_encoder = SampleEncoder(self.feature_manager.non_past_form_features)
        self.train_samples = sample_encoder.transform(list(self.train_race_cards.values()))
        self.validation_samples = sample_encoder.transform(list(self.validation_race_cards.values()))

    def get_tuned_bet_model(self) -> BetModel:
        configuration_tuner = BetModelConfigurationTuner(
            self.validation_race_cards,
            self.train_samples,
            self.validation_samples,
            self.feature_manager,
        )
        bet_model = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=1)

        return bet_model


def main():
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_first_month_non_writable()
    print(len(race_cards))

    tuning_pipeline = BetModelTuner(race_cards)
    bet_model = tuning_pipeline.get_tuned_bet_model()

    fund_history_summaries = [
        bet_model.fund_history_summary(
            tuning_pipeline.validation_race_cards,
            tuning_pipeline.validation_samples,
            name="Gradient Boosted Trees Estimators"
        )
    ]

    #validator.bettor = FavoriteBettor(kelly_wealth=1000)
    #fund_history_summaries += [validator.fund_history_summary(bet_model, name="Favorite Bettor")]

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__BEST_MODEL_PATH, "wb") as f:
        pickle.dump(bet_model, f)


if __name__ == '__main__':
    main()
    print("finished")
