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
        self.layer2 = torch.nn.Linear(hidden_size, hidden_size)
        self.layer3 = torch.nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        x = self.relu(x)
        x = self.batchnorm(x)
        x = self.layer3(x)
        return x

# training loop
def train_loop(dataloader, model, loss_fn, optimizer):
    model.train()   # set model to training mode
    size = len(dataloader.dataset)

    for batch, (X, y) in enumerate(dataloader):
        # forward pass
        pred = model(X)
        loss = loss_fn(pred, y)

        # backward pass
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
    

# validation loop
def val_loop(dataloader, model, loss_fn):
    model.eval()    # set model to evaluation mode
    num_batches = len(dataloader)
    test_loss = 0

    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()

    test_loss /= num_batches
    print(f"val loss: {test_loss:>8f}")

    return test_loss

# testing loop
def test_loop(dataloader, model):
    model.eval()

    all_y_true = []
    all_y_pred = []

    with torch.no_grad():
        for X, y in dataloader:
            pred = model(X)
            all_y_true.append(y.numpy())
            all_y_pred.append(pred.numpy())

    all_y_true = np.concatenate(all_y_true)
    all_y_pred = np.concatenate(all_y_pred)

    # RMSE
    rmse = mean_squared_error(all_y_true, all_y_pred, squared=False)
    print(f"RMSE: {rmse:.8f}")

    # MAE
    mae = mean_absolute_error(all_y_true, all_y_pred)
    print(f"MAE: {mae:.8f}")

    # R^2
    r2 = r2_score(all_y_true, all_y_pred)
    print(f"R^2: {r2:.8f}")

if __name__ == "__main__":

    X, y = read_csv()

    # split the data into training, validation, and test sets with a 70:20:10 ratio
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.33, random_state=42)

    # scale the data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    # convert to torch tensors
    X_train = torch.from_numpy(X_train).float()
    X_test = torch.from_numpy(X_test).float()
    X_val = torch.from_numpy(X_val).float()
    y_train = torch.from_numpy(y_train).float()
    y_test = torch.from_numpy(y_test).float()
    y_val = torch.from_numpy(y_val).float()

    train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=16, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=16, shuffle=True)
    test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=16, shuffle=True)

    input_size = X_train.shape[1]
    hidden_size = 16
    output_size = 2

    model = NN(input_size, hidden_size, output_size)
    loss_fn = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    n_epochs = 100

    # training
    best_loss = float('inf')
    for t in range(n_epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train_loop(train_loader, model, loss_fn, optimizer)
        loss = val_loop(val_loader, model, loss_fn)
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), 'best_nn.pth')

    print("Done!")
    print("Best validation loss: {:.4f}".format(best_loss))

    # testing
    model.load_state_dict(torch.load('best_nn.pth'))
    test_loop(test_loader, model) 