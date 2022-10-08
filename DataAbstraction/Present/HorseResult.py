from dataclasses import dataclass


@dataclass
class HorseResult:

    number: int
    position: int
    win_odds: float
    place_odds: float
