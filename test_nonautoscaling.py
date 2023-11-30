import requests
import docker
import time
import random
import csv
import statistics

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

    # container = docker_client.containers.run(
    #     "docker-kv-store",
    #     detach=True,
    #     name=container_name,
    #     ports={"80/tcp": port},
    #     auto_remove=True,
    # )

    container = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        name=container_name,
        ports={"80/tcp": port},
        mem_limit="15m",
        auto_remove=True,
    )

    servers[container.id] = f"http://{HOST}:{port}"
    return container


def client_ops(client_id, container_id, workload):
    errors = 0
    successes = 0
    num_write, num_read, _rw_ratio = workload
    server_url = servers[container_id]
    written_keys = []

    for i in range(num_write):
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"

        # print(f"Write checkpoint - Server URL: {server_url}, Key: {key} Value: {value}")

        try:
            response = requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
            # print(f"PUT response: {response.status_code}, {response.text}")
            if response.status_code == 404:
                errors += 1
                print("**" * 68)
                print("Put Error")
                # break
            else:
                successes += 1
            written_keys.append(key)  # SHOULD I ADD IT UNDER ELSE STATEMENT?
        except Exception as e:
            errors += 1
            print(f"Error during PUT request: {e}")

    for j in range(num_read):
        random_key_index = random.randint(0, len(written_keys) - 1)
        key = written_keys[random_key_index]
        # print(f"Get checkpoint - Server URL: {server_url}, Key: {key}")
        try:
            response = requests.get(f"{server_url}/retrieve", params={"key": key})
            # print(f"GET response: {response.status_code}, {response.text}")
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


def run_clients():
    throughputs = []
    latencies = []
    error_rates = []
    all_reads = []
    all_writes = []
    all_rw_ratios = []

    # cumulative_time = 0
    container = start_docker_container(0)
    time.sleep(2)

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

    # for client_id in range(0, 10):
    for client_id in range(len(workload)):
        num_reads, num_writes, rw_ratio = workload[
            client_id
        ]  # VERIFY WITH WORKLOAD_GEN.PY
        all_reads.append(num_reads)
        all_writes.append(num_writes)
        all_rw_ratios.append(rw_ratio)
        print(client_id)

        # Run client operations and measure time
        # start_time = time.time()
        start_time = time.time()
        # time.sleep(2)
        errors, succeses = client_ops(
            client_id, container.id, workload[client_id]
        )  # Assuming this function is defined
        # operation_time = time.time() - start_time

        # Update cumulative time and compute throughput and latency
        # cumulative_time += operation_time
        total_time = time.time() - start_time
        # total_time = time.perf_counter() - start_time - 2
        NUM_OPS = num_reads + num_writes
        throughput = float(succeses / total_time)
        latency = float(total_time / succeses)
        error_rate = float(errors / NUM_OPS)
        throughputs.append(throughput)
        latencies.append(latency)
        error_rates.append(error_rate)

    container.stop()

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
    with open("non-autoscaling_client_metrics.csv", "w", newline="") as csvfile:
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
    with open("non-autoscaling_overall_stats.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the overall stats header
        csvwriter.writerow(overall_stats_headers)

        # Write the overall stats
        overall_stats = [
            "Overall Stats",
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

    # headers = [
    #     "Client ID",
    #     "NUM_READS",
    #     "NUM_WRITES",
    #     "READ_WRITE_RATIO",
    #     "Throughput",
    #     "Latency",
    #     "Error Rate",
    # ]

    # # Write throughput and latency to CSV
    # with open("non_autoscaling_client_metrics.csv", "w", newline="") as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow(["Client ID", "Throughput", "Latency"])

    #     for i in range(len(throughputs)):
    #         csvwriter.writerow([i, throughputs[i], latencies[i]])


if __name__ == "__main__":
    run_clients()


# def run_clients():
#     throughputs = []
#     latencies = []
#     container = start_docker_container(0)
#     time.sleep(2)

#     # read workload from file
#     with open("workload.txt", "r") as f:
#         workload = f.readlines()
#         workload = [line.strip().split(" ") for line in workload]
#         workload = [
#             (
#                 int(n_write),
#                 int(n_read),
#                 float((int(n_read)) / (int(n_write))),
#             )
#             for n_write, n_read, rw_ratio in workload
#         ]

#     # for client_id in range(0, 30):
#     for client_id in range(len(workload)):
#         # print("Workload: ", workload[client_id])
#         num_reads, num_writes, read_write_ratio = workload[client_id]
#         start = time.time()

#         print(client_id)

#         client_ops(client_id, container.id, workload[client_id])

#         total_time = time.time() - start
#         NUM_OPS = num_reads + num_writes
#         throughput = NUM_OPS / total_time
#         latency = total_time / NUM_OPS
#         throughputs.append(throughput)
#         latencies.append(latency)

#     container.stop()

#     with open("non_autoscaling_client_metrics.csv", "w", newline="") as csvfile:
#         print("hello")
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(["Client ID", "Throughput", "Latency"])

#         for i in range(len(throughputs)):
#             csvwriter.writerow([i, throughputs[i], latencies[i]])


# if __name__ == "__main__":
#     run_clients()
