from DataAbstraction.Present.HorseResult import HorseResult


class RaceResult:

    def __init__(self, raw_result: dict):
        self.horse_results = {}
        positions_dict = raw_result["positions"]

        for position_dict in positions_dict:
            horse_number = position_dict["programNumber"]
            position = position_dict["position"]
            win_odds = position_dict["oddsWin"]
            place_odds = position_dict["oddsPlc"]

            self.horse_results[str(horse_number)] = HorseResult(horse_number, position, win_odds, place_odds)

        # TODO: Needs refactoring
        self.exacta_odds = 0
        odds = raw_result["odds"]
        if "other" in odds:
            other_odds = odds["other"]
            if "EXA" in other_odds[0]:
                self.exacta_odds = float(list(other_odds[0]["EXA"].keys())[0])

        self.win_time = -1
        if "winTimeSeconds" in raw_result:
            self.win_time = raw_result["winTimeSeconds"]

    def get_result_of_horse_id(self, horse_number: int) -> HorseResult:
        # TODO: Returning None is sloppy
        if str(horse_number) not in self.horse_results:
            return None
        return self.horse_results[str(horse_number)]
