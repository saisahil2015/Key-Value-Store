# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV file
# # df = pd.read_csv("autoscaling_client_metrics.csv")
# df = pd.read_csv("non-autoscaling_client_metrics.csv")

# # Sort the DataFrame by 'Client ID' or another metric if needed
# df.sort_values("Throughput", inplace=True)

# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(df["Throughput"], df["Latency"], marker="o", linestyle="-")

# # Adding labels and title
# plt.xlabel("Throughput (operations per second)")
# plt.ylabel("Latency (seconds)")
# plt.title("Throughput vs Latency")

# # Show the plot with a grid
# plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the data from the CSV file
# # df = pd.read_csv("autoscaling_client_metrics.csv")
# df = pd.read_csv("non-autoscaling_client_metrics.csv")

# # Sort the DataFrame by 'Client ID' or another metric if needed
# df.sort_values("Throughput", inplace=True)

# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(df["Throughput"], df["Error Rate"], marker="o", linestyle="-")

# # Adding labels and title
# plt.xlabel("Throughput")
# plt.ylabel("Error Rate")
# plt.title("Throughput vs Error Rate")

# # Show the plot with a grid
# plt.show()


import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
df = pd.read_csv("non-autoscaling_client_metrics.csv")

# Sort the DataFrame by 'Throughput'
df.sort_values("Throughput", inplace=True)

# Calculate a moving average of the latency to smoothen the plot.
# Change the window size to adjust the amount of smoothing (larger window = more smoothing)
df["Latency_Smooth"] = df["Latency"].rolling(window=5).mean()

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(
    df["Throughput"], df["Latency"], marker="o", linestyle="-", alpha=0.3
)  # Original data, more transparent
plt.plot(
    df["Throughput"], df["Latency_Smooth"], marker="", linestyle="-", color="red"
)  # Smoothed data

# Adding labels and title
plt.xlabel("Throughput (operations per second)")
plt.ylabel("Latency (seconds)")
plt.title("Throughput vs Latency (Smoothed)")

# Show the plot with a grid
plt.grid(True)
plt.show()
