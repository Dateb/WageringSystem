from Experiments.Validator import Validator


class ValidationScorer:

    def __init__(self, validator: Validator, max_rounds: int):
        self.__validator = validator
        self.__max_rounds = max_rounds

    def score(self) -> float:
        total_score = 0
        n_rounds = 1
        while n_rounds <= self.__max_rounds:
            score = self.__get_score_of_round(n_rounds)
            if score <= 1.0:
                total_score += score
                return total_score

            total_score += 1.0
            n_rounds += 1

        return total_score

    def __get_score_of_round(self, round_nr: int) -> float:
        fund_history_summary = self.__validator.create_random_fund_history(
            name="Feature_Selected_Ranker",
            random_state=round_nr,
        )

        return fund_history_summary.win_loss_ratio
