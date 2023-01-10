import datetime
from typing import List

from Agent.AgentModel import AgentModel
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.current_races.fetch import TomorrowRaceCardsFetcher, TodayRaceCardsFetcher
from DataCollection.current_races.inject import CurrentRaceCardsInjector
from DataCollection.race_cards.full import FullRaceCardsCollector


class ValueMonitor:

    def __init__(self):
        self.collect_race_cards_until_today()
        self.model = AgentModel()
        self.race_cards: List[RaceCard] = TodayRaceCardsFetcher().fetch_race_cards()
        self.race_cards_injector = CurrentRaceCardsInjector()

        self.next_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(self.race_cards[0].race_id)

    def serve_betting_slip(self) -> BettingSlip:
        if not self.next_race_card.is_open and len(self.race_cards) >= 2:
            self.skip_race()

        updated_race_card = self.race_cards_injector.inject_newest_odds_into_horses(self.next_race_card)
        estimation_result = self.model.estimate_race_card(updated_race_card)
        betting_slip = self.model.bet_model.bettor.bet(estimation_result)

        print(f"{datetime.datetime.now()}: Served betting slip")
        return list(betting_slip.values())[0]

    def skip_race(self) -> None:
        self.race_cards.pop(0)

        self.next_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(self.race_cards[0].race_id)

    def collect_race_cards_until_today(self):
        train_data_collector = TrainDataCollector(file_name="race_cards")
        query_date = datetime.date(year=2023, month=1, day=5)

        newest_date = datetime.date.today()
        train_data_collector.collect_forward_until_newest_date(query_date=query_date, newest_date=newest_date)
