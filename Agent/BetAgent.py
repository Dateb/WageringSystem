from datetime import date

from Agent.exchange_odds_request import MarketRetriever, ExchangeOddsRequester
from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Betting.BettingSlip import BettingSlip
from ModelTuning.BetModelTuner import BetModelTuner
from SampleExtraction.SampleEncoder import SampleEncoder

MARKET_CUSTOMER_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2ODExMTc0NDAsImlhdCI6MTY4MTA4MTQ0MCwiYWNjb3VudElkIjoiUElXSVhfNjNhOWZmZjA4ZDM0MiIsInN0YXR1cyI6ImFjdGl2ZSIsInBvbGljaWVzIjpbIjE5IiwiNTQiLCI4NSIsIjEwNSIsIjIwIiwiMTA3IiwiMTA4IiwiMTEwIiwiMTEzIiwiMTI5IiwiMTMwIiwiMTMxIiwiMTMzIl0sImFjY1R5cGUiOiJCSUFCIiwibG9nZ2VkSW5BY2NvdW50SWQiOiJQSVdJWF82M2E5ZmZmMDhkMzQyIiwic3ViX2NvX2RvbWFpbnMiOm51bGwsImxldmVsIjoiQklBQiIsImN1cnJlbmN5IjoiRVVSIn0.xDKOr9xWGimQ7nMntFsE_2cRj8T_MoCcw1FvEBnsY_4"


class BetAgent:

    def __init__(self):
        self.model_tuner = BetModelTuner(
            n_warm_up_months=24,
            n_sample_months=30,
        )
        bet_model_configuration = self.model_tuner.tune_model()

        train_sample, _ = self.model_tuner.sample_splitter.get_train_test_split()
        self.model = bet_model_configuration.create_bet_model(train_sample)

    def run(self) -> None:
        race_ids = DayCollector().get_open_race_ids_of_day(date.today())
        for race_id in race_ids:
            current_full_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(race_id)
            self.insert_current_market_odds(current_full_race_card)

            self.bet_on_race_card(current_full_race_card)

    def bet_on_race_card(self, race_card: RaceCard):
        sample_encoder = SampleEncoder(
            features=self.model_tuner.feature_manager.features,
            columns=self.model_tuner.race_cards_sample_factory.columns
        )

        race_card_arr = self.model_tuner.race_cards_sample_factory.race_card_to_array(race_card)
        sample_encoder.add_race_cards_arr(race_card_arr)

        race_card_sample = sample_encoder.get_race_cards_sample()

        classification_result = self.model.estimator.score_test_races(race_card_sample)

        print(f"{race_card.name}: {classification_result.y_pred}")

    def insert_current_market_odds(self, race_card: RaceCard):
        market_retriever = MarketRetriever()
        event_id, market_id = market_retriever.get_event_and_market_id(
            track_name=race_card.track_name,
            start_time=race_card.date_raw
        )

        market_odds = ExchangeOddsRequester(
            customer_id=MARKET_CUSTOMER_ID,
            event_id=event_id,
            market_id=market_id
        ).get_odds_from_exchange()

        print(market_odds)
        race_card.insert_market_odds(market_odds)


def main():
    bettor = BetAgent()
    bettor.run()


if __name__ == '__main__':
    main()
    print("finished")
