import time
import traceback
from datetime import datetime, date, timedelta
from typing import List

from tqdm import tqdm

from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.current_races.fetch import TodayRaceCardsFetcher
from DataCollection.current_races.inject import CurrentRaceCardsInjector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory


class BetAgent:

    CONTROLLER_SUBMISSION_MODE_ON = False

    def __init__(self):
        self.collect_newest_race_cards()
        self.init_feature_sources()

    def collect_newest_race_cards(self) -> None:
        train_data_collector = TrainDataCollector()

        day_before_yesterday = date.today() - timedelta(days=2)

        query_date = date(
            year=2023,
            month=10,
            day=1,
        )

        train_data_collector.collect_forward_until_newest_date(query_date, day_before_yesterday)

    def init_feature_sources(self) -> None:
        feature_manager = FeatureManager()

        race_cards_loader = RaceCardsPersistence("race_cards")
        race_cards_array_factory = RaceCardsArrayFactory(feature_manager)

        print("Loading all race cards to initialize all feature sources:")
        for race_card_file_name in tqdm(race_cards_loader.race_card_file_names[0:2]):
            race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
            race_cards_array_factory.race_cards_to_array(race_cards)

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


def main():
    bettor = BetAgent()
    # while True:
    #     try:
    #         bettor.run()
    #     except Exception as e:
    #         print(f"Agent crashed. Causing error: {str(e)}")
    #         print(traceback.format_exc())
    #     else:
    #         break


if __name__ == '__main__':
    main()
    print("finished")
