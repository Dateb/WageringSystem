from torch import nn


class SimpleMLP(nn.Module):
    def __init__(self, max_horses_per_race: int, feature_count: int):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(max_horses_per_race * feature_count, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, max_horses_per_race),
        )

    def forward(self, x):
        x = nn.functional.normalize(x)
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits
