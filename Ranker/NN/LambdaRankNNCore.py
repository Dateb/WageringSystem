from keras import backend as K
import numpy as np
import math

from keras.callbacks import EarlyStopping


class RankerNN(object):

    def __init__(self, model, solver: str):
        """
        Parameters
        ----------
        solver : {'adam', 'sgd', 'rmsprop', 'adagrad', 'adadelta', adamax},
        default 'adam'
            The solver for weight optimization.
            - 'adam' refers to a stochastic gradient-based optimizer proposed
              by Kingma, Diederik, and Jimmy Ba
        """
        self.model = model
        self.model.compile(optimizer=solver, loss="binary_crossentropy")

    @staticmethod
    def _CalcDCG(labels):
        sumdcg = 0.0
        for i in range(len(labels)):
            rel = labels[i]
            if rel != 0:
                sumdcg += ((2 ** rel) - 1) / math.log2(i + 2)
        return sumdcg

    def _fetch_qid_data(self, y, qid, eval_at=None):
        """Fetch indices, relevances, idcg and dcg for each query id.
        Parameters
        ----------
        y : array, shape (n_samples,)
            Target labels.
        qid: array, shape (n_samples,)
            Query id that represents the grouping of samples.
        eval_at: integer
            The rank postion to evaluate dcg and idcg.
        Returns
        -------
        qid2indices : array, shape (n_unique_qid,)
            Start index for each qid.
        qid2rel : array, shape (n_unique_qid,)
            A list of target labels (relevances) for each qid.
        qid2idcg: array, shape (n_unique_qid,)
            Calculated idcg@eval_at for each qid.
        qid2dcg: array, shape (n_unique_qid,)
            Calculated dcg@eval_at for each qid.
        """
        qid_unique, qid2indices, qid_inverse_indices = np.unique(qid, return_index=True, return_inverse=True)
        # get item releveance for each query id
        qid2rel = [[] for _ in range(len(qid_unique))]
        for i, qid_unique_index in enumerate(qid_inverse_indices):
            qid2rel[qid_unique_index].append(y[i])
        # get dcg, idcg for each query id @eval_at
        if eval_at:
            qid2dcg = [self._CalcDCG(qid2rel[i][:eval_at]) for i in range(len(qid_unique))]
            qid2idcg = [self._CalcDCG(sorted(qid2rel[i], reverse=True)[:eval_at]) for i in range(len(qid_unique))]
        else:
            qid2dcg = [self._CalcDCG(qid2rel[i]) for i in range(len(qid_unique))]
            qid2idcg = [self._CalcDCG(sorted(qid2rel[i], reverse=True)) for i in range(len(qid_unique))]
        return qid2indices, qid2rel, qid2idcg, qid2dcg


    def _transform_pairwise(self, X, y, qid):
        return None, None, None, None


    def fit(self, X, y, qid, validation_data, batch_size=None, epochs=1, verbose=1):
        """Transform data and fit model.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            Features.
        y : array, shape (n_samples,)
            Target labels.
        qid: array, shape (n_samples,)
            Query id that represents the grouping of samples.
        """

        callbacks = [EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)]

        X1_trans, X2_trans, y_trans, weight = self._transform_pairwise(X, y, qid)
        X1_trans_test, X2_trans_test, y_trans_test, weight_test = self._transform_pairwise(validation_data[0], validation_data[1], validation_data[2])
        self.model.fit([X1_trans, X2_trans], y_trans, sample_weight=weight, batch_size=batch_size, epochs=epochs,
                       verbose=verbose, validation_data=([X1_trans_test, X2_trans_test], y_trans_test), callbacks=callbacks)
        self.evaluate(X, y, qid)

    def predict(self, X):
        """Predict output.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            Features.
        Returns
        -------
        y_pred: array, shape (n_samples,)
            Model prediction.
        """
        ranker_output = K.function([self.model.layers[0].input], [self.model.layers[-3].get_output_at(0)])
        return ranker_output([X])[0].ravel()

    def evaluate(self, X, y, qid, eval_at=None):
        """Predict and evaluate ndcg@eval_at.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            Features.
        y : array, shape (n_samples,)
            Target labels.
        qid: array, shape (n_samples,)
            Query id that represents the grouping of samples.
        eval_at: integer
            The rank postion to evaluate NDCG.
        Returns
        -------
        ndcg@eval_at: float
        """
        y_pred = self.predict(X)
        tmp = np.array(np.hstack([y.reshape(-1, 1), y_pred.reshape(-1, 1), qid.reshape(-1, 1)]))
        tmp = tmp[np.lexsort((-tmp[:, 1], tmp[:, 2]))]
        y_sorted = tmp[:, 0]
        qid_sorted = tmp[:, 2]
        ndcg = self._EvalNDCG(y_sorted, qid_sorted, eval_at)
        if eval_at:
            print('ndcg@' + str(eval_at) + ': ' + str(ndcg))
        else:
            print('ndcg: ' + str(ndcg))

    def _EvalNDCG(self, y, qid, eval_at=None):
        """Evaluate ndcg@eval_at.
        Calculated ndcg@n is consistent with ndcg@n- in xgboost.
        """
        _, _, qid2idcg, qid2dcg = self._fetch_qid_data(y, qid, eval_at)
        sumndcg = 0
        count = 0.0
        for qid_unique_idx in range(len(qid2idcg)):
            count += 1
            if qid2idcg[qid_unique_idx] == 0:
                continue
            idcg = qid2idcg[qid_unique_idx]
            dcg = qid2dcg[qid_unique_idx]
            sumndcg += dcg / idcg
        return sumndcg / count


class RankNetNN(RankerNN):

    def __init__(self, model, solver='adam'):
        super(RankNetNN, self).__init__(model, solver)

    def _transform_pairwise(self, X, y, qid):
        """Transform data into ranknet pairs with balanced labels for
        binary classification.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            Features.
        y : array, shape (n_samples,)
            Target labels.
        qid: array, shape (n_samples,)
            Query id that represents the grouping of samples.
        Returns
        -------
        X1_trans : array, shape (k, n_feaures)
            Features of pair 1
        X2_trans : array, shape (k, n_feaures)
            Features of pair 2
        weight: array, shape (k, n_faetures)
            Sample weight lambda.
        y_trans : array, shape (k,)
            Output class labels, where classes have values {0, 1}
        """
        qid2indices, qid2rel, qid2idcg, _ = self._fetch_qid_data(y, qid)
        X1 = []
        X2 = []
        weight = []
        Y = []
        for qid_unique_idx in range(len(qid2indices)):
            if qid2idcg[qid_unique_idx] == 0:
                continue
            IDCG = 1.0 / qid2idcg[qid_unique_idx]
            rel_list = qid2rel[qid_unique_idx]
            qid_start_idx = qid2indices[qid_unique_idx]
            for pos_idx in range(len(rel_list)):
                for neg_idx in range(len(rel_list)):
                    if rel_list[pos_idx] <= rel_list[neg_idx]:
                        continue
                    # balanced class
                    if 1 != (-1) ** (qid_unique_idx + pos_idx + neg_idx):
                        X1.append(X[qid_start_idx + pos_idx])
                        X2.append(X[qid_start_idx + neg_idx])
                        weight.append(1)
                        Y.append(1)
                    else:
                        X1.append(X[qid_start_idx + neg_idx])
                        X2.append(X[qid_start_idx + pos_idx])
                        weight.append(1)
                        Y.append(0)
        return np.asarray(X1), np.asarray(X2), np.asarray(Y), np.asarray(weight)


class LambdaRankNN(RankerNN):

    def __init__(self, model, solver='adam'):
        super(LambdaRankNN, self).__init__(model, solver)

    def _transform_pairwise(self, X, y, qid):
        """Transform data into lambdarank pairs with balanced labels
        for binary classification.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            Features.
        y : array, shape (n_samples,)
            Target labels.
        qid: array, shape (n_samples,)
            Query id that represents the grouping of samples.
        Returns
        -------
        X1_trans : array, shape (k, n_feaures)
            Features of pair 1
        X2_trans : array, shape (k, n_feaures)
            Features of pair 2
        weight: array, shape (k, n_faetures)
            Sample weight lambda.
        y_trans : array, shape (k,)
            Output class labels, where classes have values {0, 1}
        """
        qid2indices, qid2rel, qid2idcg, _ = self._fetch_qid_data(y, qid)
        X1 = []
        X2 = []
        weight = []
        Y = []
        for qid_unique_idx in range(len(qid2indices)):
            if qid2idcg[qid_unique_idx] == 0:
                continue
            IDCG = 1.0 / qid2idcg[qid_unique_idx]
            rel_list = qid2rel[qid_unique_idx]
            qid_start_idx = qid2indices[qid_unique_idx]
            for pos_idx in range(len(rel_list)):
                for neg_idx in range(len(rel_list)):
                    if rel_list[pos_idx] <= rel_list[neg_idx]:
                        continue
                    # calculate lambda
                    pos_loginv = 1.0 / math.log2(pos_idx + 2)
                    neg_loginv = 1.0 / math.log2(neg_idx + 2)
                    pos_label = rel_list[pos_idx]
                    neg_label = rel_list[neg_idx]
                    original = ((1 << pos_label) - 1) * pos_loginv + ((1 << neg_label) - 1) * neg_loginv
                    changed = ((1 << neg_label) - 1) * pos_loginv + ((1 << pos_label) - 1) * neg_loginv
                    delta = (original - changed) * IDCG
                    if delta < 0:
                        delta = -delta
                    # balanced class
                    if 1 != (-1) ** (qid_unique_idx + pos_idx + neg_idx):
                        X1.append(X[qid_start_idx + pos_idx])
                        X2.append(X[qid_start_idx + neg_idx])
                        weight.append(delta)
                        Y.append(1)
                    else:
                        X1.append(X[qid_start_idx + neg_idx])
                        X2.append(X[qid_start_idx + pos_idx])
                        weight.append(delta)
                        Y.append(0)
        return np.asarray(X1), np.asarray(X2), np.asarray(Y), np.asarray(weight)
