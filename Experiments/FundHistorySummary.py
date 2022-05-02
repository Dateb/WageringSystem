from typing import List

from Betting.BetResult import BetResult
from Experiments.FundHistorySnapshot import FundHistorySnapshot


class FundHistorySummary:

    def __init__(self, name: str, bet_results: List[BetResult], start_wealth=0):
        self.__name = name
        self.__payouts = [bet_result.payout for bet_result in bet_results]
        self.__winnings = [bet_result.win for bet_result in bet_results]
        self.__loss = [bet_result.loss for bet_result in bet_results]
        self.__start_wealth = start_wealth

        self.__set_fund_snapshots()
        self.__set_summary()

    def __set_fund_snapshots(self):
        current_wealth = self.__start_wealth
        self.__snapshots = [FundHistorySnapshot(name=self.__name, time_step=0, wealth=current_wealth)]
        for i, payout in enumerate(self.__payouts):
            current_wealth += payout
            self.__snapshots += [FundHistorySnapshot(name=self.__name, time_step=i + 1, wealth=current_wealth)]

    def __set_summary(self):
        n_positive_payouts = len([payout for payout in self.__payouts if payout > 0])
        n_negative_payouts = len([payout for payout in self.__payouts if payout < 0])

        self.__n_train_test_samples = len(self.__payouts)
        self.__won_bets_percentage = n_positive_payouts / (n_positive_payouts + n_negative_payouts)
        self.__total_win = sum(self.__winnings)
        self.__total_loss = sum(self.__loss)
        self.__win_loss_ratio = self.__total_win / self.__total_loss

    @property
    def summary(self):
        return (self.__name, self.__total_win, self.__total_loss, self.__win_loss_ratio,
                self.__won_bets_percentage, self.__n_train_test_samples)

    @property
    def win_percentage(self):
        return self.__won_bets_percentage

    @property
    def win_loss_ratio(self):
        return self.__win_loss_ratio

    @property
    def snapshots(self) -> List[FundHistorySnapshot]:
        return self.__snapshots

