import matplotlib.pyplot as plt
import numpy as np
import json

t1, t2, t3 = None, None, None
l1, l2, l3 = None, None, None

# load json file
json_files = ["kv1.json", "kv2.json", "kv3.json"]

for file in json_files:
    with open("data/" + file, "r") as f:
        data = json.load(f)

    if file == "kv1.json":
        t1 = data["throughput"]
        l1 = data["latency"]
    elif file == "kv2.json":
        t2 = data["throughput"]
        l2 = data["latency"]
    elif file == "kv3.json":
        t3 = data["throughput"]
        l3 = data["latency"]

# plot latency vs throughput
plt.plot(t1, l1, label="1 KV store", color="red", linestyle="-", marker="o")
plt.plot(t2, l2, label="2 KV stores", color="blue", linestyle="-", marker="s")
plt.plot(t3, l3, label="3 KV stores", color="green", linestyle="-", marker="^")

plt.xlabel("Throughput (req/s)")
plt.ylabel("Latency (s)")
plt.title("Latency vs Throughput")

plt.legend()
plt.show()
