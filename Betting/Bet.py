

class Bet:

    TAX: float = 0.05

    def __init__(self, horse_id: str, odds: float, stakes: float, stakes_fraction: float):
        self.horse_id = horse_id
        self.odds = odds
        self.stakes_fraction = stakes_fraction
        self.set_stakes(stakes)

    def set_stakes(self, stakes: float):
        self.stakes = stakes

        self.loss = stakes * (1 + self.TAX)
        self.potential_win = self.odds * stakes
