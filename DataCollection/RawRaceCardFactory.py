from DataCollection.RawRaceCard import RawRaceCard
from DataCollection.Scraper import get_scraper


class RawRaceCardFactory:

    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/races/details/id/'

    def run(self, race_id: str) -> RawRaceCard:
        api_url = f"{self.__base_api_url}{str(race_id)}"
        raw_race_data = self.__scraper.request_data(api_url)

        raw_race_card = RawRaceCard(race_id, raw_race_data)

        self.__verify_race_data_structure(raw_race_card)

        return raw_race_card

    def __verify_race_data_structure(self, raw_race_card: RawRaceCard):
        if 'race' not in raw_race_card.raw_race_data:
            raise KeyError('Race with id {race_id} does not exist'.format(race_id=raw_race_card.race_id))

        if 'runners' not in raw_race_card.raw_race_data:
            raise KeyError('Runners for race with id {race_id} does not exist'.format(race_id=raw_race_card.race_id))

        if 'data' not in raw_race_card.raw_race_data['runners']:
            raise KeyError('Runners dict exists but does not have \'data\' key')