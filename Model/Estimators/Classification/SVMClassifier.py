from typing import Tuple
import numpy as np
import torch
from numpy import ndarray
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC

from torch.utils.data import DataLoader, TensorDataset

from Model.Estimators.Classification.networks import SimpleMLP
from Model.Estimators.util.sample_loading import TrainRaceCardLoader, TestRaceCardLoader

from Model.Estimators.Estimator import Estimator
from Model.Estimators.util.padding import FeaturePaddingTransformer, ClassificationLabelPaddingTransformer, \
    RegressionLabelPaddingTransformer, FeaturePaddingTransformer3D, FeaturePaddingTransformer2D
from ModelTuning import simulate_conf
from Persistence import neural_network_persistence
from SampleExtraction.FeatureManager import FeatureManager

from SampleExtraction.RaceCardsSample import RaceCardsSample


class SVMClassifier(Estimator):

    def __init__(
            self,
            feature_manager: FeatureManager,
            params: dict,
    ):
        super().__init__(feature_manager)

        self.params = params
        self.horses_per_race_padding_size = self.params["horses_per_race_padding_size"]
        self.loss_function = self.params["loss_function"]

        self.one_hot_encoder = OneHotEncoder(handle_unknown="ignore")
        self.standard_scaler = StandardScaler()
        self.feature_padding_transformer = FeaturePaddingTransformer2D(padding_size_per_group=self.horses_per_race_padding_size)
        self.svm = LogisticRegression()

    def predict(
            self,
            train_sample: RaceCardsSample,
            validation_sample: RaceCardsSample,
            test_sample: RaceCardsSample
    ) -> Tuple[ndarray, float]:
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.fillna(-1)

        self.fit(train_sample, validation_sample)

        print("Model tuning completed!")
        test_loss = self.score_test_sample(test_sample)

        return test_sample.race_cards_dataframe["score"], test_loss

    def score_test_sample(self, test_sample: RaceCardsSample):
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.fillna(-1)

        test_race_card_loader = TestRaceCardLoader(
            test_sample,
            self.feature_manager,
            one_hot_encoder=self.one_hot_encoder,
            standard_scaler=self.standard_scaler,
            feature_padding_transformer=self.feature_padding_transformer
        )

        predictions = self.svm.decision_function(test_race_card_loader.x).flatten()

        self.feature_padding_transformer.padding_size_per_group = len(self.svm.classes_)
        scores = self.feature_padding_transformer.get_non_padded_scores(predictions, test_race_card_loader.group_counts)

        test_sample.race_cards_dataframe["score"] = scores

        return 0.0

    def fit(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.fillna(-1)
        validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe.fillna(-1)

        train_race_card_loader = TrainRaceCardLoader(
            train_sample,
            self.feature_manager,
            one_hot_encoder=self.one_hot_encoder,
            standard_scaler=self.standard_scaler,
            feature_padding_transformer=self.feature_padding_transformer
        )

        validation_race_card_loader = TestRaceCardLoader(
            validation_sample,
            self.feature_manager,
            one_hot_encoder=self.one_hot_encoder,
            standard_scaler=self.standard_scaler,
            feature_padding_transformer=self.feature_padding_transformer
        )

        self.svm.fit(train_race_card_loader.x, train_race_card_loader.y)

        acc = self.svm.score(validation_race_card_loader.x, validation_race_card_loader.y)

        print(f"Training done: Validation accuracy: {acc}")

        return 0.0

    def run_train_epoch(self, train_dataloader: DataLoader):
        size = len(train_dataloader.dataset)
        num_batches = len(train_dataloader)

        train_loss, train_accuracy = 0, 0
        self.network.train()
        for batch_idx, (X, y) in enumerate(train_dataloader):
            X, y = X.to(self.device), y.to(self.device)

            pred = self.network(X)

            batch_loss = self.get_batch_loss(pred, y)

            batch_loss.backward()

            torch.nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=2)

            self.optimizer.step()
            self.optimizer.zero_grad()

            train_loss += batch_loss.item()

            # train_accuracy += (pred.argmax(1) == y).type(torch.float).sum().item()

        train_loss /= num_batches
        # train_accuracy /= size

        # print(f"Train Avg loss/Accuracy: {train_loss:>8f}")

        return train_loss

    def run_validation_epoch(self, validation_dataloader: DataLoader) -> float:
        size = len(validation_dataloader.dataset)
        num_batches = len(validation_dataloader)

        validation_loss, validation_accuracy = 0, 0
        self.network.eval()

        with torch.no_grad():
            for X, y in validation_dataloader:
                X, y = X.to(self.device), y.to(self.device)

                pred = self.network(X)

                loss = self.get_batch_loss(pred, y)

                validation_loss += loss.item()

                # validation_accuracy += (pred.argmax(1) == y).type(torch.float).sum().item()

        validation_loss /= num_batches
        # validation_accuracy /= size

        # print(f"Validation Avg loss/Accuracy: {validation_loss:>8f}")

        return validation_loss

    def run_test_epoch(self, test_dataloader: DataLoader) -> float:
        size = len(test_dataloader.dataset)
        num_batches = len(test_dataloader)
        self.network.eval()
        test_loss, test_acc = 0, 0

        with torch.no_grad():
            for X, y in test_dataloader:
                X, y = X.to(self.device), y.to(self.device)
                pred = self.network(X)

                if pred.dim() == 1:
                    pred = pred.unsqueeze(0)

                loss = self.get_batch_loss(pred, y)

                test_loss += loss.item()
                # test_acc += (pred.argmax(1) == y).type(torch.float).sum().item()

        test_loss /= num_batches
        # test_acc /= size

        print(f"Test Avg loss/Accuracy: {test_loss:>8f}")

        return test_loss

    def get_batch_loss(self, pred: ndarray, y: ndarray) -> float:
        return self.loss_function(pred, y)
