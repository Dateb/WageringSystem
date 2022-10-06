def get_simple_average(count: int, old_average: float, new_obs: float):
    return ((count - 1) * old_average + new_obs) / count
