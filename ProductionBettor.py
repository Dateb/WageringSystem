import pickle
from datetime import datetime
from time import sleep, time
from typing import List

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from Betting.Bet import Bet
from Betting.WinBettor import WinBettor
from DataCollection.DayCollector import DayCollector
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from DataCollection.RawRaceCardsCollector import RawRaceCardsCollector
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from SampleExtraction.FeatureManager import FeatureManager
from DataCollection.PastRacesContainer import PastRacesContainer
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder


class ProductionBettor:

    __ESTIMATOR_PATH = "data/estimator_v1-02.dat"
    __estimator: BoostedTreesRanker

    def __init__(self, kelly_wealth: float = 10.0):
        self.__race_cards: List[RaceCard] = []
        self.__raw_race_card_factory = RawRaceCardFactory()
        self.__day_collector = DayCollector()
        self.__collector = RawRaceCardsCollector(initial_raw_race_cards=[], initial_past_races_container=PastRacesContainer({}))
        self.__bettor = WinBettor(kelly_wealth)

        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

        today = datetime.today().date()
        race_ids_today = self.__day_collector.get_race_ids_of_day(today)
        self.__init_races(race_ids_today)
        self.__driver = webdriver.Firefox()

    def run(self):
        self.__login()

        next_race_card = self.__race_cards.pop(0)
        while True:
            sleep(1)
            time_until_race_start = next_race_card.datetime - datetime.now()
            print(f"Seconds until next race: {time_until_race_start.seconds}")
            if time_until_race_start.seconds < 10:
                next_race_card = self.__get_updated_race_card(next_race_card)
                bet = self.__compute_bet(next_race_card)
                self.__execute_bet(next_race_card.race_id, bet)

                if not self.__race_cards:
                    return 0

                next_race_card = self.__race_cards.pop(0)

    def __init_races(self, race_ids: List[str]):
        raw_race_cards = self.__collector.collect_from_race_ids(race_ids)
        self.__race_cards = [RaceCard(raw_race_card) for raw_race_card in raw_race_cards]

        self.__race_cards.sort(key=lambda x: x.datetime)
        self.__past_races_container = PastRacesContainer(self.__collector.raw_past_races)

    def __get_updated_race_card(self, race_card: RaceCard):
        race_id = race_card.race_id
        raw_race_card = self.__raw_race_card_factory.run(race_id)
        return RaceCard(raw_race_card)

    def __compute_bet(self, race_card: RaceCard) -> Bet:
        raw_samples = self.__encoder.transform([race_card], self.__past_races_container)

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        #winner_name = race_card.get_name_of_horse(bet.runner_ids[0])
        #print(f"Betting on --{winner_name}-- this amount: {bet.stakes}")
        return bet

    def __login(self):
        race_id = self.__race_cards[0].race_id
        self.__driver.get(f"https://www.racebets.de/de/pferdewetten/race/details/id/{race_id}/")
        self.__driver.implicitly_wait(5)
        login_name_field = self.__driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputUsername")
        login_password_field = self.__driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputPassword")
        login_button = self.__driver.find_element(by=By.ID, value="m-accWidget--rightBar__btnLogin")
        login_name_field.send_keys("Malfen")
        login_password_field.send_keys("Titctsat49_")
        login_button.click()
        sleep(10)

    def __execute_bet(self, race_id: str, bet: Bet):
        if bet.stakes < 0.5:
            return 0

        self.__driver.get(f"https://www.racebets.de/de/pferdewetten/race/details/id/{race_id}/")
        self.__driver.implicitly_wait(5)
        win_button = self.__driver.find_element(by=By.XPATH, value=f'//a[@data-id-runner={bet.runner_ids[0]}]')
        win_button.click()

        stakes_change_button = self.__driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Betrag ändern')]")
        stakes_change_button.click()

        stakes_input_field = self.__driver.find_element(by=By.XPATH, value=f'//input[@value="0,50 EUR"]')
        stakes_input_field.send_keys(str(bet.stakes))
        stakes_input_field.send_keys(Keys.RETURN)

        bet_submit_button = self.__driver.find_element(by=By.XPATH, value=f'//button[@type="submit"]')
        bet_submit_button.click()

        finish_button = self.__driver.find_element(by=By.XPATH, value=f'//button[@class="btn btn-primary"]')
        finish_button.click()

def main():
    bettor = ProductionBettor()
    bettor.run()
    #production_bettor = ProductionBettor()
    #name, stakes = production_bettor.bet("5003320")
    #print(f"Bet on horse: {name} this amount: {stakes}")


if __name__ == '__main__':
    main()
