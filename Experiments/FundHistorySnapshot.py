from dataclasses import dataclass


@dataclass
class FundHistorySnapshot:
    name: str
    time_step: int
    wealth: float
