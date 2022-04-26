from dataclasses import dataclass
from enum import Enum
from typing import List


class BetType(Enum):

    WIN = 1
    EXACTA = 2
    TRIFECTA = 3


@dataclass
class Bet:

    race_id: str
    type: BetType
    stakes: float
    runner_ids: List[str]
