from abc import abstractmethod

from Model.Betting.bet import Bet


class StakesCalculator:

    def __init__(self):
        pass

    @abstractmethod
    def set_stakes(self, bet: Bet) -> None:
        pass


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
        stakes = self.bankroll * self.bankroll_fraction
        stakes = max([6, stakes])
        stakes = min([stakes, self.max_bet_size])
        bet.set_stakes(stakes)
        self.bankroll += bet.bet_offer.live_result.profit


class KellyStakesCalculator(StakesCalculator):

    def __init__(self, max_bet_size: float = 20, min_bet_size: float = 6, kelly_fraction_for_max_bet: float = 1.0):
        super().__init__()
        self.max_bet_size = max_bet_size
        self.min_bet_size = min_bet_size
        self.kelly_fraction_for_max_bet = kelly_fraction_for_max_bet

    def set_stakes(self, bet: Bet) -> None:
        edge = bet.bet_offer.live_result.offer_odds * bet.probability_estimate
        kelly_fraction = (edge - 1) / (bet.bet_offer.live_result.offer_odds - 1)
        bet_fraction = min([1, kelly_fraction / self.kelly_fraction_for_max_bet])
        stakes = self.min_bet_size + (self.max_bet_size - self.min_bet_size) * bet_fraction

        stakes = min([stakes, self.max_bet_size])

        bet.set_stakes(stakes)
