import datetime
import pickle
import time
from copy import deepcopy
from datetime import date, timedelta
from json import JSONDecodeError
from typing import List, Dict, Tuple

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

    BETS_PATH = f"../data/bets_log/{datetime.datetime.now()}"

    def __init__(self):
        self.event_market_lookup: Dict[RaceCard, Tuple[str, str]] = {}
        self.current_bets = []
        self.bettor = Bettor(bet_threshold=1.0)
        self.feature_manager = FeatureManager()
        self.columns = None

        self.update_race_card_data()

        with open(ESTIMATOR_PATH, "rb") as f:
            self.estimator: NNClassifier = pickle.load(f)

        self.init_feature_sources()

        race_cards_sample = self.get_upcoming_race_cards_sample()

        self.estimator.score_test_sample(race_cards_sample)

        scores = race_cards_sample.race_cards_dataframe["score"].to_numpy()
        self.estimation_result = PlaceProbabilizer().create_estimation_result(deepcopy(race_cards_sample), scores)

        self.init_event_market_lookup()
        print(self.event_market_lookup)

    def update_race_card_data(self) -> None:
        print("Scraping newest race card data...")

        train_data_collector = TrainDataCollector()

        day_before_yesterday = date.today() - timedelta(days=1)

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

        for race_card_file_name in tqdm(race_cards_loader.race_card_file_names):
            race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

            if self.columns is None:
                self.columns = list(race_cards.values())[0].attributes + self.feature_manager.feature_names

            race_cards_array_factory.race_cards_to_array(race_cards)

    def get_upcoming_race_cards_sample(self) -> RaceCardsSample:
        print("Scraping race cards of upcoming races...")

        race_ids = DayCollector().get_open_race_ids_of_day(datetime.date.today())

        race_ids = race_ids

        full_race_cards_collector = FullRaceCardsCollector(collect_results=False)
        race_cards = [full_race_cards_collector.create_race_card(race_id) for race_id in race_ids]

        self.upcoming_race_cards = {str(race_card.datetime): race_card for race_card in race_cards}

        print(list(self.upcoming_race_cards.keys()))

        race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager)
        test_sample_encoder = SampleEncoder(self.feature_manager.features, self.columns)

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(self.upcoming_race_cards)
        test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        return test_sample_encoder.get_race_cards_sample()

    def init_event_market_lookup(self) -> None:
        market_retriever = MarketRetriever()
        for race_card in self.upcoming_race_cards.values():
            event_id, market_id = market_retriever.get_event_and_market_id(
                country=race_card.country,
                track_name=race_card.track_name,
                race_number=race_card.race_number,
            )

            if market_id is not None:
                self.event_market_lookup[race_card] = (event_id, market_id)

    def get_bet_offers_from_race_card(self, race_card: RaceCard) -> Dict[str, List[BetOffer]]:
        if race_card not in self.event_market_lookup:
            return {}

        bet_offers = {str(race_card.datetime): []}

        event_id, market_id = self.event_market_lookup[race_card]

        exchange_odds_requester = ExchangeOddsRequester(
            customer_id="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2OTc2MTQxODcsImlhdCI6MTY5NzU3ODE4NywiYWNjb3VudElkIjoiUElXSVhfNjNhOWZmZjA4ZDM0MiIsInN0YXR1cyI6ImFjdGl2ZSIsInBvbGljaWVzIjpbIjE5IiwiNTQiLCI4NSIsIjEwNSIsIjIwIiwiMTA3IiwiMTA4IiwiMTEwIiwiMTEzIiwiMTI5IiwiMTMwIiwiMTMxIiwiMTMzIl0sImFjY1R5cGUiOiJCSUFCIiwibG9nZ2VkSW5BY2NvdW50SWQiOiJQSVdJWF82M2E5ZmZmMDhkMzQyIiwic3ViX2NvX2RvbWFpbnMiOm51bGwsImxldmVsIjoiQklBQiIsImN1cnJlbmN5IjoiRVVSIn0.cfDf1bynv_uhmvZf5_JozGD4SH7YSclMHGaOOU9HJMM",
            event_id=event_id,
            market_id=market_id,
        )

        while True:
            try:
                exchange_odds = exchange_odds_requester.get_odds_from_exchange()
            except JSONDecodeError:
                continue
            break

        for horse_number, odds in exchange_odds.items():
            if odds > 0:
                horse = race_card.get_horse_by_number(int(horse_number))

                if horse is None:
                    print(f"Horse nr. not found: {horse_number}, at race: {race_card.race_id}")
                else:
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
        while True:
            for race_card in self.upcoming_race_cards.values():
                time.sleep(1)
                bet_offers = self.get_bet_offers_from_race_card(race_card)

                bets = self.bettor.bet(bet_offers, self.estimation_result)

                if bets:
                    print(f"Found new Bets: {bets}.\n Writing them now...")
                    self.current_bets += bets

                    with open(self.BETS_PATH, "wb") as f:
                        pickle.dump(self.current_bets, f)
                else:
                    print(f"No new bets at: {race_card.name}")


def main():
    bettor = BetAgent()
    bettor.run()
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
