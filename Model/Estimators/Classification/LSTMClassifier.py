import numpy as np
import pandas as pd
import torch
from numpy import ndarray
from numba import cuda

from torch import nn
from torch.utils.data import TensorDataset, DataLoader

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard

from Model.Estimators.Estimator import Estimator
from ModelTuning.ModelEvaluator import ModelEvaluator
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.FeatureManager import FeatureManager

from SampleExtraction.RaceCardsSample import RaceCardsSample


class NeuralNetwork(nn.Module):
    def __init__(self, max_horses_per_race: int, feature_count: int):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(max_horses_per_race * feature_count, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, max_horses_per_race),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


class LSTMClassifier(Estimator):

    def __init__(self, feature_manager: FeatureManager, model_evaluator: ModelEvaluator, block_splitter: BlockSplitter):
        super().__init__()
        self.max_horses_per_race = 40
        self.feature_manager = feature_manager
        self.model_evaluator = model_evaluator
        self.block_splitter = block_splitter

        self.feature_count = len(self.feature_manager.features)

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
        print(f"Using {self.device} device")
        self.network = NeuralNetwork(self.max_horses_per_race, self.feature_count).to(self.device)
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(self.network.parameters(), lr=1e-3)

    def predict(self, train_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        x_train, y_train = self.horse_dataframe_to_features_and_labels(train_sample.race_cards_dataframe)

        tensor_x = torch.Tensor(x_train)
        tensor_y = torch.Tensor(y_train).type(torch.LongTensor)

        dataset = TensorDataset(tensor_x, tensor_y)

        train_dataloader = DataLoader(dataset, batch_size=64)

        x_test, y_test = self.horse_dataframe_to_features_and_labels(test_sample.race_cards_dataframe)

        test_tensor_x = torch.Tensor(x_test)
        tensor_y = torch.Tensor(y_test).type(torch.LongTensor)

        dataset = TensorDataset(test_tensor_x, tensor_y)

        test_dataloader = DataLoader(dataset, batch_size=64)

        epochs = 120
        for t in range(epochs):
            print(f"Epoch {t + 1}\n-------------------------------")
            self.fit_epoch(train_dataloader)
            self.test_epoch(test_dataloader)
        print("Done!")

        predictions = self.network(test_tensor_x.to(self.device))

        #TODO: Maybe redundant calculating group_counts?
        group_counts = test_sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()
        scores = self.get_non_padded_scores(predictions, group_counts)

        return scores

    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit_epoch(self, train_dataloader: DataLoader):
        size = len(train_dataloader.dataset)
        self.network.train()
        for batch, (X, y) in enumerate(train_dataloader):
            X, y = X.to(self.device), y.to(self.device)

            # Compute prediction error
            pred = self.network(X)
            loss = self.loss_fn(pred, y)

            # Backpropagation
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()

            if batch % 100 == 0:
                loss, current = loss.item(), (batch + 1) * len(X)
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

    def transform(self, samples: pd.DataFrame) -> ndarray:
        x, y = self.horse_dataframe_to_features_and_labels(samples)
        group_counts = samples.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        predictions = self.network.predict(x)
        scores = self.get_non_padded_scores(predictions, group_counts)
        cuda.select_device(0)
        cuda.close()

        return scores

    def horse_dataframe_to_features_and_labels(self, horse_dataframe: pd.DataFrame):
        horses_features = horse_dataframe[self.feature_manager.feature_names].to_numpy()
        horses_win_indicator = horse_dataframe[Horse.RELEVANCE_KEY].to_numpy()
        group_counts = horse_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_horses, y_horses = self.get_padded_features_and_labels(
            horses_features,
            horses_win_indicator,
            group_counts,
        )

        return x_horses, y_horses

    def get_padded_features_and_labels(
            self,
            horse_features: ndarray,
            horses_win_indicator: ndarray,
            group_counts: ndarray
    ):
        padded_horse_features = np.zeros((len(group_counts), self.max_horses_per_race, self.feature_count))
        padded_horse_labels = np.zeros((len(group_counts)))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(self.max_horses_per_race):
                if j < group_count:
                    padded_horse_features[i, j, :] = horse_features[horse_idx]
                    if horses_win_indicator[horse_idx]:
                        padded_horse_labels[i] = j

                    horse_idx += 1
                else:
                    padded_horse_features[i, j, :] = 0

        return padded_horse_features, padded_horse_labels

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray):
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(group_count):
                if j < self.max_horses_per_race:
                    scores[horse_idx] = predictions[i, j]
                else:
                    scores[horse_idx] = 0
                horse_idx += 1

        return scores
