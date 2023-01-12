from DataAbstraction.Present.HorseResult import HorseResult


class RaceResult:

    def __init__(self, raw_result: dict):
        self.horse_results = {}
        positions_dict = raw_result["positions"]

        for position_dict in positions_dict:
            horse_number = position_dict["programNumber"]
            position = position_dict["position"]

            # TODO: proper extraction of odds (after odds are fixed from the api, its kinda broken now)
            self.horse_results[str(horse_number)] = HorseResult(
                race_name="",
                race_date_time="",
                number=horse_number,
                name="",
                position=position,
                win_probability=0,
                place_probability=0,
                betting_odds=0,
                place_odds=0,
                place_num=0,
                expected_value=0,
            )

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

    def get_result_of_horse_number(self, horse_number: int) -> HorseResult:
        # TODO: Returning None is sloppy
        if str(horse_number) not in self.horse_results:
            return None
        return self.horse_results[str(horse_number)]
