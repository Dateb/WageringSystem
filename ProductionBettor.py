import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from Betting.Bet import Bet
from Betting.WinBettor import WinBettor
from DataCollection.RawRaceCardsCollector import RawRaceCardsCollector
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from SampleExtraction.FeatureManager import FeatureManager
from DataCollection.PastRacesContainer import PastRacesContainer
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder


class ProductionBettor:

    __ESTIMATOR_PATH = "data/estimator_v1-02.dat"
    __estimator: BoostedTreesRanker

    def __init__(self, kelly_wealth: float = 20.0):
        self.__bettor = WinBettor(kelly_wealth)

        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

    def run(self):
        race_id = "5008740"
        bet = self.__compute_bet(race_id)
        self.__execute_bet(race_id, bet)

    def __compute_bet(self, race_id: str) -> Bet:
        collector = RawRaceCardsCollector(initial_raw_race_cards=[], initial_past_races_container=PastRacesContainer({}))
        collector.collect_from_race_ids([race_id])
        race_card = RaceCard(collector.raw_race_cards[0])

        past_races_container = PastRacesContainer(collector.raw_past_races)
        raw_samples = self.__encoder.transform([race_card], past_races_container)

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        winner_name = race_card.get_name_of_horse(bet.runner_ids[0])
        print(f"Betting on --{winner_name}-- this amount: {bet.stakes}")
        return bet

    def __execute_bet(self, race_id: str, bet: Bet):
        driver = webdriver.Firefox()
        driver.get(f"https://www.racebets.de/de/pferdewetten/race/details/id/{race_id}/")
        driver.implicitly_wait(5)
        login_name_field = driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputUsername")
        login_password_field = driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputPassword")
        login_button = driver.find_element(by=By.ID, value="m-accWidget--rightBar__btnLogin")
        login_name_field.send_keys("Malfen")
        login_password_field.send_keys("Titctsat49_")
        login_button.click()

        sleep(5)

        win_button = driver.find_element(by=By.XPATH, value=f'//a[@data-id-runner={bet.runner_ids[0]}]')
        win_button.click()

        stakes_change_button = driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Betrag ändern')]")
        stakes_change_button.click()

        stakes_input_field = driver.find_element(by=By.XPATH, value=f'//input[@value="0,50 EUR"]')
        stakes_input_field.send_keys(str(bet.stakes))
        stakes_input_field.send_keys(Keys.RETURN)


def main():
    bettor = ProductionBettor()
    bettor.run()
    #production_bettor = ProductionBettor()
    #name, stakes = production_bettor.bet("5003320")
    #print(f"Bet on horse: {name} this amount: {stakes}")


if __name__ == '__main__':
    main()
