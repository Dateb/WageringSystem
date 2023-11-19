import numpy as np
import pandas as pd
import torch
from numpy import ndarray, mean
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from torch.utils.data import DataLoader

from Model.Estimators.Classification.networks import SimpleMLP
from Model.Estimators.Classification.sample_loading import TrainRaceCardLoader, TestRaceCardLoader, \
    FeaturePaddingTransformer, ClassificationLabelPaddingTransformer, RegressionLabelPaddingTransformer

from Model.Estimators.Estimator import Estimator
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

        self.params = params
        self.horses_per_race_padding_size = self.params["horses_per_race_padding_size"]
        self.loss_function = self.params["loss_function"]

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"Using {self.device} device")

        self.missing_values_imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        self.one_hot_encoder = OneHotEncoder(handle_unknown="ignore")

        self.feature_padding_transformer = FeaturePaddingTransformer(self.horses_per_race_padding_size)

        if simulate_conf.LEARNING_MODE == "Classification":
            self.label_padding_transformer = ClassificationLabelPaddingTransformer()
        else:
            self.label_padding_transformer = RegressionLabelPaddingTransformer()

    def filter_group(self, group):
        return not any(group.isna().any())

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(self.filter_group)

        self.fit_validate(train_sample, validation_sample)

        print("Model tuning completed!")
        self.score_test_sample(test_sample)

        return test_sample.race_cards_dataframe["score"]

    def score_test_sample(self, test_sample: RaceCardsSample):
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(
            self.filter_group)

        races_to_remove = test_sample.race_cards_dataframe.groupby('race_id').filter(lambda group: all(group["PreviousWinProbability"] == -1))["race_id"]
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe[~test_sample.race_cards_dataframe["race_id"].isin(races_to_remove)]

        test_race_card_loader = TestRaceCardLoader(
            test_sample,
            self.feature_manager,
            missing_values_imputer=self.missing_values_imputer,
            one_hot_encoder=self.one_hot_encoder,
            feature_padding_transformer=self.feature_padding_transformer,
            label_padding_transformer=self.label_padding_transformer
        )

        self.test_epoch(test_race_card_loader.dataloader)

        with torch.no_grad():
            self.network.eval()
            predictions = self.network(test_race_card_loader.x_tensor.to(self.device))

        scores = self.get_non_padded_scores(predictions, test_race_card_loader.group_counts)
        test_sample.race_cards_dataframe["score"] = scores

    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(self.filter_group)

        races_to_remove = train_sample.race_cards_dataframe.groupby('race_id').filter(lambda group: all(group["PreviousWinProbability"] == -1))["race_id"]
        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe[~train_sample.race_cards_dataframe["race_id"].isin(races_to_remove)]

        validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(self.filter_group)

        races_to_remove = validation_sample.race_cards_dataframe.groupby('race_id').filter(lambda group: all(group["PreviousWinProbability"] == -1))["race_id"]
        validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe[~validation_sample.race_cards_dataframe["race_id"].isin(races_to_remove)]

        train_race_card_loader = TrainRaceCardLoader(
            train_sample,
            self.feature_manager,
            missing_values_imputer=self.missing_values_imputer,
            one_hot_encoder=self.one_hot_encoder,
            feature_padding_transformer=self.feature_padding_transformer,
            label_padding_transformer=self.label_padding_transformer
        )

        validation_race_card_loader = TestRaceCardLoader(
            validation_sample,
            self.feature_manager,
            missing_values_imputer=self.missing_values_imputer,
            one_hot_encoder=self.one_hot_encoder,
            feature_padding_transformer=self.feature_padding_transformer,
            label_padding_transformer=self.label_padding_transformer,
        )

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
            print(f"Current lr: {self.scheduler.optimizer.param_groups[-1]['lr']}\n-------------------------------")

            train_loss = self.fit_epoch(train_race_card_loader.dataloader)
            validation_loss = self.validate_epoch(validation_race_card_loader.dataloader)

            scheduler_metric = abs(validation_loss - train_loss) * mean([train_loss, validation_loss])

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

    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit_epoch(self, train_dataloader: DataLoader):
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

            train_accuracy += (pred.argmax(1) == y).type(torch.float).sum().item()

        train_loss /= num_batches
        train_accuracy /= size

        print(f"Train Avg loss/Accuracy: {train_loss:>8f}/{(100 * train_accuracy):>0.1f}%")

        return train_loss

    def validate_epoch(self, validation_dataloader: DataLoader) -> float:
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

                validation_accuracy += (pred.argmax(1) == y).type(torch.float).sum().item()

        validation_loss /= num_batches
        validation_accuracy /= size

        print(f"Validation Avg loss/Accuracy: {validation_loss:>8f}/{(100 * validation_accuracy):>0.1f}%")

        return validation_loss

    def test_epoch_per_month(self, test_sample: RaceCardsSample):
        for year_month in test_sample.year_months:
            race_cards_df = test_sample.get_dataframe_by_year_month(year_month)
            monthly_sample = RaceCardsSample(race_cards_df)
            monthly_race_cards_loader = TestRaceCardLoader(
                monthly_sample,
                self.feature_manager,
                missing_values_imputer=self.missing_values_imputer,
                one_hot_encoder=self.one_hot_encoder,
                feature_padding_transformer=self.feature_padding_transformer,
                label_padding_transformer=self.label_padding_transformer
            )
            print(f"{year_month}:")
            self.test_epoch(monthly_race_cards_loader.dataloader)

    def test_epoch(self, test_dataloader: DataLoader):
        size = len(test_dataloader.dataset)
        num_batches = len(test_dataloader)
        self.network.eval()
        test_loss, correct = 0, 0

        with torch.no_grad():
            for X, y in test_dataloader:
                X, y = X.to(self.device), y.to(self.device)
                pred = self.network(X)

                if pred.dim() == 1:
                    pred = pred.unsqueeze(0)

                loss = self.get_batch_loss(pred, y)

                test_loss += loss.item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        test_loss /= num_batches
        correct /= size

        print(f"Test Avg loss/Accuracy: {test_loss:>8f}/{(100 * correct):>0.1f}%")

    def get_batch_loss(self, pred: ndarray, y: ndarray) -> float:
        return self.loss_function(pred, y)

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray):
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        num_races = len(group_counts)

        if num_races == 1:
            for j in range(group_counts[0]):
                scores[j] = predictions[j]
            return scores

        for i in range(num_races):
            group_count = group_counts[i]
            for j in range(group_count):
                scores[horse_idx] = predictions[i, j]
                horse_idx += 1

        return scores
