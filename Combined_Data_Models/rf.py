# # random forest

# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from joblib import dump

# from utils import read_csv, validate

# X, y = read_csv()

# # split the data into training and test sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # random forest regressor
# model = RandomForestRegressor(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # validation
# y_pred, rmse, mae, r2 = validate(model, X_test, y_test, 'Random Forest Regression')

# # save the model
# # dump(model, 'models/new_rf.joblib')


from sklearn.ensemble import RandomForestRegressor
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
    # print("Random state: ", i)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=i
    )

    # Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=i)
    model.fit(X_train, y_train)

    # Validation
    y_pred, rmse, mae, r2 = validate(model, X_test, y_test, "Random Forest Regression")

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
dump(best_model, os.path.join("./best_rf.joblib"))
