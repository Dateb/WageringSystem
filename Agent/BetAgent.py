import datetime
import pickle
from abc import abstractmethod
from copy import deepcopy
from datetime import datetime, date, timedelta, time
from typing import Dict

from Agent.leakage_detection import LeakageDetector
from Agent.odds_requesting.bookie_offer_requester import BookieOfferRequester
from Agent.odds_requesting.exchange_offer_requester import Exchange
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Betting.bet import BettorFactory, OddsThreshold, BetfairOddsVigAdjuster
from Model.Estimators.estimated_probabilities_creation import PlaceProbabilizer, WinProbabilizer, EstimationResult
from ModelTuning import simulate_conf
from ModelTuning.simulate import ModelSimulator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.data_splitting import MonthDataSplitter


class Actuator:

    def __init__(self):
        pass

    @abstractmethod
    def run(self) -> None:
        pass


class ExchangeBetLogger(Actuator):

    BETS_PATH = f"../data/bets_log/{datetime.now()}"

    def __init__(
            self,
            estimation_result: EstimationResult,
            exchange: Exchange,
            upcoming_race_cards: Dict[str, RaceCard]
    ):
        super().__init__()
        self.exchange = exchange
        self.estimation_result = estimation_result
        self.bettor = BettorFactory().create_bettor(bet_threshold=0.01)
        self.upcoming_race_cards = upcoming_race_cards
        self.current_bets = []

    def remove_expired_upcoming_race_cards(self) -> None:
        expired_race_card_key = None
        for key, race_card in self.upcoming_race_cards.items():
            if datetime.now() > (race_card.datetime - timedelta(hours=0, minutes=10)):
                expired_race_card_key = key

        if expired_race_card_key is not None:
            expired_race_card = self.upcoming_race_cards[expired_race_card_key]
            try:
                self.exchange.delete_market_of_race_card(expired_race_card)
                del self.upcoming_race_cards[expired_race_card_key]

                self.exchange.reset_connection()

            except KeyError as error:
                print(f"Keyerror when deleting race: {expired_race_card}: {error}")

    def run(self) -> None:
        while self.upcoming_race_cards:
            self.remove_expired_upcoming_race_cards()
            bet_offers = self.exchange.get_bet_offers()

            if bet_offers:
                race_card = bet_offers[0].race_card
                bet_offers = {str(race_card.datetime): bet_offers}

                bets = self.bettor.bet(bet_offers, self.estimation_result)

                for bet in bets:
                    print(bet)
                    # self.current_bets += bets
                    # print(f"{datetime.now()}: Writing new bets...")
                    #
                    # with open(self.BETS_PATH, "wb") as f:
                    #     pickle.dump(self.current_bets, f)


class RacebetsBetsReporter(Actuator):

    def __init__(
            self,
            estimation_result: EstimationResult,
            upcoming_race_cards: Dict[str, RaceCard]
    ):
        super().__init__()
        self.estimation_result = estimation_result
        self.bettor = BettorFactory().create_bettor(bet_threshold=0.01)
        self.upcoming_race_cards = upcoming_race_cards
        self.current_bets = []
        self.racebets_offer_requester = BookieOfferRequester()

    def remove_expired_upcoming_race_cards(self) -> None:
        expired_race_card_key = None
        for key, race_card in self.upcoming_race_cards.items():
            if datetime.now() > (race_card.datetime - timedelta(hours=0, minutes=10)):
                expired_race_card_key = key

        if expired_race_card_key is not None:
            del self.upcoming_race_cards[expired_race_card_key]

    def run(self) -> None:
        while self.upcoming_race_cards:
            self.remove_expired_upcoming_race_cards()
            for race_card in self.upcoming_race_cards.values():
                bet_offers = self.racebets_offer_requester.get_bet_offers(race_card)

                if bet_offers:
                    race_card = bet_offers[0].race_card
                    bet_offers = {str(race_card.datetime): bet_offers}

                    bets = self.bettor.bet(bet_offers, self.estimation_result)

                    for bet in bets:
                        print(bet)
                        # self.current_bets += bets
                        # print(f"{datetime.now()}: Writing new bets...")
                        #
                        # with open(self.BETS_PATH, "wb") as f:
                        #     pickle.dump(self.current_bets, f)


class ExchangeBetRequester(Actuator):

    def __init__(self, estimation_result: EstimationResult, exchange: Exchange):
        super().__init__()
        self.exchange = exchange
        self.estimation_result = estimation_result

        odds_vig_adjuster = BetfairOddsVigAdjuster()
        self.odds_threshold = OddsThreshold(odds_vig_adjuster, alpha=0.02)

    def run(self) -> None:
        probability_estimates = self.estimation_result.probability_estimates
        for market in self.exchange.markets:
            race_key = str(market.race_card.datetime)
            race_card_probabilities = probability_estimates[race_key]
            for horse_exchange_id, horse_number in market.horse_number_by_exchange_id.items():
                horse_probability = race_card_probabilities[int(horse_number)]
                horse_min_odds = self.odds_threshold.get_min_odds(horse_probability)

                # self.exchange.place_odds_on_horse(market, horse_exchange_id, horse_min_odds)

                if horse_min_odds < 10:
                    print(f"Race/Horse-Nr/Odds: {race_key}/{horse_number}/{horse_min_odds}")


class MinOddsReporter(Actuator):

    def __init__(self, estimation_result: EstimationResult, upcoming_race_cards: Dict[str, RaceCard]):
        super().__init__()
        self.estimation_result = estimation_result
        self.upcoming_race_cards = upcoming_race_cards

        odds_vig_adjuster = BetfairOddsVigAdjuster()
        self.odds_threshold = OddsThreshold(odds_vig_adjuster, alpha=0.1)

    def run(self) -> None:
        for race_key, race_card in self.upcoming_race_cards.items():
            for horse in race_card.runners:
                horse_probability = self.estimation_result.probability_estimates[race_key][horse.number]
                horse_min_odds = self.odds_threshold.get_min_odds(horse_probability)

                if horse_min_odds < 10:
                    print(f"Race/Horse-Nr/Odds: {race_key}/{horse.number}/{horse_min_odds}")


class BetAgent:

    def __init__(self, actuator_name: str):
        self.market_type = "WIN"
        self.actuator_name = actuator_name

        if self.market_type == "WIN":
            self.probabilizer = WinProbabilizer()
        else:
            self.probabilizer = PlaceProbabilizer()

        self.leakage_detector = LeakageDetector()

        self.columns = None

        self.update_race_card_data()

        data_splitter = MonthDataSplitter(
            container_upper_limit_percentage=0.1,
            n_months_test_sample=14,
            n_months_forward_offset=0,
            race_cards_folder=simulate_conf.RELEASE_RACE_CARDS_FOLDER_NAME
        )

        model_simulator = ModelSimulator(data_splitter)

        model_simulator.simulate_prediction()
        model_simulator.simulate_betting()

        self.leakage_detector.run()

        self.upcoming_race_cards = self.get_upcoming_race_cards()
        race_cards_sample = self.race_cards_to_sample(model_simulator)

        self.leakage_detector.save_live_data(race_cards_sample)

        model_simulator.estimator.score_test_sample(race_cards_sample)
        scores = race_cards_sample.race_cards_dataframe["score"].to_numpy()

        self.estimation_result = model_simulator.probabilizer.create_estimation_result(
            deepcopy(race_cards_sample),
            scores
        )

        print(self.estimation_result.probability_estimates)

        if self.actuator_name == "ExchangeBetLogger":
            exchange = Exchange(
                market_type=self.market_type,
                upcoming_race_cards=self.upcoming_race_cards
            )
            self.actuator = ExchangeBetLogger(self.estimation_result, exchange, self.upcoming_race_cards)
        elif self.actuator_name == "ExchangeBetRequester":
            exchange = Exchange(
                market_type=self.market_type,
                upcoming_race_cards=self.upcoming_race_cards
            )
            self.actuator = ExchangeBetRequester(self.estimation_result, exchange)
        elif self.actuator_name == "RacebetsBetsReporter":
            self.actuator = RacebetsBetsReporter(self.estimation_result, self.upcoming_race_cards)
        else:
            self.actuator = MinOddsReporter(self.estimation_result, self.upcoming_race_cards)

    def update_race_card_data(self) -> None:
        print("Scraping newest race card data...")

        train_data_collector = TrainDataCollector(RaceCardsPersistence(simulate_conf.RELEASE_RACE_CARDS_FOLDER_NAME))

        query_date = date(
            year=2023,
            month=10,
            day=1,
        )

        train_data_collector.collect_forward_until_newest_date(query_date, date.today())

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

        # race_cards = [race_card for race_card in race_cards if race_card.category == "HCP"]

        return {str(race_card.datetime): race_card for race_card in race_cards}

    def race_cards_to_sample(self, model_simulator: ModelSimulator) -> RaceCardsSample:
        race_cards_array_factory = RaceCardsArrayFactory(model_simulator.feature_manager)
        test_sample_encoder = SampleEncoder(model_simulator.feature_manager.features, model_simulator.columns)

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(self.upcoming_race_cards)
        test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        return test_sample_encoder.get_race_cards_sample()

    def run(self):
        self.actuator.run()


def main():
    actuator_name = "MinOddsReporter"
    bettor = BetAgent(actuator_name=actuator_name)
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
