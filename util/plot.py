from typing import List

import seaborn as sns
from numpy import cumsum


def plot_wealth_growth(payouts: List[float], label: str = "Raw payouts") -> None:
    payout_numbers = [0] + [i+1 for i in range(len(payouts))]
    cum_payout_values = [0] + list(cumsum(payouts))
    sns.lineplot(x=payout_numbers, y=cum_payout_values, label=label)
