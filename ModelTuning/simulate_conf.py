from torch import nn

__TEST_PAYOUTS_PATH = "../data/test_payouts.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

MARKET_TYPE = "PLACE"

N_CONTAINER_MONTHS = 2
N_MONTHS_TRAIN_SAMPLE = 2
N_MONTHS_TEST_SAMPLE = 2
N_MONTHS_FORWARD_OFFSET = 114

MAX_HORSES_PER_RACE = 20

NN_CLASSIFIER_PARAMS = {
    "loss_function": nn.CrossEntropyLoss(),
    "base_lr": 1e-1,
    "decay_factor": 0.1,
    "patience": 20,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-6,
    "dropout_rate": 0.0,
    "horses_per_race_padding_size": MAX_HORSES_PER_RACE
}
