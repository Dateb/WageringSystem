from DataAbstraction.Present.Horse import Horse


class WritableHorse(Horse):

    def __init__(self, raw_data: dict):
        super().__init__(raw_data)
        self.__raw_data = raw_data

    @property
    def raw_data(self) -> dict:
        return self.__raw_data
