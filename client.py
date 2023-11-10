import requests
import time
import json
import argparse
import docker

from consistent_hashing import HashRing

# from hashring import HashRing

# TEST THE HASHRING LIBRARY IMPORT AS PROFESSOR HAD

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

        # print("Container name: ", container_name)

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

        # # DEL request
        requests.delete(f"{container_address}/remove", params={"key": key})

    end_time = time.time()
    elapsed_time = end_time - start_time

    latency = elapsed_time / (n * 3)
    throughput = (n * 3) / elapsed_time
    # latency = elapsed_time / (n)
    # throughput = (n) / elapsed_time

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

        if i % 20 == 0:
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


# PROFESSOR'S CODE
# import multiprocessing
# import requests
# import time
# import random
# import multiprocessing
# import requests
# import time
# import random
# from hashring import HashRing

# # BASE_URLS = ["http://127.0.0.1:8070"]
# BASE_URLS = ["http://127.0.0.1:8070", "http://127.0.0.1:8080"]
# # BASE_URLS = ["http://127.0.0.1:8070", "http://127.0.0.1:8080", "http://127.0.0.1:8090"]

# # BASE_URLS = ['http://127.0.0.1:8080', 'http://127.0.0.1:8081']
# # BASE_URLS = ['http://127.0.0.1:8085']
# ring = HashRing(BASE_URLS)


# def kv_store_client(operation, key, value=None):
#     # Determine which server to use based on the key
#     server_url = ring.get_node(key)
#     start_time = time.time()
#     try:
#         if operation == "set":
#             response = requests.put(
#                 f"{server_url}/store", params={"key": key}, data={"value": value}
#             )
#         elif operation == "get":
#             response = requests.get(f"{server_url}/retrieve", params={"key": key})
#         else:
#             raise ValueError("Invalid operation")
#         end_time = time.time()
#         return end_time - start_time
#     except Exception as e:
#         print(f"Error performing {operation} on {key}: {e}")
#         return None


# def worker(num_operations, latencies_queue, operation, process_index):
#     for i in range(num_operations):
#         key = f"key{process_index}_{i}"
#         value = f"value{process_index}_{i}" if operation == "set" else None
#         latency = kv_store_client(operation, key, value)
#         if latency is not None:
#             latencies_queue.put(latency)


# def benchmark(num_operations, num_processes):
#     manager = multiprocessing.Manager()
#     latencies_queue = manager.Queue()

#     set_processes = [
#         multiprocessing.Process(
#             target=worker, args=(num_operations, latencies_queue, "set", i)
#         )
#         for i in range(num_processes)
#     ]
#     get_processes = [
#         multiprocessing.Process(
#             target=worker, args=(num_operations, latencies_queue, "get", i)
#         )
#         for i in range(num_processes)
#     ]
#     start_time = time.time()

#     for p in set_processes:
#         p.start()
#     for p in set_processes:
#         p.join()

#     for p in get_processes:
#         p.start()
#     for p in get_processes:
#         p.join()

#     total_time = time.time() - start_time
#     total_operations = (
#         num_operations * num_processes * 2
#     )  # Each process does num_operations SET and GET
#     total_latencies = []

#     while not latencies_queue.empty():
#         total_latencies.append(latencies_queue.get())

#     average_latency = sum(total_latencies) / len(total_latencies)
#     print(f"Total Latency: {sum(total_latencies):.2f} second")
#     print(f"Length of latencies: {len(total_latencies):.0f} latencies")
#     throughput = total_operations / total_time
#     print(f"Total Operation: {total_operations:.0f} operations")
#     print(f"Average Latency: {average_latency:.5f} seconds per operation")
#     print(f"Throughput: {throughput:.2f} operations per second")
#     print(f"Total Benchmark Time: {total_time:.2f} seconds")


# if __name__ == "__main__":
#     num_operations_per_process = 100
#     num_processes = 5
#     benchmark(num_operations_per_process, num_processes)
