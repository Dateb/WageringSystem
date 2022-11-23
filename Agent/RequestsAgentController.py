import os
import re
from datetime import datetime
from time import sleep

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Betting.Bets.WinBet import WinBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper


class RequestsAgentController:

    def __init__(self, bet_limit: float, post_race_start_wait: int = 1, submission_mode_on: bool = False):
        self.user_name = "Malfen"
        self.password = "Titctsat49_"
        self.bet_limit = bet_limit
        self.post_race_start_wait = post_race_start_wait
        self.submission_mode_on = submission_mode_on
        self.scraper = get_scraper()

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
        html_response = self.scraper.request_html("https://www.racebets.de/de/pferdewetten/")

        game_server_profile_text = re.findall("bts041121.profile(.*)", html_response)[0].split("'")
        game_server_param_1 = game_server_profile_text[3]
        game_server_param_2 = game_server_profile_text[5]
        game_server_get_url = f"https://fpcn.bpsgameserver.com/428nmqd7j7n7op8h.js?uial7j8gob55ozwl={game_server_param_1}&ypu9e9gi3twc9mvz={game_server_param_2}"
        self.scraper.request_html(url="https://www.racebets.de/scripts/lib/tm/tm.js")

        #"bts041121.profile('fpcn.bpsgameserver.com', 'z1adydba', '9adb6aa3f6be62c63086a60a309204539b8ab980')"

        login_url = "https://www.racebets.de/rest/v1/users/me/login"
        login_data = {
            "password": self.password,
            "tmSessionId": game_server_param_2,
            "username": self.user_name,
        }
        login_response = self.scraper.post_payload(login_url, login_data)
        print(login_response.text)

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
        win_odds=2.0,
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
        win_odds=22.0,
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

    agent_controller = RequestsAgentController(bet_limit=100, submission_mode_on=False)
    agent_controller.submit_betting_slip(betting_slip=dummy_betting_slip)


if __name__ == '__main__':
    main()
    print("finished")

