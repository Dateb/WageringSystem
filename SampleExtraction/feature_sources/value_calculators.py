from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard


def win_probability(race_card: RaceCard, horse: Horse) -> float:
    return horse.betfair_win_sp
