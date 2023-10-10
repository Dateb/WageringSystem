import timeit
from typing import List, Tuple

import numpy as np
from numpy import ndarray


def compute_place_probabilities(win_information: List[Tuple]) -> List[object]:
    place_probabilities = []
    for race_win_information in win_information:
        win_probabilities_arr = np.array(race_win_information[0])
        place_probabilities.append(compute_place_probabilities_of_race(win_probabilities_arr, race_win_information[1]).tolist())
    return place_probabilities


def compute_place_probabilities_of_race(win_probabilities: ndarray, places_num: int) -> ndarray:
    place_probabilities = win_probabilities.copy()
    event_numerator = None
    event_denominator = None

    if places_num >= 2:
        event_numerator = np.outer(win_probabilities, win_probabilities)
        event_denominator = 1 - win_probabilities

        second_place_probabilities = compute_second_place_probabilities(event_numerator, event_denominator)

        place_probabilities += second_place_probabilities
    if places_num >= 3:
        event_numerator = event_numerator[:, :, None] * win_probabilities[None, None, :]

        dim = event_numerator.shape[0]
        i, j, k = np.ogrid[:dim, :dim, :dim]
        indices = np.where((i == j) | (j == k) | (i == k))

        event_numerator[indices] = 0

        event_denominator = np.multiply(event_denominator, np.subtract.outer(event_denominator, win_probabilities))
        np.fill_diagonal(event_denominator, 1)

        event_probabilities_3_places = event_numerator / event_denominator

        third_place_probabilities = np.sum(event_probabilities_3_places, axis=(1, 2))

        place_probabilities += third_place_probabilities
    if places_num >= 4:
        event_numerator = event_numerator[:, :, :, None] * win_probabilities[None, None, None, :]
        dim = event_numerator.shape[0]
        i, j, k, l = np.ogrid[:dim, :dim, :dim, :dim]

        indices = np.where((i == j) | (i == k) | (i == l) | (j == k) | (j == l) | (k == l))
        event_numerator[indices] = 0

        event_denominator = np.multiply(event_denominator, np.subtract.outer(np.subtract.outer(1 - win_probabilities, win_probabilities), win_probabilities))

        i, j, k = np.ogrid[:dim, :dim, :dim]
        indices = np.where((i == j) | (j == k) | (i == k))

        event_denominator[indices] = 1

        event_probabilities_4_places = event_numerator / event_denominator

        fourth_place_probabilities = np.sum(event_probabilities_4_places, axis=(1, 2, 3))

        place_probabilities += fourth_place_probabilities

    return place_probabilities


def compute_second_place_probabilities(event_numerator: ndarray, event_denominator: ndarray) -> ndarray:
    np.fill_diagonal(event_numerator, 0)
    event_probabilities_2_places = event_numerator / event_denominator

    return np.sum(event_probabilities_2_places, axis=1)


if __name__ == '__main__':
    #win_p = np.array([0.3, 0.5, 0.1, 0.1])
    win_p = np.array([0.1, 0.05, 0.03, 0.02, 0.4, 0.15, 0.02, 0.15, 0.05, 0.03])
    start = timeit.default_timer()
    compute_place_probabilities_of_race(win_p, places_num=4)
    stop = timeit.default_timer()
    print('Time: ', stop - start)
    print(compute_place_probabilities_of_race(win_p, places_num=4))