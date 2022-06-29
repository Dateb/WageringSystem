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

        self.lengths_behind_winner = None
        if "horseDistance" in raw_data:
            self.lengths_behind_winner = raw_data["horseDistance"]
