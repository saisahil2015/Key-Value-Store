# linear regression

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from joblib import dump

from utils import read_csv, validate

X, y = read_csv()

# split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# validation
y_pred, rmse, mae, r2 = validate(model, X_test, y_test, 'Linear Regression')

# dump(model, 'models/lin_reg.joblib')