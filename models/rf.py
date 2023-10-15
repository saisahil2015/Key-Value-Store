# random forest

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from utils import read_csv, validate

X, y = read_csv()

# split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# random forest regressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# validation
y_pred, rmse, mae, r2 = validate(model, X_test, y_test, 'Random Forest Regression')