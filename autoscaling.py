import subprocess
import docker
import random
from hashring import HashRing
import string
import requests

# globals
HOST = "localhost"
combinaitons = ["RI", "WI", "B"]

available_ports = [port for port in range(8070, 8091)]
servers = {}                            # container_id: url
available_servers = []                  # url
ring = HashRing(available_servers)      # hash ring

# docker client
docker_client = docker.from_env()

def launch_new_container():
    current_port = available_ports.pop(0)
    url = f"http://{HOST}:{current_port}"

    command = f"docker run -d -p {current_port}:80 docker-kv-store"
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    container_id = result.stdout.decode('utf-8')

    servers[container_id] = url
    available_servers.append(url)
    print(f"Avaliable servers: {available_servers}")

    # update new hash ring, TODO: need lock mechinaism
    global ring
    ring = HashRing(available_servers)

    # TODO: redistribute the key value pairs among the new hash ring

def get_resource_usage_prediction(num_read, num_write_, rw_ratio):
    # output: cpu, memory usage prediction
    # rf_model = joblib.load('models/rf.joblib')
    # prediction = rf_model.predict([[num_read, num_write, r_w_ratio]])
    predict_cpu = random.uniform(1, 100)
    predict_memory = random.uniform(1, 10000)
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

def no_space_in_container(num_write, num_read, rw_ratio):
    # List all running containers
    containers = docker_client.containers.list()

    required_cpu, required_memory = get_resource_usage_prediction(num_read, num_write, rw_ratio)

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

def generate_random_string(
    k,
    seed=None,
):
    random.seed(seed)

    return "".join(random.choice(string.ascii_letters) for _ in range(k))

def workload(workload_id):
    # generate a type of workload (read-intensive, write-intensive, balanced)
    combination = random.choice(combinaitons)
    NUM_REQUESTS = random.randint(1, 100)  # Can increase this to max
    NUM_WRITE_REQUESTS = 0
    NUM_READ_REQUESTS = 0
    RW_RATIO = 0

    if combination == "RI":
        NUM_READ_REQUESTS = round((NUM_REQUESTS * 0.9))
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
        RW_RATIO = 0.9

    elif combination == "WI":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.1)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
        RW_RATIO = 0.1

    elif combination == "B":
        NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.5)
        NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
        RW_RATIO = 0.5

    # predict the container cpu and memory usage
    # launch new container if needed
    # if no_space_in_container(NUM_WRITE_REQUESTS, NUM_READ_REQUESTS, RW_RATIO):
    #     launch_new_container()

    # handle workload
    print("handling workload...")
    for i in range(NUM_WRITE_REQUESTS):
        key = f"key-{workload_id}-{i}"
        value = generate_random_string(random.randint(1, 100))

        url = ring.get_node(key)
        print('url: ', url)
        requests.put(f"{url}/store", params={"key": key}, data={"value": value})

    for j in range(NUM_READ_REQUESTS):
        key = f"key-{workload_id}-{j}"
        
        url = ring.get_node(key)
        requests.get(f"{url}/retrieve", params={"key": key})
    pass

def remove_all_containers():
    print("terminate and remove all containers...")
    for docker_id,_ in servers.items():
        stop_command = f"docker stop {docker_id}"
        rm_command = f"docker remove {docker_id}"
        subprocess.run(stop_command.split())
        subprocess.run(rm_command.split())

if __name__ == '__main__':
    # run one container
    launch_new_container()

    # workload
    for i in range(1):
        workload(i)

    # remove all containers
    remove_all_containers()