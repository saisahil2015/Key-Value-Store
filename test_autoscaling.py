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
import docker


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

# Initialize the Docker client
client = docker.from_env()

current_port = 8070


def launch_new_container():
    global current_port
    url = f"http://{HOST}:{current_port}"
    command = f"docker run -d -p {current_port}:80 docker-kv-store"
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    container_id = result.stdout.decode('utf-8')
    servers[container_id] = url 
    _servers.append((container_id,url))     
    current_port += 10


def run_all_servers(num_of_containers):
    for i in range(0, num_of_containers):
        launch_new_container()

    print(servers)
    return 0

def remove_all_containers():
    print("terminate and remove all containers...")
    for docker_id,_ in servers.items():
        stop_command = f"docker stop {docker_id}"
        rm_command = f"docker remove {docker_id}"
        subprocess.run(stop_command.split())
        subprocess.run(rm_command.split())


def get_resource_usage_prediction(num_read, num_write_, rw_ratio):
    # TODO model predicts the resource usage
    # output: cpu, memory usage prediction
    
    # FIX LATER: get random num of cpu and memory usage now
    predict_cpu = random.uniform(1, 100)
    predict_memory = random.uniform(1, 10000)

    print("required CPU usage: {:.2f}".format(predict_cpu))
    print(f"required Memory usage: {predict_memory}")
    return predict_cpu, predict_memory


def calculate_cpu_percent(d):
    print("--------------")
    print(d["cpu_stats"]["cpu_usage"])
    print("--------------")
    #cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0
    return cpu_percent


def no_space_in_container():
    # List all running containers
    containers = client.containers.list()

    required_cpu, required_memory = get_resource_usage_prediction(10, 90, 0.9)

    # Extract and print the names of running containers
    for container in containers:
        print("Container Name:", container.name)
        stats = container.stats(stream=False)

        cpu_percentage = calculate_cpu_percent(stats)
        # Extract CPU and memory usage information
        print("cpu usage: {:.2f}".format(cpu_percentage))

        memory_stats = stats['memory_stats']['usage']
        memory_stats_mb = memory_stats / (1024 * 1024)

        # Extract the memory limit (in bytes) from the container stats
        memory_limit = stats['memory_stats']['limit']
        # Convert the memory limit to megabytes for readability
        memory_limit_mb = memory_limit / (1024 * 1024)

        print(f"memory usage {memory_stats_mb} / {memory_limit_mb}")

        # FIX LATER
        if (cpu_percentage + required_cpu <= 100) and (memory_stats_mb + required_memory <= memory_limit_mb):
            print("There is space to work on task")
            print()
            return False
        print()
    
    print("Launch the new container!!")
    launch_new_container()
    print(servers)
    print()
    print()
    return True


def test_autoscaling():
    for i in range(0, 4):
        if no_space_in_container():
            launch_new_container()



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
    run_all_servers(1) 
    test_autoscaling()

    
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
