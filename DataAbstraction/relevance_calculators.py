from DataAbstraction.Present.Horse import Horse

from util.speed_calculator import get_speed_figures_distribution
from scipy.stats import percentileofscore
from math import floor


def get_speed_figure_based_relevance(horse: Horse) -> int:
    relevance = 0
    if horse.has_won:
        relevance = 1

    if horse.speed_figure:
        get_speed_figures_distribution().append(horse.speed_figure)

        score_percentile = percentileofscore(get_speed_figures_distribution(), horse.speed_figure) / 100
        relevance += floor(score_percentile * 29)

    return relevance


def get_place_based_relevance(horse: Horse) -> int:
    if horse.place_racebets == -1:
        return 0

    relevance = max([31 - horse.place_racebets, 0])
    return relevance


def get_winner_relevance(horse: Horse) -> int:
    return horse.has_won
