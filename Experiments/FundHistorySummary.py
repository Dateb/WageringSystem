from typing import Dict

import numpy as np

from Betting.BettingSlip import BettingSlip
from Experiments.FundHistorySnapshot import FundHistorySnapshot


class FundHistorySummary:

    def __init__(self, name: str, betting_slips: Dict[str, BettingSlip], start_wealth=0):
        self.name = name
        self.betting_slips = betting_slips
        self.payouts = []
        self.winnings = []
        self.loss = []
        self.dates = []
        for date in sorted(betting_slips):
            betting_slip = betting_slips[date]
            self.payouts.append(betting_slip.payout)
            self.winnings.append(betting_slip.win)
            self.loss.append(betting_slip.loss)
            self.dates.append(date)
        self.start_wealth = start_wealth

        self.__set_fund_snapshots()
        self.__set_summary()

    def __set_fund_snapshots(self):
        current_wealth = self.start_wealth
        self.snapshots = []
        for i, payout in enumerate(self.payouts):
            current_wealth += payout
            self.snapshots += [FundHistorySnapshot(name=self.name, date=self.dates[i], wealth=current_wealth)]

    def __set_summary(self):
        n_positive_payouts = len([payout for payout in self.payouts if payout > 0])
        n_negative_payouts = len([payout for payout in self.payouts if payout < 0])

        n_payouts = n_positive_payouts + n_negative_payouts

        self.n_samples = len(self.payouts)
        if n_positive_payouts == 0:
            self.won_bets_percentage = 0
        else:
            self.won_bets_percentage = n_positive_payouts / n_payouts
        self.total_win = sum(self.winnings)
        self.total_loss = sum(self.loss)

        if self.total_loss > 0:
            self.win_loss_ratio = self.total_win / self.total_loss
        else:
            self.win_loss_ratio = -np.Inf

        self.total_payout = self.total_win - self.total_loss
        if n_payouts == 0:
            self.roi_per_bet = 0
        else:
            self.roi_per_bet = self.total_payout / n_payouts

        self.validation_score = self.total_payout

    @property
    def summary(self):
        return (self.name, self.total_win, self.total_loss, self.win_loss_ratio,
                self.won_bets_percentage, self.n_samples, self.validation_score)
