from typing import List

import numpy as np
import pandas as pd

from abc import abstractmethod, ABC
from DataAbstraction.Present.RaceCard import RaceCard
from numpy import ndarray

from Model.Estimators.place_calculation import compute_place_probabilities, compute_place_probabilities_of_race
from SampleExtraction.RaceCardsSample import RaceCardsSample


class ProbabilityEstimates:

    def __init__(self, probability_estimates: dict):
        self.probability_estimates = probability_estimates

    def get_horse_win_probability(self, race_key: str, horse_name: str, scratched_horse_names: List[str]) -> float:
        total_probability_scratched_horses = 0
        for scratched_horse_name in scratched_horse_names:
            if scratched_horse_name.upper() in self.probability_estimates[race_key]:
                total_probability_scratched_horses += self.probability_estimates[race_key][scratched_horse_name.upper()]

        total_race_prob = sum(list(self.probability_estimates[race_key].values()))
        if horse_name.upper() in self.probability_estimates[race_key]:
            return self.probability_estimates[race_key][horse_name.upper()] / (total_race_prob - total_probability_scratched_horses)


class Probabilizer(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def create_estimation_result(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> ProbabilityEstimates:
        pass

    def set_win_probabilities(self, race_cards_dataframe: pd.DataFrame, scores: ndarray) -> pd.DataFrame:
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return race_cards_dataframe


class WinProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_estimation_result(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> ProbabilityEstimates:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe, scores)

        #TODO: fetch races from dataframe to create the estimates dynamically
        probability_estimates = {}

        for row in race_cards_dataframe.itertuples(index=False):
            horse_name = row.name.replace("'", "").upper()
            win_probability = row.win_probability

            race_datetime = str(row.date_time)
            if race_datetime not in probability_estimates:
                probability_estimates[race_datetime] = {}

            probability_estimates[race_datetime][horse_name] = win_probability

        return ProbabilityEstimates(probability_estimates)


class PlaceProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_estimation_result(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> ProbabilityEstimates:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe, scores)

        grouped_win_information = race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[["win_probability", RaceCard.PLACE_NUM_KEY]].agg({
            "win_probability": lambda x: list(x),
            RaceCard.PLACE_NUM_KEY: "first"
        })

        print(grouped_win_information)

        win_information = [tuple(row) for row in grouped_win_information.values]
        place_probabilities = compute_place_probabilities(win_information)

        flattened_place_probabilities = [item for sublist in place_probabilities for item in sublist]

        for place_probability in flattened_place_probabilities:
            if place_probability > 1:
                print('yellow')

        race_cards_dataframe["place_probability"] = flattened_place_probabilities

        probability_estimates = {}

        for row in race_cards_dataframe.itertuples(index=False):
            horse_name = row.name.replace("'", "").upper()
            place_probability = row.place_probability

            race_datetime = str(row.date_time)
            if race_datetime not in probability_estimates:
                probability_estimates[race_datetime] = {}

            probability_estimates[race_datetime][horse_name] = place_probability

        return ProbabilityEstimates(probability_estimates)
