import numpy as np
import torch
from numpy import ndarray
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

from torch import nn
from torch.utils.data import DataLoader

from Model.Estimators.Classification.networks import SimpleMLP, SimpleLSTM
from Model.Estimators.Classification.sample_loading import TrainRaceCardLoader, TestRaceCardLoader

from Model.Estimators.Estimator import Estimator
from ModelTuning.ModelEvaluator import ModelEvaluator
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.FeatureManager import FeatureManager

from SampleExtraction.RaceCardsSample import RaceCardsSample


class NNClassifier(Estimator):

    def __init__(self, feature_manager: FeatureManager, model_evaluator: ModelEvaluator, block_splitter: BlockSplitter):
        super().__init__()
        self.horses_per_race_padding_size = 40
        self.feature_manager = feature_manager
        self.model_evaluator = model_evaluator
        self.block_splitter = block_splitter

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"Using {self.device} device")

    def predict(self, train_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        missing_values_imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
        one_hot_encoder = OneHotEncoder()

        train_race_card_loader = TrainRaceCardLoader(
            train_sample,
            self.feature_manager,
            horses_per_race_padding_size=self.horses_per_race_padding_size,
            missing_values_imputer=missing_values_imputer,
            one_hot_encoder=one_hot_encoder
        )

        test_race_card_loader = TestRaceCardLoader(
            test_sample,
            self.feature_manager,
            horses_per_race_padding_size=self.horses_per_race_padding_size,
            missing_values_imputer=missing_values_imputer,
            one_hot_encoder=one_hot_encoder
        )

        self.network = SimpleMLP(self.horses_per_race_padding_size, train_race_card_loader.n_feature_values).to(self.device)
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(self.network.parameters(), lr=1e-3)

        epochs = 200
        for t in range(epochs):
            print(f"Epoch {t + 1}\n-------------------------------")
            self.fit_epoch(train_race_card_loader.dataloader)
            self.test_epoch(test_race_card_loader.dataloader)
        print("Done!")

        predictions = self.network(test_race_card_loader.x_tensor.to(self.device))

        scores = self.get_non_padded_scores(predictions, test_race_card_loader.group_counts)

        return scores

    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit_epoch(self, train_dataloader: DataLoader):
        size = len(train_dataloader.dataset)
        self.network.train()
        for batch_idx, (X, y) in enumerate(train_dataloader):
            X, y = X.to(self.device), y.to(self.device)

            pred = self.network(X)
            loss = self.loss_fn(pred, y)

            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()

            if batch_idx % 1000 == 0:
                loss, current = loss.item(), (batch_idx + 1) * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")

    def test_epoch(self, test_dataloader: DataLoader):
        size = len(test_dataloader.dataset)
        num_batches = len(test_dataloader)
        self.network.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in test_dataloader:
                X, y = X.to(self.device), y.to(self.device)
                pred = self.network(X)
                test_loss += self.loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        test_loss /= num_batches
        correct /= size
        print(f"Test Error: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray):
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(group_count):
                if j < self.horses_per_race_padding_size:
                    scores[horse_idx] = predictions[i, j]
                else:
                    scores[horse_idx] = 0
                horse_idx += 1

        return scores
