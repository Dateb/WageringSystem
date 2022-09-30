from typing import Dict

import numpy as np

from Betting.BettingSlip import BettingSlip
from Experiments.FundHistorySnapshot import FundHistorySnapshot


class FundHistorySummary:

    def __init__(self, name: str, betting_slips: Dict[str, BettingSlip], start_wealth=0):
        self.__name = name
        self.betting_slips = betting_slips
        self.payouts = []
        self.__winnings = []
        self.__loss = []
        self.__dates = []
        for date in sorted(betting_slips):
            betting_slip = betting_slips[date]
            self.payouts.append(betting_slip.payout)
            self.__winnings.append(betting_slip.win)
            self.__loss.append(betting_slip.loss)
            self.__dates.append(date)
        self.start_wealth = start_wealth

        self.__set_fund_snapshots()
        self.__set_summary()

    def __set_fund_snapshots(self):
        current_wealth = self.start_wealth
        self.snapshots = []
        for i, payout in enumerate(self.payouts):
            current_wealth += payout
            self.snapshots += [FundHistorySnapshot(name=self.__name, date=self.__dates[i], wealth=current_wealth)]

    def __set_summary(self):
        n_positive_payouts = len([payout for payout in self.payouts if payout > 0])
        n_negative_payouts = len([payout for payout in self.payouts if payout < 0])

        n_payouts = n_positive_payouts + n_negative_payouts

        self.__n_validation_samples = len(self.payouts)
        if n_positive_payouts == 0:
            self.won_bets_percentage = 0
        else:
            self.won_bets_percentage = n_positive_payouts / n_payouts
        self.total_win = sum(self.__winnings)
        self.total_loss = sum(self.__loss)

        if self.total_loss > 0:
            self.win_loss_ratio = self.total_win / self.total_loss
        else:
            self.win_loss_ratio = -np.Inf

        self.total_payout = self.total_win - self.total_loss
        if n_payouts == 0:
            self.roi_per_bet = 0
        else:
            self.roi_per_bet = self.total_payout / n_payouts

        self.validation_score = self.win_loss_ratio

    @property
    def summary(self):
        return (self.__name, self.total_win, self.total_loss, self.win_loss_ratio,
                self.won_bets_percentage, self.__n_validation_samples, self.validation_score)
