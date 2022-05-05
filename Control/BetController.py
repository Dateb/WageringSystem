from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from Betting.Bet import Bet
from SampleExtraction.RaceCard import RaceCard


class BetController:

    def __init__(self, user_name: str, password: str, post_race_start_wait: int = 15, submission_mode_on: bool = False):
        self.__driver = webdriver.Firefox()
        self.__user_name = user_name
        self.__password = password
        self.__post_race_start_wait = post_race_start_wait
        self.__submission_mode_on = submission_mode_on

        self.__driver.get("https://www.racebets.de")
        sleep(2)
        self.accept_cookies()
        self.__driver.implicitly_wait(5)

    def login(self):
        login_name_field = self.__driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputUsername")
        login_password_field = self.__driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputPassword")
        login_button = self.__driver.find_element(by=By.ID, value="m-accWidget--rightBar__btnLogin")
        login_name_field.send_keys(self.__user_name)
        login_password_field.send_keys(self.__password)
        login_button.click()
        sleep(2)

    def open_race_card(self, race_card: RaceCard):
        self.__driver.get(f"https://www.racebets.de/de/pferdewetten/race/details/id/{race_card.race_id}/")

    def wait_for_race_start(self, race_card: RaceCard):
        time_until_race_start = race_card.datetime - datetime.now()
        print(f"Now waiting for race: ---{race_card.name}--- for {time_until_race_start}")
        sleep(1)

        if self.is_logged_out():
            self.login()

        print(f"Race starting every moment, delaying bet for {self.__post_race_start_wait} seconds...")
        sleep(self.__post_race_start_wait)

    def execute_bet(self, race_card: RaceCard, bet: Bet):
        if bet.stakes < 0.5:
            print("No value found here. Skipping to next race.")
            return 0

        self.__driver.implicitly_wait(5)
        win_button = self.__driver.find_element(by=By.XPATH, value=f'//a[@data-id-runner={bet.runner_ids[0]}]')
        win_button.click()

        stakes_change_button = self.__driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Betrag ändern')]")
        stakes_change_button.click()

        stakes_input_field = self.__driver.find_element(by=By.XPATH, value=f'//input[@value="0,50 EUR"]')
        stakes_input_field.send_keys(str(bet.stakes))
        stakes_input_field.send_keys(Keys.RETURN)

        if self.__submission_mode_on:
            submit_bet_button = self.__driver.find_element(by=By.XPATH, value=f'//button[@type="submit"]')
            submit_bet_button.click()

            finish_button = self.__driver.find_element(by=By.XPATH, value=f'//button[@class="btn btn-primary"]')
            finish_button.click()

        sleep(1)

        bet_horse_id = bet.runner_ids[0]
        print("Successfully done this bet.")
        print("----------------------------")
        print(f"Horse name: {race_card.get_name_of_horse(bet_horse_id)}")
        print(f"Odds: {race_card.get_current_odds_of_horse(bet_horse_id)}")
        print(f"Stakes: {bet.stakes}")
        print("----------------------------")

    def accept_cookies(self):
        cookies_accept_button = self.__driver.find_element(by=By.XPATH, value=f'//button[@id="onetrust-accept-btn-handler"]')
        cookies_accept_button.click()

    def is_logged_out(self) -> bool:
        self.__driver.refresh()
        return len(self.__driver.find_elements(by=By.ID, value="m-accWidget--rightBar__inputUsername")) > 0



