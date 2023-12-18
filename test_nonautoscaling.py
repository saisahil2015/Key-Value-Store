# Was not computing throughput and latency for each opeariont's time but overall all operations for a client
# import requests
# import docker
# import time
# import random
# import csv
# import statistics
# import threading

# NUM_CLIENTS = 20
# NUM_REQUESTS = 100
# HOST = "127.0.0.1"

# docker_client = docker.from_env()
# available_ports = [port for port in range(8081, 9070)]
# servers = {}


# def start_docker_container(client_id):
#     print(f"Starting Docker container for client {client_id}")
#     container_name = f"non_auto_client-{client_id}"

#     if available_ports:
#         port = available_ports.pop(0)
#     else:
#         raise Exception("No available ports left")

#     container = docker_client.containers.run(
#         "docker-kv-store",
#         detach=True,
#         name=container_name,
#         ports={"80/tcp": port},
#         mem_limit="15m",
#         auto_remove=True,
#     )

#     servers[container.id] = f"http://{HOST}:{port}"
#     return container


# def client_ops(client_id, container_id, workload):
#     errors = 0
#     successes = 0
#     num_write, num_read, _rw_ratio = workload
#     server_url = servers[container_id]
#     written_keys = []

#     for i in range(num_write):
#         key = f"key-{client_id}-{i}"
#         value = f"value-{client_id}-{i}"

#         try:
#             response = requests.put(
#                 f"{server_url}/store", params={"key": key}, data={"value": value}
#             )
#             if response.status_code == 404:
#                 print(f"Write failed for key {key}")
#                 errors += 1
#             else:
#                 print(f"Write successful for key {key}")
#                 successes += 1
#             written_keys.append(key)
#         except Exception as e:
#             print(f"Error during PUT request for key {key}: {e}")
#             errors += 1

#     for j in range(num_read):
#         if written_keys:
#             random_key_index = random.randint(0, len(written_keys) - 1)
#             key = written_keys[random_key_index]

#             try:
#                 response = requests.get(f"{server_url}/retrieve", params={"key": key})
#                 if response.status_code == 404:
#                     print(f"Read failed for key {key}")
#                     errors += 1
#                 else:
#                     print(f"Read successful for key {key}")
#                     successes += 1
#             except Exception as e:
#                 print(f"Error during GET request for key {key}: {e}")
#                 errors += 1

#     return errors, successes


# def client_thread(client_id, container_id, workload, result_lists):
#     print(f"Starting client thread {client_id}")
#     errors, successes = client_ops(client_id, container_id, workload)
#     result_lists["errors"].append(errors)
#     result_lists["successes"].append(successes)
#     result_lists["num_reads"].append(workload[1])
#     result_lists["num_writes"].append(workload[0])
#     result_lists["rw_ratios"].append(workload[2])
#     print(f"Finished client thread {client_id}")


# def run_clients():
#     print("Initializing run_clients")
#     container = start_docker_container(0)
#     time.sleep(2)  # Allow time for container to start

#     threads = []
#     result_lists = {
#         "errors": [],
#         "successes": [],
#         "num_reads": [],
#         "num_writes": [],
#         "rw_ratios": [],
#     }

#     with open("workload.txt", "r") as f:
#         workload = [line.strip().split(" ") for line in f.readlines()]
#         workload = [
#             (int(n_write), int(n_read), float(rw_ratio))
#             for n_write, n_read, rw_ratio in workload
#         ]

#     for client_id, wl in enumerate(workload):
#         thread = threading.Thread(
#             target=client_thread, args=(client_id, container.id, wl, result_lists)
#         )
#         threads.append(thread)
#         print(f"Starting thread for client {client_id}")
#         thread.start()

#     for thread in threads:
#         thread.join()

#     container.stop()
#     print("Stopped Docker container")

#     # Process and write results to CSV
#     latencies = [
#         s / (r + w) if r + w > 0 else 0
#         for s, r, w in zip(
#             result_lists["successes"],
#             result_lists["num_reads"],
#             result_lists["num_writes"],
#         )
#     ]
#     throughputs = [
#         (r + w) / s if s > 0 else float("inf")
#         for s, r, w in zip(
#             result_lists["successes"],
#             result_lists["num_reads"],
#             result_lists["num_writes"],
#         )
#     ]
#     error_rates = [
#         e / (r + w) if r + w > 0 else 0
#         for e, r, w in zip(
#             result_lists["errors"],
#             result_lists["num_reads"],
#             result_lists["num_writes"],
#         )
#     ]

#     with open("non-autoscaling_client_metrics.csv", "w", newline="") as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(
#             [
#                 "Client ID",
#                 "NUM_READS",
#                 "NUM_WRITES",
#                 "READ_WRITE_RATIO",
#                 "Throughput",
#                 "Latency",
#                 "Error Rate",
#             ]
#         )

#         for i in range(len(throughputs)):
#             csvwriter.writerow(
#                 [
#                     i,
#                     result_lists["num_reads"][i],
#                     result_lists["num_writes"][i],
#                     result_lists["rw_ratios"][i],
#                     throughputs[i],
#                     latencies[i],
#                     error_rates[i],
#                 ]
#             )

#     # Write overall statistics
#     overall_stats_headers = [
#         "Metric",
#         "Mean Reads",
#         "Std Dev Reads",
#         "Variance Reads",
#         "Mean Writes",
#         "Std Dev Writes",
#         "Variance Writes",
#         "Mean RW Ratio",
#         "Std Dev RW Ratio",
#         "Variance RW Ratio",
#         "Mean Throughput",
#         "Std Dev Throughput",
#         "Variance Throughput",
#         "Mean Latency",
#         "Std Dev Latency",
#         "Variance Latency",
#         "Mean Error Rate",
#         "Std Dev Error Rate",
#         "Variance Error Rate",
#     ]

#     with open("non-autoscaling_overall_stats.csv", "w", newline="") as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(overall_stats_headers)
#         csvwriter.writerow(
#             [
#                 "Overall Stats",
#                 statistics.mean(result_lists["num_reads"]),
#                 statistics.stdev(result_lists["num_reads"]),
#                 statistics.variance(result_lists["num_reads"]),
#                 statistics.mean(result_lists["num_writes"]),
#                 statistics.stdev(result_lists["num_writes"]),
#                 statistics.variance(result_lists["num_writes"]),
#                 statistics.mean(result_lists["rw_ratios"]),
#                 statistics.stdev(result_lists["rw_ratios"]),
#                 statistics.variance(result_lists["rw_ratios"]),
#                 statistics.mean(throughputs),
#                 statistics.stdev(throughputs),
#                 statistics.variance(throughputs),
#                 statistics.mean(latencies),
#                 statistics.stdev(latencies),
#                 statistics.variance(latencies),
#                 statistics.mean(error_rates),
#                 statistics.stdev(error_rates),
#                 statistics.variance(error_rates),
#             ]
#         )


# if __name__ == "__main__":
#     run_clients()


# Computing throughput and latency by computing time for each opeartion and summing it over for each client
# import requests
# import docker
# import time
# import random
# import csv
# import statistics
# import threading

# NUM_CLIENTS = 20
# NUM_REQUESTS = 100
# HOST = "127.0.0.1"

# docker_client = docker.from_env()
# available_ports = [port for port in range(8081, 9070)]
# servers = {}


# def start_docker_container(client_id):
#     print(f"Starting Docker container for client {client_id}")
#     container_name = f"non_auto_client-{client_id}"

#     if available_ports:
#         port = available_ports.pop(0)
#     else:
#         raise Exception("No available ports left")

#     container = docker_client.containers.run(
#         "docker-kv-store",
#         detach=True,
#         name=container_name,
#         ports={"80/tcp": port},
#         mem_limit="15m",
#         auto_remove=True,
#     )

#     print(f"Container for client {client_id} started at {HOST}:{port}")
#     servers[container.id] = f"http://{HOST}:{port}"
#     return container


# def client_ops(client_id, container_id, workload):
#     errors = 0
#     successes = 0
#     total_operation_time = 0
#     num_write, num_read, _rw_ratio = workload
#     server_url = servers[container_id]
#     print(f"Client {client_id} starting operations")

#     for i in range(num_write):
#         key = f"key-{client_id}-{i}"
#         value = f"value-{client_id}-{i}"
#         start_time = time.time()

#         try:
#             response = requests.put(
#                 f"{server_url}/store", params={"key": key}, data={"value": value}
#             )
#             operation_time = time.time() - start_time
#             total_operation_time += operation_time
#             if response.status_code == 404:
#                 print(f"Write failed for key {key}")
#                 errors += 1
#             else:
#                 print(f"Write successful for key {key}")
#                 successes += 1
#         except Exception as e:
#             print(f"Error during PUT request for key {key}: {e}")
#             errors += 1

#     for j in range(num_read):
#         key = f"key-{client_id}-{random.randint(0, num_write-1)}"
#         start_time = time.time()

#         try:
#             response = requests.get(f"{server_url}/retrieve", params={"key": key})
#             operation_time = time.time() - start_time
#             total_operation_time += operation_time
#             if response.status_code == 404:
#                 print(f"Read failed for key {key}")
#                 errors += 1
#             else:
#                 print(f"Read successful for key {key}")
#                 successes += 1
#         except Exception as e:
#             print(f"Error during GET request for key {key}: {e}")
#             errors += 1

#     print(f"Client {client_id} finished operations")
#     return errors, successes, total_operation_time


# def client_thread(client_id, container_id, workload, result_lists):
#     print(f"Starting client thread {client_id}")
#     errors, successes, total_operation_time = client_ops(
#         client_id, container_id, workload
#     )
#     result_lists["errors"].append(errors)
#     result_lists["successes"].append(successes)
#     result_lists["operation_times"].append(total_operation_time)
#     print(f"Finished client thread {client_id}")


# def run_clients():
#     print("Initializing run_clients")
#     container = start_docker_container(0)
#     time.sleep(2)

#     threads = []
#     result_lists = {
#         "errors": [],
#         "successes": [],
#         "operation_times": [],
#     }

#     with open("workload.txt", "r") as f:
#         workload = [line.strip().split(" ") for line in f.readlines()]
#         workload = [
#             (int(n_write), int(n_read), float(rw_ratio))
#             for n_write, n_read, rw_ratio in workload
#         ]

#     for client_id, wl in enumerate(workload):
#         thread = threading.Thread(
#             target=client_thread, args=(client_id, container.id, wl, result_lists)
#         )
#         threads.append(thread)
#         print(f"Starting thread for client {client_id}")
#         thread.start()

#     for thread in threads:
#         thread.join()

#     container.stop()
#     print("Stopped Docker container")

#     throughputs = [
#         s / t if t > 0 else 0
#         for s, t in zip(result_lists["successes"], result_lists["operation_times"])
#     ]
#     latencies = [
#         t / s if s > 0 else float("inf")
#         for s, t in zip(result_lists["successes"], result_lists["operation_times"])
#     ]
#     error_rates = [
#         e / (r + w) if r + w > 0 else 0
#         for e, r, w in zip(
#             result_lists["errors"], [w[0] for w in workload], [w[1] for w in workload]
#         )
#     ]

#     # Write results to CSV
#     with open("non-autoscaling_client_metrics.csv", "w", newline="") as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(
#             [
#                 "Client ID",
#                 "NUM_READS",
#                 "NUM_WRITES",
#                 "READ_WRITE_RATIO",
#                 "Throughput",
#                 "Latency",
#                 "Error Rate",
#             ]
#         )

#         for i, (num_reads, num_writes, rw_ratio) in enumerate(workload):
#             csvwriter.writerow(
#                 [
#                     i,
#                     num_reads,
#                     num_writes,
#                     rw_ratio,
#                     throughputs[i],
#                     latencies[i],
#                     error_rates[i],
#                 ]
#             )

#     # Write overall statistics
#     overall_stats_headers = [
#         "Metric",
#         "Mean Reads",
#         "Std Dev Reads",
#         "Variance Reads",
#         "Mean Writes",
#         "Std Dev Writes",
#         "Variance Writes",
#         "Mean RW Ratio",
#         "Std Dev RW Ratio",
#         "Variance RW Ratio",
#         "Mean Throughput",
#         "Std Dev Throughput",
#         "Variance Throughput",
#         "Mean Latency",
#         "Std Dev Latency",
#         "Variance Latency",
#         "Mean Error Rate",
#         "Std Dev Error Rate",
#         "Variance Error Rate",
#     ]

#     with open("non-autoscaling_overall_stats.csv", "w", newline="") as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(overall_stats_headers)
#         csvwriter.writerow(
#             [
#                 "Overall Stats",
#                 statistics.mean([w[0] for w in workload]),
#                 statistics.stdev([w[0] for w in workload]),
#                 statistics.variance([w[0] for w in workload]),
#                 statistics.mean([w[1] for w in workload]),
#                 statistics.stdev([w[1] for w in workload]),
#                 statistics.variance([w[1] for w in workload]),
#                 statistics.mean([w[2] for w in workload]),
#                 statistics.stdev([w[2] for w in workload]),
#                 statistics.variance([w[2] for w in workload]),
#                 statistics.mean(throughputs),
#                 statistics.stdev(throughputs),
#                 statistics.variance(throughputs),
#                 statistics.mean(latencies),
#                 statistics.stdev(latencies),
#                 statistics.variance(latencies),
#                 statistics.mean(error_rates),
#                 statistics.stdev(error_rates),
#                 statistics.variance(error_rates),
#             ]
#         )


# if __name__ == "__main__":
#     run_clients()


# computing by having average latency per operation. modified version of above
# need to test whether only successes or even failtures be computed with the operation time
# can have throughput(for successful operations) and latency for only successful and another latency for only failed operations
# Try adding locks for it to see if errors are reduced
# figure out if Error Rate represnts percentage or not
import requests
import docker
import time
import random
import csv
import statistics
import threading
import string

HOST = "127.0.0.1"

docker_client = docker.from_env()
# available_ports = [port for port in range(8081, 9080)]
port = 8080
servers = {}

random.seed(123)


def start_docker_container(client_id):
    print(f"Starting Docker container for client {client_id}")
    container_name = f"non_auto_client-{client_id}"

    # port = available_ports.pop(0) if available_ports else None
    if not port:
        raise Exception("No available ports left")

    container = docker_client.containers.run(
        "docker-kv-store",
        detach=True,
        name=container_name,
        ports={"80/tcp": port},
        mem_limit="15m",
        auto_remove=True,
    )

    print(f"Container for client {client_id} started at {HOST}:{port}")
    servers[container.id] = f"http://{HOST}:{port}"
    return container


def generate_random_string(length, seed=None):
    # random.seed(seed)
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def client_ops(client_id, container_id, workload):
    errors = 0
    successes = 0
    operation_times = []
    written_keys = []
    total_ops = 0

    num_write, num_read, _rw_ratio = workload
    server_url = servers[container_id]
    print(f"Client {client_id} starting operations at {server_url}")

    for i in range(num_write):
        # key_seed = f"key-{client_id}-{i}"
        # key = generate_random_string(random.randint(1, 250), key_seed)
        # val_seed = f"value-{client_id}-{i}"
        # value = generate_random_string(random.randint(1, 250), val_seed)

        # if i % 10 == 0:
        #     with open("non_autoscaling_logs.txt", "a") as f:
        #         f.write((f"Key size: {len(key)} Value size: {len(value)}\n"))

        # print(f"Key: {key} Value: {value}")

        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"
        start_time = time.time()

        try:
            response = requests.put(
                f"{server_url}/store", params={"key": key}, data={"value": value}
            )
            # operation_time = time.time() - start_time
            # operation_times.append(operation_time)

            if response.status_code != 404:
                written_keys.append(key)

            successes += 1
            total_ops += 1

            # if response.status_code == 404:
            #     # print(f"Write failed for key {key}")
            #     # errors += 1
            #     errors += 0
            # else:
            #     # print(
            #     #     f"Write successful for key {key}, took {operation_time:.4f} seconds"
            #     # )
            #     successes += 1
            # operation_times.append(operation_time)
        except Exception as e:
            # with open("non-autoscaling_logs.txt", "a") as f:
            #     f.write(f"Error during PUT request for key {key}: {e}")
            #     f.write(f"\n")

            # print(f"Error during PUT request for key {key}: {e}")
            errors += 1
            total_ops += 1
            # operation_time = (
            #     time.time() - start_time
            # )  # Calculate the operation time even on exception
            # operation_times.append(operation_time)
        operation_time = time.time() - start_time
        operation_times.append(operation_time)
    # keyTested = []
    for j in range(num_read):
        if not written_keys:  # Check if there are keys to read
            break
        # random_key_index = random.randint(0, len(written_keys) - 1)
        # key = written_keys[random_key_index]
        # key = written_keys[j]
        # if key in keyTested:
        #     with open("non-autoscaling_logs.txt", "a") as f:
        #         f.write(f"Key already tested: {key}")
        #         f.write(f"\n")
        # else:
        #     keyTested.append(key)
        random_key_index = random.randint(0, num_write - 1)
        key = f"key-{client_id}-{random_key_index}"
        start_time = time.time()

        try:
            response = requests.get(f"{server_url}/retrieve", params={"key": key})
            # operation_time = time.time() - start_time
            # operation_times.append(operation_time)

            if response.status_code == 404:
                # with open("non-autoscaling_logs.txt", "a") as f:
                #     f.write(f"Read failed for key {key}")
                #     f.write(f"\n")
                # print(f"Read failed for key {key}")
                errors += 1
                total_ops += 1
            else:
                # print(
                #     f"Read successful for key {key}, took {operation_time:.4f} seconds"
                # )
                successes += 1
                total_ops += 1
                # operation_times.append(operation_time)

        except Exception as e:
            # with open("non-autoscaling_logs.txt", "a") as f:
            #     f.write(f"Error during GET request for key {key}: {e}")
            #     f.write(f"\n")
            # print(f"Error during GET request for key {key}: {e}")
            errors += 1
            total_ops += 1
            # operation_time = (
            #     time.time() - start_time
            # )  # Calculate the operation time even on exception
            # operation_times.append(operation_time)
        operation_time = time.time() - start_time
        operation_times.append(operation_time)

    print(f"Client {client_id} finished operations")
    return errors, successes, operation_times, total_ops


def client_thread(client_id, container_id, workload, result_lists):
    # print(f"Starting client thread {client_id}")
    errors, successes, operation_times, total_ops = client_ops(
        client_id, container_id, workload
    )
    # print("Opertaions times: ", operation_times)
    result_lists["errors"].append(errors)
    result_lists["successes"].append(successes)
    result_lists["operation_times"].append(operation_times)
    result_lists["total_ops"].append(total_ops)

    # Collect all operation times
    # print(f"Client {client_id} Errors: ", result_lists["errors"])
    # print(f"Client {client_id} Successes: ", result_lists["successes"])
    # print(f"Client {client_id} Operation Times: ", result_lists["operation_times"])
    # print(f"Finished client thread {client_id}")


def run_clients_nonAutoscaling(
    WORKLOAD_TYPE,
    STATS_FILE_NAME,
    OVERALL_STATS_FILE_NAME,
):
    print("Initializing run_clients")
    container = start_docker_container(0)
    # time.sleep(2)  # Allow time for container to start

    threads = []
    result_lists = {
        "errors": [],
        "successes": [],
        "operation_times": [],
        "total_ops": [],
    }

    with open(WORKLOAD_TYPE, "r") as f:
        workload = [line.strip().split(" ") for line in f.readlines()]
        workload = [
            (int(n_write), int(n_read), float(rw_ratio))
            for n_read, n_write, rw_ratio in workload
        ]

    for client_id, wl in enumerate(workload):
        thread = threading.Thread(
            target=client_thread, args=(client_id, container.id, wl, result_lists)
        )
        threads.append(thread)
        print(f"Starting thread for client {client_id}")
        thread.start()

    for thread in threads:
        thread.join()

    container.stop()
    print("Stopped Docker container")

    # Calculate throughput and latency

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

    # error_rates = [
    #     e / (r + w) if r + w > 0 else 0
    #     for e, r, w in zip(
    #         result_lists["errors"], [w[0] for w in workload], [w[1] for w in workload]
    #     )
    # ]

    error_rates = []

    for errors, num_reads, num_writes, total_ops in zip(
        result_lists["errors"],
        [w[0] for w in workload],
        [w[1] for w in workload],
        result_lists["total_ops"],
    ):
        # total_operations = num_writes + num_reads
        if total_ops > 0:
            # print(
            #     f"Num Reads: {num_reads} Num Writes: {num_writes} Total operations: {total_ops}"
            # )
            # print("Errors: ", errors)
            error_rate = errors / total_ops
            # print("Error Rate: ", error_rate)
        else:
            error_rate = 0
        error_rates.append(error_rate)

    # Write results to CSV
    with open(STATS_FILE_NAME, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            [
                "Client ID",
                "NUM_READS",
                "NUM_WRITES",
                "READ_WRITE_RATIO",
                "Throughput",
                "Latency",
                "Error Rate",
            ]
        )

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

    # Write overall statistics
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

    with open(OVERALL_STATS_FILE_NAME, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(overall_stats_headers)
        csvwriter.writerow(
            [
                "Overall Stats",
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
        )
    print("Data written to CSV files successfully")


# if __name__ == "__main__":
#     run_clients()


# Computing throughput and latency by computing time for each opeartion and averaging it over for each client
# import requests
# import docker
# import time
# import random
# import csv
# import statistics
# import threading

# NUM_CLIENTS = 20
# NUM_REQUESTS = 100
# HOST = "127.0.0.1"

# docker_client = docker.from_env()
# available_ports = [port for port in range(8081, 9070)]
# servers = {}


# def start_docker_container(client_id):
#     print(f"Starting Docker container for client {client_id}")
#     container_name = f"non_auto_client-{client_id}"

#     if available_ports:
#         port = available_ports.pop(0)
#     else:
#         raise Exception("No available ports left")

#     container = docker_client.containers.run(
#         "docker-kv-store",
#         detach=True,
#         name=container_name,
#         ports={"80/tcp": port},
#         mem_limit="15m",
#         auto_remove=True,
#     )

#     servers[container.id] = f"http://{HOST}:{port}"
#     print(f"Container started for client {client_id} at {servers[container.id]}")
#     return container


# def client_ops(client_id, container_id, workload):
#     errors = 0
#     successes = 0
#     total_operation_time = 0
#     num_write, num_read, _ = workload
#     server_url = servers[container_id]

#     for i in range(num_write + num_read):
#         operation_start_time = time.time()

#         key = f"key-{client_id}-{i}"
#         value = f"value-{client_id}-{i}" if i < num_write else None

#         try:
#             if value:  # It's a write operation
#                 response = requests.put(
#                     f"{server_url}/store", params={"key": key}, data={"value": value}
#                 )
#                 print(f"Client {client_id} - Write operation for key: {key}")
#             else:  # It's a read operation
#                 response = requests.get(f"{server_url}/retrieve", params={"key": key})
#                 print(f"Client {client_id} - Read operation for key: {key}")

#             if response.status_code == 200:
#                 successes += 1
#             else:
#                 errors += 1

#         except Exception as e:
#             print(f"Error during operation for key {key}: {e}")
#             errors += 1

#         operation_end_time = time.time()
#         total_operation_time += operation_end_time - operation_start_time

#     avg_operation_time = (
#         total_operation_time / (num_write + num_read)
#         if (num_write + num_read) > 0
#         else 0
#     )
#     return errors, successes, avg_operation_time


# def client_thread(client_id, container_id, workload, result_lists):
#     print(f"Starting client thread {client_id}")
#     errors, successes, avg_operation_time = client_ops(
#         client_id, container_id, workload
#     )
#     result_lists["errors"].append(errors)
#     result_lists["successes"].append(successes)
#     result_lists["operation_times"].append(avg_operation_time)
#     print(
#         f"Finished client thread {client_id} with {successes} successes and {errors} errors"
#     )


# def run_clients():
#     print("Initializing run_clients")
#     container = start_docker_container(0)
#     time.sleep(2)

#     threads = []
#     result_lists = {
#         "errors": [],
#         "successes": [],
#         "operation_times": [],
#     }

#     with open("workload.txt", "r") as f:
#         workload = [
#             (int(n_write), int(n_read), float(rw_ratio))
#             for n_write, n_read, rw_ratio in [
#                 line.strip().split(" ") for line in f.readlines()
#             ]
#         ]

#     for client_id, wl in enumerate(workload):
#         thread = threading.Thread(
#             target=client_thread, args=(client_id, container.id, wl, result_lists)
#         )
#         threads.append(thread)
#         print(f"Starting thread for client {client_id}")
#         thread.start()

#     for thread in threads:
#         thread.join()

#     container.stop()
#     print("Stopped Docker container")

#     # Process and write results to CSV
#     latencies = [t for t in result_lists["operation_times"]]
#     throughputs = [
#         num_ops / t if t > 0 else 0
#         for num_ops, t in zip(
#             [wl[0] + wl[1] for wl in workload], result_lists["operation_times"]
#         )
#     ]
#     error_rates = [
#         e / num_ops
#         for e, num_ops in zip(
#             result_lists["errors"], [wl[0] + wl[1] for wl in workload]
#         )
#     ]

#     with open("non-autoscaling_client_metrics.csv", "w", newline="") as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(
#             [
#                 "Client ID",
#                 "NUM_READS",
#                 "NUM_WRITES",
#                 "READ_WRITE_RATIO",
#                 "Throughput",
#                 "Latency",
#                 "Error Rate",
#             ]
#         )
#         for i in range(len(throughputs)):
#             csvwriter.writerow(
#                 [
#                     i,
#                     workload[i][1],
#                     workload[i][0],
#                     workload[i][2],
#                     throughputs[i],
#                     latencies[i],
#                     error_rates[i],
#                 ]
#             )

#     # Write overall statistics
#     overall_stats_headers = [
#         "Metric",
#         "Mean Reads",
#         "Std Dev Reads",
#         "Variance Reads",
#         "Mean Writes",
#         "Std Dev Writes",
#         "Variance Writes",
#         "Mean RW Ratio",
#         "Std Dev RW Ratio",
#         "Variance RW Ratio",
#         "Mean Throughput",
#         "Std Dev Throughput",
#         "Variance Throughput",
#         "Mean Latency",
#         "Std Dev Latency",
#         "Variance Latency",
#         "Mean Error Rate",
#         "Std Dev Error Rate",
#         "Variance Error Rate",
#     ]
#     with open("non-autoscaling_overall_stats.csv", "w", newline="") as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(overall_stats_headers)
#         csvwriter.writerow(
#             [
#                 "Overall Stats",
#                 statistics.mean([wl[1] for wl in workload]),
#                 statistics.stdev([wl[1] for wl in workload]),
#                 statistics.variance([wl[1] for wl in workload]),
#                 statistics.mean([wl[0] for wl in workload]),
#                 statistics.stdev([wl[0] for wl in workload]),
#                 statistics.variance([wl[0] for wl in workload]),
#                 statistics.mean([wl[2] for wl in workload]),
#                 statistics.stdev([wl[2] for wl in workload]),
#                 statistics.variance([wl[2] for wl in workload]),
#                 statistics.mean(throughputs),
#                 statistics.stdev(throughputs),
#                 statistics.variance(throughputs),
#                 statistics.mean(latencies),
#                 statistics.stdev(latencies),
#                 statistics.variance(latencies),
#                 statistics.mean(error_rates),
#                 statistics.stdev(error_rates),
#                 statistics.variance(error_rates),
#             ]
#         )


# if __name__ == "__main__":
#     run_clients()
