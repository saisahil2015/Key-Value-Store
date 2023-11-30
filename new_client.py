# import requests
# import time
# import subprocess
# import threading
# import random
# import string
# import docker

# HOST = "127.0.0.1"
# PORT = 80
# BASE_URL = f"http://{HOST}:{PORT}"
# NUM_CLIENTS = 10
# combinations = ["RI", "WI", "B"]

# # Use the Docker Python client for better container management
# docker_client = docker.from_env()


# def generate_random_string(length, seed=None):
#     random.seed(seed)
#     return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# def start_docker_container(client_id):
#     container_name = f"client_container_{client_id}"
#     container = docker_client.containers.run(
#         "docker-kv-store",
#         detach=True,
#         name=container_name,
#         ports={"80/tcp": PORT},
#         auto_remove=True,
#     )
#     return container


# def monitor_container_stats(container, max_stats):
#     while True:
#         try:
#             stats = container.stats(stream=False)
#             cpu_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
#             memory_usage = stats["memory_stats"]["usage"]
#             max_stats[container.id] = {"cpu": cpu_usage, "memory": memory_usage}
#         except docker.errors.NotFound:
#             break
#         time.sleep(1)


# def wait_container_created(container):
#     while True:
#         container.reload()
#         if container.status == "running":
#             print("container is running")
#             break
#         time.sleep(1)


# def client_ops(client_id, max_stats):
#     container = start_docker_container(client_id)
#     wait_container_created(container)

#     stats_thread = threading.Thread(
#         target=monitor_container_stats, args=(container, max_stats)
#     )
#     stats_thread.start()

#     combination = random.choice(combinations)
#     NUM_REQUESTS = random.randint(1, 100)
#     NUM_WRITE_REQUESTS, NUM_READ_REQUESTS = 0, 0

#     if combination == "RI":
#         NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.9)
#         NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
#     elif combination == "WI":
#         NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.1)
#         NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
#     elif combination == "B":
#         NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.5)
#         NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS

#     for i in range(NUM_WRITE_REQUESTS):
#         key, value = generate_random_string(
#             10, f"key-{client_id}-{i}"
#         ), generate_random_string(10)
#         requests.put(f"{BASE_URL}/store", data={"key": key, "value": value})
#     for j in range(NUM_READ_REQUESTS):
#         key = generate_random_string(10, f"key-{client_id}-{j}")
#         requests.get(f"{BASE_URL}/retrieve", data={"key": key})

#     stats_thread.join()
#     container.stop()

#     cpu_usage, memory_usage = max_stats[container.id].values()
#     print(f"Client-{client_id} CPU Usage: {cpu_usage}, Memory Usage: {memory_usage}")

#     METRICS_URL = f"http://{HOST}:90"

#     # Send metrics to server
#     metrics = {
#         "num_reads": NUM_READ_REQUESTS,
#         "num_writes": NUM_WRITE_REQUESTS,
#         "cpu_usage": cpu_usage,
#         "memory_used": memory_usage,
#     }
#     response = requests.post(f"{METRICS_URL}/metrics", json=metrics)
#     if response.status_code != 201:
#         print(f"Client-{client_id} Error sending metrics: {response.text}")


# def run_clients():
#     max_stats = {}
#     for client_id in range(NUM_CLIENTS):
#         client_ops(client_id, max_stats)


# if __name__ == "__main__":
#     run_clients()


import requests
import time
import threading
import random
import string
import docker

HOST = "127.0.0.1"
NUM_CLIENTS = 500
combinations = ["RI", "WI", "B"]
docker_client = docker.from_env()

# Define a range of available ports
available_ports = [port for port in range(8070, 9070)]
servers = {}  # Mapping of container ID to URL


def generate_random_string(length, seed=None):
    random.seed(seed)
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def start_docker_container(client_id):
    container_name = f"client_container_{client_id}"

    if available_ports:
        port = available_ports.pop(0)
    else:
        raise Exception("No available ports left")

    container = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        name=container_name,
        ports={"80/tcp": port},
        auto_remove=True,
    )
    servers[container.id] = f"http://{HOST}:{port}"
    return container


# def monitor_container_stats(container, max_stats, stop_thread):
#     while True:
#         if stop_thread.is_set():
#             # print("Stopping monitoring thread for container", container.id)
#             break
#         try:
#             stats = container.stats(stream=False)
#             cpu_percent = 0.0
#             cpu_delta = float(stats["cpu_stats"]["cpu_usage"]["total_usage"]) - float(
#                 stats["precpu_stats"]["cpu_usage"]["total_usage"]
#             )
#             system_delta = float(stats["cpu_stats"]["system_cpu_usage"]) - float(
#                 stats["precpu_stats"]["system_cpu_usage"]
#             )
#             if system_delta > 0.0:
#                 cpu_percent = cpu_delta / system_delta * 100.0
#             # cpu_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
#             # memory_usage = stats["memory_stats"]["usage"]
#             memory_stats = stats["memory_stats"]["usage"]
#             memory_stats_mb = memory_stats / (1024 * 1024)
#             max_stats[container.id] = {"cpu": cpu_percent, "memory": memory_stats_mb}
#         except docker.errors.NotFound:
#             print("Container not found, stopping monitoring thread", container.id)
#             break
#         except Exception as e:
#             print("Exception in monitoring thread for container", container.id, ":", e)
#             break
#         time.sleep(0.02)


def monitor_container_stats(container, max_stats, stop_thread):
    max_cpu = 0
    max_memory = 0
    while True:
        if stop_thread.is_set():
            # print("Stopping monitoring thread for container", container.id)
            break
        try:
            stats = container.stats(stream=False)
            cpu_delta = float(stats["cpu_stats"]["cpu_usage"]["total_usage"]) - float(
                stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = float(stats["cpu_stats"]["system_cpu_usage"]) - float(
                stats["precpu_stats"]["system_cpu_usage"]
            )
            if system_delta > 0.0:
                cpu_percent = cpu_delta / system_delta * 100.0
                max_cpu = max(max_cpu, cpu_percent)
            memory_usage = stats["memory_stats"]["usage"] / (
                1024 * 1024
            )  # Convert to MB
            max_memory = max(max_memory, memory_usage)
        except docker.errors.NotFound:
            print("Container not found, stopping monitoring thread", container.id)
            break
        except Exception as e:
            print("Exception in monitoring thread for container", container.id, ":", e)
            break
        time.sleep(0.02)

    max_stats[container.id] = {"cpu": max_cpu, "memory": max_memory}


# NOTE
"""
noticed that just before the container ends the cpu usage peaks but i think we shouldn't capture that as it's more to do due to the shutdown of the container
and not representative of the workload

can add more metrics after first iteration of testing

"""


def wait_container_created(container):
    while True:
        container.reload()
        if container.status == "running":
            # print("container is running")
            break
        time.sleep(1)


def client_ops(client_id, max_stats):
    container = start_docker_container(client_id)
    # wait_container_created(container)

    stop_thread = threading.Event()
    stats_thread = threading.Thread(
        target=monitor_container_stats, args=(container, max_stats, stop_thread)
    )
    stats_thread.start()

    server_url = servers[container.id]
    # print("Server url: ", server_url)
    combination = random.choice(combinations)
    NUM_REQUESTS = random.randint(150, 10000)
    NUM_WRITE_REQUESTS, NUM_READ_REQUESTS = 0, 0

    if combination == "RI":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.9)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
    elif combination == "WI":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.1)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
    elif combination == "B":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.5)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS

    time.sleep(5)  # helped resolved errors

    written_keys = []
    written_values = []

    for i in range(NUM_WRITE_REQUESTS):
        seed = f"key-{client_id}-{i}"
        key = generate_random_string(random.randint(1, 250), seed)
        value = generate_random_string(random.randint(1, 250))
        # print(f"Put checkpoint - Server URL: {server_url}, Key: {key}, Value: {value}")
        try:
            response = requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
            # print(f"PUT response: {response.status_code}, {response.text}")
            written_keys.append(key)
            written_values.append(value)
        except Exception as e:
            print(f"Error during PUT request: {e}")

    FOUND_REQUESTS = random.randint(0, NUM_WRITE_REQUESTS)
    NOTFOUND_REQUESTS = NUM_WRITE_REQUESTS - FOUND_REQUESTS

    for j in range(len(written_keys[:FOUND_REQUESTS])):
        # print(f"Get checkpoint - Server URL: {server_url}, Key: {written_keys[j]}")
        try:
            response = requests.get(
                f"{server_url}/retrieve", params={"key": written_keys[j]}
            )
            # print(f"GET response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error during GET request: {e}")

    for _ in range(NOTFOUND_REQUESTS):
        key = generate_random_string(random.randint(1, 250))
        # print(f"Get checkpoint - Server URL: {server_url}, Key: {key}")
        try:
            response = requests.get(f"{server_url}/retrieve", params={"key": key})
            # print(f"GET response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error during GET request: {e}")

    # print("Checkpoint")
    try:
        # print("Joining stats checkpoint")
        stop_thread.set()
        stats_thread.join()
    except Exception as e:
        print(f"Error joinging the stats thread: {e}")
    try:
        # print("Stopping container checkpoint")
        container.stop()
    except Exception as e:
        print(f"Error stopping the container: {e}")

    # print("Container stopped")

    max_cpu_usage, max_memory_usage = max_stats[container.id].values()
    # print(
    #     f"Client-{client_id} Num Read: {NUM_READ_REQUESTS} Num Write {NUM_WRITE_REQUESTS} Read-Write-Ratio: {NUM_READ_REQUESTS/NUM_WRITE_REQUESTS} Max CPU Usage: {max_cpu_usage}, Max Memory Usage: {max_memory_usage}"
    # )

    # calculate mean, std, var of key and value size
    mean_key_size, mean_value_size, std_key_size, std_value_size, var_key_size, var_value_size = 0, 0, 0, 0, 0, 0

    if len(written_keys) > 0:
        mean_key_size = sum([len(key) for key in written_keys]) / len(written_keys)
        mean_value_size = sum([len(value) for value in written_values]) / len(
            written_values
        )
        std_key_size = (
            sum([(len(key) - mean_key_size) ** 2 for key in written_keys])
            / len(written_keys)
        ) ** 0.5
        std_value_size = (
            sum([(len(value) - mean_value_size) ** 2 for value in written_values])
            / len(written_values)
        ) ** 0.5
        var_key_size = std_key_size ** 2
        var_value_size = std_value_size ** 2


    METRICS_URL = f"http://{HOST}:90"
    metrics = {
        "num_reads": NUM_READ_REQUESTS,
        "num_writes": NUM_WRITE_REQUESTS,
        "read_write_ratio": NUM_READ_REQUESTS / NUM_WRITE_REQUESTS,
        "mean_key_size": mean_key_size,
        "mean_value_size": mean_value_size,
        # "std_key_size": std_key_size,
        # "std_value_size": std_value_size,
        # "var_key_size": var_key_size,
        # "var_value_size": var_value_size,
        "max_cpu_usage": max_cpu_usage,
        "max_memory_usage": max_memory_usage,
    }
    response = requests.post(f"{METRICS_URL}/metrics", json=metrics)
    if response.status_code != 201:
        print(f"Client-{client_id} Error sending metrics: {response.text}")


def run_clients():
    max_stats = {}
    for client_id in range(NUM_CLIENTS):
        client_ops(client_id, max_stats)


if __name__ == "__main__":
    run_clients()


# curl -X PUT http://127.0.0.1:8070/store -d "key=myKey&value=myValue"
