import requests
import random
import subprocess
import docker
from hashring import HashRing
import time
import joblib
import string
import statistics
import csv
import threading

from hash_ring import MyHashRing

# globals
HOST = "localhost"
combinaitons = ["RI", "WI", "B"]

available_ports = [port for port in range(8080, 9080)]
servers = {}  # container_id: url
available_servers = []  # url
ring = HashRing(available_servers)  # hash ring

# docker client
docker_client = docker.from_env()

transition = False
total_containers = 0


combined_threshold = 18.53
cpu_weight = 0.7
memory_weight = 0.3

AVG_CPU_USAGES = []
AVG_MEMORY_USAGES = []


key_lengths = []
value_lengths = []

num_reads_list = []
num_writes_list = []
# start = False


lock = threading.Lock()

monitoring_active = True

hashring = None
hashring_config = {}
vnode_factor = 2


def launch_new_container():
    # time.sleep(2)
    # TRY REMOVING START
    # global start
    # if start:
    #     time.sleep(2)
    global total_containers
    total_containers += 1
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
        mem_limit="15m",  # 10m #15m
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
    # print(container_id)

    servers[container_id] = url
    available_servers.append(url)
    # print(f"Avaliable servers: {available_servers}")

    # update new hash ring, TODO: need lock mechinaism
    global ring
    ring = HashRing(available_servers)

    # TODO: redistribute the key value pairs among the new hash ring

def start_containers(n):
    '''
        starting up with n containers, initialize the hash ring
    '''
    global hashring, hashring_config

    # launch containers
    for _ in range(n):
        current_port = available_ports.pop(0)
        container = docker_client.containers.run(
            "docker-kv-store",
            detach=True,
            ports={"80/tcp": current_port},
            # mem_limit="15m",  # 10m #15m
        )

        hashring_config[container.name] = {
            "port": current_port,
            "vnodes": vnode_factor,
        }

    # initialize the hash ring
    with lock:
        hashring = MyHashRing(hashring_config)

def redistribute_key_value_pairs(old_nodes):
    '''
        redistribute the key value pairs among the new hash ring
    '''
    global hashring, hashring_config

    # get all key value pairs from the old hash ring
    key_value_pairs = []
    for node in old_nodes:

def add_new_container():
    '''
        add a new container to the hash ring
    '''
    global hashring, hashring_config

    # launch new container
    current_port = available_ports.pop(0)
    container = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        ports={"80/tcp": current_port},
        # mem_limit="15m",  # 10m #15m
    )

    with lock:
        # update the hash ring
        hashring_config[container.name] = {
            "port": current_port,
            "vnodes": vnode_factor,
        }
        hashring.add_node(container.name, {"port": current_port, "vnodes": vnode_factor})

        # get the next nodes of every new virtual nodes

        # redistribute the key value pairs among the new hash ring
        new_virtual_nodes = hashring.get_all_virtual_nodes(container.name)
        old_nodes = []
        for nvn_i in new_virtual_nodes:
            old_nodes.append(hashring.get_node_by_index(nvn_i))
        redistribute_key_value_pairs(old_nodes)

# TODO: need one that remove just one container (remove container when finish hadnling workload)
def remove_all_containers():
    print("terminate and remove all containers...")
    for docker_id, _ in servers.items():
        stop_command = f"docker stop {docker_id}"
        rm_command = f"docker remove {docker_id}"
        subprocess.run(stop_command.split())
        subprocess.run(rm_command.split())


def get_resource_usage_prediction(
    num_read,
    num_write,
    rw_ratio,
    mean_key_size,
    mean_value_size,
    std_key_size,
    std_value_size,
    var_key_size,
    var_value_size,
):
    model = joblib.load("models/lin_reg_best.joblib")  # change model file here
    prediction = model.predict(
        [
            [
                num_read,
                num_write,
                rw_ratio,
                mean_key_size,
                mean_value_size,
                std_key_size,
                std_value_size,
                var_key_size,
                var_value_size,
            ]
        ]
    )
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
        cpu_percent = (
            cpu_delta / system_delta * 100.0
        )  # maybe multiply by 8 cores but didn't help improve the performance

    memory_usage = stats["memory_stats"]["usage"] / (1024 * 1024)  # Convert to MB

    memory_limt = stats["memory_stats"]["limit"] / (1024 * 1024)

    return cpu_percent, memory_usage, memory_limt


def monitor_containers():
    # print("Monitor Check")
    global monitoring_active

    if not monitoring_active:
        return

    else:
        threading.Timer(2, monitor_containers).start()

    # print("Are we monitoring?")

    # threading.Timer(2, monitor_containers).start()
    # if key_lengths and value_lengths:
    # print("Key lengths: ", key_lengths)
    # print("Value lengths: ", value_lengths)
    # print("Num Reads: ", num_reads_list)
    # print("Num Writes: ", num_writes_list)

    if not (key_lengths and value_lengths and num_reads_list and num_writes_list):
        # print("Not check")
        return
    # print("Are we here?")

    if len(key_lengths) > 2:
        # print("Length check")
        mean_key_length = statistics.mean(key_lengths)
        std_key_length = statistics.stdev(key_lengths)
        var_key_length = statistics.variance(key_lengths)

        mean_value_length = statistics.mean(value_lengths)
        std_value_length = statistics.stdev(value_lengths)
        var_value_length = statistics.variance(value_lengths)

        # Calculate statistics for reads and writes
        mean_reads = statistics.mean(
            num_reads_list
        )  # though in model only tested with certain reads and writes
        mean_writes = statistics.mean(num_writes_list)

        # Use these statistics in your model
        required_cpu, required_memory = get_resource_usage_prediction(
            mean_reads,
            mean_writes,
            mean_reads / mean_writes,
            mean_key_length,
            mean_value_length,
            std_key_length,
            std_value_length,
            var_key_length,
            var_value_length,
        )

        # print("Required cpu: ", required_cpu)
        # print("Required memory: ", required_memory)

        # Reset the lists for the next interval
        # with lock:
        # print("Locking check")
        key_lengths.clear()
        value_lengths.clear()
        num_reads_list.clear()
        num_writes_list.clear()

        containers = docker_client.containers.list()

        total_cpu_usage, total_memory_usage = 0, 0
        total_memory_limit = 0
        for container in containers:
            stats = container.stats(stream=False)
            cpu_usage, memory_usage, memory_limit = get_cpu_memory_usage(stats)
            total_cpu_usage += cpu_usage
            total_memory_usage += memory_usage
            total_memory_limit += memory_limit

        avg_cpu_usage = total_cpu_usage / len(containers) if containers else 0
        avg_memory_usage = total_memory_usage / len(containers) if containers else 0

        AVG_CPU_USAGES.append(avg_cpu_usage)
        AVG_MEMORY_USAGES.append(avg_memory_usage)

        with open("autoscaling_logs.txt", "a") as f:
            f.write(
                f"Autoscale checkpint combined_memory_usage: {required_memory + avg_memory_usage } combined_cpu_usage: {required_cpu + avg_cpu_usage}\n"
            )

        if (
            required_memory + avg_memory_usage > 15
            and required_cpu + avg_cpu_usage > 1.8
        ):
            return True

        # curr_weighted_utilization = (cpu_weight * avg_cpu_usage) + (
        #     memory_weight * avg_memory_usage
        # )

        # req_weighted_utilization = (cpu_weight * required_cpu) + (
        #     memory_weight * required_memory
        # )

        # print("Current weighted cpu average: ", cpu_weight * avg_cpu_usage)
        # print("Current weighted memory average: ", memory_weight * avg_memory_usage)
        # print("Current Weighted utilization: ", curr_weighted_utilization)
        # print("Required weighted cpu average: ", cpu_weight * required_cpu)
        # print("Required weighted memory average: ", memory_weight * required_memory)
        # print("Required Weighted utilization: ", req_weighted_utilization)
        # print(
        #     "Combined Weighted utilization: ",
        #     curr_weighted_utilization + req_weighted_utilization,
        # )

        # if curr_weighted_utilization + req_weighted_utilization > combined_threshold:
        #     return True

    return False


def client_ops(client_id, workload):
    global hashring

    num_write, num_read, rw_ratio = workload

    with lock:
        num_reads_list.append(num_read)
        num_writes_list.append(num_write)
    written_keys = []
    operation_times = []
    need_new_container = False
    errors = 0
    successes = 0

    # predict the container cpu and memory usage
    # launch new container if needed
    global transition
    # if no_space_in_container(num_write, num_read, rw_ratio):
    # if monitoring_thread(num_write, num_read, rw_ratio):
    with lock:
        need_new_container = monitor_containers()

    if need_new_container:
        launch_new_container()
        with lock:
            transition = True

    for i in range(num_write):
        with lock:
            if transition:
                time.sleep(5)  # 0.5
                transition = False
        # print("Transition Put check: ", transition)
        key = f"key-{client_id}-{i}"  # NEED TO ADD RANDOMNESS IN KEY GENERATION AND VALUE GENERATION
        value = f"value-{client_id}-{i}"

        with lock:
            key_lengths.append(len(key))
            value_lengths.append(len(value))

        # server_url = ring.get_node(key)
        node_obj = hashring.get(key)
        replicas = hashring.get_replicas(node_obj['nodename'])
        port = node_obj['port']

        server_urls = [f"http://{HOST}:{port}"]
        for rep in replicas:
            server_urls.append(f"http://{HOST}:{rep['port']}")

        # print(f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}")

        # with open("autoscaling_logs.txt", "a") as f:
        #     f.write(
        #         f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}\n"
        #     )

        start_time = time.time()

        try:
            for server_url in server_urls:
                response = requests.put(
                    f"{server_url}/store", params={"key": key}, data={"value": value}
                )
                # print(f"PUT response: {response.status_code}, {response.text}")
                # with open("autoscaling_logs.txt", "a") as f:
                #     f.write(f"PUT response: {response.status_code}, {response.text}\n")
                if response.status_code == 404:
                    errors += 1
                    # print("**" * 68)
                    # print("Put Error")
                    # break
                else:
                    successes += 1
                    break

            written_keys.append(key)

        except Exception as e:
            errors += 1
            # launch_new_container()
            # print(f"Error during PUT request: {e}")

        operation_time = time.time() - start_time
        operation_times.append(operation_time)

    for j in range(num_read):
        if not written_keys:  # Check if there are keys to read
            break

        with lock:
            if transition:
                time.sleep(5)  # 0.5 #MAYBE HAVE IT NONBLOCKING
                transition = False
        # print("Transition Get check: ", transition)
        random_key_index = random.randint(0, len(written_keys) - 1)
        key = written_keys[random_key_index]

        # server_url = ring.get_node(key)
        port = hashring.get_node_port(key)
        server_url = f"http://{HOST}:{port}"

        # print(f"Get checkpoint - Server URL: {server_url}, Key: {key}")
        # with open("autoscaling_logs.txt", "a") as f:
        #     f.write(f"Get checkpoint - Server URL: {server_url}, Key: {key}\n")

        start_time = time.time()

        try:
            response = requests.get(f"{server_url}/retrieve", params={"key": key})
            # print(f"GET response: {response.status_code}, {response.text}")
            # with open("autoscaling_logs.txt", "a") as f:
            #     f.write(f"GET response: {response.status_code}, {response.text}\n")
            if response.status_code == 404:
                errors += 1
                # print("**" * 68)
                # print("Get Error")
                # break
            else:
                successes += 1
        except Exception as e:
            errors += 1
            # print(f"Error during GET request: {e}")
            # launch_new_container()

        operation_time = time.time() - start_time
        operation_times.append(operation_time)

    return errors, successes, operation_times


# def client_thread(client_id, workload, result_lists):
def client_thread(client_id, workload):
    print(f"Starting client thread {client_id}")
    errors, successes, operation_times = client_ops(client_id, workload)
    # print("Opertaions times: ", operation_times)

    # with lock:
    #     result_lists["errors"].append(errors)
    #     result_lists["successes"].append(successes)
    #     result_lists["operation_times"].append(
    #         operation_times
    #     )  # Collect all operation times
    # print(f"Client {client_id} Errors: ", result_lists["errors"])
    # print(f"Client {client_id} Successes: ", result_lists["successes"])
    # print(f"Client {client_id} Operation Times: ", result_lists["operation_times"])
    # print(f"Finished client thread {client_id}")


def run_clients():
    # run one container
    global monitoring_active

    # LAUNCHING TWO CONTAINRES AT BEGNINNG MADE NO DIFFERENCE
    # global start
    threads = []
    # result_lists = {
    #     "errors": [],
    #     "successes": [],
    #     "operation_times": [],
    # }
    # start = True
    launch_new_container()
    # start = False
    # launch_new_container()
    monitor_containers()

    # monitoring_thread = threading.Thread(target=monitor_key_values)
    # monitoring_thread.start()
    # launch_new_container()

    # print("Check")

    # time.sleep(5)

    # read workload from file

    # Worked well with workload.txt
    with open("new_workload.txt", "r") as f:
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
        # workload = [
        #     (
        #         int(n_write * 10),
        #         int(n_read * 10),
        #         float(int(n_write * 10) / int(n_write * 10)),
        #     )
        #     for n_write, n_read, rw_ratio in workload
        # ]

    for client_id, wl in enumerate(workload):
        thread = threading.Thread(
            # target=client_thread, args=(client_id, wl, result_lists)
            target=client_thread, args=(client_id, wl)
        )
        threads.append(thread)
        # print(f"Starting thread for client {client_id}")
        thread.start()

    for thread in threads:
        thread.join()

    # throughputs = [
    #     successes / sum(operation_times) if operation_times else 0
    #     for successes, operation_times in zip(
    #         result_lists["successes"], result_lists["operation_times"]
    #     )
    # ]
    # latencies = [
    #     statistics.mean(operation_times) if operation_times else float("inf")
    #     for operation_times in result_lists["operation_times"]
    # ]
    # error_rates = [
    #     e / (r + w) if r + w > 0 else 0
    #     for e, r, w in zip(
    #         result_lists["errors"], [w[0] for w in workload], [w[1] for w in workload]
    #     )
    # ]

    monitoring_active = False
    # might remove the transition time or reduce it
    # remove all containers
    remove_all_containers()
    # monitoring_thread.join()

    print("Done")

if __name__ == "__main__":
    run_clients()