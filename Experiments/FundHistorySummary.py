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

    @property
    def bet_rate(self):
        non_betting_slips = [betting_slip for betting_slip in self.betting_slips.values() if len(betting_slip.bets) == 0]
        real_betting_slips = [betting_slip for betting_slip in self.betting_slips.values() if len(betting_slip.bets) > 0]
        return len(real_betting_slips) / (len(real_betting_slips) + len(non_betting_slips))
