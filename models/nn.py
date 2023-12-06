import torch
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from utils import read_csv


class NN(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(NN, self).__init__()
        self.layer1 = torch.nn.Linear(input_size, hidden_size)
        self.relu = torch.nn.ReLU()
        self.batchnorm = torch.nn.BatchNorm1d(hidden_size)
        self.layer2 = torch.nn.Linear(
            hidden_size, hidden_size // 2
        )  # Adjusted to match the hidden size
        self.layer3 = torch.nn.Linear(
            hidden_size // 2, output_size
        )  # Adjusted to match the hidden size / 2

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.batchnorm(x)  # Batch normalization after ReLU
        x = self.layer2(x)
        x = self.relu(x)
        x = self.layer3(x)
        return x


# class NN(torch.nn.Module):
#     def __init__(self, input_size, hidden_size, output_size):
#         super(NN, self).__init__()
#         # Define more layers
#         self.layer1 = torch.nn.Linear(input_size, hidden_size)
#         self.relu1 = torch.nn.ReLU()
#         self.batchnorm1 = torch.nn.BatchNorm1d(hidden_size)

#         self.layer2 = torch.nn.Linear(hidden_size, hidden_size)
#         self.relu2 = torch.nn.ReLU()
#         self.batchnorm2 = torch.nn.BatchNorm1d(hidden_size)

#         self.layer3 = torch.nn.Linear(hidden_size, hidden_size // 2)
#         self.relu3 = torch.nn.ReLU()
#         self.batchnorm3 = torch.nn.BatchNorm1d(hidden_size // 2)

#         # Add additional layers as needed
#         self.layer4 = torch.nn.Linear(hidden_size // 2, hidden_size // 4)
#         self.relu4 = torch.nn.ReLU()
#         self.batchnorm4 = torch.nn.BatchNorm1d(hidden_size // 4)

#         self.layer5 = torch.nn.Linear(hidden_size // 4, hidden_size // 8)
#         self.relu5 = torch.nn.ReLU()
#         # ... you can continue adding more layers in a similar fashion

#         self.output_layer = torch.nn.Linear(hidden_size // 8, output_size)

#     def forward(self, x):
#         x = self.layer1(x)
#         x = self.relu1(x)
#         x = self.batchnorm1(x)

#         x = self.layer2(x)
#         x = self.relu2(x)
#         x = self.batchnorm2(x)

#         x = self.layer3(x)
#         x = self.relu3(x)
#         x = self.batchnorm3(x)

#         x = self.layer4(x)
#         x = self.relu4(x)
#         x = self.batchnorm4(x)

#         x = self.layer5(x)
#         x = self.relu5(x)
#         # ... continue the forward pass through all the layers

#         x = self.output_layer(x)
#         return x


# Training loop
def train_loop(dataloader, model, loss_fn, optimizer):
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        pred = model(X)
        loss = loss_fn(pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # if batch % 100 == 0:
        #     print(
        #         f"loss: {loss.item():>7f}  [{batch * len(X):>5d}/{len(dataloader.dataset):>5d}]"
        #     )


# Validation loop
def val_loop(dataloader, model, loss_fn):
    model.eval()
    total_loss, total_samples = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            total_loss += loss_fn(pred, y).item() * X.size(0)
            total_samples += X.size(0)
    avg_loss = total_loss / total_samples
    # print(f"Validation loss: {avg_loss:>8f}")
    return avg_loss


# Testing loop
def test_loop(dataloader, model):
    model.eval()
    all_y_true, all_y_pred = [], []
    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            all_y_true.append(y.numpy())
            all_y_pred.append(pred.numpy())
    all_y_true = np.concatenate(all_y_true)
    all_y_pred = np.concatenate(all_y_pred)
    rmse = mean_squared_error(all_y_true, all_y_pred, squared=False)
    mae = mean_absolute_error(all_y_true, all_y_pred)
    r2 = r2_score(all_y_true, all_y_pred)
    print(f"RMSE: {rmse:.8f}, MAE: {mae:.8f}, R^2: {r2:.8f}")


if __name__ == "__main__":
    X, y = read_csv()

    # Split the data into training, validation, and test sets with a 70:20:10 ratio
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_test, X_val, y_test, y_val = train_test_split(
        X_test, y_test, test_size=0.33, random_state=42
    )

    # Scale the data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    # Convert to torch tensors
    X_train = torch.from_numpy(X_train).float()
    X_val = torch.from_numpy(X_val).float()
    X_test = torch.from_numpy(X_test).float()
    y_train = torch.from_numpy(y_train).float()
    y_val = torch.from_numpy(y_val).float()
    y_test = torch.from_numpy(y_test).float()

    # Create data loaders
    train_loader = DataLoader(
        TensorDataset(X_train, y_train), batch_size=16, shuffle=True
    )
    val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=16)
    test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=16)

    input_size = X_train.shape[1]  # Set the input size to match the number of features
    hidden_size = 16  # 16
    output_size = 2  # Set the output size to match the number of target variables

    model = NN(input_size, hidden_size, output_size)
    loss_fn = torch.nn.MSELoss()
    # optimizer = torch.optim.Adagrad(model.parameters(), lr=0.1)
    # optimizer = torch.optim.RMSprop(model.parameters(), lr=0.1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    best_val_loss = float("inf")
    for epoch in range(100):
        # print(f"Epoch {epoch+1}")
        train_loop(train_loader, model, loss_fn, optimizer)
        val_loss = val_loop(val_loader, model, loss_fn)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "best_nn.pth")

    print("Done with training")
    model.load_state_dict(torch.load("best_nn.pth"))
    test_loop(test_loader, model)
