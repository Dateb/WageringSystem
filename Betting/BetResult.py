from dataclasses import dataclass


@dataclass
class BetResult:
    win: float
    loss: float
    payout: float

