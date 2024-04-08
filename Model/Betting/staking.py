from abc import abstractmethod

from Model.Betting.bet import Bet


class StakesCalculator:

    def __init__(self):
        pass

    @abstractmethod
    def set_stakes(self, bet: Bet) -> None:
        pass


class KellyStakesCalculator(StakesCalculator):

    def get_stakes(self, probability_estimate: float, odds: float) -> float:
        ev = odds * probability_estimate
        stakes = (ev - 1) / (odds - 1)

        return stakes


class FixedStakesCalculator(StakesCalculator):

    def __init__(self, fixed_stakes: float):
        super().__init__()
        self.fixed_stakes = fixed_stakes

    def set_stakes(self, bet: Bet) -> None:
        bet.set_stakes(self.fixed_stakes)


class FlatStakesCalculator(StakesCalculator):

    def __init__(self, bankroll_fraction: float = 0.004, starting_bankroll: float = 1500, max_bet_size: float = 20):
        super().__init__()
        self.bankroll_fraction = bankroll_fraction
        self.bankroll = starting_bankroll
        self.max_bet_size = max_bet_size

    def set_stakes(self, bet: Bet) -> None:
        stakes = max([6, self.bankroll * self.bankroll_fraction])
        stakes = min([stakes, self.max_bet_size])
        bet.set_stakes(stakes)
        self.bankroll += bet.payout
