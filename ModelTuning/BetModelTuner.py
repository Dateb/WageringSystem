import pickle
from typing import Dict

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from ModelTuning.BetModel import BetModel
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BEST_MODEL_PATH = "../data/best_ranker.dat"


class BetModelTuner:

    def __init__(self, race_cards: Dict[str, RaceCard]):
        self.__race_cards = race_cards

        sample_encoder = SampleEncoder(FeatureManager())
        self.train_samples, self.validation_samples = sample_encoder.transform(race_cards)

    def get_tuned_bet_model(self) -> BetModel:
        configuration_tuner = BetModelConfigurationTuner(self.__race_cards, self.train_samples, self.validation_samples)
        bet_model = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=500)

        return bet_model


def main():
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_every_month_non_writable()
    print(len(race_cards))

    tuning_pipeline = BetModelTuner(race_cards)
    bet_model = tuning_pipeline.get_tuned_bet_model()

    fund_history_summaries = [
        bet_model.fund_history_summary(
            race_cards,
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
