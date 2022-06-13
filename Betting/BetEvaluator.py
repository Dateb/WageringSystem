from typing import Dict

from Betting.BettingSlip import BettingSlip


class BetEvaluator:

    def __init__(self):
        pass

    def update_wins(self, betting_slips: Dict[str, BettingSlip]) -> Dict[str, BettingSlip]:
        for date in betting_slips:
            betting_slips[date] = self.__update_betting_slip(betting_slips[date])

        return betting_slips

    def __update_betting_slip(self, betting_slip: BettingSlip) -> BettingSlip:
        if betting_slip.winner_id in betting_slip.bets:
            winning_bet = betting_slip.get_bet(betting_slip.winner_id)
            betting_slip.update_won_bet(winning_bet)

        #print("--------------------------------")
        #print(f"race card: {race_card.name}")
        #print(f"Bet on: {race_card.get_name_of_horse(bet.runner_ids[0])}")
        #print(f"Stakes:{bet.stakes}")
        #print(f"Odds:{odds}")
        #print(f"won:{win_indicator}")
        #print(f"win:{win}")
        #print(f"loss:{loss}")
        #print("---------------------------------")

        return betting_slip

