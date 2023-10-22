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
import subprocess
import signal


HOST, PORT = "127.0.0.1", 80
#BASE_URL = f"http://{HOST}:{PORT}"
# NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 10  # 10 # Number of concurrent clients

throughputs = []
latencies = []


combinations = [
    "RI",
    "WI",
    "B",
]  # for each case, have varied sizes of keys/values to have large/small keys/values

writeOps = ["Put", "Delete"]

servers = {}
_servers = []
task_in_servers = {}
server_available = threading.Condition()


url0 = f"http://{HOST}:8080"
url1 = f"http://{HOST}:8081"
url2 = f"http://{HOST}:8082"

def run_all_servers(num_of_containers):
    first_port = 8080
    for i in range(0, num_of_containers):
        port_num = first_port + i
        url = f"http://{HOST}:{port_num}"
        command = f"docker run -d -p {port_num}:80 docker-kv-store"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        container_id = result.stdout.decode('utf-8')
        servers[container_id] = url
        _servers.append((container_id,url))
        task_in_servers[container_id] = True

    print(servers)
    return 0

def remove_all_containers():
    print("terminate and remove all containers...")
    for docker_id,_ in servers.items():
        stop_command = f"docker stop {docker_id}"
        rm_command = f"docker remove {docker_id}"
        subprocess.run(stop_command.split())
        subprocess.run(rm_command.split())


def get_config_prediction(num_read, num_write, r_w_ratio):
    # TODO model implementation
    # output: cpu, memory usage prediction
    return 0


def change_docker_config(server, cpu, memory, memory_swap):
    
    command = f"docker update --memory={memory} --memory-swap={memory_swap} --cpuset-cpus={cpu} {server}"
    subprocess.run(command.split())

    return 0

def get_random_server():
    return random.choice(_servers)


def _url0(client_id, s_id):
    global url0
    save_url = url0

    with server_available:
        while url0 is None:
            server_available.wait()

        url0 = None
        print(f"client {client_id} task STARTS on {servers[s_id]}")

        time.sleep(3)
        # config_prediction impelemented here

        change_docker_config(s_id, 1, "500MB", "600MB")

        client_ops(client_id, url0)

        print(f"client {client_id} task is COMPLETED on {servers[s_id]}")
        url0 = save_url
        server_available.notify()

def _url1(client_id, s_id):
    global url1
    
    save_url = url1

    with server_available:
        while url1 is None:
            server_available.wait()

        url1 = None
        print(f"client {client_id} task STARTS on {servers[s_id]}")

        time.sleep(3)
        # config_prediction impelemented here

        change_docker_config(s_id, 1, "500MB", "600MB")

        client_ops(client_id, url1)

        print(f"client {client_id} task is COMPLETED on {servers[s_id]}")
        url1 = save_url
        server_available.notify()

def _url2(client_id, s_id):
    global url2

    save_url = url2

    with server_available:
        while url2 is None:
            server_available.wait()

        url2 = None
        print(f"client {client_id} task STARTS on {servers[s_id]}")

        time.sleep(3)
        # config_prediction impelemented here

        change_docker_config(s_id, 1, "500MB", "600MB")

        client_ops(client_id, url2)

        print(f"client {client_id} task is COMPLETED on {servers[s_id]}")
        url2 = save_url
        server_available.notify()

def task_on_server2(client_id):
    s_id, s_url = get_random_server()

    if s_url == url0:
        _url0(client_id, s_id)
    elif s_url == url1:
        _url1(client_id, s_id)
    else:
        _url2(client_id, s_id)


def task_on_server(client_id):
    global task_in_servers, url0, url1, url2


    s_id, s_url = get_random_server()
    server_found = False
    server_id = None
    #print(client_id, task_in_servers)

    with server_available:
        while task_in_servers[s_id] is False:
            server_available.wait()

        '''
        while not server_found:
            for _id, avail in task_in_servers.items():
                if avail:
                    server_found = True
                    server_id = _id
                    task_in_servers[_id] = False
                    print(client_id, " server found")
                    break
            if server_found:
                break
            server_available.wait()
        '''
        print(f"client {client_id} task STARTS on {servers[s_id]}")
        task_in_servers[s_id] = False

        time.sleep(3)
        # config_prediction impelemented here

        change_docker_config(s_id, 1, "500MB", "600MB")

        client_ops(client_id, s_url)

        task_in_servers[s_id] = True
        print(f"client {client_id} task is COMPLETED on {servers[s_id]}")
        server_available.notify_all()




def run_on_available_server(client_id):
    global task_in_servers

    with server_available:
        server_found = False
        server_id = None
        print(client_id, task_in_servers)
        while not server_found:
            for _id, avail in task_in_servers.items():
                if avail:
                    server_found = True
                    server_id = _id
                    task_in_servers[_id] = False
                    print(client_id, " server found")
                    break
            if server_found:
                break
            server_available.wait()
        print(f"client {client_id} task STARTS on {servers[server_id]}")
        task_in_servers[server_id] = False

        time.sleep(3)
        # config_prediction impelemented here
        
        change_docker_config(server_id, 1, 100, 200)
        
        client_ops(client_id, servers[server_id])

        task_in_servers[server_id] = True
        print(f"client {client_id} task is COMPLETED on {servers[server_id]}")
        server_available.notify()




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

    num_read, num_write, throughput, latency = client_ops(client_id, None)

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
        "num_read": num_read,
        "num_write": num_write,
        "read_write_ratio": num_read / num_write,
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


def client_ops(client_id, url):
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
        #print("write")
        value = generate_random_string(random.randint(1, 100))
        requests.put(f"{url}/store", data={"key": key, "value": value})
        # else:
        #     print("delete")
        #     requests.delete(f"{url}/remove", data={"key": key})

    for j in range(NUM_READ_REQUESTS):
        # print("CHECK Retrive")
        seed = f"key-{client_id}-{j}"
        key = generate_random_string(random.randint(1, 100), seed)
        requests.get(f"{url}/retrieve", data={"key": key})

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

    return NUM_READ_REQUESTS, NUM_WRITE_REQUESTS, throughput, latency


def custom_interrupt_handler(signum, frame):
    print('ctrl+c pressed')
    remove_all_containers()


if __name__ == "__main__":
    clients = []
    
    run_all_servers(3)
    # Set the custom handler for Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, custom_interrupt_handler)

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=task_on_server, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    
    '''
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    print("Overall Throughput: ", sum(throughputs) / len(throughputs))
    print("Overall Latency: ", sum(latencies) / len(latencies))

    print("Testing completed.")
    '''

    remove_all_containers()
