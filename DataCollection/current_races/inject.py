from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.race_cards.base import BaseRaceCardsCollector


class TodayRaceCardsInjector:

    def __init__(self):
        self.today_race_cards_factory = BaseRaceCardsCollector()

    def inject_newest_odds_into_horses(self, race_card: RaceCard) -> RaceCard:
        updated_race_card = self.today_race_cards_factory.create_race_card(race_card.race_id)
        # TODO: implement this update less naively
        race_card.total_inverse_win_odds = 0
        for horse in race_card.horses:
            horse_with_updated_odds = [updated_horse for updated_horse in updated_race_card.horses if updated_horse.horse_id == horse.horse_id][0]
            horse.set_win_odds(horse_with_updated_odds.current_win_odds)
            if horse_with_updated_odds.is_scratched:
                race_card.horses.remove(horse)
            else:
                race_card.total_inverse_win_odds += horse.inverse_win_odds

        return race_card
