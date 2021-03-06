import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from LSTM import shifting
from LSTM import separate_data

class LSTM(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_layer_size, num_layers):
        super(LSTM, self).__init__()

        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_layer_size = hidden_layer_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(input_dim, hidden_layer_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_layer_size, output_dim)

    def forward(self, input):
        hidden_state = torch.zeros(self.num_layers, input.size(0), self.hidden_layer_size)
        cell_state = torch.zeros(self.num_layers, input.size(0), self.hidden_layer_size)

        output, (hidden_state, cell_state) = self.lstm(input, (hidden_state, cell_state))
        out = hidden_state.view(-1, 2)

        out = self.fc(out)

        return out

dataframe = pd.read_csv('global_data.csv')
training_set = dataframe.iloc[:,1:2].values
train_size = int(len(training_set) * 0.75)

#Parameters
input_dim = 1;
hidden_layer_size = 2
num_layers = 1
output_dim = 1
seq_length = 4

model = LSTM(input_dim, output_dim, hidden_layer_size, num_layers)
model.load_state_dict(torch.load('LSTM.pkl'))
model.eval()

sc = MinMaxScaler()
training_data = sc.fit_transform(training_set)

X, y = shifting(training_data, seq_length)
dataX = torch.Tensor(X)
dataY = torch.Tensor(y)

train_X, train_Y, test_X, test_Y = separate_data(X, y)

train_predict = model(dataX)
data_predict = train_predict.data.numpy()
data_predict = sc.inverse_transform(data_predict)

actual_data = dataY.data.numpy()
actual_data = sc.inverse_transform(actual_data)

plt.plot(data_predict, c='r')
plt.plot(actual_data)
plt.axvline(x=train_size, linestyle='--')

plt.show()
