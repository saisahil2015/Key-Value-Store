import requests
import time
import threading
import json
import argparse
import docker
from consistent_hashing import HashRing

# HOST, PORT = "127.0.0.1", 8000
# BASE_URL = f"http://{HOST}:{PORT}"
BASE_URL = "http://localhost:80"
NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 10  # Number of concurrent clients

throughputs = []
latencies = []

image_name = "docker-kv-store"

# container_names = ["container1"]
container_names = ["container1", "container2"]
# container_names = ["container1", "container2", "container3"]

ring = HashRing(nodes=container_names)


def client_thread(client_id):
    # Start time
    start_time = time.time()

    for i in range(NUM_REQUESTS):
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"

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

    # End time
    end_time = time.time()

    elapsed_time = end_time - start_time
    throughput = NUM_REQUESTS * 3 / elapsed_time  # Multiply by 3 for PUT, GET, DEL
    throughputs.append(throughput)
    latency = elapsed_time / (NUM_REQUESTS * 3)  # Average latency per request
    latencies.append(latency)

    print(
        f"Client-{client_id} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", type=str, default="key value store")
    parser.add_argument("--filename", type=str, default="kv.json")

    args = parser.parse_args()
    title = args.title
    filename = args.filename

    print(f"Testing {title}.")

    clients = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    # write throughput and latency into a json file
    json_data = {"throughput": throughputs, "latency": latencies}
    with open("data/" + filename, "w") as f:
        print("Writing data to", filename)
        json.dump(json_data, f)

    print("Overall Throughput: ", sum(throughputs))
    print("Overall Latency: ", sum(latencies) / NUM_CLIENTS)

    print("Testing completed.")
