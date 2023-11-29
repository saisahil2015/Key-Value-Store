import requests
import random
import subprocess
import docker
from hashring import HashRing
import time
import joblib
import string

# globals
HOST = "localhost"
combinaitons = ["RI", "WI", "B"]
NUM_CLIENTS = 10
NUM_REQUESTS = 100

available_ports = [port for port in range(8080, 9080)]
servers = {}  # container_id: url
available_servers = []  # url
ring = HashRing(available_servers)  # hash ring

# docker client
docker_client = docker.from_env()

transition = False


def launch_new_container():
    print("New container launched")
    current_port = available_ports.pop(0)
    url = f"http://{HOST}:{current_port}"

    # container = docker_client.containers.run(
    #     "docker-kv-store", detach=True, ports={80: current_port}
    # )

    # container = docker_client.containers.run(
    #     "docker-kv-store",
    #     detach=True,
    #     ports={"80/tcp": current_port},
    #     mem_limit="6m",
    #     cpu_shares=10,
    # )

    container = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        ports={"80/tcp": current_port},
        mem_limit="15m",  # 10m
        auto_remove=True,
    )
    # container = docker_client.containers.run(
    #     "docker-kv-store",
    #     detach=True,
    #     ports={"80/tcp": current_port},
    #     mem_limit="15m",  # 10m
    # )
    # removed auto_remove but try with auto_remove and see how it goes

    # time.sleep(3)

    container_id = container.id
    print(container_id)

    servers[container_id] = url
    available_servers.append(url)
    print(f"Avaliable servers: {available_servers}")

    # update new hash ring, TODO: need lock mechinaism
    global ring
    ring = HashRing(available_servers)

    # TODO: redistribute the key value pairs among the new hash ring


# TODO: need one that remove just one container (remove container when finish hadnling workload)
def remove_all_containers():
    print("terminate and remove all containers...")
    for docker_id, _ in servers.items():
        stop_command = f"docker stop {docker_id}"
        rm_command = f"docker remove {docker_id}"
        subprocess.run(stop_command.split())
        subprocess.run(rm_command.split())


def get_resource_usage_prediction(num_read, num_write, rw_ratio):
    model = joblib.load("models/lin_reg.joblib")  # change model file here
    prediction = model.predict([[num_read, num_write, rw_ratio]])
    pred_cpu, pred_memory = prediction[0][0], prediction[0][1]
    return pred_cpu, pred_memory


def get_cpu_memory_usage(stats):
    cpu_delta = float(stats["cpu_stats"]["cpu_usage"]["total_usage"]) - float(
        stats["precpu_stats"]["cpu_usage"]["total_usage"]
    )
    system_delta = float(stats["cpu_stats"]["system_cpu_usage"]) - float(
        stats["precpu_stats"]["system_cpu_usage"]
    )
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0

    memory_usage = stats["memory_stats"]["usage"] / (1024 * 1024)  # Convert to MB

    memory_limt = stats["memory_stats"]["limit"] / (1024 * 1024)

    return cpu_percent, memory_usage, memory_limt


def no_space_in_container(num_write, num_read, rw_ratio):
    # List all running containers
    containers = docker_client.containers.list()

    # print("Contaienrs: ", containers)

    required_cpu, required_memory = get_resource_usage_prediction(
        num_read, num_write, rw_ratio
    )
    print("required cpu: {:.2f}".format(required_cpu))
    print("required memory: {:.2f}".format(required_memory))

    # Extract and print the names of running containers
    for container in containers:
        # print("Check")
        print("Container Name:", container.name)
        stats = container.stats(stream=False)

        cpu_usage, memory_usage, memory_limit = get_cpu_memory_usage(stats)
        print("cpu usage: {:.2f}".format(cpu_usage))
        print("memory usage: {:.2f}".format(memory_usage))
        print("memory limit: {:.2f}".format(memory_limit))

        # FIX LATER
        if (cpu_usage + required_cpu <= 100) and (
            memory_usage + required_memory <= memory_limit
        ):
            print("There is space to work on task")
            print()
            return False
        print()

    print("Unable to handle workload, launch the new container!!")
    return True


def client_ops(client_id, workload):
    num_write, num_read, rw_ratio = workload
    written_keys = []

    # predict the container cpu and memory usage
    # launch new container if needed
    global transition
    if no_space_in_container(num_write, num_read, rw_ratio):
        launch_new_container()
        transition = True
        # print("Transition: ", transition)

    for i in range(num_write):
        if transition:
            time.sleep(5)
            transition = False
        # print("Transition Put check: ", transition)
        key = f"key-{client_id}-{i}"  # NEED TO ADD RANDOMNESS IN KEY GENERATION AND VALUE GENERATION
        value = f"value-{client_id}-{i}"

        # seed = f"key-{client_id}-{i}"
        # key = generate_random_string(random.randint(1, 100), seed)
        # value = generate_random_string(random.randint(1, 100))

        server_url = ring.get_node(key)

        print(f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}")

        try:
            response = requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
            print(f"PUT response: {response.status_code}, {response.text}")
            if response.status_code == 404:
                print("**" * 68)
                print("Put Error")
                break
            written_keys.append(key)
        except Exception as e:
            print(f"Error during PUT request: {e}")

    for j in range(num_read):
        if transition:
            time.sleep(5)
            transition = False
        # print("Transition Get check: ", transition)
        random_key_index = random.randint(0, len(written_keys) - 1)
        key = written_keys[random_key_index]

        server_url = ring.get_node(key)

        print(f"Get checkpoint - Server URL: {server_url}, Key: {key}")
        try:
            response = requests.get(f"{server_url}/retrieve", params={"key": key})
            print(f"GET response: {response.status_code}, {response.text}")
            if response.status_code == 404:
                print("**" * 68)
                print("Get Error")
                break
        except Exception as e:
            print(f"Error during GET request: {e}")


if __name__ == "__main__":
    # run one container
    launch_new_container()

    # print("Check")

    # time.sleep(5)

    # read workload from file
    with open("workload.txt", "r") as f:
        workload = f.readlines()
        workload = [line.strip().split(" ") for line in workload]
        workload = [
            (
                int(n_write),
                int(n_read),
                float(rw_ratio),
            )
            for n_write, n_read, rw_ratio in workload
        ]

    # throughputs = []
    # latencies = []

    for client_id in range(len(workload)):
        # print("Workload: ", workload)
        # print("Workload check: ", workload[client_id])
        # num_reads, num_writes, read_write_ratio = workload[client_id]
        # print("Num reads: ", num_reads)
        # print("Num writes: ", num_writes)
        # print("Num read_write_ratio: ", read_write_ratio)
        print("***" * 68)
        print("This is a new workload")

        # with open("autoscaling_logs.txt", "w") as f:
        #     f.write(f"This is a new workload that has the following num_read:\n")
        # print("Workload: ", workload, len(workload))
        # break
        # start = time.time()
        client_ops(client_id, workload[client_id])
        # total_time = time.time() - start
        # throughput = NUM_OPS / total_time
        # latency = total_time / NUM_OPS
    # remove all containers
    remove_all_containers()
