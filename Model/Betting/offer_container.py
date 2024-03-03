import os
import pickle
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import BetOffer, LiveResult
from Model.Betting.exchange_offers_parsing import RaceDateToCardMapper, BetfairHistoryDictIterator
from ModelTuning import simulate_conf


class BetOfferContainer(ABC):

    def __init__(self):
        self.race_offers = {}
        self.race_offers_path = ""

    @abstractmethod
    def insert_race_cards(self, race_cards: Dict[str, RaceCard]):
        pass

    def get_offers_from_race(self, race_key: str) -> List[BetOffer]:
        if race_key in self.race_offers:
            return self.race_offers[race_key]
        return []

    def save_race_offers(self) -> None:
        with open(self.race_offers_path, "wb") as f:
            pickle.dump(self.race_offers, f)

    def load_race_offers(self):
        with open(self.race_offers_path, "rb") as f:
            self.race_offers = pickle.load(f)


class RaceBetsOfferContainer(BetOfferContainer):

    def __init__(self):
        super().__init__()
        self.race_offers_path = "../data/racebets_race_offers.dat"

    def insert_race_cards(self, race_cards: Dict[str, RaceCard]):
        for race_card in race_cards.values():
            scratched_horses = [horse.name for horse in race_card.horses if horse.is_scratched]
            race_bet_offers = []
            for horse in race_card.horses:
                for racebets_win_odds in horse.racebets_win_odds_history[0:2]:
                    bet_offer = BetOffer(
                        race_card=race_card,
                        horse=horse,
                        odds=racebets_win_odds,
                        scratched_horse_numbers=scratched_horses,
                        event_datetime=race_card.datetime - timedelta(hours=1),
                        adjustment_factor=1.0
                    )
                    race_bet_offers.append(bet_offer)

            self.race_offers[str(race_card.datetime)] = race_bet_offers


class BetfairOfferContainer(BetOfferContainer):

    def __init__(self):
        super().__init__()
        if simulate_conf.MARKET_TYPE == "WIN":
            self.race_offers_path = "../data/betfair_race_win_offers.dat"
        else:
            self.race_offers_path = "../data/betfair_race_place_offers.dat"

    def insert_race_cards(self, race_cards: Dict[str, RaceCard]):
        self.test_race_cards_mapper = RaceDateToCardMapper(race_cards)

        history_path = "../data/exchange_odds_history/"

        year_dirs = os.listdir(history_path)
        for year_dir in year_dirs:
            month_dirs = os.listdir(f"{history_path}/{year_dir}")
            for month_dir in month_dirs:
                day_dirs = os.listdir(f"{history_path}/{year_dir}/{month_dir}")
                for day_dir in day_dirs:
                    race_series_dirs = os.listdir(f"{history_path}/{year_dir}/{month_dir}/{day_dir}")
                    for race_series_dir in race_series_dirs:
                        history_files = os.listdir(f"{history_path}/{year_dir}/{month_dir}/{day_dir}/{race_series_dir}")

                        for file_name in history_files:
                            if file_name.startswith("1"):
                                self.load_offers_from_race(f"{history_path}/{year_dir}/{month_dir}/{day_dir}/{race_series_dir}/{file_name}")

    def load_offers_from_race(self, race_history_file_path: str):
        betfair_offers = []

        history_dict_iterator = BetfairHistoryDictIterator(race_history_file_path)

        initial_history_dict = next(history_dict_iterator)

        if initial_history_dict is None:
            print(f"failed to decode file: {race_history_file_path}")
            return

        market_definition = initial_history_dict["mc"][0]["marketDefinition"]
        scratched_horse_numbers = []

        race_datetime = self.create_datetime_from_market_time(market_definition["suspendTime"])
        race_card = self.test_race_cards_mapper.get_race_card(str(race_datetime))

        if race_card is not None:
            if market_definition["marketType"] == simulate_conf.MARKET_TYPE and market_definition["countryCode"] == "GB":
                horses = market_definition["runners"]
                n_winners = market_definition["numberOfWinners"]
                n_horses = len(horses)
                id_to_horse_map = {runner["id"]: race_card.get_horse_by_horse_name(runner["name"]) for runner in horses}

                if n_winners == race_card.places_num or simulate_conf.MARKET_TYPE != "PLACE":
                    for history_dict in history_dict_iterator:
                        unix_time_stamp = int(history_dict["pt"] / 1000)
                        event_datetime = datetime.fromtimestamp(unix_time_stamp)
                        market_condition = history_dict["mc"][0]

                        if "marketDefinition" in market_condition:
                            market_definition = history_dict["mc"][0]["marketDefinition"]
                            if "runners" in market_definition:
                                scratched_horses = self.get_scratched_horses(race_card, market_definition["runners"])
                                scratched_horse_numbers = [horse.number for horse in scratched_horses]
                                n_horses = len(market_definition["runners"]) - len(scratched_horse_numbers)

                        if "rc" in market_condition:
                            if event_datetime < race_card.off_time:
                                new_offers = []
                                for offer_data in market_condition["rc"]:
                                    horse = id_to_horse_map[offer_data["id"]]
                                    if horse is None:
                                        print(f"Could not find horse: {offer_data['id']} on race: {race_card.race_id}")
                                        print(f"race datetime: {race_datetime}")
                                        print("-----------------------------------------")
                                    else:
                                        live_result = LiveResult(
                                            offer_odds=offer_data["ltp"],
                                            starting_odds=horse.betfair_win_sp,
                                            has_won=horse.has_won,
                                            adjustment_factor=1.0,
                                        )

                                        bef_offer = BetOffer(
                                            race_card=race_card,
                                            horse=horse,
                                            live_result=live_result,
                                            scratched_horse_numbers=scratched_horse_numbers,
                                            event_datetime=event_datetime,
                                            n_horses=n_horses,
                                            n_winners=n_winners
                                        )
                                        new_offers.append(bef_offer)

                                betfair_offers += new_offers

                    adjustment_factor_lookup = {}
                    final_runners = market_definition["runners"]

                    for runner in final_runners:
                        if runner["status"] == "REMOVED":
                            adjustment_factor = 0.0
                            if "adjustmentFactor" in runner:
                                adjustment_factor = runner["adjustmentFactor"]
                            if adjustment_factor >= 2.5 or simulate_conf.MARKET_TYPE == "PLACE":
                                removal_datetime = datetime.strptime(runner["removalDate"][:-5], "%Y-%m-%dT%H:%M:%S")
                                adjustment_factor_lookup[runner["name"]] = {"factor": adjustment_factor, "date": removal_datetime}

                    for offer in betfair_offers:
                        for removed_runner in adjustment_factor_lookup.values():
                            if offer.event_datetime < removed_runner["date"]:
                                offer.live_result.adjustment_factor *= (1 - removed_runner["factor"] / 100)

                    self.race_offers[str(race_card.datetime)] = betfair_offers

    def get_scratched_horses(self, race_card: RaceCard, horses: dict) -> List[Horse]:
        scratched_horses = []
        for horse in horses:
            if horse["status"] == "REMOVED":
                horse_name = horse["name"]
                horse = race_card.get_horse_by_horse_name(horse_name)
                if horse is not None:
                    scratched_horses.append(horse)

        return scratched_horses

    def create_datetime_from_market_time(self, market_time: str) -> datetime:
        datetime_substrings = market_time.split('T')
        date_str = datetime_substrings[0]
        time_str = datetime_substrings[1][0:5] + ":00"

        datetime_str = f"{date_str} {time_str}"

        market_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        if self.is_winter_time(market_datetime):
            return market_datetime + timedelta(hours=1)
        else:
            return market_datetime + timedelta(hours=2)

    def is_winter_time(self, datetime) -> bool:
        return (datetime.date().month == 3 and datetime.date().day <= 25
                or datetime.date().month == 10 and datetime.date().day >= 29
                or datetime.date().month <= 2
                or datetime.date().month >= 11)
