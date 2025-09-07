import datetime
import pickle
from abc import abstractmethod
from datetime import datetime, date, timedelta, time
from typing import Dict

from Agent.leakage_detection import LeakageDetector
from Agent.odds_requesting.exchange_offer_requester import Exchange
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Betting.bet import BettorFactory, OddsThreshold, BetfairOddsVigAdjuster
from Model.Estimation.estimated_probabilities_creation import PlaceProbabilizer, EstimationResult
from ModelTuning import simulate_conf
from ModelTuning.simulate import ModelSimulator
from Persistence.RaceCardPersistence import RaceDataPersistence
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


class ValueReporter(Actuator):

    def __init__(self, estimation_result: EstimationResult, exchange: Exchange):
        super().__init__()
        self.exchange = exchange
        self.estimation_result = estimation_result

        odds_vig_adjuster = BetfairOddsVigAdjuster()
        self.odds_threshold = OddsThreshold(odds_vig_adjuster, min_ev=1.0)
        self.value_opportunities = []

    def run(self) -> None:
        probability_estimates = self.estimation_result.results
        for market in self.exchange.markets:
            if market.market_id:
                race_key = str(market.race_card.datetime)
                if race_key in probability_estimates:
                    race_card_probabilities = probability_estimates[race_key]
                    for horse_exchange_id, horse_number in market.horse_number_by_exchange_id.items():
                        if int(horse_number) in race_card_probabilities:
                            horse_probability = race_card_probabilities[int(horse_number)]["probability"]
                            horse_odds = race_card_probabilities[int(horse_number)]["odds"]
                            horse_min_odds = self.odds_threshold.get_min_odds(horse_probability)
                            horse_ev = horse_odds * horse_probability

                            if horse_ev > 1.1 and horse_min_odds <= 10:
                                value_opportunity = {
                                    "Race": market.race_card.name,
                                    "Horse number": horse_number,
                                    "Min Odds": horse_min_odds,
                                    "EV": horse_ev
                                }
                                self.value_opportunities.append(value_opportunity)
                else:
                    print(f"Skipped betting on race due to missing estimates: {market.race_card.race_id}")

        self.value_opportunities.sort(key=lambda x: x["EV"], reverse=True)

        for value_opportunity in self.value_opportunities:
            print(value_opportunity)


class ExchangeBetRequester(Actuator):

    CURRENT_BANKROLL: float = 820.38

    def __init__(self, estimation_result: EstimationResult, exchange: Exchange):
        super().__init__()
        self.exchange = exchange
        self.estimation_result = estimation_result

        odds_vig_adjuster = BetfairOddsVigAdjuster()
        self.odds_threshold = OddsThreshold(odds_vig_adjuster, min_ev=1.0)
        self.stakes = max([round(self.CURRENT_BANKROLL * 0.0033, 2), 6.0])

    def run(self) -> None:
        probability_estimates = self.estimation_result.results
        for market in self.exchange.markets:
            if market.market_id:
                race_key = str(market.race_card.datetime)
                if race_key in probability_estimates:
                    race_card_probabilities = probability_estimates[race_key]
                    for horse_exchange_id, horse_number in market.horse_number_by_exchange_id.items():
                        if int(horse_number) in race_card_probabilities:
                            horse_probability = race_card_probabilities[int(horse_number)]["probability"]
                            horse_odds = race_card_probabilities[int(horse_number)]["odds"]
                            horse_min_odds = self.odds_threshold.get_min_odds(horse_probability)
                            horse_ev = horse_odds * horse_probability

                            print(f"Race/Horse-Nr/Min-Odds/EV: "
                                  f"{market.race_card.name}/{horse_number}/{horse_min_odds}/{horse_ev}")
                            # self.exchange.add_bet(market, int(horse_exchange_id), horse_min_odds, self.stakes)
                else:
                    print(f"Skipped betting on race due to missing estimates: {market.race_card.race_id}")

        # self.exchange.submit_bets()


class BetAgent:

    def __init__(self, actuator_name: str):
        self.market_type = "WIN"
        self.actuator_name = actuator_name

        self.leakage_detector = LeakageDetector()

        self.columns = None

        self.scrape_newest_race_cards()

        data_splitter = MonthDataSplitter(
            container_upper_limit_percentage=0.1,
            n_months_test_sample=14,
            n_months_forward_offset=0,
            race_cards_folder=simulate_conf.RELEASE_RACE_CARDS_FOLDER_NAME
        )

        model_simulator = ModelSimulator(data_splitter)

        model_simulator.simulate_prediction()
        model_simulator.simulate_betting()

        # self.leakage_detector.run()

        self.upcoming_race_cards = self.get_upcoming_race_cards()
        race_cards_sample = self.race_cards_to_sample(model_simulator)

        self.leakage_detector.save_live_data(race_cards_sample)

        self.estimation_result, _ = model_simulator.estimator.predict(race_cards_sample)

        print(self.estimation_result.results)

        if self.actuator_name == "ExchangeBetRequester":
            exchange = Exchange(
                market_type=self.market_type,
                upcoming_race_cards=self.upcoming_race_cards
            )
            self.actuator = ExchangeBetRequester(self.estimation_result, exchange)
        elif self.actuator_name == "ValueReporter":
            exchange = Exchange(
                market_type=self.market_type,
                upcoming_race_cards=self.upcoming_race_cards
            )
            self.actuator = ValueReporter(self.estimation_result, exchange)

    def scrape_newest_race_cards(self) -> None:
        print("Scraping newest race card data...")

        train_data_collector = TrainDataCollector(RaceDataPersistence(simulate_conf.RELEASE_RACE_CARDS_FOLDER_NAME))

        query_date = date(
            year=2023,
            month=10,
            day=1,
        )

        start_time = datetime.strptime('21:00:00', '%H:%M:%S').time()
        end_time = datetime.strptime('23:55:00', '%H:%M:%S').time()

        newest_date = date.today()
        if start_time <= datetime.now().time() < end_time:
            newest_date = date.today() + timedelta(days=1)

        train_data_collector.collect_forward_until_newest_date(query_date, newest_date)

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
    actuator_name = "ValueReporter"
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
