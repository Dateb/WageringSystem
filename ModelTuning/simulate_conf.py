from torch import nn

LEARNING_CURVE_PATH = "../data/learning_curve.dat"
TEST_PAYOUTS_PATH = "../data/test_payouts.dat"
ESTIMATOR_PATH = "../data/estimator.dat"

LEARNING_MODE = "Classification"

if LEARNING_MODE == "Classification":
    LOSS_FUNCTION = nn.CrossEntropyLoss()
else:
    LOSS_FUNCTION = nn.KLDivLoss(reduction="batchmean")

MARKET_TYPE = "WIN"
MARKET_SOURCE = "Betfair"
STAKES_CALCULATOR = "Fixed"

NN_CLASSIFIER_PARAMS = {
    "loss_function": LOSS_FUNCTION,
    "base_lr": 1e-1,
    "decay_factor": 0.1,
    "patience": 30,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-3,
    "dropout_rate": 0.5,
    "horses_per_race_padding_size": 20
}
