# support vector regression

from sklearn.svm import SVR
from sklearn.model_selection import train_test_split

from utils import read_csv, validate

X, y = read_csv()
N_LABELS = 7

# split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# svr
svrs = []
for i in range(N_LABELS):
    svr = SVR(kernel='linear', C=1.0, epsilon=0.1)
    svr.fit(X_train, y_train[:, i])
    svrs.append(svr)

# validation
overall_rmse = 0
overall_mae = 0
for i, svr in enumerate(svrs):
    y_pred, rmse, mae = validate(svr, X_test, y_test[:, i], f'SVR {["max_memory_used", "cpu_total_tottime", "cpu_total_cumtime", "cpu_percall_tottime", "cpu_percall_cumtime", "throughput", "latency"][i]}')
    overall_rmse += rmse
    overall_mae += mae

# average RMSE and MAE
print(f'Average RMSE: {overall_rmse / N_LABELS:.8f}')
print(f'Average MAE: {overall_mae / N_LABELS:.8f}')