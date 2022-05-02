from typing import List

from Betting.Bet import Bet, BetType
from Betting.BetResult import BetResult
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.RaceCard import RaceCard


class BetEvaluator:
    __TAX = 0.05

    def __init__(self, file_name: str):
        self.__race_cards = RaceCardsPersistence(file_name).load()

    def evaluate(self, bets: List[Bet]) -> List[BetResult]:
        bet_results = [self.__create_bet_result(bet) for bet in bets]
        return bet_results

    def __create_bet_result(self, bet: Bet) -> BetResult:
        race_card = self.__race_cards[bet.race_id]
        win_indicator = self.__get_win_indicator(race_card, bet)
        odds = self.__get_odds(race_card, bet)
        win = win_indicator * bet.stakes * odds
        loss = bet.stakes * (1 + self.__TAX) if odds > 0.0 else 0
        payout = win - loss

        return BetResult(win, loss, payout)

    def __get_win_indicator(self, race_card: RaceCard, bet: Bet) -> int:
        if len(bet.runner_ids) < bet.type.value:
            return 0

        places_of_predicted_horses = [race_card.get_place_of_horse(runner_id) for runner_id in bet.runner_ids]
        for i, place in enumerate(places_of_predicted_horses):
            if place != (i+1):
                return 0

        return 1

    def __get_odds(self, race_card: RaceCard, bet: Bet):
        if bet.type == BetType.WIN:
            return race_card.get_current_odds_of_horse(bet.runner_ids[0])
        if bet.type == BetType.EXACTA:
            return race_card.exacta_odds
        if bet.type == BetType.TRIFECTA:
            return race_card.trifecta_odds

