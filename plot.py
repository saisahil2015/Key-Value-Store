import matplotlib.pyplot as plt

# TODO: replace with actual data
throughput1 = [50, 60, 70, 80, 90]
throughput2 = [45, 55, 65, 75, 85]
throughput3 = [40, 50, 60, 70, 80]

latency1 = [1, 2, 3, 4, 5]
latency2 = [2, 3, 4, 5, 6]
latency3 = [3, 4, 5, 6, 7]

elasticput1 = [tp / lt for tp, lt in zip(throughput1, latency1)]
elasticput2 = [tp / lt for tp, lt in zip(throughput2, latency2)]
elasticput3 = [tp / lt for tp, lt in zip(throughput3, latency3)]

fig, (ax1, ax2) = plt.subplots(2, 1)

# latency vs throughput
ax1.plot(throughput1, latency1, marker="o", label="1 KV store")
ax1.plot(throughput2, latency2, marker="s", label="2 KV stores")
ax1.plot(throughput3, latency3, marker="^", label="3 KV stores")
ax1.set_xlabel("Throughput")
ax1.set_ylabel("Latency (ms)")
ax1.tick_params(axis="y")
ax1.legend()

# elasticput vs throughput
ax2.plot(throughput1, elasticput1, marker="o", label="1 KV store")
ax2.plot(throughput2, elasticput2, marker="s", label="2 KV stores")
ax2.plot(throughput3, elasticput3, marker="^", label="3 KV stores")
ax2.set_xlabel("Throughput")
ax2.set_ylabel("Elastic Throughput")
ax2.tick_params(axis="y")
ax2.legend()

plt.suptitle("Latency and Elastic Throughput vs. Throughput")
plt.tight_layout()

plt.show()
plt.savefig("plot.png")
