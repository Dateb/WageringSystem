import datetime
import pickle
from time import sleep
from copy import deepcopy
from datetime import datetime, date, timedelta, time
from typing import Dict

import requests
from tqdm import tqdm

from Agent.odds_requesting.bookie_offer_requester import BookieOfferRequester
from Agent.odds_requesting.exchange_offer_requester import ExchangeOfferRequester
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Betting.bet import RacebetsBettor
from Model.Estimators.Classification.NNClassifier import NNClassifier
from Model.Estimators.estimated_probabilities_creation import PlaceProbabilizer, WinProbabilizer
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from ModelTuning.simulate_conf import ESTIMATOR_PATH
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder


class BetAgent:

    BETS_PATH = f"../data/bets_log/{datetime.now()}"

    def __init__(self):
        self.market_type = "WIN"
        self.offer_source = "Betfair"
        self.betting_mode = "Write"

        if self.market_type == "WIN":
            self.probabilizer = WinProbabilizer()
        else:
            self.probabilizer = PlaceProbabilizer()

        self.current_bets = []
        self.bettor = RacebetsBettor(bet_threshold=0.1)
        self.feature_manager = FeatureManager()
        self.columns = None

        self.update_race_card_data()

        with open(ESTIMATOR_PATH, "rb") as f:
            self.estimator: NNClassifier = pickle.load(f)

        self.upcoming_race_cards = self.get_upcoming_race_cards()
        self.init_feature_sources()

        race_cards_sample = self.race_cards_to_sample()

        self.estimator.score_test_sample(race_cards_sample)

        scores = race_cards_sample.race_cards_dataframe["score"].to_numpy()
        self.estimation_result = self.probabilizer.create_estimation_result(deepcopy(race_cards_sample), scores)

        print(self.estimation_result.probability_estimates)

        if self.offer_source == "Betfair":
            customer_id = self.get_customer_id()
            self.offer_requester = ExchangeOfferRequester(
                customer_id=customer_id,
                market_type=self.market_type,
                upcoming_race_cards=self.upcoming_race_cards
            )
        else:
            self.offer_requester = BookieOfferRequester(self.upcoming_race_cards)

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

    def get_upcoming_race_cards(self) -> Dict[str, RaceCard]:
        print("Scraping race cards of upcoming races...")

        current_time = datetime.now().time()

        day_to_collect = date.today()

        if time(20, 0) <= current_time <= time(23, 59):
            day_to_collect += timedelta(days=1)

        race_ids = DayCollector().get_open_race_ids_of_day(day_to_collect)

        race_ids = race_ids
        print(race_ids)

        full_race_cards_collector = FullRaceCardsCollector(collect_results=False)
        race_cards = [full_race_cards_collector.create_race_card(race_id) for race_id in race_ids]

        race_cards = [race_card for race_card in race_cards if race_card.category == "HCP"]

        return {str(race_card.datetime): race_card for race_card in race_cards}

    def race_cards_to_sample(self) -> RaceCardsSample:
        race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager)
        test_sample_encoder = SampleEncoder(self.feature_manager.features, self.columns)

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(self.upcoming_race_cards)
        test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        return test_sample_encoder.get_race_cards_sample()

    def get_customer_id(self) -> str:
        login_response = requests.post(
            "https://api.piwi247.com/api/users/login",
            data={
                "email": "daniel.tebart@googlemail.com",
                "password": "Ds*#de!@6846",
                "loginType": 1,
                "remember": False
            }
        )

        login_response_data = login_response.json()["data"]
        return login_response_data["token"]["orbit"]["access_token"]

    def run(self):
        while True:
            bet_offers = self.offer_requester.get_bet_offers()

            if bet_offers is not None:
                race_card = bet_offers[0].race_card
                bet_offers = {str(race_card.datetime): bet_offers}

                bets = self.bettor.bet(bet_offers, self.estimation_result)

                if bets:
                    self.current_bets += bets
                    if self.betting_mode == "Write":
                        print("Writing new bets...")

                        with open(self.BETS_PATH, "wb") as f:
                            pickle.dump(self.current_bets, f)

                    if self.betting_mode == "Print":
                        for bet in bets:
                            print("Found suitable bet:")
                            print(bet)
                            print("---------------------")


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
