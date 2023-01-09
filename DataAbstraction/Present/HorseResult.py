from dataclasses import dataclass


@dataclass
class HorseResult:

    race_name: str
    race_date_time: str
    number: int
    name: str
    position: int
    win_probability: float
    place_probability: float
    win_betting_odds: float
    place_odds: float
    place_num: int
    expected_value: float
