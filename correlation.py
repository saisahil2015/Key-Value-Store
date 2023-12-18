# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt


# # Example loading data into DataFrame
# # Replace this with how you actually load your data
# df = pd.read_csv("updated_features_data.csv")  # if your data is in a CSV file

# correlation_matrix = df.corr()


# # Assuming 'max_cpu_usage' and 'max_memory_usage' are your target variables
# target_correlation = correlation_matrix[["max_cpu_usage", "max_memory_usage"]].drop(
#     ["max_cpu_usage", "max_memory_usage"]
# )


# plt.figure(figsize=(12, 8))
# sns.heatmap(target_correlation, annot=True, cmap="coolwarm", fmt=".2f")
# plt.title("Correlation of Features with Target Variables")
# plt.show()


import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import numpy as np

# Replace with your actual data loading mechanism
df = pd.read_csv("updated_features_data.csv")


X = df.drop(["max_cpu_usage", "max_memory_usage"], axis=1)  # Features
y = df[
    ["max_cpu_usage", "max_memory_usage"]
]  # Note the double brackets indicating a list of columns


# Initialize the model
rf_model = RandomForestRegressor(n_estimators=100)

# Train the model
rf_model.fit(X, y)

importances = rf_model.feature_importances_
feature_names = X.columns

# Sort feature importances in descending order
indices = np.argsort(importances)[::-1]

# Rearrange feature names so they match the sorted feature importances
names = [feature_names[i] for i in indices]

# Create a plot
plt.figure(figsize=(12, 6))

# Create plot title
plt.title("Feature Importance")

# Add bars
plt.bar(range(X.shape[1]), importances[indices])

# Add feature names as x-axis labels
plt.xticks(range(X.shape[1]), names, rotation=90)

# Show plot
plt.show()
