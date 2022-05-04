import pickle
from datetime import datetime
from typing import List

from Betting.Bet import Bet
from Betting.WinBettor import WinBettor
from Control.BetController import BetController
from DataCollection.DayCollector import DayCollector
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from DataCollection.RawRaceCardsCollector import RawRaceCardsCollector
from SampleExtraction.FeatureManager import FeatureManager
from DataCollection.PastRacesContainer import PastRacesContainer
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder


class BettingAgent:

    __ESTIMATOR_PATH = "data/estimator_v1-02.dat"

    def __init__(self, kelly_wealth: float):
        self.__race_cards: List[RaceCard] = []
        self.__raw_race_card_factory = RawRaceCardFactory()
        self.__day_collector = DayCollector()
        self.__collector = RawRaceCardsCollector(initial_raw_race_cards=[], initial_past_races_container=PastRacesContainer({}))
        self.__bettor = WinBettor(kelly_wealth)
        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))
        self.__controller = BetController(user_name="Malfen", password="Titctsat49_")

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

        today = datetime.today().date()
        #race_ids_today = self.__day_collector.get_race_ids_of_day(today)
        race_ids_today = ["5013700", "5013701"]
        print("Initialising races:")
        self.__init_races(race_ids_today)

    def __init_races(self, race_ids: List[str]):
        raw_race_cards = self.__collector.collect_from_race_ids(race_ids)
        self.__race_cards = [RaceCard(raw_race_card) for raw_race_card in raw_race_cards]

        self.__race_cards.sort(key=lambda x: x.datetime)
        self.__past_races_container = PastRacesContainer(self.__collector.raw_past_races)

    def run(self):
        self.__controller.open_race_card(self.__race_cards[0])
        self.__controller.accept_cookies()

        while self.__race_cards:
            next_race_card = self.__race_cards.pop(0)

            self.__controller.wait_for_race_start(next_race_card)

            next_race_card = self.__get_updated_race_card(next_race_card)

            bet = self.__compute_bet(next_race_card)
            self.__controller.execute_bet(next_race_card, bet)

    def __get_updated_race_card(self, race_card: RaceCard):
        race_id = race_card.race_id
        raw_race_card = self.__raw_race_card_factory.run(race_id)
        return RaceCard(raw_race_card)

    def __compute_bet(self, race_card: RaceCard) -> Bet:
        raw_samples = self.__encoder.transform([race_card], self.__past_races_container)

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        return bet


def main():
    bettor = BettingAgent(kelly_wealth=13)
    bettor.run()
    #production_bettor = ProductionBettor()
    #name, stakes = production_bettor.bet("5003320")
    #print(f"Bet on horse: {name} this amount: {stakes}")


if __name__ == '__main__':
    main()
