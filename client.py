import requests
import time
import threading
import random
import string
import cProfile
import pstats
from memory_profiler import memory_usage
import io
import psutil
import os
from queue import Queue


HOST, PORT = "127.0.0.1", 80
BASE_URL = f"http://{HOST}:{PORT}"
# NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 500  # 10 # Number of concurrent clients

throughputs = []
latencies = []


combinations = [
    "RI",
    "WI",
    "B",
]  # for each case, have varied sizes of keys/values to have large/small keys/values

writeOps = ["Put", "Delete"]


def generate_random_string(
    k,
    seed=None,
):
    random.seed(seed)

    return "".join(random.choice(string.ascii_letters) for _ in range(k))


def client_thread(client_id):
    # print(f"Thread {client_id} started")
    pr = cProfile.Profile()
    pr.enable()

    process = psutil.Process(os.getpid())
    before_memory = process.memory_info().rss / 1024 / 1024  # Convert bytes to MB

    throughput, latency = client_ops(client_id)

    after_memory = process.memory_info().rss / 1024 / 1024  # Convert bytes to MB

    pr.disable()

    s = io.StringIO()
    stats = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(pstats.SortKey.TIME)
    stats.print_stats()

    max_memory_used = after_memory - before_memory
    print(f"Client-{client_id} | Max Memory Used: {max_memory_used:.2f} MB")

    total_tottime = 0
    total_cumtime = 0
    total_calls = 0

    # Loop through all recorded function stats
    for func_name, func_stats in stats.stats.items():
        cc, nc, tottime, cumtime, callers = func_stats

        total_tottime += tottime
        total_cumtime += cumtime
        total_calls += cc  # considering primitive calls

    overall_percall_tottime = total_tottime / total_calls if total_calls != 0 else 0
    overall_percall_cumtime = total_cumtime / total_calls if total_calls != 0 else 0

    print(f"Client {client_id} | Overall Total Time: {total_tottime}")
    print(f"Client {client_id} | Overall Cumulative Time: {total_cumtime}")
    print(
        f"Client {client_id} | Overall Total Time Per Call: {overall_percall_tottime}"
    )
    print(
        f"Client {client_id} | Overall Cumulative Time Per Call: {overall_percall_cumtime}"
    )

    metrics = {
        "client_id": client_id,
        "max_memory_used": max_memory_used,
        "cpu_total_tottime": total_tottime,
        "cpu_total_cumtime": total_cumtime,
        "cpu_percall_tottime": overall_percall_tottime,
        "cpu_percall_cumtime": overall_percall_cumtime,
        "throughput": throughput,
        "latency": latency,
    }

    response = requests.post(f"{BASE_URL}/metrics", json=metrics)
    if response.status_code == 201:
        print(f"Client-{client_id} | Metrics successfully sent to the server.")
    else:
        print(f"Client-{client_id} | Failed to send metrics to server: {response.text}")


def client_ops(client_id):
    start_time = time.time()
    # print(f"Client {client_id} operations started")

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
        print("write")
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

    end_time = time.time()
    elapsed_time = end_time - start_time
    throughput = NUM_REQUESTS / elapsed_time
    latency = elapsed_time / NUM_REQUESTS
    throughputs.append(throughput)
    latencies.append(latency)

    # print(f"Client {client_id} operations ended")

    print(
        f"Client-{client_id} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds"
    )

    return throughput, latency


if __name__ == "__main__":
    clients = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    print("Overall Throughput: ", sum(throughputs) / len(throughputs))
    print("Overall Latency: ", sum(latencies) / len(latencies))

    print("Testing completed.")
