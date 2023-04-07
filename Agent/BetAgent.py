from datetime import date

from DataAbstraction.Present.RaceCard import RaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from Model.Betting.BettingSlip import BettingSlip
from ModelTuning.BetModelTuner import BetModelTuner
from SampleExtraction.SampleEncoder import SampleEncoder


class BetAgent:

    def __init__(self):
        self.model_tuner = BetModelTuner(
            n_warm_up_months=24,
            n_sample_months=30,
        )
        self.model, fund_history_summary = self.model_tuner.tune_model()

    def run(self) -> None:
        race_ids = DayCollector().get_open_race_ids_of_day(date.today())
        print(race_ids)
        for race_id in race_ids:
            current_full_race_card = FullRaceCardsCollector(collect_results=False).create_race_card(race_id)

            betting_slip = self.bet_on_race_card(current_full_race_card)

            print(betting_slip)

    def bet_on_race_card(self, race_card: RaceCard) -> BettingSlip:
        sample_encoder = SampleEncoder(self.model_tuner.feature_manager.features,
                                       self.model_tuner.race_cards_sample_factory.columns)

        race_card_arr = self.model_tuner.race_cards_sample_factory.race_card_to_array(race_card)
        sample_encoder.add_race_cards_arr(race_card_arr)

        race_card_sample = sample_encoder.get_race_cards_sample()

        betting_slips = self.model.bet_on_race_cards_sample(race_card_sample)

        return list(betting_slips.values())[0]


def main():
    bettor = BetAgent()
    bettor.run()


if __name__ == '__main__':
    main()
    print("finished")
