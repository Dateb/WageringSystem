from keras import backend as K

def rebalanced_kelly_loss(opportunity_loss_scale: float):
    def loss(y_true, y_pred):
        #TODO: do proper ceiling of y_true for win_indicator
        win_indicator = y_true
        bet_loss = (y_true - y_pred) * (1 - win_indicator)
        opportunity_loss = (y_true - y_pred) * win_indicator
        total_loss = bet_loss + opportunity_loss_scale * opportunity_loss
        return K.mean(K.square(total_loss), axis=-1)

    return loss


def expected_value_loss(y_true, y_pred):
    has_won_true = y_true[:, :40]
    odds = y_true[:, 40:]

    has_won_pred = y_pred[:, :40]

    true_value = odds * has_won_true - 1
    kelly_fraction = K.relu(odds * has_won_pred - 1, alpha=0.05) / (odds - 1)
    payout = K.sum(true_value * kelly_fraction)
    loss = -payout

    return loss

# TODO: Make this a metric
# def expected_value_loss(y_true, y_pred):
#     has_won_true = y_true[:, 0, :]
#     has_won_pred = y_pred[:, 0, :]
#
#     odds = y_true[:, 1, :]
#
#     true_value = odds * has_won_true - 1
#     kelly_fraction = K.relu(odds * has_won_pred - 1) / (odds - 1)
#     payout = K.sum(true_value * kelly_fraction)
#     loss = -payout
#
#     return loss
