import datetime
import json
import time
from typing import List

from Agent.AgentModel import AgentModel
from Betting.Bets.Bet import Bet
from Betting.Bettor import Bettor
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.current_races.fetch import TomorrowRaceCardsFetcher, TodayRaceCardsFetcher
from DataCollection.current_races.inject import CurrentRaceCardsInjector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Estimators.EstimationResult import EstimationResult
from Persistence.RaceCardPersistence import RaceCardsPersistence

VALUE_MONITOR_DATA_PATH = "/home/daniel/PycharmProjects/horsacle/src/data/race_ev.json"


class MonitorData:

    def __init__(self, estimation_result: EstimationResult, bettor: Bettor):
        self.estimation_result = estimation_result
        self.bettor = bettor

    @property
    def json(self) -> dict:
        estimation_json = {
            "race": {
                "id": self.estimation_result.race_ids[0],
                "name": self.estimation_result.horse_results[0].race_name,
                "date_time": self.estimation_result.horse_results[0].race_date_time,
                "time_until_start": str(datetime.datetime.strptime(self.estimation_result.horse_results[0].race_date_time, '%Y-%m-%d %H:%M:%S') - datetime.datetime.now())
            },
            "horses": [
                {
                    "id": horse_result.number,
                    "name": horse_result.name,
                    "place_probability": horse_result.place_probability,
                    "min_odds_place": (1 + self.bettor.additional_ev_threshold) / (horse_result.place_probability * (1 - Bet.WIN_COMMISION)),
                    "racebets_odds": horse_result.place_odds,
                    "racebets_stakes": (horse_result.place_odds * horse_result.win_probability - 1) / (horse_result.place_odds - 1)
                 }
                for horse_result in sorted(self.estimation_result.horse_results, key=lambda x: x.win_probability, reverse=True)
            ]
        }

        return estimation_json


class ValueMonitor:

    def __init__(self):
        self.collect_race_cards_until_today()
        self.model = AgentModel()
        self.race_cards: List[RaceCard] = TodayRaceCardsFetcher().fetch_race_cards()
        self.race_cards_injector = CurrentRaceCardsInjector()

    def run(self):
        while self.race_cards:
            next_race_card = self.race_cards[0]
            full_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(next_race_card.race_id)

            self.poll_race_card(full_race_card)
            self.race_cards.remove(next_race_card)

    def poll_race_card(self, race_card):
        while race_card.is_open:
            updated_race_card = self.race_cards_injector.inject_newest_odds_into_horses(race_card)
            self.write_race_card(updated_race_card)
            time.sleep(2)

    def write_race_card(self, race_card: RaceCard):
        estimation_result = self.model.estimate_race_card(race_card)
        monitor_data = MonitorData(estimation_result, self.model.bet_model.bettor)
        with open(VALUE_MONITOR_DATA_PATH, 'w') as fp:
            json.dump(monitor_data.json, fp)

        print(f"{datetime.datetime.now()}: changed monitor data")

    def collect_race_cards_until_today(self):
        train_data_collector = TrainDataCollector(file_name="race_cards")
        query_date = datetime.date(year=2022, month=12, day=1)

        newest_date = datetime.date.today()
        train_data_collector.collect_forward_until_newest_date(query_date=query_date, newest_date=newest_date)


def main():
    ValueMonitor().run()


if __name__ == '__main__':
    main()
    print("finished")
