import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
# df = pd.read_csv("autoscaling_client_metrics.csv")
df = pd.read_csv("autoscaling_client_metrics.csv")

# Sort the DataFrame by 'Client ID' or another metric if needed
df.sort_values("Throughput", inplace=True)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df["Throughput"], df["Latency"], marker="o", linestyle="-")

# Adding labels and title
plt.xlabel("Throughput (operations per second)")
plt.ylabel("Latency (seconds)")
plt.title("Throughput vs Latency")

# Show the plot with a grid
plt.show()
