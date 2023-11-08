import requests
import time
import threading
import json
import argparse

# HOST, PORT = "127.0.0.1", 5000
# BASE_URL = f"http://{HOST}:{PORT}"
BASE_URL = "http://localhost:80"
NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 10  # Number of concurrent clients

throughputs = []
latencies = []


def client_thread(client_id):
    # Start time
    start_time = time.time()

    for i in range(NUM_REQUESTS):
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"

        # PUT request
        requests.put(f"{BASE_URL}/store", params={"key": key}, data={"value": value})

        # GET request
        requests.get(f"{BASE_URL}/retrieve", params={"key": key})

        # DEL request
        requests.delete(f"{BASE_URL}/remove", params={"key": key})

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

    # # write throughput and latency into a json file
    # json_data = {"throughput": throughputs, "latency": latencies}
    # with open("data/" + filename, "w") as f:
    #     print("Writing data to", filename)
    #     json.dump(json_data, f)

    print("Overall Throughput: ", sum(throughputs))
    print("Overall Latency: ", sum(latencies) / NUM_CLIENTS)

    print("Testing completed.")
