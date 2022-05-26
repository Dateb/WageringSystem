from Experiments.Validator import Validator


class ValidationScorer:

    def __init__(self, validator: Validator):
        self.__validator = validator

    def score(self) -> float:
        fund_history_summary = self.__validator.create_fund_history(
            name="Feature_Selected_Ranker",
        )

        return fund_history_summary.win_loss_ratio

