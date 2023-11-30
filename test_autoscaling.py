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


def launch_new_container():
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
        cpu_percent = (
            cpu_delta / system_delta * 100.0
        )  # maybe multiply by 8 cores but didn't help improve the performance

    memory_usage = stats["memory_stats"]["usage"] / (1024 * 1024)  # Convert to MB

    memory_limt = stats["memory_stats"]["limit"] / (1024 * 1024)

    return cpu_percent, memory_usage, memory_limt


# # AGGREGATE VERSION. not much improvement with this
# def no_space_in_container(num_write, num_read, rw_ratio):
#     # List all running containers
#     containers = docker_client.containers.list()

#     # Get resource usage prediction for the workload
#     required_cpu, required_memory = get_resource_usage_prediction(
#         num_read, num_write, rw_ratio
#     )

#     # Initialize total CPU and memory usage
#     total_cpu_usage, total_memory_usage = 0.0, 0.0
#     total_memory_limit = 0.0

#     # Iterate over all containers to aggregate resource usage
#     for container in containers:
#         stats = container.stats(stream=False)
#         cpu_usage, memory_usage, memory_limit = get_cpu_memory_usage(stats)
#         total_cpu_usage += cpu_usage
#         total_memory_usage += memory_usage
#         total_memory_limit += memory_limit

#     # Calculate the mean CPU and memory usage
#     if containers:
#         mean_cpu_usage = total_cpu_usage / len(containers)
#         mean_memory_usage = total_memory_usage / len(containers)
#         mean_memory_limit = total_memory_limit / len(containers)
#     else:
#         # If there are no containers, set usage to zero
#         mean_cpu_usage, mean_memory_usage, mean_memory_limit = 0.0, 0.0, 0.0

#     # Check if the system can handle the workload
#     can_handle_workload = (mean_cpu_usage + required_cpu <= 100) and (
#         mean_memory_usage + required_memory <= mean_memory_limit
#     )

#     # If unable to handle workload, return True to indicate need for new container
#     return not can_handle_workload


# CHECKING FOR EACH CONTAINER (#around 50 throughput and 0.003 latency but with few errors and certainly worse than non-autoscaling)
# def no_space_in_container(num_write, num_read, rw_ratio):
#     # List all running containers
#     containers = docker_client.containers.list()

#     # print("Contaienrs: ", containers)

#     required_cpu, required_memory = get_resource_usage_prediction(
#         num_read, num_write, rw_ratio
#     )
#     # print("required cpu: {:.2f}".format(required_cpu))
#     # print("required memory: {:.2f}".format(required_memory))

#     # Extract and print the names of running containers
#     for container in containers:
#         # print("Check")
#         # print("Container Name:", container.name)
#         stats = container.stats(stream=False)

#         cpu_usage, memory_usage, memory_limit = get_cpu_memory_usage(stats)
#         # print("cpu usage: {:.2f}".format(cpu_usage))
#         # print("memory usage: {:.2f}".format(memory_usage))
#         # print("memory limit: {:.2f}".format(memory_limit))

#         # FIX LATER
#         # if (cpu_usage + required_cpu <= 0.95) or (
#         #     memory_usage + required_memory <= memory_limit - 0.2
#         # ):
#         #     # print("There is space to work on task")
#         #     # print()
#         #     return False
#         # # print()
#         # if (cpu_usage + required_cpu < 100) or (
#         #     memory_usage + required_memory < memory_limit
#         # ):
#         #     # print("There is space to work on task")
#         #     # print()
#         #     return False
#         if cpu_usage + required_cpu < 15:
#             return False

#         if memory_usage + required_memory == memory_limit:
#             return False

#     # print("Unable to handle workload, launch the new container!!")
#     return True


def no_space_in_container(num_write, num_read, rw_ratio):
    containers = docker_client.containers.list()

    required_cpu, required_memory = get_resource_usage_prediction(
        num_read, num_write, rw_ratio
    )

    total_cpu_usage, total_memory_usage = 0, 0
    total_memory_limit = 0
    for container in containers:
        stats = container.stats(stream=False)
        cpu_usage, memory_usage, memory_limit = get_cpu_memory_usage(stats)
        total_cpu_usage += cpu_usage
        total_memory_usage += memory_usage
        total_memory_limit += memory_limit

    # Calculate average usage
    avg_cpu_usage = total_cpu_usage / len(containers) if containers else 0
    avg_memory_usage = total_memory_usage / len(containers) if containers else 0

    AVG_CPU_USAGES.append(avg_cpu_usage)
    AVG_MEMORY_USAGES.append(avg_memory_usage)

    # Define weights based on importance
    # cpu_weight = 0.3  # Example weight for CPU
    # memory_weight = 0.7  # Example weight for memory

    # Calculate weighted utilization
    curr_weighted_utilization = (cpu_weight * avg_cpu_usage) + (
        memory_weight * avg_memory_usage
    )

    req_weighted_utilization = (cpu_weight * required_cpu) + (
        memory_weight * required_memory
    )

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

    # Define a combined threshold (for example, 80%)
    # combined_threshold = 34.7

    # Check against the combined threshold and predicted requirements
    if curr_weighted_utilization + req_weighted_utilization > combined_threshold:
        return True

    return False


# def no_space_in_container(num_write, num_read, rw_ratio):
#     containers = docker_client.containers.list()

#     required_cpu, required_memory = get_resource_usage_prediction(
#         num_read, num_write, rw_ratio
#     )

#     total_cpu_usage, total_memory_usage = 0, 0
#     total_memory_limit = 0
#     for container in containers:
#         stats = container.stats(stream=False)
#         cpu_usage, memory_usage, memory_limit = get_cpu_memory_usage(stats)
#         total_cpu_usage += cpu_usage
#         total_memory_usage += memory_usage
#         total_memory_limit += memory_limit

#     # Calculate average usage
#     avg_cpu_usage = total_cpu_usage / len(containers) if containers else 0
#     avg_memory_usage = total_memory_usage / len(containers) if containers else 0

#     print("Current Avg cpu usage: ", avg_cpu_usage)
#     print("Current Avg memory usage: ", avg_memory_usage)
#     print("Req cpu usage: ", required_cpu)
#     print("Req memory usage: ", required_memory)

#     current_ratio = avg_cpu_usage / avg_memory_usage
#     required_ratio = required_cpu / required_memory

#     print("Current Ratio: ", current_ratio)
#     print("Req Ratio: ", required_ratio)

#     print("Combined Ratio: ", current_ratio + required_ratio)

#     # print("Current weighted cpu average: ", cpu_weight * avg_cpu_usage)
#     # print("Current weighted memory average: ", memory_weight * avg_memory_usage)
#     # print("Current Weighted utilization: ", curr_weighted_utilization)
#     # print("Required weighted cpu average: ", cpu_weight * required_cpu)
#     # print("Required weighted memory average: ", memory_weight * required_memory)
#     # print("Required Weighted utilization: ", req_weighted_utilization)
#     # print(
#     #     "Combined Weighted utilization: ",
#     #     curr_weighted_utilization + req_weighted_utilization,
#     # )

#     # Define a combined threshold (for example, 80%)
#     # combined_threshold = 34.7

#     # Check against the combined threshold and predicted requirements
#     # if curr_weighted_utilization + req_weighted_utilization > combined_threshold:
#     #     return True

#     return False


def client_ops(client_id, workload):
    num_write, num_read, rw_ratio = workload
    written_keys = []

    errors = 0
    successes = 0

    # predict the container cpu and memory usage
    # launch new container if needed
    global transition
    if no_space_in_container(num_write, num_read, rw_ratio):
        launch_new_container()
        # launch_new_container() launch multiple cotnainres at a time?
        transition = True
        # print("Transition: ", transition)

    for i in range(num_write):
        if transition:
            time.sleep(2)  # 0.5
            transition = False
        # print("Transition Put check: ", transition)
        key = f"key-{client_id}-{i}"  # NEED TO ADD RANDOMNESS IN KEY GENERATION AND VALUE GENERATION
        value = f"value-{client_id}-{i}"

        # seed = f"key-{client_id}-{i}"
        # key = generate_random_string(random.randint(1, 100), seed)
        # value = generate_random_string(random.randint(1, 100))

        server_url = ring.get_node(key)

        # print(f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}")

        # with open("autoscaling_logs.txt", "a") as f:
        #     f.write(
        #         f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}\n"
        #     )

        try:
            response = requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
            # print(f"PUT response: {response.status_code}, {response.text}")
            # with open("autoscaling_logs.txt", "a") as f:
            #     f.write(f"PUT response: {response.status_code}, {response.text}\n")
            if response.status_code == 404:
                errors += 1
                print("**" * 68)
                print("Put Error")
                # break
            else:
                successes += 1
            written_keys.append(key)
        except Exception as e:
            errors += 1
            print(f"Error during PUT request: {e}")

    for j in range(num_read):
        if transition:
            time.sleep(2)  # 0.5
            transition = False
        # print("Transition Get check: ", transition)
        random_key_index = random.randint(0, len(written_keys) - 1)
        key = written_keys[random_key_index]

        server_url = ring.get_node(key)

        # print(f"Get checkpoint - Server URL: {server_url}, Key: {key}")
        # with open("autoscaling_logs.txt", "a") as f:
        #     f.write(f"Get checkpoint - Server URL: {server_url}, Key: {key}\n")
        try:
            response = requests.get(f"{server_url}/retrieve", params={"key": key})
            # print(f"GET response: {response.status_code}, {response.text}")
            # with open("autoscaling_logs.txt", "a") as f:
            #     f.write(f"GET response: {response.status_code}, {response.text}\n")
            if response.status_code == 404:
                errors += 1
                print("**" * 68)
                print("Get Error")
                # break
            else:
                successes += 1
        except Exception as e:
            errors += 1
            print(f"Error during GET request: {e}")

    return errors, successes


if __name__ == "__main__":
    # run one container

    # LAUNCHING TWO CONTAINRES AT BEGNINNG MADE NO DIFFERENCE
    launch_new_container()
    # launch_new_container()

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
        # workload = [
        #     (
        #         int(n_write * 10),
        #         int(n_read * 10),
        #         float(int(n_write * 10) / int(n_write * 10)),
        #     )
        #     for n_write, n_read, rw_ratio in workload
        # ]

    throughputs = []
    latencies = []
    error_rates = []
    all_reads = []
    all_writes = []
    all_rw_ratios = []

    for client_id in range(len(workload)):
        # for clie in range(len(workload)):
        # for client_id in range(0, 10):
        print(client_id)
        # print("Total containers: ", total_containers)
        # print("Workload: ", workload)
        # print("Workload check: ", workload[client_id])
        num_reads, num_writes, read_write_ratio = workload[0]

        # GETTING LOT OF ERRORS WHEN DOING SO

        # num_reads *= 10
        # num_writes *= 10
        # read_write_ratio = num_reads / num_writes

        all_reads.append(num_reads)
        all_writes.append(num_writes)
        all_rw_ratios.append(read_write_ratio)

        # print("***" * 68)

        # with open("autoscaling_logs.txt", "a") as f:
        #     f.write("**" * 60 + "\n")
        #     f.write(f"New Workload: {client_id}\n")
        #     f.write("\n")
        # print("Workload: ", workload, len(workload))
        # break
        start = time.time()
        # errors, succeses = client_ops(0, workload[0])
        errors, succeses = client_ops(client_id, workload[client_id])
        total_time = time.time() - start
        NUM_OPS = num_reads + num_writes
        throughput = float(succeses / total_time)  # or succeses or NUM_OPS
        latency = float(total_time / succeses)  #  or succeses or NUM_OPS
        error_rate = float(errors / NUM_OPS)
        throughputs.append(throughput)
        latencies.append(latency)
        error_rates.append(error_rate)

        # might remove the transition time or reduce it
    # remove all containers
    remove_all_containers()

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
        for i in range(len(throughputs)):
            row = [
                i,
                all_reads[i],
                all_writes[i],
                all_rw_ratios[i],
                throughputs[i],
                latencies[i],
                error_rates[i],
            ]
            csvwriter.writerow(row)

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
            statistics.mean(all_reads),
            statistics.stdev(all_reads),
            statistics.variance(all_reads),
            statistics.mean(all_writes),
            statistics.stdev(all_writes),
            statistics.variance(all_writes),
            statistics.mean(all_rw_ratios),
            statistics.stdev(all_rw_ratios),
            statistics.variance(all_rw_ratios),
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
