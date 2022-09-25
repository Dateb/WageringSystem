from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class HighestOddsWin(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Highest_Odds_Win"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        odds_of_wins = [past_form.odds for past_form in horse.form_table.past_forms if past_form.has_won]
        if not odds_of_wins:
            return self.PLACEHOLDER_VALUE
        return max(odds_of_wins)
