from dataclasses import dataclass


@dataclass
class HorseResult:

    race_name: str
    race_date_time: str
    name: str
    place: int
    win_probability: float
    place_probability: float
    win_odds: float
    place_odds: float
    place_num: int
