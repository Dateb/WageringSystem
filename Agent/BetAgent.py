from datetime import datetime
from typing import List, Dict

from Agent.AgentController import AgentController
from Agent.AgentModel import AgentModel
from DataCollection.DayCollector import DayCollector
from DataAbstraction.RaceCardFactory import RaceCardFactory
from DataCollection.RaceCardsCollector import RaceCardsCollector
from DataAbstraction.Present.RaceCard import RaceCard
from Persistence.RaceCardPersistence import RaceCardsPersistence

CONTROLLER_SUBMISSION_MODE_ON = False


class BetAgent:

    def __init__(self):
        self.controller = AgentController(bet_limit=20, submission_mode_on=CONTROLLER_SUBMISSION_MODE_ON)
        self.model = AgentModel()

        self.today_race_cards: List[RaceCard] = []
        self.today_race_cards_factory = RaceCardFactory(collect_results=False)
        self.day_collector = DayCollector()
        self.race_cards_collector = RaceCardsCollector()

        today = datetime.today().date()
        race_ids_today = self.day_collector.get_open_race_ids_of_day(today)
        print("Initialising races:")
        self.__init_races(race_ids_today)

    def __init_races(self, race_ids: List[str]):
        base_race_cards = self.race_cards_collector.collect_base_race_cards_from_race_ids(race_ids)

        base_race_cards.sort(key=lambda x: x.datetime)

        # The persistence is used because of the conversion inside. This needs to be fixed quickly.
        # race_cards_persistence = RaceCardsPersistence(f"production_cache_{race_ids[0]}")
        #
        # race_cards_persistence.save(base_race_cards)
        # race_card_files = [race_cards_persistence.race_card_file_names[0]]
        self.today_race_cards = base_race_cards

    def run(self):
        for race_card in self.today_race_cards:
            full_race_card = self.today_race_cards_factory.run(race_card.race_id)

            self.controller.open_race_card(full_race_card)
            #self.__controller.wait_for_race_start(next_race_card)
            self.controller.prepare_for_race_start()

            updated_race_card = self.__update_current_race_card(full_race_card)

            betting_slip = self.model.bet_on_race_card(updated_race_card)
            print(betting_slip)
            if betting_slip.bets:
                self.controller.submit_betting_slip(betting_slip)
            else:
                print("No value found. Skipping race.")

    def __update_current_race_card(self, race_card: RaceCard) -> RaceCard:
        updated_race_card = self.today_race_cards_factory.get_race_card(race_card.race_id)
        # TODO: implement this update less naively
        for horse in race_card.horses:
            horse_with_updated_odds = [updated_horse for updated_horse in updated_race_card.horses if updated_horse.horse_id == horse.horse_id][0]
            horse.current_win_odds = horse_with_updated_odds.current_win_odds
            if horse_with_updated_odds.is_scratched:
                race_card.horses.remove(horse)

        return race_card


def main():
    bettor = BetAgent()
    bettor.run()


if __name__ == '__main__':
    main()
    print("finished")
