from dataclasses import dataclass


@dataclass
class PayoutSnapshot:
    name: str
    date: str
    payout_percentages: float
