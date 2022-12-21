from dataclasses import dataclass


@dataclass
class HorseResult:

    race_name: str
    race_date_time: str
    number: int
    position: int
    win_probability: float
    win_odds: float
    place_odds: float
