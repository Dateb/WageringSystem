from numpy import ndarray

from SampleExtraction.RaceCardsSample import RaceCardsSample


def get_accuracy(race_cards_sample: RaceCardsSample, prob: ndarray) -> float:
    races_df = race_cards_sample.race_cards_dataframe
    races_df["prob"] = prob

    grouped = races_df.groupby('race_id')
    max_score_indexes = grouped['prob'].idxmax()
    predicted_winners_df = races_df.loc[max_score_indexes]

    n_predictions = len(predicted_winners_df[predicted_winners_df["place"] >= 1])

    n_correct_predictions = len(predicted_winners_df[predicted_winners_df["place"] == 1])

    if n_predictions == 0:
        return 0.0

    acc = n_correct_predictions / n_predictions

    return acc


def get_accuracy_by_win_probability(race_cards_sample: RaceCardsSample) -> float:
    races_df = race_cards_sample.race_cards_dataframe

    grouped = races_df.groupby('race_id')
    max_win_prob_indices = grouped["win_probability"].idxmax()
    predicted_winners_df = races_df.loc[max_win_prob_indices]

    n_predictions = len(predicted_winners_df)
    n_correct_predictions = len(predicted_winners_df[predicted_winners_df["place"] == 1])

    acc = n_correct_predictions / n_predictions

    return acc
