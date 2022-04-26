from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class PastPlacesExtractor(FeatureExtractor):

    #PU
    #SU
    #UR
    #F

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.__n_races_ago = n_races_ago

    def get_name(self) -> str:
        return f"Place_{self.__n_races_ago}_Races_Ago"

    def get_value(self, horse_id: str, horse_data: dict) -> str:
        past_places = horse_data[horse_id]["ppString"].split(' - ')

        if past_places[0] == '':
            return "0"

        if len(past_places) >= self.__n_races_ago:
            past_place = past_places[self.__n_races_ago - 1]
            if past_place.isdigit():
                return past_place

        return "0"
