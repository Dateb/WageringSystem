from typing import Dict

import numpy as np
from numpy import ndarray
from scipy.optimize import minimize

from Model.Betting.Bets.Bet import Bet
from Model.Betting.kelly_optimizer import kelly_objective, kelly_jacobian

previous_stakes: Dict[str, ndarray] = {}


def get_most_probable_value_stakes(ev_threshold: float, win_probabilities: ndarray, odds: ndarray) -> ndarray:
    stakes = np.zeros(shape=win_probabilities.shape)
    n_horses = len(win_probabilities)
    highest_probability = 0
    highest_probability_idx = -1
    final_ev = 0
    for i in range(n_horses):
        win_probability = win_probabilities[i]
        ev = win_probability * odds[i]

        if ev > 1 + ev_threshold:
            if win_probability > highest_probability:
                final_ev = ev
                highest_probability = win_probability
                highest_probability_idx = i

    if highest_probability_idx != -1:
        numerator = final_ev - (1 + ev_threshold)
        denominator = odds[highest_probability_idx] - (1 + Bet.BET_TAX + ev_threshold)

        stakes[highest_probability_idx] = numerator / denominator

    return stakes


def get_highest_value_stakes(ev_threshold: float, win_probabilities: ndarray, odds: ndarray) -> ndarray:
    stakes = np.zeros(shape=win_probabilities.shape)
    n_horses = len(win_probabilities)
    highest_ev = 0
    highest_ev_idx = -1
    for i in range(n_horses):
        ev = win_probabilities[i] * odds[i]

        if ev > highest_ev:
            highest_ev = ev
            highest_ev_idx = i

    if highest_ev > 1 + ev_threshold:
        numerator = highest_ev - (1 + ev_threshold)
        denominator = odds[highest_ev_idx] - (1 + Bet.BET_TAX + ev_threshold)

        stakes[highest_ev_idx] = numerator / denominator

    return stakes


def get_multiple_win_stakes(race_id: str, probabilities: ndarray, odds: ndarray) -> ndarray:
    n_horses = len(probabilities)
    bounds = [(0, 1) for _ in range(len(probabilities))]
    if race_id in previous_stakes:
        init_stakes = previous_stakes[race_id]
    else:
        init_stakes = np.array([1 / n_horses for _ in range(n_horses)])

    result = minimize(
        fun=kelly_objective,
        jac=kelly_jacobian,
        x0=init_stakes,
        method="SLSQP",
        args=(probabilities, odds),
        bounds=bounds,
        constraints=({'type': "ineq", "fun": lambda x: 1 - sum(x)})
    )

    previous_stakes[race_id] = result.x

    return result.x
