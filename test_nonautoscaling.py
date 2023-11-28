import requests
import docker
import time
import random

NUM_CLIENTS = 20
NUM_REQUESTS = 100
HOST = "127.0.0.1"

docker_client = docker.from_env()
available_ports = [port for port in range(8080, 9070)]
servers = {}

def start_docker_container(client_id):
    container_name = f"non_auto_client-{client_id}"

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

def client_ops(client_id, container_id, workload):
    num_write, num_read, _rw_ratio = workload
    server_url = servers[container_id]
    written_keys = []

    for i in range(num_write):
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"

        try:
            response = requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
            # print(f"PUT response: {response.status_code}, {response.text}")
            written_keys.append(key)
        except Exception as e:
            print(f"Error during PUT request: {e}")

    for j in range(num_read):
        random_key_index = random.randint(0, len(written_keys) - 1)
        key = written_keys[random_key_index]
        # print(f"Get checkpoint - Server URL: {server_url}, Key: {written_keys[j]}")
        try:
            response = requests.get(
                f"{server_url}/retrieve", params={"key": key}
            )
            # print(f"GET response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error during GET request: {e}")

def run_clients():
    container = start_docker_container(0)
    time.sleep(2)

    # read workload from file
    with open("workload.txt", "r") as f:
        workload = f.readlines()
        workload = [line.strip().split(" ") for line in workload]
        workload = [(int(n_write), int(n_read), float(rw_ratio)) for n_write, n_read, rw_ratio in workload]

    for client_id in range(len(workload)):
        client_ops(client_id, container.id, workload[client_id])

    container.stop()

if __name__ == "__main__":
    run_clients()