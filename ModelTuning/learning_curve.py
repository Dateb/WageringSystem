import pickle

from ModelTuning.simulate import ModelSimulator
from SampleExtraction.data_splitting import MonthDataSplitter


def save_learning_curve() -> None:
    learning_curve = {}
    max_forward_offset = 94

    for i in range(10):
        data_splitter = MonthDataSplitter(
            container_upper_limit_percentage=0.1,
            train_upper_limit_percentage=0.8,
            n_months_test_sample=10,
            n_months_forward_offset=max_forward_offset-(i*10)
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
