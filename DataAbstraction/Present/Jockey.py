class Jockey:

    def __init__(self, raw_data: dict):
        self.id = -1
        if "idPerson" in raw_data:
            self.id = raw_data["idPerson"]

        self.stats = raw_data["stats"]
        self.last_name = raw_data["lastName"]

        self.num_wins = -1
        self.num_places = -1
        self.earnings = -1

        self.num_races = -1

        self.win_rate = -1
        self.place_rate = -1
        self.earnings_rate = -1

        if self.stats is not False:
            self.num_wins = self.stats["numWin"]
            self.num_places = self.stats["numPlace"]
            self.earnings = self.stats["earnings"]

            self.num_races = self.stats["numRaces"]

            self.win_rate = self.num_wins / self.num_races
            self.place_rate = self.num_places / self.num_races
            self.earnings_rate = self.earnings / self.num_races

        self.weight = -1
        self.allowance = -1
        if "weight" in raw_data:
            self.weight = raw_data["weight"]["weight"]
            self.allowance = raw_data["weight"]["allowance"]
