import time
import traceback
from datetime import datetime, date
from typing import List

from Agent.AgentModel import AgentModel
from Agent.SeleniumAgentController import SeleniumAgentController
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.current_races.fetch import TodayRaceCardsFetcher
from DataCollection.current_races.inject import TodayRaceCardsInjector
from DataCollection.race_cards.full import FullRaceCardsCollector


class BetAgent:

    CONTROLLER_SUBMISSION_MODE_ON = False

    def __init__(self):
        self.collect_race_cards_until_today()
        self.model = AgentModel()
        self.controller = SeleniumAgentController(submission_mode_on=self.CONTROLLER_SUBMISSION_MODE_ON)

        self.today_race_cards: List[RaceCard] = TodayRaceCardsFetcher().fetch_today_race_cards()
        self.today_race_cards_injector = TodayRaceCardsInjector()

    def run(self):
        self.controller.restart_driver()
        self.controller.relogin()

        print([race_card.datetime for race_card in self.today_race_cards])
        while self.today_race_cards:
            race_card = self.today_race_cards[0]
            print("Loading full version of race card...")
            full_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(race_card.race_id)

            self.controller.read_wealth()
            print(f"Using bet limit: {self.controller.bet_limit}")
            self.controller.open_race_card(full_race_card)

            self.today_race_cards.remove(race_card)
            self.controller.wait_for_race_start(full_race_card)
            self.controller.prepare_for_race_start()

            updated_race_card = self.today_race_cards_injector.inject_newest_odds_into_horses(full_race_card)
            start_betting_time = time.time()

            betting_slip = self.model.bet_on_race_card(updated_race_card)
            below_minimum_stakes_bet = [bet for bet in betting_slip.bets if bet.stakes_fraction * self.controller.bet_limit < 0.5]
            if betting_slip.bets and len(below_minimum_stakes_bet) == 0:
                self.controller.submit_betting_slip(betting_slip)
                end_betting_time = time.time()
                print(betting_slip)
                print(f"time to execute on race odds:{end_betting_time - start_betting_time}")
                # Quick and dirty security measure: could otherwise stick in an unsafe state regarding open betting slips
                raise ValueError("Just restarting for security.")
            else:
                print("No value found. Skipping race.")

    def collect_race_cards_until_today(self):
        train_data_collector = TrainDataCollector(file_name="race_cards")
        query_date = date(year=2022, month=1, day=1)

        newest_date = datetime.today().date()
        train_data_collector.collect_forward_until_newest_date(query_date=query_date, newest_date=newest_date)


def main():
    bettor = BetAgent()
    while True:
        try:
            bettor.run()
        except Exception as e:
            print(f"Agent crashed. Causing error: {str(e)}")
            print(traceback.format_exc())
        else:
            break


if __name__ == '__main__':
    main()
    print("finished")
