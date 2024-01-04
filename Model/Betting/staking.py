from abc import abstractmethod


class StakesCalculator:

    def __init__(self):
        pass

    @abstractmethod
    def get_stakes(self, probability_estimate: float, odds: float) -> float:
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

    def get_stakes(self, probability_estimate: float, odds: float) -> float:
        return self.fixed_stakes
