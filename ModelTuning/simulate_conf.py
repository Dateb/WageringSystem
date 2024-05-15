DEV_RACE_CARDS_FOLDER_NAME = "race_cards_dev"
RELEASE_RACE_CARDS_FOLDER_NAME = "race_cards_release"
BET_RESULT_PATH = "../data/test_payouts.dat"

GBT_CONFIG_PATH: str = "../Model/Estimation/gbt_config"

MARKET_TYPE = "WIN"
MARKET_SOURCE = "Betfair"
STAKES_CALCULATOR = "Fixed"
RUN_MODEL_TUNER = False


NN_CLASSIFIER_PARAMS = {
    "base_lr": 1e-1,
    "decay_factor": 0.1,
    "patience": 30,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-3,
    "dropout_rate": 0.5,
    "horses_per_race_padding_size": 20
}