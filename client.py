import requests
import time
import json
import argparse
import docker
from consistent_hashing import HashRing

BASE_URL = "http://localhost:80"


image_name = "docker-kv-store"

container_names = ["container1"]
# container_names = ["container1", "container2"]
# container_names = ["container1", "container2", "container3"]

ring = HashRing(nodes=container_names)


throughputs = []
latencies = []
n_requests = []


def measure(n):
    start_time = time.time()
    for i in range(n):
        key = f"key-{i}"
        value = f"value-{i}"

    container_address = None

    container_name = ring.get_node(key)

    if container_name == "container1":
        container_address = "http://localhost:8070"
    elif container_name == "container2":
        container_address = "http://localhost:8080"
    elif container_name == "container3":
        container_address = "http://localhost:8090"

    # PUT request
    requests.put(
        f"{container_address}/store", params={"key": key}, data={"value": value}
    )

    # GET request
    requests.get(f"{container_address}/retrieve", params={"key": key})

    # DEL request
    requests.delete(f"{container_address}/remove", params={"key": key})

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

    for i in range(1, 301):
        latency, throughput = measure(i)
        latencies.append(latency)
        throughputs.append(throughput)
        n_requests.append(i)

        print(
            f"Number of requests: {i} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds"
        )

    # write throughput and latency into a json file
    json_data = {
        "throughput": throughputs,
        "latency": latencies,
        "n_requests": n_requests,
    }
    with open("data/" + filename, "w") as f:
        print("Writing data to", filename)
        json.dump(json_data, f)

    print("Testing completed.")
