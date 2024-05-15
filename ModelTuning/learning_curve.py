import pickle
from math import ceil

from ModelTuning import simulate_conf
from ModelTuning.simulate import ModelSimulator
from SampleExtraction.data_splitting import MonthDataSplitter


def save_learning_curve() -> None:
    learning_curve = {}
    max_forward_offset = 95
    n_iter = int(ceil(max_forward_offset / 10)) + 1

    for i in range(n_iter):
        data_splitter = MonthDataSplitter(
            container_upper_limit_percentage=0.1,
            n_months_test_sample=10,
            n_months_forward_offset=max([max_forward_offset-(i*10), 0]),
            race_cards_folder=simulate_conf.DEV_RACE_CARDS_FOLDER_NAME
        )
        model_simulator = ModelSimulator(data_splitter)
        test_loss = model_simulator.simulate_prediction()
        learning_curve[data_splitter.n_non_test_months] = test_loss
        print(learning_curve)

    with open("../data/learning_curve.dat", "wb") as f:
        pickle.dump(learning_curve, f)


if __name__ == '__main__':
    save_learning_curve()
    print("finished")
