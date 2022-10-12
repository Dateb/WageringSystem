from typing import Dict
from Betting.BettingSlip import BettingSlip
from Experiments.PayoutSnapshot import PayoutSnapshot


class FundHistorySummary:

    def __init__(self, name: str, betting_slips: Dict[str, BettingSlip]):
        self.name = name
        self.betting_slips = betting_slips

        dates = sorted(betting_slips)
        payout_percentages = [betting_slips[date].payout_percentage for date in dates]

        self.snapshots = [
            PayoutSnapshot(
                name=self.name,
                date=dates[i],
                payout_percentages=payout_percentages[i]
            )
            for i in range(len(dates))
        ]

        self.validation_score = (sum(payout_percentages) / len(betting_slips)) * 1000
