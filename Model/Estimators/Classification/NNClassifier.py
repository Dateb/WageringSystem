import numpy as np
import torch
from numpy import ndarray
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from torch.utils.data import DataLoader

from Model.Estimators.Classification.networks import SimpleMLP
from Model.Estimators.Classification.sample_loading import TrainRaceCardLoader, TestRaceCardLoader, \
    FeaturePaddingTransformer, ClassificationLabelPaddingTransformer, RegressionLabelPaddingTransformer

from Model.Estimators.Estimator import Estimator
from ModelTuning import simulate_conf
from ModelTuning.ModelEvaluator import ModelEvaluator
from Persistence import neural_network_persistence
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.FeatureManager import FeatureManager

from SampleExtraction.RaceCardsSample import RaceCardsSample


class NNClassifier(Estimator):

    def __init__(
            self,
            feature_manager: FeatureManager,
            model_evaluator: ModelEvaluator,
            params: dict,
    ):
        super().__init__()
        self.feature_manager = feature_manager
        self.model_evaluator = model_evaluator

        self.params = params
        self.horses_per_race_padding_size = self.params["horses_per_race_padding_size"]
        self.loss_function = self.params["loss_function"]

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"Using {self.device} device")

        self.best_validation_loss = np.inf

        self.missing_values_imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        self.one_hot_encoder = OneHotEncoder()

        self.feature_padding_transformer = FeaturePaddingTransformer(self.horses_per_race_padding_size)

        if simulate_conf.LEARNING_MODE == "Classification":
            self.label_padding_transformer = ClassificationLabelPaddingTransformer()
        else:
            self.label_padding_transformer = RegressionLabelPaddingTransformer()

    def filter_group(self, group):
        return not any(group.isna().any())

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(self.filter_group)
        validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(self.filter_group)
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.groupby("race_id", sort=True).filter(self.filter_group)

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

        while self.scheduler.optimizer.param_groups[-1]['lr'] > self.params["lr_to_stop"]:
            current_lr = self.scheduler.optimizer.param_groups[-1]['lr']
            print(f"Current lr: {self.scheduler.optimizer.param_groups[-1]['lr']}\n-------------------------------")
            self.fit_epoch(train_race_card_loader.dataloader)
            self.validate_epoch(validation_race_card_loader.dataloader)
            next_lr = self.scheduler.optimizer.param_groups[-1]['lr']

            if current_lr > next_lr:
                neural_network_persistence.load_state_into_neural_network(self.network)

        print("Model tuning completed!")

        self.test_epoch_per_month(train_sample)
        self.score_test_sample(test_sample)

        return test_sample.race_cards_dataframe["score"]

    def score_test_sample(self, test_sample: RaceCardsSample):
        test_race_card_loader = TestRaceCardLoader(
            test_sample,
            self.feature_manager,
            missing_values_imputer=self.missing_values_imputer,
            one_hot_encoder=self.one_hot_encoder,
            feature_padding_transformer=self.feature_padding_transformer,
            label_padding_transformer=self.label_padding_transformer
        )

        with torch.no_grad():
            self.network.eval()
            predictions = self.network(test_race_card_loader.x_tensor.to(self.device))

        scores = self.get_non_padded_scores(predictions, test_race_card_loader.group_counts)
        test_sample.race_cards_dataframe["score"] = scores

        self.test_epoch_per_month(test_sample)

    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit_epoch(self, train_dataloader: DataLoader):
        size = len(train_dataloader.dataset)
        num_batches = len(train_dataloader)

        train_loss, correct = 0, 0
        self.network.train()
        for batch_idx, (X, y) in enumerate(train_dataloader):
            X, y = X.to(self.device), y.to(self.device)

            pred = self.network(X)

            batch_loss = self.loss_function(pred, y)

            batch_loss.backward()

            torch.nn.utils.clip_grad_norm_(self.network.parameters(), max_norm=2)

            self.optimizer.step()
            self.optimizer.zero_grad()

            train_loss += batch_loss.item()

            # correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        train_loss /= num_batches
        correct /= size

        print(f"Train Error: \n Avg loss: {train_loss:>8f} \n")
        # print(f"Accuracy: {(100 * correct):>0.1f}%")

    def validate_epoch(self, validation_dataloader: DataLoader):
        size = len(validation_dataloader.dataset)
        num_batches = len(validation_dataloader)

        validation_loss, validation_accuracy = 0, 0
        self.network.eval()

        with torch.no_grad():
            for X, y in validation_dataloader:
                X, y = X.to(self.device), y.to(self.device)

                pred = self.network(X)

                loss = self.loss_function(pred, y)

                validation_loss += loss.item()

                # validation_accuracy += (pred.argmax(1) == y).type(torch.float).sum().item()

        validation_loss /= num_batches
        validation_accuracy /= size

        print(f"Validation Error: \n Avg loss: {validation_loss:>8f} \n")
        # print(f"Accuracy: {(100 * correct):>0.1f}%")

        self.scheduler.step(validation_loss)

        if validation_loss < self.best_validation_loss:
            self.best_validation_loss = validation_loss
            neural_network_persistence.save(self.network)

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

                loss = self.loss_function(pred, y)

                test_loss += loss.item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()

        test_loss /= num_batches
        correct /= size

        print(f"Avg loss/Accuracy: {test_loss:>8f}/{(100 * correct):>0.1f}%")

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
