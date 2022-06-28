from typing import List

from DataAbstraction.PastForm import PastForm


class FormTable:

    def __init__(self, raw_data: List):
        self.past_forms = [PastForm(raw_data[idx]) for idx in range(len(raw_data))]

    def get(self, idx: int) -> PastForm:
        return self.past_forms[idx]
