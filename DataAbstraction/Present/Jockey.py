class Jockey:

    def __init__(self, raw_data: dict):
        self.stats = raw_data["stats"]
        self.last_name = raw_data["lastName"]
        self.num_wins = -1
        self.num_races = -1
        self.earnings = -1
        self.win_rate = -1

        if self.stats is not False:
            self.num_wins = self.stats["numWin"]
            self.num_races = self.stats["numRaces"]
            self.earnings = self.stats["earnings"]
            self.win_rate = self.num_wins / self.num_races

        self.weight = -1
        self.allowance = -1
        if "weight" in raw_data:
            self.weight = raw_data["weight"]["weight"]
            self.allowance = raw_data["weight"]["allowance"]
