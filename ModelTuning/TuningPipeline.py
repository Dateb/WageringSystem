import pickle

from Betting.FavoriteBettor import FavoriteBettor
from Betting.FirstHorseBettor import FirstHorseBettor
from Betting.WinBettor import WinBettor
from DataAbstraction.RaceCard import RaceCard
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.NeuralNetworkRanker import NeuralNetworkRanker
from Estimation.SampleSet import SampleSet
from ModelTuning.Features.FeatureSelector import FeatureSelector
from ModelTuning.Validator import Validator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__ESTIMATOR_PATH = "../data/estimator.dat"


def main():
    raw_races = RaceCardsPersistence("train_race_cards").load_raw()
    race_cards = [RaceCard(race_id, raw_races[race_id], remove_non_starters=False) for race_id in raw_races]

    sample_encoder = SampleEncoder(FeatureManager())
    samples = sample_encoder.transform(race_cards)
    sample_set = SampleSet(samples)
    bettor = WinBettor(kelly_wealth=1000)
    validator = Validator(bettor, sample_set, raw_races)

    #estimator = NeuralNetworkRanker(FeatureManager.FEATURE_NAMES, {})
    estimator = BoostedTreesRanker(FeatureManager.FEATURE_NAMES, {})

    feature_selector = FeatureSelector(estimator, validator)
    best_feature_subset = feature_selector.search_for_best_feature_subset(n_iter=150)
    estimator.feature_subset = best_feature_subset

    fund_history_summaries = [validator.fund_history_summary(estimator, name="Gradient Boosted Trees Ranker")]

    validator.bettor = FavoriteBettor(kelly_wealth=1000)
    fund_history_summaries += [validator.fund_history_summary(estimator, name="Favorite Bettor")]

    #validator.bettor = FirstHorseBettor(kelly_wealth=1000)
    #fund_history_summaries += [validator.fund_history_summary(best_estimator, name="First Horse Bettor")]

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__ESTIMATOR_PATH, "wb") as f:
        pickle.dump(estimator, f)


if __name__ == '__main__':
    main()
