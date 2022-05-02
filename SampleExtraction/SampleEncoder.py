import numpy as np
import pandas as pd
from typing import List

from pandas import DataFrame

from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.Paths import SAMPLES_PATH
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.HorseFactory import HorseFactory
from DataCollection.PastRacesContainer import PastRacesContainer
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.RaceCardsFilter import RaceCardsFilter


class SampleEncoder:

    def __init__(self, feature_manager: FeatureManager):
        self.__horse_factory = HorseFactory(feature_manager)

    def transform(self, race_cards: List[RaceCard], past_races_container: PastRacesContainer) -> DataFrame:
        horses = []
        for race_card in race_cards:
            horses += self.__horse_factory.create(race_card, past_races_container)

        horse_attributes = horses[0].attributes
        runners_data = np.array([horse.values for horse in horses])
        runners_df = pd.DataFrame(data=runners_data, columns=horse_attributes)

        return runners_df


def main():
    raw_race_cards = RawRaceCardsPersistence("raw_race_cards").load()
    race_cards = [RaceCard(raw_race_card) for raw_race_card in raw_race_cards]
    past_races_container = PastRacesContainerPersistence("past_races").load()
    race_cards = RaceCardsFilter(race_cards, past_races_container).get_filtered_race_cards()
    print(len(race_cards))

    sample_encoder = SampleEncoder(FeatureManager())
    samples_df = sample_encoder.transform(race_cards, past_races_container)

    print(f"Samples: {samples_df}")

    samples_df.to_csv(SAMPLES_PATH)


if __name__ == '__main__':
    main()
