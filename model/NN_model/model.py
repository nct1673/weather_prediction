import torch
import torch.nn as nn

class NNModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(NNModel, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.Sigmoid(),
            nn.BatchNorm1d(256),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0),
            nn.Linear(128, 32),
            nn.Sigmoid(),
            nn.Dropout(0),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.net(x)
