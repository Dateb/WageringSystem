from dataclasses import dataclass


@dataclass
class HorseResult:

    horse_id: str
    position: int
    win_odds: float
    place_odds: float
