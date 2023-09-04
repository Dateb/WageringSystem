from torch import nn

__TEST_PAYOUTS_PATH = "../data/test_payouts.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

N_CONTAINER_MONTHS = 1
N_MONTHS_TRAIN_SAMPLE = 6
N_MONTHS_TEST_SAMPLE = 7
N_MONTHS_FORWARD_OFFSET = 100

MAX_HORSES_PER_RACE = 20

NN_CLASSIFIER_PARAMS = {
    "loss_function": nn.CrossEntropyLoss(),
    "base_lr": 1e-2,
    "decay_factor": 0.1,
    "patience": 5,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-3,
    "dropout_rate": 0.2,
    "horses_per_race_padding_size": MAX_HORSES_PER_RACE
}
