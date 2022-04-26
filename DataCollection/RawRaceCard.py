class RawRaceCard:
    def __init__(self, race_id, raw_race_data):
        self.__race_id = race_id
        self.__raw_race_data = raw_race_data

    @property
    def race_id(self):
        return self.__race_id

    @property
    def raw_race_data(self):
        return self.__raw_race_data

    @property
    def subject_ids(self):
        runners = self.__raw_race_data['runners']['data']
        return [runners[runner_id]["idSubject"] for runner_id in runners]

