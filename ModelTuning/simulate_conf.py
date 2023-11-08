from torch import nn

__TEST_PAYOUTS_PATH = "../data/test_payouts.dat"
ESTIMATOR_PATH = "../data/estimator.dat"

LEARNING_MODE = "Classification"

if LEARNING_MODE == "Classification":
    LOSS_FUNCTION = nn.CrossEntropyLoss()
else:
    LOSS_FUNCTION = nn.KLDivLoss(reduction="batchmean")

MARKET_TYPE = "WIN"

CONTAINER_UPPER_LIMIT_PERCENTAGE = 0.2
TRAIN_UPPER_LIMIT_PERCENTAGE = 0.8

N_MONTHS_TEST_SAMPLE = 10
N_MONTHS_FORWARD_OFFSET = 0

MAX_HORSES_PER_RACE = 20

NN_CLASSIFIER_PARAMS = {
    "loss_function": LOSS_FUNCTION,
    "base_lr": 1e-1,
    "decay_factor": 0.1,
    "patience": 20,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-6,
    "dropout_rate": 0.2,
    "horses_per_race_padding_size": MAX_HORSES_PER_RACE
}
