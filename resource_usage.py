import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
df = pd.read_csv("resource_usage.csv")

# Convert memory usage to percentage of 15 MB
df["Average Memory Usage"] = (df["Average Memory Usage"] / 15) * 100

# Sort the DataFrame by 'Index'
df.sort_values("Index", inplace=True)

# Plotting
plt.figure(figsize=(10, 6))

# Plot Average CPU Usage
plt.plot(
    df["Index"],
    df["Average CPU Usage"],
    marker="o",
    linestyle="-",
    label="Average CPU Usage (%)",
)

# Plot Average Memory Usage
plt.plot(
    df["Index"],
    df["Average Memory Usage"],
    marker="o",
    linestyle="-",
    label="Average Memory Usage (%)",
)

# Adding labels, legend, and title
plt.xlabel("Workloads")
plt.ylabel("Resource Usage (%)")
plt.title("Average CPU and Memory Usage Over Workloads")
plt.legend()

plt.show()
