from copy import deepcopy
from typing import Dict

from Betting.BetEvaluator import BetEvaluator
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.RaceResult import RaceResult
from Experiments.FundHistorySummary import FundHistorySummary
from Model.BetModel import BetModel
from SampleExtraction.RaceCardsSample import RaceCardsSample


class ModelEvaluator:

    def __init__(self):
        self.race_card_results: Dict[str, RaceResult] = {}

    def add_results_from_race_cards(self, race_cards: Dict[str, RaceCard]):
        for date in race_cards:
            self.race_card_results[date] = race_cards[date].race_result

    def get_fund_history_summary_of_model(self, bet_model: BetModel, race_cards_sample: RaceCardsSample) -> FundHistorySummary:
        bet_evaluator = BetEvaluator(self.race_card_results)
        race_cards_sample = deepcopy(race_cards_sample)

        estimated_race_cards_sample = bet_model.estimator.transform(race_cards_sample)
        betting_slips = bet_model.bettor.bet(estimated_race_cards_sample)

        bet_evaluator.add_wins_to_betting_slips(betting_slips)

        fund_history_summary = FundHistorySummary("Some Name", betting_slips)

        return fund_history_summary
