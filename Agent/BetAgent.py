import datetime
import pickle
import time
from copy import deepcopy
from datetime import date, timedelta
from typing import List, Dict

from tqdm import tqdm

from Agent.exchange_odds_request import ExchangeOddsRequester, MarketRetriever
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.current_races.fetch import TodayRaceCardsFetcher
from DataCollection.race_cards.base import BaseRaceCardsCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Betting.bet import Bettor, BetOffer
from Model.Betting.exchange_offers_parsing import RaceDateToCardMapper
from Model.Estimators.Classification.NNClassifier import NNClassifier
from Model.Estimators.estimated_probabilities_creation import PlaceProbabilizer
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from ModelTuning.simulate_conf import ESTIMATOR_PATH
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder


class BetAgent:

    CONTROLLER_SUBMISSION_MODE_ON = False

    def __init__(self):
        self.race_cards_mapper = None
        self.feature_manager = FeatureManager()
        self.columns = None

        self.update_race_card_data()

        with open(ESTIMATOR_PATH, "rb") as f:
            self.estimator: NNClassifier = pickle.load(f)

        self.init_feature_sources()

        race_cards_sample = self.get_upcoming_race_cards_sample()

        self.estimator.score_test_sample(race_cards_sample)

        scores = race_cards_sample.race_cards_dataframe["score"].to_numpy()
        estimation_result = PlaceProbabilizer().create_estimation_result(deepcopy(race_cards_sample), scores)

        bet_offers = self.get_bet_offers()

        bettor = Bettor(bet_threshold=1.0)

        bets = bettor.bet(bet_offers, estimation_result)

        print(bets)

    def update_race_card_data(self) -> None:
        print("Scraping newest race card data...")

        train_data_collector = TrainDataCollector()

        day_before_yesterday = date.today() - timedelta(days=2)

        query_date = date(
            year=2023,
            month=10,
            day=1,
        )

        train_data_collector.collect_forward_until_newest_date(query_date, day_before_yesterday)

    def init_feature_sources(self) -> None:
        print("Loading all race cards to initialize all feature sources...")

        race_cards_loader = RaceCardsPersistence("race_cards")
        race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager)

        for race_card_file_name in tqdm(race_cards_loader.race_card_file_names[0:2]):
            race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

            if self.columns is None:
                self.columns = list(race_cards.values())[0].attributes + self.feature_manager.feature_names

            race_cards_array_factory.race_cards_to_array(race_cards)

    def get_upcoming_race_cards_sample(self) -> RaceCardsSample:
        print("Scraping race cards of upcoming races...")

        race_ids = DayCollector().get_open_race_ids_of_day(datetime.date.today())
        race_ids = ["6365974", "6365975"]

        race_ids.sort()

        full_race_cards_collector = FullRaceCardsCollector(collect_results=False)
        race_cards = [full_race_cards_collector.create_race_card(race_id) for race_id in race_ids]

        self.upcoming_race_cards = {str(race_card.datetime): race_card for race_card in race_cards}

        print(list(self.upcoming_race_cards.keys()))

        race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager)
        test_sample_encoder = SampleEncoder(self.feature_manager.features, self.columns)

        self.race_cards_mapper = RaceDateToCardMapper(self.upcoming_race_cards)

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(self.upcoming_race_cards)
        test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        return test_sample_encoder.get_race_cards_sample()

    def get_bet_offers(self) -> Dict[str, List[BetOffer]]:
        bet_offers = {}
        for race_card in self.upcoming_race_cards.values():
            bet_offers[str(race_card.datetime)] = []

            market_retriever = MarketRetriever()
            event_id, market_id = market_retriever.get_event_and_market_id(
                country=race_card.country,
                track_name=race_card.track_name,
                race_number=race_card.race_number,
            )

            exchange_odds_requester = ExchangeOddsRequester(
                customer_id="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2OTczNzE0ODYsImlhdCI6MTY5NzMzNTQ4NiwiYWNjb3VudElkIjoiUElXSVhfNjNhOWZmZjA4ZDM0MiIsInN0YXR1cyI6ImFjdGl2ZSIsInBvbGljaWVzIjpbIjE5IiwiNTQiLCI4NSIsIjEwNSIsIjIwIiwiMTA3IiwiMTA4IiwiMTEwIiwiMTEzIiwiMTI5IiwiMTMwIiwiMTMxIiwiMTMzIl0sImFjY1R5cGUiOiJCSUFCIiwibG9nZ2VkSW5BY2NvdW50SWQiOiJQSVdJWF82M2E5ZmZmMDhkMzQyIiwic3ViX2NvX2RvbWFpbnMiOm51bGwsImxldmVsIjoiQklBQiIsImN1cnJlbmN5IjoiRVVSIn0.Qq6lJ9RPybL7QLcdBzrv772F3y1EU0UY1hOg4o1LFAM",
                event_id=event_id,
                market_id=market_id,
            )

            exchange_odds = exchange_odds_requester.get_odds_from_exchange()

            for horse_number, odds in exchange_odds.items():
                if odds > 0:
                    horse = race_card.get_horse_by_number(int(horse_number))

                    new_offer = BetOffer(
                        race_card=race_card,
                        horse_name=horse.name,
                        odds=odds,
                        scratched_horses=[],
                        event_datetime=None,
                        adjustment_factor=1.0,
                    )

                    bet_offers[str(race_card.datetime)].append(new_offer)

        return bet_offers

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
