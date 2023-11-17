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
import subprocess

# BASE_URLS = ['http://localhost:8080', 'http://localhost:8081', 'http://localhost:8082']
# BASE_URLS = ['http://localhost:8080', 'http://localhost:8081']
# BASE_URLS = ['http://localhost:8080']
# ring = HashRing(BASE_URLS)

HOST, PORT = "127.0.0.1", 80


def start_docker_container(client_id):
    # container_id = (
    #     subprocess.check_output(
    #         [
    #             "docker",
    #             "run",
    #             "-d",
    #             "-p",
    #             "8070:80",
    #             "docker-kv-store",
    #             str(client_id),
    #         ]
    #     )
    #     .strip()
    #     .decode()
    # )
    url = "http://127.0.0.1:8070"
    command = f"docker run -d -p {url}:80 docker-kv-store"
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    container_id = result.stdout.decode("utf-8")
    return container_id


def stop_docker_container_and_collect_stats(container_id):
    try:
        # Stop the Docker container
        subprocess.call(["docker", "stop", container_id])

        # Retrieve formatted stats
        stats_output = subprocess.check_output(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "'{{.CPUPerc}} {{.MemUsage}}'",
                container_id,
            ]
        ).decode()

        subprocess.call(["docker", "remove", container_id])

        # Parse the stats output
        cpu_usage, memory_usage = stats_output.strip().split(" ")

        # Remove trailing '%' from CPU usage and 'MiB' or 'GiB' from memory usage
        cpu_usage = float(cpu_usage.replace("%", ""))
        memory_usage_value, memory_usage_unit = memory_usage.split("/")
        memory_usage = float(
            memory_usage_value.replace("MiB", "").replace("GiB", "").strip()
        )

        # Convert memory usage to a consistent unit (e.g., MiB)
        if "GiB" in memory_usage_unit:
            memory_usage *= 1024  # Convert GiB to MiB

        return cpu_usage, memory_usage
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Docker container or collecting stats: {e}")
        return None, None


def kv_store_client(operation, key, value=None):
    # Determine which server to use based on the key
    # server_url = ring.get_node(key) # for client side hashing
    # server_url = "http://localhost:8085"  # for nginx

    url = "http://127.0.0.1:8070"
    server_url = f"{url}:80"

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


def worker(num_operations, latencies_queue, process_index):
    container_id = start_docker_container(f"client_{process_index}")
    start_time = time.time()
    total_latency = 0
    successful_operations = 0

    for operation in ["set", "get", "del"]:
        for i in range(num_operations):
            key = f"key_{process_index}_{operation}_{i}"
            value = f"value_{process_index}_{i}" if operation == "set" else None
            latency = kv_store_client(operation, key, value)

            if latency is not None:
                latencies_queue.put(latency)
                total_latency += latency
                successful_operations += 1

    cpu_usage, memory_usage = stop_docker_container_and_collect_stats(container_id)
    end_time = time.time()
    total_time = end_time - start_time
    num_read = num_operations
    num_write = num_operations * 2
    total_ops = num_read + num_write
    throughput = total_ops / total_time
    average_latency = total_latency / total_ops

    print("Throughput: ", throughput)
    print("Average Latency: ", average_latency)

    metrics = {
        "num_read": num_read,
        "num_write": num_write,
        "read_write_ratio": num_read / num_write,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "throughput": throughput,
        "latency": average_latency,
    }

    # response = requests.post(f"http://localhost:8085/metrics", json=metrics)
    response = requests.post(f"http://localhost:8070:80/metrics", json=metrics)

    if response.status_code == 201:
        print(f"Client-{process_index} | Metrics successfully sent to the server.")
    else:
        print(
            f"Client-{process_index} | Failed to send metrics to server: {response.text}"
        )


def benchmark(num_operations, num_processes):
    manager = multiprocessing.Manager()
    latencies_queue = manager.Queue()
    processes = [
        multiprocessing.Process(
            target=worker, args=(num_operations, latencies_queue, i)
        )
        for i in range(num_processes)
    ]

    start_time = time.time()

    for p in processes:
        p.start()
    for p in processes:
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

    # For testing multiple settings at once
    parser.add_argument("--filename", type=str, default="default-kv.json")

    # For testing one setting at a time
    parser.add_argument("--n_ops", type=int, default=100)
    parser.add_argument("--n_proc", type=int, default=10)

    args = parser.parse_args()
    filename = args.filename
    num_operations = args.n_ops  # Use the command-line argument
    num_processes = args.n_proc  # Use the command-line argument

    for i in range(1, num_processes + 1):
        print("Number of processes:", i)
        print("Number of operations:", num_operations)
        settings.append(str((num_operations, i)))

        t, l = benchmark(num_operations, i)
        average_latencies.append(l)
        throughputs.append(t)

    # Write throughput and latency into a JSON file
    json_data = {
        "settings": settings,
        "throughput": throughputs,
        "latency": average_latencies,
    }

    with open("temp/" + filename, "w") as f:
        print("Writing data to", filename)
        json.dump(json_data, f, indent=2)
