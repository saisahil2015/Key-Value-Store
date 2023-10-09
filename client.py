import requests
import time
import threading
import random

HOST, PORT = "127.0.0.1", 80
BASE_URL = f"http://{HOST}:{PORT}"
NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 10  # Number of concurrent clients

throughputs = []
latencies = []

combinations = [
    "RI",
    "WI",
    "B",
]  # for each case, have varied sizes of keys/values to have large/small keys/values

writeOps = ["Put", "Delete"]

import random
import string


def generate_random_string(
    k,
    seed=None,
):
    random.seed(seed)

    return "".join(random.choice(string.ascii_letters) for _ in range(k))


def client_thread(client_id):
    # Start time
    start_time = time.time()

    combination = random.choice(combinations)

    NUM_OPS = random.randint(1, 100)  # Can increase this to max

    NUM_WRITE_REQUESTS = 0
    NUM_READ_REQUESTS = 0

    if combination == "RI":
        NUM_READ_REQUESTS = round((NUM_OPS * 0.9))
        NUM_WRITE_REQUESTS = 1 - NUM_READ_REQUESTS

    elif combination == "WI":
        NUM_READ_REQUESTS = round(NUM_OPS * 0.1)
        NUM_WRITE_REQUESTS = 1 - NUM_READ_REQUESTS

    elif combination == "B":
        NUM_READ_REQUESTS = round(NUM_OPS * 0.5)
        NUM_WRITE_REQUESTS = 1 - NUM_READ_REQUESTS

    for i in range(NUM_WRITE_REQUESTS):
        seed = f"key-{client_id}-{i}"
        key = generate_random_string(
            seed, random.randint(1, 100)
        )  # Can change this and increase the possible values
        writeRequest = random.choice(writeOps)

        if writeRequest == "PUT":
            value = generate_random_string(random.randint(1, 100))
            requests.put(f"{BASE_URL}/store", data={"key": key, "value": value})
        else:
            requests.delete(f"{BASE_URL}/remove", data={"key": key})

    for j in range(NUM_READ_REQUESTS):
        seed = f"key-{client_id}-{j}"
        key = generate_random_string(seed, random.randint(1, 100))
        requests.get(f"{BASE_URL}/retrieve", data={"key": key})

    # End time
    end_time = time.time()

    # Fix this and add the additional values
    elapsed_time = end_time - start_time
    throughput = NUM_REQUESTS * 3 / elapsed_time  # Multiply by 3 for PUT, GET, DEL
    throughputs.append(throughput)
    latency = elapsed_time / (NUM_REQUESTS * 3)  # Average latency per request
    latencies.append(latency)

    print(
        f"Client-{client_id} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds"
    )


if __name__ == "__main__":
    clients = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    print("Overall Throughput: ", sum(throughputs) / NUM_CLIENTS)
    print("Overall Latency: ", sum(latencies) / NUM_CLIENTS)

    print("Testing completed.")
