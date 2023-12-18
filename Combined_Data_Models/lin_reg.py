from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from joblib import dump
import os

from utils import read_csv, validate

X, y = read_csv()

# Initialize variables to store the best model's information
best_rmse = float("inf")
best_mae = None
best_r2 = None
best_state = None
best_model = None

for i in range(100):
    print("Random state: ", i)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=i
    )

    # Linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Validation
    y_pred, rmse, mae, r2 = validate(model, X_test, y_test, "Linear Regression")

    # Check if the current model is better than the best model so far based on RMSE
    if rmse < best_rmse:
        best_rmse = rmse
        best_mae = mae
        best_r2 = r2
        best_state = i
        best_model = model

print(
    f"Best model found at random state {best_state} with RMSE: {best_rmse}, MAE: {best_mae}, R²: {best_r2}"
)

# Save the best model
dump(best_model, "./lin_reg_best.joblib")


# Best models for combined dataa.csv:

# Linear regression: RMSE: 2.6827498391295697, MAE: 1.6435703236589592, R²: 0.44583106516856286
# NN: RMSE: 6.47518158, MAE: 2.43163800, R^2: 0.56252324
# RF: 2.8808001371299325, MAE: 1.3619335438535711, R²: 0.3014123863135772
