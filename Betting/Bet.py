

class Bet:

    TAX: float = 0.05

    def __init__(self, horse_id: str, odds: float, stakes: float):
        self.horse_id = horse_id
        self.odds = odds
        self.stakes = stakes

        self.loss = stakes * (1 + self.TAX)
        self.potential_win = odds * stakes

