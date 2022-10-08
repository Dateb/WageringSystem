import os
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Betting.Bets.WinBet import WinBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard


class AgentController:

    def __init__(self, post_race_start_wait: int = 5, submission_mode_on: bool = False):
        self.driver = webdriver.Firefox()
        self.user_name = "Malfen"
        self.password = "Titctsat49_"
        self.__post_race_start_wait = post_race_start_wait
        self.__submission_mode_on = submission_mode_on

        self.driver.get("https://m.racebets.de/")
        sleep(4)
        self.accept_cookies()
        self.driver.implicitly_wait(5)

    def login(self):
        login_name_field = self.driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputUsername")
        login_password_field = self.driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputPassword")
        login_button = self.driver.find_element(by=By.ID, value="m-accWidget--rightBar__btnLogin")
        login_name_field.send_keys(self.user_name)
        login_password_field.send_keys(self.password)
        login_button.click()
        sleep(2)

    def open_race_card(self, race_card: RaceCard):
        self.driver.get(f"https://www.racebets.de/de/pferdewetten/race/details/id/{race_card.race_id}/")
        sleep(3)

    def wait_for_race_start(self, race_card: RaceCard):
        time_until_race_start = race_card.datetime - datetime.now()
        print(f"Now waiting for race: ---{race_card.name}--- which starts at: {race_card.datetime}")
        if race_card.datetime > datetime.now():
            sleep(max(0, time_until_race_start.seconds))

    def prepare_for_race_start(self):
        if self.is_logged_out():
            self.login()

        print(f"Race starting every moment, delaying bet for {self.__post_race_start_wait} seconds...")
        sleep(self.__post_race_start_wait)

    def execute_betting_slip(self, race_card: RaceCard, betting_slip: BettingSlip):
        bet_list = list(betting_slip.bets.values())
        bet = bet_list[0]

        print(bet.odds)
        print(bet.horse_ids)

        win_button = self.driver.find_element(by=By.XPATH, value=f'//a[@data-id-runner=\"{bet.horse_ids}\" and @data-bet-type=\"WIN\"]')
        win_button.click()

        if self.__is_bet_closed():
            print("Bet is already closed. Skipping to next race.")
            return 0

        stakes_change_button = self.driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Betrag ändern')]")
        stakes_change_button.click()

        stakes_input_field = self.driver.find_element(by=By.XPATH, value=f'//input[@value="0,50 EUR"]')
        stakes_input_field.send_keys(str(bet.stakes))
        stakes_input_field.send_keys(Keys.RETURN)

        if self.__submission_mode_on:
            submit_bet_button = self.driver.find_element(by=By.XPATH, value=f'//button[@type="submit"]')
            submit_bet_button.click()

            finish_button = self.driver.find_element(by=By.XPATH, value=f'//button[@class="btn btn-primary"]')
            finish_button.click()

        sleep(1)

        # TODO: Fix this part
        # print(f"bet horse id: {bet.horse_id}")
        # bet_horse = race_card.get_horse_with_id(bet.horse_id)
        print("Successfully done this bet.")
        # print("----------------------------")
        # print(f"Horse name: {bet_horse.name}")
        # print(f"Odds: {bet_horse.current_odds}")
        # print(f"Stakes: {bet.stakes}")
        # print("----------------------------")

    def accept_cookies(self):
        cookies_accept_button = self.driver.find_element(by=By.XPATH, value=f'//button[@id="onetrust-accept-btn-handler"]')
        cookies_accept_button.click()

    def is_logged_out(self) -> bool:
        self.driver.refresh()
        return len(self.driver.find_elements(by=By.ID, value="m-accWidget--rightBar__inputUsername")) > 0

    def __is_bet_closed(self) -> bool:
        stakes_change_buttons = self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'Betrag ändern')]")

        return len(stakes_change_buttons) == 0

    def submit_betting_slip(self, betting_slip: BettingSlip):
        race_url = f"https://m.racebets.de/race/details/id/{betting_slip.race_id}"
        print(race_url)
        self.driver.get(race_url)
        self.click_on_horses_in_betting_slip(betting_slip)
        self.driver.close()

    def click_on_horses_in_betting_slip(self, betting_slip: BettingSlip):
        # for bet in betting_slip.bets:
        #     for horse_result in bet.predicted_horse_results:
        self.click_on_horse_fixed_odds_button(2)
        self.click_on_append_to_betting_slip_button()

        self.click_on_horse_fixed_odds_button(4)

        sleep(10)

    def click_on_horse_fixed_odds_button(self, program_number: int):
        horse_fixed_odds_button = self.driver.find_elements(by=By.XPATH, value="//div[@data-button-1='']")[program_number - 1]
        horse_fixed_odds_button.click()

    def click_on_append_to_betting_slip_button(self):
        append_to_betting_slip_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Betslip')]")))
        append_to_betting_slip_button.click()


def main():
    first_predicted_horse_result = HorseResult(
        horse_id="49061326",
        position=1,
        win_odds=3.75,
        place_odds=0.0,
    )
    first_bet = WinBet(
        predicted_horse_results=[first_predicted_horse_result],
        stakes_fraction=0.05,
        success_probability=0.0,
    )

    dummy_betting_slip = BettingSlip(race_id="5419583")
    dummy_betting_slip.add_bet(first_bet)

    agent_controller = AgentController()
    agent_controller.submit_betting_slip(betting_slip=dummy_betting_slip)


if __name__ == '__main__':
    main()
    print("finished")

