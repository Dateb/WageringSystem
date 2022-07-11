from datetime import datetime


class PastForm:

    def __init__(self, raw_data: dict):
        self.country = raw_data["country"]
        self.distance = raw_data["raceDistance"]
        self.type = raw_data["raceType"]
        self.surface = raw_data["trackSurface"]
        self.going = raw_data["trackGoing"]
        self.win_time = raw_data["winTimeSeconds"]
        self.category = raw_data["categoryLetter"]
        self.track_name = raw_data["trackName"]
        self.date_time = datetime.fromtimestamp(raw_data["date"])
        self.date = self.date_time.date()
        self.final_position = self.__extract_final_position(raw_data)
        self.has_won = 1 if self.final_position == 1 else 0

        self.lengths_behind_winner = None
        if "horseDistance" in raw_data:
            self.lengths_behind_winner = raw_data["horseDistance"]

        self.purse = self.__purse_to_value(raw_data["purse"])
        self.rating = self.__extract_rating(raw_data)

    def __extract_final_position(self, raw_data: dict) -> int:
        if "finalPosition" in raw_data:
            return int(raw_data["finalPosition"])
        return -1

    def __extract_rating(self, raw_data: dict) -> float:
        if "rating" not in raw_data:
            return -1
        return float(raw_data["rating"])

    def __purse_to_value(self, purse: str):
        purse_suffix = purse[-1]
        purse_without_suffix = purse[:-1]
        if purse_suffix == "k":
            return float(purse_without_suffix) * 1000
        elif purse_suffix == "M":
            return float(purse_without_suffix) * 1000000
        else:
            return 0.0
