import json
import time

from Agent.AgentModel import AgentModel
from Betting.Bettor import Bettor
from DataAbstraction.Present.RaceCard import RaceCard
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
            },
            "horses": [
                {
                    "id": horse_result.number,
                    "name": horse_result.name,
                    "win_probability": horse_result.win_probability,
                    "min_odds": (1 + self.bettor.additional_ev_threshold) / horse_result.win_probability,
                    "racebets_odds": horse_result.win_odds,
                 }
                for horse_result in self.estimation_result.horse_results
            ]
        }

        return estimation_json


class ValueMonitor:

    def __init__(self):
        self.model = AgentModel()

    def write_race_card(self, race_card: RaceCard):
        estimation_result = self.model.estimate_race_card(race_card)
        monitor_data = MonitorData(estimation_result, self.model.bet_model.bettor)
        with open(VALUE_MONITOR_DATA_PATH, 'w') as fp:
            json.dump(monitor_data.json, fp)

        print("changed monitor data")
        time.sleep(15)


def main():
    race_cards_loader = RaceCardsPersistence("race_cards")
    race_cards = list(race_cards_loader.load_first_month_non_writable().values())

    monitor = ValueMonitor()
    for race_card in race_cards:
        monitor.write_race_card(race_card)


if __name__ == '__main__':
    main()
    print("finished")
