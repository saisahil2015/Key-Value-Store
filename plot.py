import matplotlib.pyplot as plt
import numpy as np
import json

# file = "3kv-nginx-fix-op-var-proc.json"
# t, l = [], []
# with open("temp/" + file, "r") as f:
#     data = json.load(f)
#     t = data["throughput"]
#     l = data["latency"]

# plt.plot(t, l)
# plt.xlabel("Throughput (req/s)")
# plt.ylabel("Latency (s)")

# plt.show()


files = [
    "1kv-nginx-fix-op-var-proc.json", 
    "2kv-nginx-fix-op-var-proc.json", 
    "3kv-nginx-fix-op-var-proc.json"
]
# files = [
#     "1kv-fix-op-var-proc.json", 
#     "2kv-fix-op-var-proc.json", 
#     "3kv-fix-op-var-proc.json"
# ]
data_list = []
for file in files:
    with open("temp/" + file, "r") as f:
        data = json.load(f)
        data_list.append(data)

colors = ["blue", "red", "green"]
for i, data in enumerate(data_list):
    title = data["title"]
    throughput = data["throughput"]
    latency = data["latency"]

    plt.plot(throughput, latency, label=title, color=colors[i])

plt.title("Latency vs Throughput\n flask with nginx, fix n_ops, vary n_proc")
plt.xlabel("Throughput (req/s)")
plt.ylabel("Latency (s)")
plt.legend()

plt.show()