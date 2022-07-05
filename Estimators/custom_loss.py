from tensorflow.python.keras import backend as K
import tensorflow as tf


def rebalanced_kelly_loss(opportunity_loss_scale: float):
    def loss(y_true, y_pred):
        win_indicator = tf.math.ceil(y_true)
        bet_loss = (y_true - y_pred) * (1 - win_indicator)
        opportunity_loss = (y_true - y_pred) * win_indicator
        total_loss = bet_loss + opportunity_loss_scale * opportunity_loss
        return K.mean(K.square(total_loss), axis=-1)

    return loss
