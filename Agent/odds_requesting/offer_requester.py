from abc import ABC, abstractmethod
from typing import List, Dict

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import BetOffer


class OfferRequester(ABC):

    def __init__(self, upcoming_race_cards: Dict[str, RaceCard]):
        self.upcoming_race_cards = upcoming_race_cards

    @abstractmethod
    def get_bet_offers(self) -> List[BetOffer]:
        pass

    @abstractmethod
    def delete_markets(self, deleted_race_card: RaceCard) -> None:
        pass
