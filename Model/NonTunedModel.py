from Betting.BetEvaluator import BetEvaluator
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Model.BetModel import BetModel
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator
from SampleExtraction.SampleEncoder import SampleEncoder

from Persistence.RaceCardPersistence import RaceCardsPersistence
from Betting.StaticKellyBettor import StaticKellyBettor
import pickle

__BET_MODEL_PATH = "../data/non_tuned_bet_model.dat"


def main():
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_every_month_non_writable()

    train_race_cards, validation_race_cards = SampleSplitGenerator().split_race_cards(race_cards)

    feature_manager = FeatureManager()

    feature_manager.fit_enabled_container(list(train_race_cards.values()))
    feature_manager.set_features(list(race_cards.values()))

    sample_encoder = SampleEncoder(features=feature_manager.features)

    train_samples = sample_encoder.transform(list(train_race_cards.values()))
    validation_samples = sample_encoder.transform(list(validation_race_cards.values()))

    estimator = BoostedTreesRanker(feature_manager.features, search_params={})
    bettor = StaticKellyBettor(expected_value_additional_threshold=0, kelly_wealth=20)
    bet_evaluator = BetEvaluator()

    bet_model = BetModel(estimator, bettor, bet_evaluator)
    bet_model.fit_estimator(train_samples, validation_samples)

    with open(__BET_MODEL_PATH, "wb") as f:
        pickle.dump(bet_model, f)


if __name__ == '__main__':
    main()
    print("finished")
