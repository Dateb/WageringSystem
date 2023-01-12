import os
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from Betting.Bets.WinBet import WinBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard


class SeleniumAgentController:

    def __init__(self, post_race_start_wait: int = 1, submission_mode_on: bool = False):
        self.driver = None
        self.open_connection()
        self.user_name = "Malfen"
        self.password = "Titctsat49_"
        self.bet_limit = 0
        self.post_race_start_wait = post_race_start_wait
        self.submission_mode_on = submission_mode_on

    def open_connection(self):
        options = Options()
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        self.driver.get("https://m.racebets.de")

    def restart_driver(self):
        self.driver.close()
        self.open_connection()
        self.accept_cookies()
        self.driver.implicitly_wait(5)

    def login(self):
        login_name_field = self.driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputUsername")
        login_password_field = self.driver.find_element(by=By.ID, value="m-accWidget--rightBar__inputPassword")
        login_button = self.driver.find_element(by=By.ID, value="m-accWidget--rightBar__btnLogin")
        login_name_field.send_keys(self.user_name)
        login_password_field.send_keys(self.password)
        login_button.click()

    def open_race_card(self, race_card: RaceCard):
        self.driver.get(f"https://m.racebets.de/race/details/id/{race_card.race_id}/")
        self.driver.implicitly_wait(10)

    def wait_for_race_start(self, race_card: RaceCard):
        time_until_race_start = race_card.datetime - datetime.now()
        print(f"Now waiting for race: ---{race_card.name}--- which starts at: {race_card.datetime}")
        if race_card.datetime > datetime.now():
            sleep(max(0, time_until_race_start.seconds))

    def prepare_for_race_start(self):
        self.relogin()

        print(f"Race starting every moment, delaying bet for {self.post_race_start_wait} seconds...")
        sleep(self.post_race_start_wait)

    def accept_cookies(self):
        cookies_accept_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')))
        cookies_accept_button.click()

    def relogin(self) -> bool:
        self.driver.refresh()
        right_sidemenu_icon = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//i[@data-right-sidemenu-icon='']")))
        is_logged_out = "key" in right_sidemenu_icon.get_attribute("class")
        if is_logged_out:
            right_sidemenu_icon.click()

            username_input_field = self.driver.find_element(by=By.XPATH, value="//input[@data-username='']")
            password_input_field = self.driver.find_element(by=By.XPATH, value="//input[@data-password='']")

            username_input_field.send_keys(self.user_name)
            password_input_field.send_keys(self.password)

            submit_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@id='submit']")))
            submit_button.click()

        return is_logged_out

    def submit_betting_slip(self, betting_slip: BettingSlip):
        self.click_on_horses_in_betting_slip(betting_slip)
        self.click_on_betting_slip_icon()
        self.enter_bet_stakes(betting_slip)
        if self.submission_mode_on:
            self.click_on_submit_button()

    def click_on_horses_in_betting_slip(self, betting_slip: BettingSlip):
        created_betting_slip = False
        for bet in betting_slip.bets:
            for horse_result in bet.predicted_horse_results:
                self.click_on_horse_fixed_odds_button(horse_result.number)
                if not created_betting_slip:
                    self.click_on_append_to_betting_slip_button()
                    created_betting_slip = True

    def click_on_horse_fixed_odds_button(self, program_number: int):
        horse_fixed_odds_button = self.driver.find_elements(by=By.XPATH, value="//div[@data-button-1='']")[program_number - 1]
        horse_fixed_odds_button.click()

    def click_on_append_to_betting_slip_button(self):
        append_to_betting_slip_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Zum Wettschein an')]")))
        append_to_betting_slip_button.click()

    def click_on_betting_slip_icon(self):
        betting_slip_icon = self.driver.find_element(by=By.XPATH, value="//div[@data-betslip='']")
        betting_slip_icon.click()

    def enter_bet_stakes(self, betting_slip: BettingSlip):
        for bet_idx, bet in enumerate(betting_slip.bets):
            self.enter_stakes(input_idx=bet_idx, stakes=round(bet.stakes_fraction * self.bet_limit))

    def enter_stakes(self, input_idx: int, stakes: float):
        WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//input[@data-unit='']")))[input_idx].send_keys(stakes)

    def click_on_submit_button(self):
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@data-place-bet='']")
        submit_button.click()

    def read_wealth(self) -> float:
        wealth_element = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-user-balance='']")))
        current_wealth = float(wealth_element.text.split(sep=" ")[0].replace(",", "."))
        self.bet_limit = current_wealth * 0.7
        return current_wealth


def main():
    first_predicted_horse_result = HorseResult(
        number=3,
        position=1,
        betting_odds=2.0,
        place_odds=0.0,
    )
    first_bet = WinBet(
        predicted_horse_results=[first_predicted_horse_result],
        stakes_fraction=0.08,
        success_probability=0.48,
    )

    second_predicted_horse_result = HorseResult(
        number=1,
        position=1,
        betting_odds=22.0,
        place_odds=0.0,
    )
    second_bet = WinBet(
        predicted_horse_results=[second_predicted_horse_result],
        stakes_fraction=0.05,
        success_probability=0.12,
    )

    dummy_betting_slip = BettingSlip(race_id="5515596")
    dummy_betting_slip.add_bet(first_bet)
    dummy_betting_slip.add_bet(second_bet)

    print(dummy_betting_slip)

    agent_controller = SeleniumAgentController(submission_mode_on=False)
    agent_controller.relogin()
    agent_controller.submit_betting_slip(betting_slip=dummy_betting_slip)


if __name__ == '__main__':
    main()
    print("finished")

