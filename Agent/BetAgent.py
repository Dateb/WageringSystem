import os
import time
from datetime import datetime
from typing import List

from Agent.AgentController import AgentController
from Agent.AgentModel import AgentModel
from DataCollection.DayCollector import DayCollector
from DataAbstraction.RaceCardFactory import RaceCardFactory
from DataCollection.RaceCardsCollector import RaceCardsCollector
from DataAbstraction.Present.RaceCard import RaceCard

CONTROLLER_SUBMISSION_MODE_ON = True
BET_LIMIT = 30


class BetAgent:

    def __init__(self):
        self.model = AgentModel()
        self.controller = AgentController(bet_limit=BET_LIMIT, submission_mode_on=CONTROLLER_SUBMISSION_MODE_ON)

        self.today_race_cards: List[RaceCard] = []
        self.today_race_cards_factory = RaceCardFactory(collect_results=False)
        self.day_collector = DayCollector()
        self.race_cards_collector = RaceCardsCollector()

    def init_races(self, race_ids: List[str]):
        base_race_cards = self.race_cards_collector.collect_base_race_cards_from_race_ids(race_ids)

        base_race_cards.sort(key=lambda x: x.datetime)
        self.today_race_cards = base_race_cards

    def run(self):
        today = datetime.today().date()
        race_ids_today = self.day_collector.get_open_race_ids_of_day(today)
        print("Initialising races:")
        self.init_races(race_ids_today)
        self.controller.restart_driver()
        self.controller.relogin()

        for race_card in self.today_race_cards:
            print("Loading full version of race card...")
            full_race_card = self.today_race_cards_factory.run(race_card.race_id)

            self.controller.open_race_card(full_race_card)
            self.controller.wait_for_race_start(full_race_card)
            self.controller.prepare_for_race_start()

            updated_race_card = self.__update_current_race_card(full_race_card)
            start_newest_info = time.time()

            betting_slip = self.model.bet_on_race_card(updated_race_card)
            below_minimum_stakes_bet = [bet for bet in betting_slip.bets if bet.stakes_fraction * BET_LIMIT < 0.5]
            if betting_slip.bets and len(below_minimum_stakes_bet) == 0:
                self.controller.submit_betting_slip(betting_slip)
                end_bet = time.time()
                print(betting_slip)
                print(f"time to execute on race odds:{end_bet - start_newest_info}")
                # Quick and dirty security measure: could otherwise stick in an unsafe state regarding open betting slips
                raise ValueError("Just restarting for security.")
            else:
                print("No value found. Skipping race.")

    def __update_current_race_card(self, race_card: RaceCard) -> RaceCard:
        updated_race_card = self.today_race_cards_factory.get_race_card(race_card.race_id)
        # TODO: implement this update less naively
        for horse in race_card.horses:
            horse_with_updated_odds = [updated_horse for updated_horse in updated_race_card.horses if updated_horse.horse_id == horse.horse_id][0]
            horse.set_win_odds(horse_with_updated_odds.current_win_odds)
            if horse_with_updated_odds.is_scratched:
                race_card.horses.remove(horse)

        return race_card


def main():
    bettor = BetAgent()
    while True:
        try:
            bettor.run()
        except Exception as e:
            print(f"Agent crashed. Causing error: {str(e)}")
        else:
            break


if __name__ == '__main__':
    main()
    print("finished")
