import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

def read_csv(file_name='new_data.csv'):
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)

    # remove first column
    data = np.delete(data, [0], axis=1)

    # split the data into features and labels
    X = data[:, :-2]
    y = data[:, -2:]

    print(X.shape)
    print(y.shape)


    return X, y

def validate(model, X_test, y_test, model_name):
    print(f'Model: {model_name}')
    y_pred = model.predict(X_test)

    # RMSE
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    print(f"RMSE: {rmse:.8f}")

    # MAE
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE: {mae:.8f}")

    # R^2
    r2 = model.score(X_test, y_test)
    print(f"R^2: {r2:.8f}")

    return y_pred, rmse, mae, r2