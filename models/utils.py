import numpy as np
from sklearn.metrics import mean_squared_error

def read_csv(file_name='data.csv'):
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)

    # remove first and second columns
    data = np.delete(data, [0, 1], axis=1)

    # split the data into features and labels
    X = data[:, :3]
    y = data[:, 3:]

    return X, y

def validate(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    print(f'Model: {model_name}')
    print(f"RMSE: {rmse:.8f}")

    score = model.score(X_test, y_test)
    print(f"R^2 Score: {score:.8f}")

    return y_pred