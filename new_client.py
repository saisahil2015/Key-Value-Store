# multi-threaded approach

# import subprocess
# import time
# import multiprocessing
# import requests
# import threading

# HOST = "127.0.0.1"
# last_used_port = multiprocessing.Value(
#     "i", 8069
# )  # Starting from 8069 so the first used port is 8070


# def get_next_port():
#     with last_used_port.get_lock():  # Ensures thread safety
#         last_used_port.value += 1
#         return last_used_port.value


# def start_docker_container(container_id):
#     port = get_next_port()
#     # print("Port got: ", port)
#     command = f"docker run -d -p {port}:80 docker-kv-store"
#     subprocess.run(command.split(), stdout=subprocess.PIPE)
#     return container_id, port  # Return both container_id and port


# def stop_docker_container_and_collect_stats(container_id, max_stats):
#     subprocess.call(["docker", "stop", container_id])
#     subprocess.call(["docker", "rm", container_id])
#     print(
#         f"Container {container_id} stats - CPU: {max_stats[container_id]['cpu']}%, Memory: {max_stats[container_id]['memory']}MiB"
#     )


# def monitor_container_stats(container_id, max_stats):
#     while True:
#         try:
#             stats_output = (
#                 subprocess.check_output(
#                     [
#                         "docker",
#                         "stats",
#                         "--no-stream",
#                         "--format",
#                         "{{.CPUPerc}} {{.MemUsage}}",
#                         container_id,
#                     ]
#                 )
#                 .decode()
#                 .strip()
#             )
#             cpu_usage, memory_usage = stats_output.split(" ")
#             cpu_usage = float(cpu_usage.replace("%", ""))
#             memory_usage_value, _ = memory_usage.split("/")
#             memory_usage = float(
#                 memory_usage_value.replace("MiB", "").replace("GiB", "").strip()
#             )

#             if container_id not in max_stats:
#                 max_stats[container_id] = {"cpu": 0, "memory": 0}
#             max_stats[container_id]["cpu"] = max(
#                 max_stats[container_id]["cpu"], cpu_usage
#             )
#             max_stats[container_id]["memory"] = max(
#                 max_stats[container_id]["memory"], memory_usage
#             )
#         except subprocess.CalledProcessError:
#             break  # Container stopped
#         time.sleep(1)  # Poll every second


# def kv_store_client(operation, key, port, value=None):
#     server_url = f"http://{HOST}:{port}"
#     # print(f"Operation: {operation}, Key: {key}, Port: {port}")

#     start_time = time.time()

#     try:
#         if operation == "set":
#             requests.put(
#                 f"{server_url}/store", params={"key": key}, data={"value": value}
#             )
#         elif operation == "get":
#             requests.get(f"{server_url}/retrieve", params={"key": key})
#         elif operation == "del":
#             requests.get(f"{server_url}/remove", params={"key": key})
#         else:
#             raise ValueError("Invalid operation")
#         return time.time() - start_time
#     except Exception as e:
#         print(f"Error performing {operation} on {key}: {e}")
#         return None


# def worker(num_operations, latencies_queue, process_index, max_stats):
#     container_id, port = start_docker_container(f"client_{process_index}")
#     time.sleep(5)
#     max_stats[container_id] = {"cpu": 0, "memory": 0}
#     monitor_thread = threading.Thread(
#         target=monitor_container_stats, args=(container_id, max_stats)
#     )
#     monitor_thread.start()

#     total_latency = 0
#     for operation in ["set", "get", "del"]:
#         for i in range(num_operations):
#             key = f"key_{process_index}_{operation}_{i}"
#             value = f"value_{process_index}_{i}" if operation == "set" else None
#             latency = kv_store_client(operation, key, port, value)
#             if latency is not None:
#                 latencies_queue.put(latency)
#                 total_latency += latency

#     monitor_thread.join()
#     # print(
#     #     f"Container {container_id} stats - CPU: {max_stats[container_id]['cpu']}%, Memory: {max_stats[container_id]['memory']}MiB"
#     # )
#     stop_docker_container_and_collect_stats(container_id, max_stats)
#     return total_latency / (num_operations * 3)  # Average latency


# def benchmark(num_operations, num_processes, max_stats):
#     latencies_queue = multiprocessing.Queue()
#     processes = []
#     for i in range(num_processes):
#         p = multiprocessing.Process(
#             target=worker, args=(num_operations, latencies_queue, i, max_stats)
#         )
#         processes.append(p)
#         p.start()

#     for p in processes:
#         p.join()

#     total_latency = 0
#     while not latencies_queue.empty():
#         total_latency += latencies_queue.get()

#     return total_latency / (
#         num_operations * num_processes * 3
#     )  # Overall average latency


# if __name__ == "__main__":
#     # print("Hello")
#     num_operations = 2  # Adjust as needed
#     num_processes = 5  # Adjust as needed
#     max_stats = multiprocessing.Manager().dict()

#     avg_latency = benchmark(num_operations, num_processes, max_stats)
#     print(f"Average Latency: {avg_latency:.5f} seconds")


# Single threaded approach

import requests
import time
import subprocess
import threading
import random
import string

HOST, PORT = "127.0.0.1", 80
BASE_URL = f"http://{HOST}:{PORT}"
NUM_CLIENTS = 10  # Number of clients


combinations = [
    "RI",
    "WI",
    "B",
]  # for each case, have varied sizes of keys/values to have large/small keys/values

writeOps = ["Put", "Delete"]


def generate_random_string(length, seed=None):
    random.seed(seed)
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def start_docker_container(client_id):
    # command = f"docker run -d -p {PORT} docker-kv-store"
    container_name = f"client_container_{client_id}"
    command = f"docker run -d --name {container_name} -p 8070:{PORT} docker-kv-store"
    subprocess.run(command, shell=True)
    return container_name


def monitor_container_stats(container_name, max_stats):
    while True:
        try:
            stats_output = (
                subprocess.check_output(
                    f"docker stats --no-stream --format '{{{{.CPUPerc}}}} {{{{.MemUsage}}}}' {container_name}",
                    shell=True,
                )
                .decode()
                .strip()
            )

            # Split the stats output
            cpu_usage_str, memory_usage_str = stats_output.split(" ")
            cpu_usage = float(cpu_usage_str.replace("%", ""))

            # Extract actual memory usage (before the slash)
            memory_usage_value = (
                memory_usage_str.split("/")[0].replace("MiB", "").strip()
            )
            memory_usage = float(memory_usage_value)

            # Update max stats
            max_stats[container_name] = {
                "cpu": max(max_stats.get(container_name, {}).get("cpu", 0), cpu_usage),
                "memory": max(
                    max_stats.get(container_name, {}).get("memory", 0), memory_usage
                ),
            }
        except subprocess.CalledProcessError:
            break  # Container stopped
        except ValueError as e:
            print(f"Error parsing stats: {e}")
        time.sleep(1)  # Poll every second


def stop_docker_container_and_collect_stats(container_name):
    subprocess.run(f"docker stop {container_name}", shell=True)
    subprocess.run(f"docker rm {container_name}", shell=True)


def client_ops(client_id, max_stats):
    container_name = start_docker_container(client_id)
    stats_thread = threading.Thread(
        target=monitor_container_stats, args=(container_name, max_stats)
    )
    stats_thread.start()

    combination = random.choice(combinations)

    NUM_REQUESTS = random.randint(1, 100)  # Can increase this to max

    NUM_WRITE_REQUESTS = 0
    NUM_READ_REQUESTS = 0

    if combination == "RI":
        NUM_READ_REQUESTS = round((NUM_REQUESTS * 0.9))
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS

    elif combination == "WI":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.1)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS

    elif combination == "B":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.5)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS

    for i in range(NUM_WRITE_REQUESTS):
        seed = f"key-{client_id}-{i}"
        key = generate_random_string(
            random.randint(1, 100), seed
        )  # Can change this and increase the possible values
        # writeRequest = random.choice(writeOps)
        # print("Ops: ", writeRequest)
        # writeRequest = "PUT"

        # print("Check PUT:")

        # if writeRequest == "PUT":
        # print("write")
        value = generate_random_string(random.randint(1, 100))
        requests.put(f"{BASE_URL}/store", data={"key": key, "value": value})
        # else:
        #     print("delete")
        #     requests.delete(f"{BASE_URL}/remove", data={"key": key})

    for j in range(NUM_READ_REQUESTS):
        # print("CHECK Retrive")
        seed = f"key-{client_id}-{j}"
        key = generate_random_string(random.randint(1, 100), seed)
        requests.get(f"{BASE_URL}/retrieve", data={"key": key})

    stats_thread.join()
    stop_docker_container_and_collect_stats(container_name)

    cpu_usage, memory_usage = max_stats[container_name].values()

    print("Cpu usage: ", cpu_usage, "Memory_usage: ", memory_usage)

    metrics = {
        "num_reads": NUM_READ_REQUESTS,
        "num_writes": NUM_WRITE_REQUESTS,
        "read_write_ratio": NUM_READ_REQUESTS / NUM_WRITE_REQUESTS,
        "cpu_usage": cpu_usage,
        "max_memory_used": memory_usage,
    }

    METRICS_URL = f"http://{HOST}:{90}"
    response = requests.post(f"{METRICS_URL}/metrics", json=metrics)
    if response.status_code == 201:
        print(f"Client-{client_id} | Metrics successfully sent to the server.")
    else:
        print(f"Client-{client_id} | Failed to send metrics to server: {response.text}")


def run_clients():
    max_stats = {}
    for client_id in range(NUM_CLIENTS):
        client_ops(client_id, max_stats)


if __name__ == "__main__":
    run_clients()
