import requests
import time
import json
import argparse

BASE_URL = "http://localhost:80"
NUM_REQUESTS = 2000

throughputs = []
latencies = []
n_requests = []

def measure(n):
    start_time = time.time()
    for i in range(n):
        key = f"key-{i}"
        value = f"value-{i}"

        # PUT request
        requests.put(f"{BASE_URL}/store", params={"key": key}, data={"value": value})

        # GET request
        requests.get(f"{BASE_URL}/retrieve", params={"key": key})

        # DEL request
        requests.delete(f"{BASE_URL}/remove", params={"key": key})

    end_time = time.time()
    elapsed_time = end_time - start_time

    latency = elapsed_time / (n * 3)
    throughput = (n * 3) / elapsed_time

    return latency, throughput

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="key value store")
    parser.add_argument("--filename", type=str, default="kv.json")

    args = parser.parse_args()
    title = args.title
    filename = args.filename

    print(f"Testing {title}.")

    for i in range(1, 1000):
        latency, throughput = measure(i)
        latencies.append(latency)
        throughputs.append(throughput)
        n_requests.append(i)

        print(f"Number of requests: {i} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds")

    # write throughput and latency into a json file
    json_data = {"throughput": throughputs, "latency": latencies, "n_requests": n_requests}
    with open("data/" + filename, "w") as f:
        print("Writing data to", filename)
        json.dump(json_data, f)

    print("Testing completed.")