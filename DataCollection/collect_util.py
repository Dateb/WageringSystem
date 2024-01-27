import math


def distance_to_meters(distance: str) -> int:
    distance_amount_per_unit = {
        "m": 0,
        "f": 0,
        "y": 0,
    }

    distance_split = distance.split(sep=" ")

    for distance_unit in distance_split:
        unit = distance_unit[-1]
        distance_amount = distance_unit[:-1]
        if distance_amount.isnumeric() and unit in distance_amount_per_unit:
            distance_amount_per_unit[unit] = float(distance_amount)

    distance_in_metres = distance_amount_per_unit["m"] * 1609.34 + distance_amount_per_unit["f"] * 201.168 \
                         + distance_amount_per_unit["y"] * 0.9144

    return math.floor(distance_in_metres)
