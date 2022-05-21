import pickle
from datetime import datetime
from typing import List

from Betting.Bet import Bet
from Betting.WinBettor import WinBettor
from Control.BetController import BetController
from DataCollection.DayCollector import DayCollector
from DataAbstraction.RaceCardFactory import RaceCardFactory
from DataCollection.RaceCardsCollector import RaceCardsCollector
from SampleExtraction.FeatureManager import FeatureManager
from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder

CONTROLLER_SUBMISSION_MODE_ON = True


class BettingAgent:

    __ESTIMATOR_PATH = "data/estimator_v2-03.dat"

    def __init__(self, kelly_wealth: float):
        self.__base_race_cards: List[RaceCard] = []
        self.__race_card_factory = RaceCardFactory()
        self.__day_collector = DayCollector()
        self.__collector = RaceCardsCollector(initial_race_cards=[])
        self.__bettor = WinBettor(kelly_wealth)
        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))
        self.__controller = BetController(
            submission_mode_on=CONTROLLER_SUBMISSION_MODE_ON,
        )

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

        today = datetime.today().date()
        race_ids_today = self.__day_collector.get_open_race_ids_of_day(today)
        print("Initialising races:")
        self.__init_races(race_ids_today)

    def __init_races(self, race_ids: List[str]):
        self.__base_race_cards = self.__collector.collect_base_race_cards_from_race_ids(race_ids)

        self.__base_race_cards.sort(key=lambda x: x.datetime)

    def run(self):
        while self.__base_race_cards:
            next_race_card = self.__collector.collect_full_race_cards_from_race_ids([self.__base_race_cards.pop(0).race_id])[0]

            self.__controller.open_race_card(next_race_card)
            self.__controller.wait_for_race_start(next_race_card)

            next_race_card = self.__get_race_card_with_latest_odds(next_race_card)

            bet = self.__compute_bet(next_race_card)
            next_race_card = self.__get_race_card_with_latest_odds(next_race_card)
            self.__controller.execute_bet(next_race_card, bet)

    def __get_race_card_with_latest_odds(self, race_card: RaceCard) -> RaceCard:
        race_card_latest_odds = self.__race_card_factory.get_race_card(race_card.race_id)
        for horse in race_card.horses:
            if race_card_latest_odds.is_horse_scratched(horse):
                race_card.remove_horse(horse)
            else:
                new_odds = race_card_latest_odds.get_current_odds_of_horse(horse)
                race_card.set_odds_of_horse(horse, new_odds)

        return race_card

    def __compute_bet(self, race_card: RaceCard) -> Bet:
        raw_samples = self.__encoder.transform([race_card])

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        return bet


def main():
    bettor = BettingAgent(kelly_wealth=10)
    bettor.run()


if __name__ == '__main__':
    main()
