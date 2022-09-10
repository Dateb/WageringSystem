from DataAbstraction.Present.HorseResult import HorseResult


class RaceResult:

    def __init__(self, raw_result: dict):
        self.horse_results = {}
        positions_dict = raw_result["positions"]

        for position_dict in positions_dict:
            horse_id = position_dict["idRunner"]
            position = position_dict["position"]
            win_odds = position_dict["oddsWin"]
            place_odds = position_dict["oddsPlc"]

            self.horse_results[horse_id] = HorseResult(horse_id, position, win_odds, place_odds)

    def get_result_of_horse_id(self, horse_id: str) -> HorseResult:
        # TODO: Returning None is sloppy
        if horse_id not in self.horse_results:
            return None
        return self.horse_results[horse_id]
