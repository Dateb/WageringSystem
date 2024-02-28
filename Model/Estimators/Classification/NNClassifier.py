from typing import Tuple

import numpy as np
import torch
from numpy import ndarray
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from torch.utils.data import DataLoader, TensorDataset

from Model.Estimators.Classification.networks import SimpleMLP
from Model.Estimators.estimated_probabilities_creation import EstimationResult, RawWinProbabilizer
from Model.Estimators.util.metrics import get_accuracy
from Model.Estimators.util.sample_loading import TrainRaceCardLoader, TestRaceCardLoader

from Model.Estimators.Estimator import Estimator
from Model.Estimators.util.padding import FeaturePaddingTransformer, ClassificationLabelPaddingTransformer, \
    RegressionLabelPaddingTransformer, FeaturePaddingTransformer3D
from ModelTuning import simulate_conf
from Persistence import neural_network_persistence
from SampleExtraction.FeatureManager import FeatureManager

from SampleExtraction.RaceCardsSample import RaceCardsSample


class NNClassifier(Estimator):

    def __init__(
            self,
            feature_manager: FeatureManager,
            params: dict,
    ):
        super().__init__(feature_manager)

        self.probabilizer = RawWinProbabilizer()
        self.params = params
        self.horses_per_race_padding_size = self.params["horses_per_race_padding_size"]
        self.loss_function = self.params["loss_function"]

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"Using {self.device} device")

        self.one_hot_encoder = OneHotEncoder(handle_unknown="ignore")
        self.standard_scaler = StandardScaler()
        self.feature_padding_transformer = FeaturePaddingTransformer3D(padding_size_per_group=self.horses_per_race_padding_size)

    def predict(
            self,
            train_sample: RaceCardsSample,
            validation_sample: RaceCardsSample,
            test_sample: RaceCardsSample
    ) -> Tuple[EstimationResult, float]:
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.fillna(-1)

        self.fit_validate(train_sample, validation_sample)

        print("Model tuning completed!")
        test_loss = self.score_test_sample(test_sample)

        print(f"Test accuracy NN-Model: {get_accuracy(test_sample)}")

        estimation_result = self.probabilizer.create_estimation_result(
            test_sample,
            test_sample.race_cards_dataframe["score"]
        )

        return estimation_result, test_loss

    def score_test_sample(self, test_sample: RaceCardsSample):
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.fillna(-1)

        test_race_card_loader = TestRaceCardLoader(
            test_sample,
            self.feature_manager,
            one_hot_encoder=self.one_hot_encoder,
            standard_scaler=self.standard_scaler,
            feature_padding_transformer=self.feature_padding_transformer
        )

        test_dataloader = self.create_dataloader(test_race_card_loader.x, test_race_card_loader.y)

        test_loss = self.run_test_epoch(test_dataloader)

        with torch.no_grad():
            self.network.eval()
            predictions = self.network(test_dataloader.dataset.tensors[0].to(self.device))

        scores = self.feature_padding_transformer.get_non_padded_scores(predictions, test_race_card_loader.group_counts)
        test_sample.race_cards_dataframe["score"] = scores

        return test_loss

    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.fillna(-1)

        validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe.fillna(-1)

        train_race_card_loader = TrainRaceCardLoader(
            train_sample,
            self.feature_manager,
            one_hot_encoder=self.one_hot_encoder,
            standard_scaler=self.standard_scaler,
            feature_padding_transformer=self.feature_padding_transformer
        )

        train_dataloader = self.create_dataloader(train_race_card_loader.x, train_race_card_loader.y)

        validation_race_card_loader = TestRaceCardLoader(
            validation_sample,
            self.feature_manager,
            one_hot_encoder=self.one_hot_encoder,
            standard_scaler=self.standard_scaler,
            feature_padding_transformer=self.feature_padding_transformer
        )

        validation_dataloader = self.create_dataloader(validation_race_card_loader.x, validation_race_card_loader.y)

        self.network = SimpleMLP(train_race_card_loader.n_feature_values, self.params["dropout_rate"]).to(self.device)

        self.optimizer = torch.optim.SGD(self.network.parameters(), lr=self.params["base_lr"])
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min',
            factor=self.params["decay_factor"],
            patience=self.params["patience"],
            threshold=self.params["threshold"],
            eps=self.params["eps"]
        )

        best_scheduler_metric = np.inf
        best_train_loss = np.inf
        best_validation_loss = np.inf

        while self.scheduler.optimizer.param_groups[-1]['lr'] > self.params["lr_to_stop"]:
            current_lr = self.scheduler.optimizer.param_groups[-1]['lr']
            # print(f"Current lr: {self.scheduler.optimizer.param_groups[-1]['lr']}\n-------------------------------")

            train_loss = self.run_train_epoch(train_dataloader)
            validation_loss = self.run_validation_epoch(validation_dataloader)

            scheduler_metric = validation_loss

            self.scheduler.step(scheduler_metric)

            if scheduler_metric < best_scheduler_metric:
                best_train_loss = train_loss
                best_validation_loss = validation_loss
                best_scheduler_metric = scheduler_metric
                neural_network_persistence.save(self.network)

            next_lr = self.scheduler.optimizer.param_groups[-1]['lr']

            if current_lr > next_lr:
                print(f"restarting at model with train/validation loss: {best_train_loss}/{best_validation_loss}")
                neural_network_persistence.load_state_into_neural_network(self.network)

        return best_scheduler_metric

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

        print(f"Train Avg loss/Accuracy: {train_loss:>8f}")

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

    def get_batch_loss(self, pred, y) -> float:
        return self.loss_function(pred, y)

    def create_dataloader(self, x: ndarray, y: ndarray) -> DataLoader:
        tensor_x = torch.Tensor(x)
        label_dtype = torch.FloatTensor

        tensor_y = torch.Tensor(y).type(label_dtype)

        dataset = TensorDataset(tensor_x, tensor_y)

        return DataLoader(dataset, batch_size=256, shuffle=True)
