import pickle

from ModelTuning.RankerConfigMCTS.RankerConfigurationTuner import RankerConfigurationTuner
from ModelTuning.Validator import Validator, get_validator

from Ranker.Ranker import Ranker

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BEST_RANKER_PATH = "../data/best_ranker.dat"


class TuningPipeline:

    def __init__(self, validator: Validator):
        self.__validator = validator

    def tune_ranker(self) -> Ranker:
        feature_selector = RankerConfigurationTuner(self.__validator)
        ranker = feature_selector.search_for_best_ranker_config(max_iter_without_improvement=2000)

        return ranker


def main():
    validator = get_validator()

    tuning_pipeline = TuningPipeline(validator)
    ranker = tuning_pipeline.tune_ranker()

    fund_history_summaries = [validator.fund_history_summary(ranker, name="NN Ranker")]

    #validator.bettor = FavoriteBettor(kelly_wealth=1000)
    #fund_history_summaries += [validator.fund_history_summary(ranker, name="Favorite Bettor")]

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__BEST_RANKER_PATH, "wb") as f:
        pickle.dump(ranker, f)


if __name__ == '__main__':
    main()
    print("finished")
