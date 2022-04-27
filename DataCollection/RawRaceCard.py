class RawRaceCard:
    def __init__(self, race_id, raw_race_data):
        self.__race_id = race_id
        self.__raw_race_data = raw_race_data

    def get_subject_id_of_horse(self, horse_id: str) -> str:
        return self.__raw_race_data["runners"]["data"][horse_id]["idSubject"]

    def is_horse_scratched(self, horse_id: str) -> bool:
        return self.__raw_race_data["runners"]["data"][horse_id]["scratched"]

    @property
    def race_id(self):
        return self.__race_id

    @property
    def raw_race_data(self):
        return self.__raw_race_data

    @property
    def horses(self):
        return self.__raw_race_data['runners']['data']

    @property
    def subject_ids(self):
        runners = self.__raw_race_data['runners']['data']
        return [runners[runner_id]["idSubject"] for runner_id in runners]

