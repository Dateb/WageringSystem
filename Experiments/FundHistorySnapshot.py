from dataclasses import dataclass


@dataclass
class FundHistorySnapshot:
    name: str
    date: str
    wealth: float
