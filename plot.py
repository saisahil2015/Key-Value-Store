import matplotlib.pyplot as plt
import numpy as np
import json

import re

t, l = [], []
err_count = 0

# Open the text file for reading
with open('m.txt', 'r') as file:
    # Iterate through each line in the file
    for line in file:
        # Define regular expressions to match throughput and average latency
        throughput_pattern = r'Throughput: (\d+\.\d+) req/s'
        latency_pattern = r'Average Latency: (\d+\.\d+) seconds'

        # Use regular expressions to extract the values from the current line
        throughput_match = re.search(throughput_pattern, line)
        latency_match = re.search(latency_pattern, line)

        # Check if the matches were found for the current line
        if throughput_match and latency_match:
            throughput_value = throughput_match.group(1)
            latency_value = latency_match.group(1)

            # Append the values to the lists
            t.append(float(throughput_value))
            l.append(float(latency_value))
        else:
            err_count += 1

print(f"Number of errors: {err_count}")

plt.plot(t, l, label="1 KV store", color="red", linestyle="-")
plt.xlabel("Throughput (req/s)")
plt.ylabel("Latency (s)")
plt.title("Latency vs Throughput")
plt.legend()

plt.show()


# t1, t2, t3 = None, None, None
# l1, l2, l3 = None, None, None
# n1 = None

# # load json file
# json_files = ["kv.json"]

# for file in json_files:
#     with open("data/" + file, "r") as f:
#         data = json.load(f)

#     if file == "kv.json":
#         t1 = data["throughput"]
#         l1 = data["latency"]
#         n1 = data["n_requests"]
#     elif file == "kv2.json":
#         t2 = data["throughput"]
#         l2 = data["latency"]
#     elif file == "kv3.json":
#         t3 = data["throughput"]
#         l3 = data["latency"]

# # plot latency vs throughput
# plt.plot(n1, l1, label="1 KV store", color="red", linestyle="-", marker="o")
# # plt.plot(t2, l2, label="2 KV stores", color="blue", linestyle="-", marker="s")
# # plt.plot(t3, l3, label="3 KV stores", color="green", linestyle="-", marker="^")

# plt.xlabel("Throughput (req/s)")
# plt.ylabel("Latency (s)")
# plt.title("Latency vs Throughput")

# plt.legend()
# plt.show()
