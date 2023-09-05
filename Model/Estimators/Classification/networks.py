import torch
from torch import nn
from torch.autograd import Variable


class SimpleMLP(nn.Module):
    def __init__(self, max_horses_per_race: int, feature_count: int, dropout_rate: float):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(

            nn.Linear(max_horses_per_race * (feature_count + 1), 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),

            nn.Dropout(dropout_rate),

            nn.Linear(128, max_horses_per_race),
        )

    def forward(self, x):
        x = nn.functional.normalize(x)
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


class SimpleLSTM(nn.Module):
    def __init__(self, max_horses_per_race: int, feature_count: int, device: str):
        super(SimpleLSTM, self).__init__()
        self.device = device
        self.num_layers = 1
        self.hidden_size = max_horses_per_race

        self.lstm = nn.LSTM(input_size=feature_count + 1, hidden_size=self.hidden_size,
                            num_layers=self.num_layers, batch_first=True)

    def forward(self, x):
        x = nn.functional.normalize(x)
        h_0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device))
        c_0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device))

        output, (hn, cn) = self.lstm(x, (h_0, c_0))
        out = hn.view(-1, self.hidden_size)  # reshaping the data for Dense layer next

        return out
