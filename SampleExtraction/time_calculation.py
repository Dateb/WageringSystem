from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard


def get_day_difference(race_card: RaceCard, horse: Horse, first_race_idx: int, second_race_idx: int) -> int:
    if first_race_idx == -1:
        first_datetime = race_card.datetime
    else:
        first_datetime = horse.form_table.past_forms[first_race_idx].datetime
    second_date_time = horse.form_table.past_forms[second_race_idx].datetime
    return (first_datetime - second_date_time).days
