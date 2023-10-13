# support vector regression

from sklearn.svm import SVR
from sklearn.model_selection import train_test_split

from utils import read_csv, validate

X, y = read_csv()

# split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# svr
svrs = []
for i in range(7):
    svr = SVR(kernel='linear', C=1.0, epsilon=0.1)
    svr.fit(X_train, y_train[:, i])
    svrs.append(svr)

# validation
for i, svr in enumerate(svrs):
    y_pred = validate(svr, X_test, y_test[:, i], f'SVR {["max_memory_used", "cpu_total_tottime", "cpu_total_cumtime", "cpu_percall_tottime", "cpu_percall_cumtime", "throughput", "latency"][i]}')