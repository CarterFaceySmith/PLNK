import config, torch
from alpaca_trade_api import TimeFrame

# Load data
api = config.rest_api
barset = api.get_bars('AAPL', TimeFrame.Day).df

# Prepare data
n_steps = 7
X, y = [], []
for i in range(len(barset)-n_steps-1):
    X.append(barset[i:i+n_steps])
    y.append(barset[i+n_steps])
X = torch.tensor(X)
y = torch.tensor(y)

# Define model
class LSTM(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = torch.nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.fc(x[:, -1, :])
        return x

model = LSTM(1, 64, 1)
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters())

# Train model
for epoch in range(100):
    optimizer.zero_grad()
    output = model(X)
    loss = criterion(output.squeeze(), y)
    loss.backward()
    optimizer.step()

# Predict next day price
last_week = barset[-n_steps:]
next_day = model(torch.tensor(last_week).unsqueeze(0).unsqueeze(2))
print("Predicted price for next day:", next_day.item())
