class FormGuide:
    def __init__(self, base_race_id: str, subject_id: str, raw_formguide: dict):
        self.__base_race_id = base_race_id
        self.__subject_id = subject_id
        self.__raw_formguide = raw_formguide

        self.__form_table = raw_formguide["formTable"]
        base_race_card_idx = self.__get_base_race_card_idx()

        self.__form_table = self.__form_table[base_race_card_idx+1:]

    def __get_base_race_card_idx(self):
        for idx, past_race in enumerate(self.__form_table):
            if str(past_race["idRace"]) == self.__base_race_id:
                return idx

        return 0

    @property
    def subject_id(self):
        return self.__subject_id

    @property
    def form_table(self):
        return self.__form_table
