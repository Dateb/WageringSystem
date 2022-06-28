from datetime import datetime


class PastForm:

    def __init__(self, raw_data: dict):
        self.distance = raw_data["raceDistance"]
        self.win_time = raw_data["winTimeSeconds"]
        self.category = raw_data["categoryLetter"]
        self.track_name = raw_data["trackName"]
        self.date_time = datetime.fromtimestamp(raw_data["date"])
        self.date = self.date_time.date()

        self.lengths_behind_winner = None
        if "horseDistance" in raw_data:
            self.lengths_behind_winner = raw_data["horseDistance"]
