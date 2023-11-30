from time import sleep
from typing import List, Dict

from Agent.odds_requesting.offer_requester import OfferRequester
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.race_cards.base import BaseRaceCardsCollector
from Model.Betting.bet import BetOffer


class BookieOfferRequester(OfferRequester):

    def __init__(self, upcoming_race_cards: Dict[str, RaceCard]):
        super().__init__(upcoming_race_cards)
        self.race_cards_collector = BaseRaceCardsCollector(remove_non_starters=True)

    def get_bet_offers(self) -> List[BetOffer]:
        bet_offers = []
        for race_card in self.upcoming_race_cards.values():
            updated_race_card = self.race_cards_collector.get_race_card(race_card.race_id)
            sleep(1)

            for horse in updated_race_card.horses:
                new_offer = BetOffer(
                    race_card=race_card,
                    horse=horse,
                    odds=horse.racebets_win_sp,
                    scratched_horses=[],
                    event_datetime=None,
                    adjustment_factor=1.0,
                )
                bet_offers.append(new_offer)

        return bet_offers
