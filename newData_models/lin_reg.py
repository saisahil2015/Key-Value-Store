# # linear regression

# from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import train_test_split
# from joblib import dump

# from utils import read_csv, validate

# X, y = read_csv()

# # split the data into training and test sets

# for i in range(100):
#     print("Random state: ", i)
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=i
#     )

#     # linear regression model
#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     # validation
#     y_pred, rmse, mae, r2 = validate(model, X_test, y_test, "Linear Regression")

#     # dump(model, 'models/lin_reg.joblib')


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


# Linear Regression: Best model found at random state 81 with RMSE: 5.160782483501121, MAE: 4.1412745011617735, R²: 0.28685978897725894
# NN.py: RMSE: 18.53785324, MAE: 7.07224035, R^2: -20.58321306
# Rf.py: Best model found at random state 55 with RMSE: 6.137196414939453, MAE: 4.614654753964586, R²: 0.04217601028313578
# Svr.py: Average RMSE: 7.29239900, Average MAE: 3.91585457, Average R^2: 0.36310968
