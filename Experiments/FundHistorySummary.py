from typing import List, Dict

from Betting.BettingSlip import BettingSlip
from Experiments.FundHistorySnapshot import FundHistorySnapshot


class FundHistorySummary:

    def __init__(self, name: str, betting_slips: Dict[str, BettingSlip], start_wealth=0):
        self.__name = name
        self.__payouts = []
        self.__winnings = []
        self.__loss = []
        self.__dates = []
        for date in sorted(betting_slips):
            betting_slip = betting_slips[date]
            self.__payouts.append(betting_slip.payout)
            self.__winnings.append(betting_slip.win)
            self.__loss.append(betting_slip.loss)
            self.__dates.append(betting_slip.date)
        self.__start_wealth = start_wealth

        self.__set_fund_snapshots()
        self.__set_summary()

    def __set_fund_snapshots(self):
        current_wealth = self.__start_wealth
        self.__snapshots = []
        for i, payout in enumerate(self.__payouts):
            current_wealth += payout
            self.__snapshots += [FundHistorySnapshot(name=self.__name, date=self.__dates[i], wealth=current_wealth)]

    def __set_summary(self):
        n_positive_payouts = len([payout for payout in self.__payouts if payout > 0])
        n_negative_payouts = len([payout for payout in self.__payouts if payout < 0])

        self.__n_train_test_samples = len(self.__payouts)
        if n_positive_payouts == 0:
            self.__won_bets_percentage = 0
        else:
            self.__won_bets_percentage = n_positive_payouts / (n_positive_payouts + n_negative_payouts)
        self.__total_win = sum(self.__winnings)
        self.__total_loss = sum(self.__loss)

        self.__win_loss_ratio = self.__total_win / self.__total_loss
        self.__roi_per_bet = ((self.win_loss_ratio - 1) / self.__n_train_test_samples) + 1

    @property
    def summary(self):
        return (self.__name, self.__total_win, self.__total_loss, self.__win_loss_ratio,
                self.__won_bets_percentage, self.__n_train_test_samples, self.__roi_per_bet)

    @property
    def win_percentage(self):
        return self.__won_bets_percentage

    @property
    def win_loss_ratio(self):
        return self.__win_loss_ratio

    @property
    def roi_per_bet(self):
        return self.__roi_per_bet

    @property
    def snapshots(self) -> List[FundHistorySnapshot]:
        return self.__snapshots

