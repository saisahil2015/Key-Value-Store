import multiprocessing
import requests
import time
import random
import multiprocessing
import requests
import time
import random
from hashring import HashRing
import matplotlib.pyplot as plt
import json
import argparse

# BASE_URLS = ['http://localhost:8080', 'http://localhost:8081', 'http://localhost:8082']
# BASE_URLS = ['http://localhost:8080', 'http://localhost:8081']
# BASE_URLS = ['http://localhost:8080']
# ring = HashRing(BASE_URLS)


def kv_store_client(operation, key, value=None):
    # Determine which server to use based on the key
    # server_url = ring.get_node(key) # for client side hashing
    server_url = "http://localhost:8085"  # for nginx
    start_time = time.time()
    try:
        if operation == "set":
            requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
        elif operation == "get":
            requests.get(f"{server_url}/retrieve", params={"key": key})
        elif operation == "del":
            requests.get(f"{server_url}/remove", params={"key": key})
        else:
            raise ValueError("Invalid operation")
        end_time = time.time()
        return end_time - start_time
    except Exception as e:
        print(f"Error performing {operation} on {key}: {e}")
        return None


def worker(num_operations, latencies_queue, operation, process_index):
    for i in range(num_operations):
        key = f"key{process_index}_{i}"
        value = f"value{process_index}_{i}" if operation == "set" else None
        latency = kv_store_client(operation, key, value)
        if latency is not None:
            latencies_queue.put(latency)


def benchmark(num_operations, num_processes):
    manager = multiprocessing.Manager()
    latencies_queue = manager.Queue()

    set_processes = [
        multiprocessing.Process(
            target=worker, args=(num_operations, latencies_queue, "set", i)
        )
        for i in range(num_processes)
    ]
    get_processes = [
        multiprocessing.Process(
            target=worker, args=(num_operations, latencies_queue, "get", i)
        )
        for i in range(num_processes)
    ]

    del_processes = [
        multiprocessing.Process(
            target=worker, args=(num_operations, latencies_queue, "del", i)
        )
        for i in range(num_processes)
    ]

    start_time = time.time()

    for p in set_processes:
        p.start()
    for p in set_processes:
        p.join()

    for p in get_processes:
        p.start()
    for p in get_processes:
        p.join()

    for p in del_processes:
        p.start()
    for p in del_processes:
        p.join()

    total_time = time.time() - start_time
    total_operations = (
        num_operations * num_processes * 3
    )  # Each process does num_operations SET and GET and DEL
    total_latencies = []

    while not latencies_queue.empty():
        total_latencies.append(latencies_queue.get())

    average_latency = sum(total_latencies) / len(total_latencies)
    print(f"Total Latency: {sum(total_latencies):.2f} second")
    print(f"Length of latencies: {len(total_latencies):.0f} latencies")
    throughput = total_operations / total_time
    print(f"Total Operation: {total_operations:.0f} operations")
    print(f"Average Latency: {average_latency:.5f} seconds per operation")
    print(f"Throughput: {throughput:.2f} operations per second")
    print(f"Total Benchmark Time: {total_time:.2f} seconds")
    print("\n")

    return throughput, average_latency


if __name__ == "__main__":
    throughputs = []
    average_latencies = []
    settings = []

    parser = argparse.ArgumentParser()

    # for testing multiple settings at once
    parser.add_argument("--filename", type=str, default="default-kv.json")

    # # for testing one setting at a time
    # parser.add_argument("--n_ops", type=int, default=100)
    # parser.add_argument("--n_proc", type=int, default=10)

    args = parser.parse_args()
    filename = args.filename
    num_operations = args.n_ops
    num_processes = args.n_proc

    # =============== testing multiple settings at once ===============
    # comment out this part if you want to test one setting at a time

    num_operations = 100  # fix

    for num_processes in range(1, 10):
        print("Number of processes:", num_processes)
        print("Number of operations:", num_operations)
        settings.append(str((num_operations, num_processes)))

        t, l = benchmark(num_operations, num_processes)
        average_latencies.append(l)
        throughputs.append(t)

    # write throughput and latency into a json file
    json_data = {
        "settings": settings,
        "throughput": throughputs,
        "latency": average_latencies,
    }

    with open("temp/" + filename, "w") as f:
        print("Writing data to", filename)
        json.dump(json_data, f, indent=2)

    # ================= testing one setting at a time =================
    # uncomment this part if you want to test one setting at a time

    # print("Number of processes:", num_processes)
    # print("Number of operations:", num_operations)
    # t, l = benchmark(num_operations, num_processes)
