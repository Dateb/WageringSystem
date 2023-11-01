import datetime
from typing import List

from Agent.AgentModel import AgentModel
from Agent.exchange_odds_request import ExchangeOddsRequester
from Model.Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.current_races.fetch import TodayRaceCardsFetcher
from DataCollection.current_races.inject import CurrentRaceCardsInjector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Estimators.RaceEventProbabilities import RaceEventProbabilities


class MonitorData:

    def __init__(self, estimation_result: RaceEventProbabilities, betting_slip: BettingSlip):
        self.estimation_result = estimation_result
        self.betting_slip = betting_slip

    @property
    def json(self):
        return {
            "estimation_result": self.estimation_result.json,
            "betting_slip": self.betting_slip.json,
        }


class ExchangeMonitor:

    def __init__(self):
        self.collect_race_cards_until_today()
        self.model = AgentModel()
        self.race_cards: List[RaceCard] = TodayRaceCardsFetcher().fetch_race_cards()

        self.current_full_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(self.race_cards[0].race_id)

        self.exchange_odds_requester: ExchangeOddsRequester = None

    def open_race(self, customer_id, event_id: str, market_id: str) -> None:
        if self.exchange_odds_requester is not None:
            self.exchange_odds_requester.close_race_connection()

        self.exchange_odds_requester = ExchangeOddsRequester(
            customer_id=customer_id,
            event_id=event_id,
            market_id=market_id,
        )

        next_race_card_id = self.get_requested_race_card_id()

        self.current_full_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(next_race_card_id)

    def serve_monitor_data(self) -> MonitorData:
        if self.exchange_odds_requester is not None:
            race_cards_injector = CurrentRaceCardsInjector(self.exchange_odds_requester.get_odds_by_horse_number_from_message())
            updated_race_card = race_cards_injector.inject_newest_odds_into_horses(self.current_full_race_card)
            estimation_result = self.model.estimate_race_card(updated_race_card)
            betting_slip = self.model.bet_model.bettor.bet(estimation_result)

            print(self.current_full_race_card.race_id)
            print(f"{datetime.datetime.now()}: Served betting slip")
            return MonitorData(estimation_result, list(betting_slip.values())[0])

    def get_requested_race_card_id(self) -> str:
        market_date_raw = str(self.exchange_odds_requester.market_data["marketStartTime"])[:-3]
        for race_card in self.race_cards:
            if market_date_raw == str(race_card.date_raw):
                return race_card.race_id

    def collect_race_cards_until_today(self):
        train_data_collector = TrainDataCollector(file_name="race_cards")
        query_date = datetime.date(year=2023, month=1, day=5)

        newest_date = datetime.date.today()
        train_data_collector.collect_forward_until_newest_date(query_date=query_date, newest_date=newest_date)
