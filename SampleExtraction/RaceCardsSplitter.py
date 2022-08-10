from typing import Dict, Tuple

from DataAbstraction.Present.RaceCard import RaceCard


class RaceCardsSplitter:

    def __init__(self, train_fraction: float = 0.8):
        self.__train_fraction = train_fraction

    def split_race_cards(self, race_cards: Dict[str, RaceCard]) -> Tuple[dict, dict]:
        race_keys = list(race_cards.keys())
        race_keys.sort()

        n_races = len(race_keys)
        n_races_train = int(self.__train_fraction * n_races)

        train_race_keys = race_keys[:n_races_train]
        validation_race_keys = race_keys[n_races_train:]

        train_race_cards = {race_key: race_cards[race_key] for race_key in train_race_keys}
        validation_race_cards = {race_key: race_cards[race_key] for race_key in validation_race_keys}

        return train_race_cards, validation_race_cards
