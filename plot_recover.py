import pandas as pd
import matplotlib.pyplot as plt

# load csv
before = pd.read_csv("recovery/autoscaling_client_metrics_before_recover.csv")
during = pd.read_csv("recovery/autoscaling_client_metrics_during_recover.csv")
after = pd.read_csv("recovery/autoscaling_client_metrics_after_recover.csv")

# sort by throughput
before.sort_values("Throughput", inplace=True)
during.sort_values("Throughput", inplace=True)
after.sort_values("Throughput", inplace=True)

# plot throughput vs latency separately using subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].plot(before["Throughput"], before["Latency"], linestyle="-")
axes[0].set_title("Before")
axes[0].set_xlabel("Throughput")
axes[0].set_ylabel("Latency")

axes[1].plot(during["Throughput"], during["Latency"], linestyle="-")
axes[1].set_title("During")
axes[1].set_xlabel("Throughput")
axes[1].set_ylabel("Latency")

axes[2].plot(after["Throughput"], after["Latency"], linestyle="-")
axes[2].set_title("After")
axes[2].set_xlabel("Throughput")
axes[2].set_ylabel("Latency")

plt.show()