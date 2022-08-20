from typing import List, Dict

import numpy as np

from Betting.BettingSlip import BettingSlip
from Experiments.FundHistorySnapshot import FundHistorySnapshot


class FundHistorySummary:

    def __init__(self, name: str, betting_slips: Dict[str, BettingSlip], start_wealth=0):
        self.__name = name
        self.__betting_slips = betting_slips
        self.payouts = []
        self.__winnings = []
        self.__loss = []
        self.__dates = []
        for date in sorted(betting_slips):
            betting_slip = betting_slips[date]
            self.payouts.append(betting_slip.payout)
            self.__winnings.append(betting_slip.win)
            self.__loss.append(betting_slip.loss)
            self.__dates.append(betting_slip.date)
        self.start_wealth = start_wealth

        self.__set_fund_snapshots()
        self.__set_summary()

    def __set_fund_snapshots(self):
        current_wealth = self.start_wealth
        self.__snapshots = []
        for i, payout in enumerate(self.payouts):
            current_wealth += payout
            self.__snapshots += [FundHistorySnapshot(name=self.__name, date=self.__dates[i], wealth=current_wealth)]

    def __set_summary(self):
        n_positive_payouts = len([payout for payout in self.payouts if payout > 0])
        n_negative_payouts = len([payout for payout in self.payouts if payout < 0])

        self.__n_validation_samples = len(self.payouts)
        if n_positive_payouts == 0:
            self.__won_bets_percentage = 0
        else:
            self.__won_bets_percentage = n_positive_payouts / (n_positive_payouts + n_negative_payouts)
        self.__total_win = sum(self.__winnings)
        self.__total_loss = sum(self.__loss)

        if self.__total_loss > 0:
            self.__win_loss_ratio = self.__total_win / self.__total_loss
        else:
            self.__win_loss_ratio = -np.Inf
        self.roi_per_bet = ((self.win_loss_ratio - 1) / self.__n_validation_samples)
        self.total_payout = self.__total_win - self.__total_loss
        self.validation_score = self.total_payout

    @property
    def betting_slips(self):
        return self.__betting_slips

    @property
    def summary(self):
        return (self.__name, self.__total_win, self.__total_loss, self.__win_loss_ratio,
                self.__won_bets_percentage, self.__n_validation_samples, self.validation_score)

    @property
    def win_percentage(self):
        return self.__won_bets_percentage

    @property
    def win_loss_ratio(self):
        return self.__win_loss_ratio

    @property
    def snapshots(self) -> List[FundHistorySnapshot]:
        return self.__snapshots

