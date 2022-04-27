import numpy as np
import pandas as pd
from typing import List

from pandas import DataFrame

from Persistence.Paths import SAMPLES_PATH
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.HorseFactory import HorseFactory
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.RaceCardsFilter import RaceCardsFilter


class SampleEncoder:

    def __init__(self, feature_manager: FeatureManager):
        self.__horse_factory = HorseFactory(feature_manager)

    def fit(self, race_cards: List[RaceCard]):
        pass

    def transform(self, race_cards: List[RaceCard]) -> DataFrame:
        horses = []
        for race_card in race_cards:
            horses += self.__horse_factory.create(race_card)

        horse_attributes = horses[0].attributes
        runners_data = np.array([horse.values for horse in horses])
        runners_df = pd.DataFrame(data=runners_data, columns=horse_attributes)

        return runners_df


def main():
    raw_race_cards = RawRaceCardsPersistence().load()
    race_cards = [RaceCard(raw_race_card) for raw_race_card in raw_race_cards]
    race_cards = RaceCardsFilter(race_cards).filtered_race_cards
    print(len(race_cards))

    sample_encoder = SampleEncoder(FeatureManager())
    sample_encoder.fit(race_cards)
    samples_df = sample_encoder.transform(race_cards)

    print(f"Samples: {samples_df}")

    samples_df.to_csv(SAMPLES_PATH)


if __name__ == '__main__':
    main()
