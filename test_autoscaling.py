import requests
import random
import subprocess
import docker
import time
import joblib
import string
import statistics
import csv
import threading
from hash_ring import HashRing
# from hashring import HashRing


# globals
HOST = "localhost"
combinaitons = ["RI", "WI", "B"]

ring_lock = threading.Lock()    # lock for hash ring, servers, and available_ports
available_ports = [port for port in range(8080, 9080)]
ring = None
servers = {}  # container_name: port
vnode_factor = 5
replica_factor = 2
recovering = 0 # 0: before recovering, 1: recovering, 2: after recovering

# available_ports = [port for port in range(8080, 9080)]
# servers = {}  # container_id: url
# available_servers = []  # url
# ring = HashRing(available_servers)  # hash ring


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
health_check_active = True

def init_hash_ring():
    '''
        Initialize the hash ring with the 2 new containers
    '''
    global total_containers
    global ring

    total_containers += 2
    print("Initializing hash ring with 2 new containers")

    with ring_lock:
        current_port_1 = available_ports.pop(0)
        current_port_2 = available_ports.pop(0)

    container_1 = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        ports={"80/tcp": current_port_1},
        mem_limit="15m",  # 10m #15m
    )

    container_2 = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        ports={"80/tcp": current_port_2},
        mem_limit="15m",  # 10m #15m
    )

    with ring_lock:
        servers[container_1.name] = current_port_1
        servers[container_2.name] = current_port_2

        nodes = {
            container_1.name: {
                'port': current_port_1,
                'vnodes': vnode_factor,
            },
            container_2.name: {
                'port': current_port_2,
                'vnodes': vnode_factor,
            },
        }

        ring = HashRing(nodes, hash_fn='ketama', replicas=replica_factor)

    # start health check every 5 seconds
    health_check()

# add new node into the hash ring
def launch_new_container():

    # time.sleep(2)
    # TRY REMOVING START
    # global start
    # if start:
    #     time.sleep(2)
    global recovering
    global total_containers
    total_containers += 1

    while recovering == 1:
        print("waiting for recovery to finish")
        time.sleep(1)

    print("New container launched")

    with ring_lock:
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

    time.sleep(3)

    with ring_lock:
        servers[container.name] = current_port
        ring.add_node(container.name, {
            'port': current_port,
            'vnodes': vnode_factor,
        })

    # redistribute the keys next n nodes of the new node
    redistribute_keys(container.name)

def redistribute_keys(name):
    '''
        Redistribute the keys to the next n nodes of the given a node
            name: name of the node to redistribute keys from
    '''
    print("redistributing keys")

    all_kvs = []
    with ring_lock:
        for node_info in ring.get_next_n_nodes(name, replica_factor - 1):
            port = node_info['port']

            # get all keys and values from the node
            response = requests.get(f"http://{HOST}:{port}/get_all")
            if response.status_code == 200:
                all_kvs.append(response.json())

        for all_kv in all_kvs:
            for k, v in all_kv.items():
                for node in ring.range(k, replica_factor):
                    port = node['port']
                    response = requests.put(f"http://{HOST}:{port}/store", params={"key": k}, data={"value": v})    

        print("finished redistributing keys")

def health_check():
    '''
        health check for all containers every 5 seconds
    '''
    global recovering

    if not health_check_active:
        return
    else:
        threading.Timer(5, health_check).start()

    containers = docker_client.containers.list(all=True)
    for container in containers:
        with ring_lock:
            if container.name not in servers:
                continue

        name = container.name
        port = servers[name]
        if container.status == "paused" or container.status == "exited":
            # found a container that is down (pauseed or exited)
            print("found a container that is down (pauseed or exited)")

            with ring_lock:
                recovering = 1
                print("removing the node from hash ring")
                servers.pop(name)
                ring.remove_node(name)      # remove node from hash ring

            container.remove(force=True)    # remove container from docker
            
            # bring the cotnainer back up with same name and port
            print("bringing the container back up with same name and port")
            container = docker_client.containers.run(
                "docker-kv-store",
                detach=True,
                ports={"80/tcp": port},
                mem_limit="15m",  # 10m #15m
                name=name,
            )
            time.sleep(3)

            with ring_lock:
                # add the container back to the hash ring
                print("adding the node back to the hash ring")
                servers[name] = port
                ring.add_node(name, {
                    'port': port,
                    'vnodes': vnode_factor,
                })

            # redistrubute the keys next n nodes of the new node
            redistribute_keys(name)
            
            with ring_lock:
                recovering = 2

    print("health check done for all containers")

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
    model = joblib.load("newData_models/lin_reg_best.joblib")  # change model file here
    print(f"Check num_read: {num_read} num_write: {num_write}")
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
    print("Prediction Check: ", prediction)
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

        containers = docker_client.containers.list(all=True)

        total_cpu_usage, total_memory_usage = 0, 0
        total_memory_limit = 0
        for container in containers:
            if container.status != "running":
                continue
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
                f"Autoscale checkpint Required Memory: {required_memory} Avg Memory Usage: {avg_memory_usage} Required CPU: {required_cpu} Avg CPU Usage: {avg_cpu_usage} combined_memory_usage: {required_memory + avg_memory_usage } combined_cpu_usage: {required_cpu + avg_cpu_usage}\n"
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
    num_write, num_read, rw_ratio = workload

    with lock:
        num_reads_list.append(num_read)
        num_writes_list.append(num_write)
    written_keys = []
    operation_times = []

    operation_times_before_recover = []
    operation_times_during_recover = []
    operation_times_after_recover = []

    need_new_container = False
    errors = 0
    successes = 0

    errors_before_recover = 0
    successes_before_recover = 0
    errors_during_recover = 0
    successes_during_recover = 0
    errors_after_recover = 0
    successes_after_recover = 0

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

        # seed = f"key-{client_id}-{i}"
        # key = generate_random_string(random.randint(1, 100), seed)
        # value = generate_random_string(random.randint(1, 100))
        
        server_urls = []
        with ring_lock:
            for node in ring.range(key, replica_factor):
                port = node["port"]
                server_urls.append(f"http://{HOST}:{port}")

        # print(f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}")

        # with open("autoscaling_logs.txt", "a") as f:
        #     f.write(
        #         f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}\n"
        #     )

        start_time = time.time()

        try:
            success_count, error_count = 0, 0
            for server_url in server_urls:
                response = requests.put(
                    f"{server_url}/store", params={"key": key}, data={"value": value}
                )
                if response.status_code != 404:
                    success_count += 1

            if success_count == replica_factor:
                successes += 1
                written_keys.append(key)

                if recovering == 0:
                    successes_before_recover += 1
                elif recovering == 1:
                    successes_during_recover += 1
                else:
                    successes_after_recover += 1

        except Exception as e:
            errors += 1
            if recovering == 0:
                errors_before_recover += 1
            elif recovering == 1:
                errors_during_recover += 1
            else:
                errors_after_recover += 1

            # launch_new_container()
            # print(f"Error during PUT request: {e}")

        operation_time = time.time() - start_time
        operation_times.append(operation_time)

        if recovering == 0:
            operation_times_before_recover.append(operation_time)
        elif recovering == 1:
            operation_times_during_recover.append(operation_time)
        else:
            operation_times_after_recover.append(operation_time)

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

        with lock:
            node = ring.get(key)    
        server_url = f"http://{HOST}:{node['port']}"

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
                if recovering == 0:
                    errors_before_recover += 1
                elif recovering == 1:
                    errors_during_recover += 1
                else:
                    errors_after_recover += 1
                # print("**" * 68)
                # print("Get Error")
                # break
            else:
                successes += 1
                if recovering == 0:
                    successes_before_recover += 1
                elif recovering == 1:
                    successes_during_recover += 1
                else:
                    successes_after_recover += 1

        except Exception as e:
            errors += 1
            # print(f"Error during GET request: {e}")
            # launch_new_container()

        operation_time = time.time() - start_time
        operation_times.append(operation_time)

        if recovering == 0:
            operation_times_before_recover.append(operation_time)
        elif recovering == 1:
            operation_times_during_recover.append(operation_time)
        else:
            operation_times_after_recover.append(operation_time)

    return (
        errors, successes, operation_times, 
        operation_times_before_recover, operation_times_during_recover, operation_times_after_recover, 
        errors_before_recover, errors_during_recover, errors_after_recover,
        successes_before_recover, successes_during_recover, successes_after_recover,
    )


def client_thread(client_id, workload, result_lists, recover_result_lists):
    print(f"Starting client thread {client_id}")
    # errors, successes, operation_times = client_ops(client_id, workload)
    (
        errors, successes, operation_times, 
        operation_times_before_recover, operation_times_during_recover, operation_times_after_recover, 
        errors_before_recover, errors_during_recover, errors_after_recover,
        successes_before_recover, successes_during_recover, successes_after_recover,
    ) = client_ops(client_id, workload)

    # print("Opertaions times: ", operation_times)

    with lock:
        result_lists["errors"].append(errors)
        result_lists["successes"].append(successes)
        result_lists["operation_times"].append(
            operation_times
        )  # Collect all operation times

        # before_recover
        recover_result_lists["before_recover"]["errors"].append(errors_before_recover)
        recover_result_lists["before_recover"]["successes"].append(successes_before_recover)
        recover_result_lists["before_recover"]["operation_times"].append(
            operation_times_before_recover
        )

        # during_recover
        recover_result_lists["during_recover"]["errors"].append(errors_during_recover)
        recover_result_lists["during_recover"]["successes"].append(successes_during_recover)
        recover_result_lists["during_recover"]["operation_times"].append(
            operation_times_during_recover
        )

        # after_recover
        recover_result_lists["after_recover"]["errors"].append(errors_after_recover)
        recover_result_lists["after_recover"]["successes"].append(successes_after_recover)
        recover_result_lists["after_recover"]["operation_times"].append(
            operation_times_after_recover
        )

    # print(f"Client {client_id} Errors: ", result_lists["errors"])
    # print(f"Client {client_id} Successes: ", result_lists["successes"])
    # print(f"Client {client_id} Operation Times: ", result_lists["operation_times"])
    # print(f"Finished client thread {client_id}")


def run_clients():
    # run one container
    global monitoring_active
    global health_check_active

    # LAUNCHING TWO CONTAINRES AT BEGNINNG MADE NO DIFFERENCE
    # global start
    threads = []
    result_lists = {
        "errors": [],
        "successes": [],
        "operation_times": [],
    }

    recover_result_lists = {
        "before_recover": {
            "errors": [],
            "successes": [],
            "operation_times": [],
        },
        "during_recover": {
            "errors": [],
            "successes": [],
            "operation_times": [],
        },
        "after_recover": {
            "errors": [],
            "successes": [],
            "operation_times": [],
        },
    }

    init_hash_ring()
    # launch_new_container()
    monitor_containers()

    # monitoring_thread = threading.Thread(target=monitor_key_values)
    # monitoring_thread.start()
    # launch_new_container()

    # print("Check")

    # time.sleep(5)

    # read workload from file

    # Worked well with workload.txt
    with open("workload.txt", "r") as f:
    # with open("new_workload.txt", "r") as f:
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
            target=client_thread, args=(client_id, wl, result_lists, recover_result_lists)
        )
        threads.append(thread)
        # print(f"Starting thread for client {client_id}")
        thread.start()

    for thread in threads:
        thread.join()

    throughputs = [
        successes / sum(operation_times) if operation_times else 0
        for successes, operation_times in zip(
            result_lists["successes"], result_lists["operation_times"]
        )
    ]
    latencies = [
        statistics.mean(operation_times) if operation_times else float("inf")
        for operation_times in result_lists["operation_times"]
    ]
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
    error_rates = [
        e / (r + w) if r + w > 0 else 0
        for e, r, w in zip(
            result_lists["errors"], [w[0] for w in workload], [w[1] for w in workload]
        )
    ]

    # before_recover
    before_recover_throughputs = [
        successes / sum(operation_times) if operation_times else 0
        for successes, operation_times in zip(
            recover_result_lists["before_recover"]["successes"], recover_result_lists["before_recover"]["operation_times"]
        )
    ]
    before_recover_latencies = [
        statistics.mean(operation_times) if operation_times else float("inf")
        for operation_times in recover_result_lists["before_recover"]["operation_times"]
    ]

    # during_recover
    during_recover_throughputs = [
        successes / sum(operation_times) if operation_times else 0
        for successes, operation_times in zip(
            recover_result_lists["during_recover"]["successes"], recover_result_lists["during_recover"]["operation_times"]
        )
    ]
    during_recover_latencies = [
        statistics.mean(operation_times) if operation_times else float("inf")
        for operation_times in recover_result_lists["during_recover"]["operation_times"]
    ]

    # after_recover
    after_recover_throughputs = [
        successes / sum(operation_times) if operation_times else 0
        for successes, operation_times in zip(
            recover_result_lists["after_recover"]["successes"], recover_result_lists["after_recover"]["operation_times"]
        )
    ]
    after_recover_latencies = [
        statistics.mean(operation_times) if operation_times else float("inf")
        for operation_times in recover_result_lists["after_recover"]["operation_times"]
    ]

    health_check_active = False
    monitoring_active = False
    # might remove the transition time or reduce it
    # remove all containers
    remove_all_containers()
    # monitoring_thread.join()

    headers = [
        "Client ID",
        "NUM_READS",
        "NUM_WRITES",
        "READ_WRITE_RATIO",
        "Throughput",
        "Latency",
        "Error Rate",
    ]

    # Open a CSV file to write the client data
    with open("autoscaling_client_metrics.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow(headers)

        # Write the data for each client

        for i, (num_reads, num_writes, rw_ratio) in enumerate(workload):
            csvwriter.writerow(
                [
                    i,
                    num_reads,
                    num_writes,
                    rw_ratio,
                    throughputs[i],
                    latencies[i],
                    error_rates[i],
                ]
            )

    recover_headers = ["Client ID", "Throughput", "Latency"]
    with open("autoscaling_client_metrics_before_recover.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow(recover_headers)

        # Write the data for each client
        for i, (num_reads, num_writes, rw_ratio) in enumerate(workload):
            csvwriter.writerow([i, before_recover_throughputs[i], before_recover_latencies[i]])

    with open("autoscaling_client_metrics_during_recover.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow(recover_headers)

        # Write the data for each client
        for i, (num_reads, num_writes, rw_ratio) in enumerate(workload):
            csvwriter.writerow([i, during_recover_throughputs[i], during_recover_latencies[i]])

    with open("autoscaling_client_metrics_after_recover.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow(recover_headers)

        # Write the data for each client
        for i, (num_reads, num_writes, rw_ratio) in enumerate(workload):
            csvwriter.writerow([i, after_recover_throughputs[i], after_recover_latencies[i]])
    
    # print("All metrics check")
    # Define additional headers for overall statistics
    overall_stats_headers = [
        "Metric",
        "Num Containers Launched",
        "Combined Threshold",
        "CPU Weight",
        "Memory Weight",
        "Mean Reads",
        "Std Dev Reads",
        "Variance Reads",
        "Mean Writes",
        "Std Dev Writes",
        "Variance Writes",
        "Mean RW Ratio",
        "Std Dev RW Ratio",
        "Variance RW Ratio",
        "Mean Throughput",
        "Std Dev Throughput",
        "Variance Throughput",
        "Mean Latency",
        "Std Dev Latency",
        "Variance Latency",
        "Mean Error Rate",
        "Std Dev Error Rate",
        "Variance Error Rate",
    ]

    # Open another CSV file to write the overall statistics
    # print("OVerall Check")
    with open("autoscaling_overall_stats.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the overall stats header
        csvwriter.writerow(overall_stats_headers)

        # Write the overall stats
        overall_stats = [
            "Overall Stats",
            total_containers,
            combined_threshold,
            cpu_weight,
            memory_weight,
            statistics.mean([w[0] for w in workload]),
            statistics.stdev([w[0] for w in workload]),
            statistics.variance([w[0] for w in workload]),
            statistics.mean([w[1] for w in workload]),
            statistics.stdev([w[1] for w in workload]),
            statistics.variance([w[1] for w in workload]),
            statistics.mean([w[2] for w in workload]),
            statistics.stdev([w[2] for w in workload]),
            statistics.variance([w[2] for w in workload]),
            statistics.mean(throughputs),
            statistics.stdev(throughputs),
            statistics.variance(throughputs),
            statistics.mean(latencies),
            statistics.stdev(latencies),
            statistics.variance(latencies),
            statistics.mean(error_rates),
            statistics.stdev(error_rates),
            statistics.variance(error_rates),
        ]
        csvwriter.writerow(overall_stats)

    with open("resource_usage.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # Writing the headers
        csvwriter.writerow(["Index", "Average CPU Usage", "Average Memory Usage"])

        # Writing the data
        for index, (cpu, memory) in enumerate(zip(AVG_CPU_USAGES, AVG_MEMORY_USAGES)):
            csvwriter.writerow([index, cpu, memory])

    print("Done")


# CAN EVEN CREATE GRAPH OF RESPONSE TIME FOR EACH WORKLOAD OR AS CONTAINRES ARE ADDED. FIGURE THIS OUT

# with open("autoscaling_logs.txt", "a") as f:
#     for i in range(len(throughputs)):
#         f.write(
#             f"Client {i} NUM_READS: {all_reads[i]} NUM_WRITES: {all_writes[i]} READ_WRITE_RATIO: {all_rw_ratios[i]} Throughput: {throughputs[i]}, Latency: {latencies[i]}, Error Rate: {error_rates[i]}\n"
#         )

# # Maybe add other stats too like std deviation, variation, etc
# overall_average_throughput = statistics.mean(throughputs)
# overall_average_latency = statistics.mean(latencies)
# overall_average_errorRate = statistics.mean(error_rates)

# with open("autoscaling_logs.txt", "a") as f:
#     f.write(
#         f": overall_average_throughput: {overall_average_throughput}, overall_average_latency: {overall_average_latency}, overall_average_errorRate: {overall_average_errorRate}\n"
#     )


if __name__ == "__main__":
    run_clients()


# TEST IT WITH ACUTALLY SEEING REQUIRED AND AVERGAE CPU BEING COMPUTED AND MAYBE BASE THRESHOLD ON THAT TOO
# MIGHT NEED TO RETEST NONAUOSCALING WITH LOCKS
# FIX THE ERROR RATE COMPUTATION ERROR
# PREVIOUS WORKLOAD RETEST MAYBE BUT WORKED WELL IN GENERAL AS AUTOSCALE PERFORMED BETTER THAN NON-AUTOSCALE
# IMPLEMENT DYNAMIC CHANGING IN THRESHOLD
# - test if this benefical or if keeping the low threshold as now good in all cases cause if dynamically changed then we may get errors as each container won't be able to handle that i guess
# Test for latencies as being divided by operations or not: already doing that
# IMPLEMENT ML MODEL OR SCHEDULER FOR GETTING THRESHOLD
# TEST WITH UPDATED/NEW THRESHOLD WITH NEW WORKLOAD AND SEE IF IT REDUCES ERRORS
# NEED TO TEST IT WITH BOTH VARIABLE KEY SIZE AND VALUE SIZE AND DIFFERENT KEY AND VALUE SIZES. CURRENTLY DOING IT FOR SAME
# TEST WITH YCSRB LIKE BENCHMARKS FOR OVERALL THROUGHPUT AND LATENCY
# try having throughput as throughput = successes / mean(operation_times)
# WAS USING OLD STATS MEAN AND STD FOR NEW WORKLOAD TESTING. GENERATE NEW .CSV FILE WITH UPDATED STATS MEAN AND STD AND USE THEN THAT FOR TRAINING THE MODEL WITH NEW WORKLOAD
# Test it with Redis/Memcache
# Check PROFESSOR'S WAY OF COMPUTING THROUGHPUT AND LATENCY AND MAKE CHANGES IF NECESSARY
# Batching testing and testing with more reads and writes vs otherwise
