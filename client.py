import multiprocessing
import requests
import time
import random
import multiprocessing
import requests
import time
import random
from hashring import HashRing

BASE_URLS = ["http://127.0.0.1:8070", "http://127.0.0.1:8080", "http://127.0.0.1:8090"]
# BASE_URLS = ['http://127.0.0.1:8080', 'http://127.0.0.1:8081']
# BASE_URLS = ["http://127.0.0.1"]
# BASE_URLS = ["http://127.0.0.1:80"]

session = requests.Session()


ring = HashRing(BASE_URLS)

# 20, 50,
batch_size = 20


def kv_store_client_batch(operation, batch_kv):
    # Determine which server to use based on the first key in the batch
    server_url = ring.get_node(batch_kv[0])

    if operation == "set":
        kv_pairs = {key: f"value_for_{key}" for key in batch_kv}
        session.put(f"{server_url}/store_batch", json=kv_pairs)
    elif operation == "get":
        session.get(f"{server_url}/retrieve_batch", json=batch_kv)
    else:
        raise ValueError("Invalid operation")


def worker(num_operations, latencies_queue, operation, process_index):
    batch_kv = []
    for i in range(num_operations):
        key = f"key{process_index}_{i}"
        batch_kv.append(key)
        if len(batch_kv) == batch_size:
            start_time = time.time()
            kv_store_client_batch(operation, batch_kv)
            latency = time.time() - start_time
            latencies_queue.put(latency)
            batch_kv = []


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

    start_time = time.time()

    for p in set_processes:
        p.start()
    for p in set_processes:
        p.join()

    for p in get_processes:
        p.start()
    for p in get_processes:
        p.join()

    total_time = time.time() - start_time
    total_operations = num_operations * num_processes * 2
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


if __name__ == "__main__":
    num_operations_per_process = 800
    num_processes = 10
    benchmark(num_operations_per_process, num_processes)
