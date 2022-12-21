import json
import time

from Agent.AgentModel import AgentModel
from DataAbstraction.Present.RaceCard import RaceCard
from Persistence.RaceCardPersistence import RaceCardsPersistence

VALUE_MONITOR_DATA_PATH = "/home/daniel/PycharmProjects/horsacle/src/data/horse_data.json"


class ValueMonitor:

    def __init__(self):
        self.model = AgentModel()

    def write_race_card(self, race_card: RaceCard):
        estimation_result = self.model.estimate_race_card(race_card)
        monitor_data = estimation_result.json
        with open(VALUE_MONITOR_DATA_PATH, 'w') as fp:
            json.dump(monitor_data, fp)

        print("changed monitor data")
        time.sleep(5)


def main():
    race_cards_loader = RaceCardsPersistence("race_cards")
    race_cards = list(race_cards_loader.load_first_month_non_writable().values())

    monitor = ValueMonitor()
    for race_card in race_cards:
        monitor.write_race_card(race_card)


if __name__ == '__main__':
    main()
    print("finished")
