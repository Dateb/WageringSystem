from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import max_win_prob_source


class RacebetsWinProbability(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        inverse_odds = [1 / horse.racebets_win_sp for horse in race_card.horses if horse.racebets_win_sp > 0]
        total_inverse_odds = sum(inverse_odds)

        if total_inverse_odds == 0 or horse.racebets_win_sp == 0:
            return self.PLACEHOLDER_VALUE
        return (1 / horse.racebets_win_sp) / total_inverse_odds


class BetfairOverround(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        inverse_odds = [1 / horse.betfair_win_sp for horse in race_card.horses if horse.betfair_win_sp > 0]
        overround = sum(inverse_odds)

        return float(overround)


class BetfairWinMarketWinProbability(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        inverse_odds = [1 / horse.betfair_win_sp for horse in race_card.horses if horse.betfair_win_sp > 0]
        total_inverse_odds = sum(inverse_odds)

        if total_inverse_odds == 0 or horse.betfair_win_sp == 0:
            return self.PLACEHOLDER_VALUE
        return (1 / horse.betfair_win_sp) / total_inverse_odds


class BetfairPlaceMarketWinProbability(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        inverse_odds = [1 / horse.betfair_place_sp for horse in race_card.horses if horse.betfair_place_sp > 0]

        if len(inverse_odds) < race_card.n_horses:
            return self.PLACEHOLDER_VALUE

        total_inverse_odds = sum(inverse_odds)

        if total_inverse_odds == 0 or horse.betfair_place_sp == 0:
            return self.PLACEHOLDER_VALUE
        return (1 / horse.betfair_place_sp) / total_inverse_odds


class IndustryMarketWinProbabilityDiff(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        inverse_odds_market = [1 / horse.betfair_win_sp for horse in race_card.horses if horse.betfair_win_sp > 0]
        total_inverse_odds_market = sum(inverse_odds_market)

        inverse_odds_industry = [1 / horse.racebets_win_sp for horse in race_card.horses if horse.racebets_win_sp > 0]
        total_inverse_odds_industry = sum(inverse_odds_industry)

        if total_inverse_odds_market == 0 or horse.betfair_win_sp == 0 or horse.racebets_win_sp == 0 or total_inverse_odds_industry == 0:
            return self.PLACEHOLDER_VALUE

        market_win_prob = (1 / horse.betfair_win_sp) / total_inverse_odds_market
        industry_win_prob = (1 / horse.racebets_win_sp) / total_inverse_odds_industry

        industry_market_win_probability_diff = market_win_prob - industry_win_prob

        if industry_market_win_probability_diff < -1 or industry_market_win_probability_diff > 1:
            print("yellow")

        return industry_market_win_probability_diff


class IsFavorite(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        is_favorite = horse.betfair_win_sp == min([h.betfair_win_sp for h in race_card.horses])
        return is_favorite


class IsUnderdog(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        is_underdog = horse.betfair_win_sp == max([h.betfair_win_sp for h in race_card.horses])
        return is_underdog


class HighestLifetimeWinProbability(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        max_win_prob = max_win_prob_source.get_max_of_name(str(horse.subject_id))

        if max_win_prob is None:
            return self.PLACEHOLDER_VALUE

        return max_win_prob
