from typing import Dict
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.race_cards.base import BaseRaceCardsCollector


class CurrentRaceCardsInjector:

    def __init__(self, newest_betting_odds: Dict[str, float]):
        self.today_race_cards_factory = BaseRaceCardsCollector()
        self.newest_betting_odds = newest_betting_odds

    def inject_newest_odds_into_horses(self, race_card: RaceCard) -> RaceCard:
        race_card = self.inject_newest_estimation_odds_into_horses(race_card)
        race_card = self.inject_newest_betting_odds_into_horses(race_card)

        return race_card

    def inject_newest_estimation_odds_into_horses(self, race_card: RaceCard) -> RaceCard:
        updated_race_card = self.today_race_cards_factory.create_race_card(race_card.race_id)
        # TODO: implement this update less naively
        race_card.total_inverse_win_odds = 0
        for horse in race_card.horses:
            horse_with_updated_odds = [updated_horse for updated_horse in updated_race_card.horses if updated_horse.horse_id == horse.horse_id][0]
            horse.set_estimation_win_odds(horse_with_updated_odds.current_win_odds)
            if horse_with_updated_odds.is_scratched:
                race_card.horses.remove(horse)
            else:
                race_card.total_inverse_win_odds += horse.inverse_win_odds

        race_card.is_open = updated_race_card.is_open
        return race_card

    def inject_newest_betting_odds_into_horses(self, race_card) -> RaceCard:
        for horse in race_card.horses:
            horse.set_betting_odds(self.newest_betting_odds[str(horse.number)])
        return race_card
