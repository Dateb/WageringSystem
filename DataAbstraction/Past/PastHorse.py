from DataAbstraction.Present.Jockey import Jockey
from DataAbstraction.Present.Trainer import Trainer


class PastHorse:

    def __init__(self, raw_data: dict):
        self.name = raw_data["name"]
        self.age = raw_data["age"]
        self.gender = raw_data["gender"]
        self.horse_id = raw_data["idRunner"]
        self.subject_id = raw_data["idSubject"]
        self.place = self.__extract_place(raw_data)
        self.current_win_odds = self.__extract_current_win_odds(raw_data)
        self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place == 1 else 0
        self.has_blinkers = raw_data["blinkers"]
        self.jockey = Jockey(raw_data["jockey"])
        self.trainer = Trainer(raw_data["trainer"])
        self.is_scratched = raw_data["scratched"]
        self.past_performance = raw_data["ppString"]

    def __extract_place(self, raw_data: dict):
        if raw_data["scratched"]:
            return -1

        if 'finalPosition' in raw_data:
            return int(raw_data["finalPosition"])

        return -1

    def __extract_current_win_odds(self, raw_data: dict):
        odds_of_horse = raw_data["odds"]
        if odds_of_horse["FXW"] == 0:
            return float(odds_of_horse["PRC"])
        return float(odds_of_horse["FXW"])

    def __extract_post_position(self, raw_data: dict) -> int:
        if "postPosition" in raw_data:
            return int(raw_data["postPosition"])
        return -1
