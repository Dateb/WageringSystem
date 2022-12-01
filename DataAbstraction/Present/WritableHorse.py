from DataAbstraction.Present.Horse import Horse


class WritableHorse(Horse):

    def __init__(self, raw_data: dict):
        super().__init__(raw_data)
        self.raw_data = raw_data
