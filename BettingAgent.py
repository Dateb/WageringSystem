import pickle
from datetime import datetime
from typing import List

from Betting.Bet import Bet
from Betting.WinBettor import WinBettor
from Control.BetController import BetController
from DataCollection.DayCollector import DayCollector
from DataCollection.RaceCardFactory import RaceCardFactory
from DataCollection.RaceCardsCollector import RaceCardsCollector
from SampleExtraction.FeatureManager import FeatureManager
from DataCollection.PastRacesContainer import PastRacesContainer
from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder

CONTROLLER_SUBMISSION_MODE_ON = True


class BettingAgent:

    __ESTIMATOR_PATH = "data/estimator_v1-03.dat"

    def __init__(self, kelly_wealth: float):
        self.__race_cards: List[RaceCard] = []
        self.__race_card_factory = RaceCardFactory()
        self.__day_collector = DayCollector()
        self.__collector = RaceCardsCollector(initial_race_cards=[], initial_past_races_container=PastRacesContainer({}))
        self.__bettor = WinBettor(kelly_wealth)
        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))
        self.__controller = BetController(
            user_name="Malfen",
            password="Titctsat49_",
            submission_mode_on=CONTROLLER_SUBMISSION_MODE_ON,
        )

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

        today = datetime.today().date()
        race_ids_today = self.__day_collector.get_open_race_ids_of_day(today)
        #race_ids_today = ["5013700"]
        print("Initialising races:")
        self.__init_races(race_ids_today)

    def __init_races(self, race_ids: List[str]):
        self.__race_cards = self.__collector.collect_from_race_ids(race_ids)

        self.__race_cards.sort(key=lambda x: x.datetime)
        self.__past_races_container = PastRacesContainer(self.__collector.past_races)

    def run(self):
        while self.__race_cards:
            next_race_card = self.__race_cards.pop(0)

            self.__controller.open_race_card(next_race_card)
            self.__controller.wait_for_race_start(next_race_card)

            next_race_card = self.__race_card_factory.run(next_race_card.race_id)

            bet = self.__compute_bet(next_race_card)
            self.__controller.execute_bet(next_race_card, bet)

    def __compute_bet(self, race_card: RaceCard) -> Bet:
        raw_samples = self.__encoder.transform([race_card], self.__past_races_container)

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        return bet


def main():
    bettor = BettingAgent(kelly_wealth=13)
    bettor.run()


if __name__ == '__main__':
    main()
