from torch import nn

__TEST_PAYOUTS_PATH = "../data/test_payouts.dat"
ESTIMATOR_PATH = "../data/estimator.dat"

MARKET_TYPE = "PLACE"

N_CONTAINER_MONTHS = 3
N_MONTHS_TRAIN_SAMPLE = 32
N_MONTHS_VALIDATION_SAMPLE = 8
N_MONTHS_TEST_SAMPLE = 9
N_MONTHS_FORWARD_OFFSET = 0

MAX_HORSES_PER_RACE = 20

NN_CLASSIFIER_PARAMS = {
    "loss_function": nn.CrossEntropyLoss(),
    "base_lr": 1e-1,
    "decay_factor": 0.1,
    "patience": 20,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-6,
    "dropout_rate": 0.05,
    "horses_per_race_padding_size": MAX_HORSES_PER_RACE
}
