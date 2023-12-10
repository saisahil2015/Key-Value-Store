import multiprocessing
import docker
import time
import random

# globals
HOST = "localhost"
available_ports = [port for port in range(8080, 9080)]

# docker client
docker_client = docker.from_env()

def start_containers(n):
    '''
        starting up with n containers,
        return hash ring config
    '''
    hash_ring_config = {}

    # launch containers
    for _ in range(n):
        current_port = available_ports.pop(0)
        container = docker_client.containers.run(
            "docker-kv-store",
            detach=True,
            ports={"80/tcp": current_port},
        )

        print(f"container {container.name} is running on port {current_port}")

        hash_ring_config[container.name] = {
            "port": current_port,
            "vnodes": 4,
        }

    return hash_ring_config

def add_container():
    '''
        add a new container to the hash ring
    '''
    # lock the hash ring
    # add the new container to the hash ring
    # unlock the hash ring
    pass

def health_check(hash_ring, status_queue):
    '''
        check all containers status, return a list of unhealthy containers
    '''
    while True:
        queue = []

        print("checking containers")
        for container_name in hash_ring.keys():
            container = docker_client.containers.get(container_name)
            if container.status != "running":
                print(f"container {container_name} is unhealthy")
                del hash_ring[container_name]
                queue.append(container_name)
                # status_queue.put(container_name)

        if len(queue) > 0:
            for _ in range(len(queue)):
                container_name = queue.pop(0)
                print(f"removing container {container_name}")

        print("=====================================")
        time.sleep(2)   # check every 2 seconds

def recover_container(container_name, hash_ring):
    '''
        recover a unhealthy container
        
        get its replicas from the hash ring, adjust hash ring, redistribute the keys
    '''
    # get the nodes and its replicas
    replicas = hash_ring.get_replicas(container_name)

    # lock the hash ring
    # get the keys of the unhealthy container from its replicas
    # remove the unhealthy container from the hash ring

    # redistribute the keys to the new hash ring

    # unlock the hash ring
    pass

def inject_fault(hash_ring):
    '''
        inject fault to a random container
    '''
    # get a random container
    nodes = hash_ring.keys()
    l = len(nodes)
    index = random.randint(0, l-1)
    container_name = nodes[index]

    # stop the container
    container = docker_client.containers.get(container_name)
    print(f"stopping container {container.name}")
    container.stop()

def remove_all_containers(hash_ring):
    '''
        remove all containers
    '''
    # remove all containers
    for container_name in hash_ring.keys():
        container = docker_client.containers.get(container_name)
        container.remove(force=True)
    print("finish removing all containers")

def workload(hash_ring):
    '''
        workload for testing
    '''

    nodes = hash_ring.keys()
    container = docker_client.containers.get(nodes[0])
    print(f"stopping container {container.name}")
    container.stop()

if __name__ == "__main__":
    # start up
    hash_ring_config = start_containers(2)
    time.sleep(4)

    # create a new process for health check
    manager = multiprocessing.Manager()
    status_queue = manager.Queue()

    hash_ring = manager.dict(hash_ring_config)

    health_check_process = multiprocessing.Process(target=health_check, args=(hash_ring, status_queue,))
    health_check_process.start()

    # inject fault
    time.sleep(3)
    inject_fault(hash_ring)

    # question: do i create another process for status queue? or just do it here?
    # if there is a unhealthy container, recover it here

    time.sleep(6)
    health_check_process.terminate()
    print("finish checking containers")

    # remove containers
    remove_all_containers(hash_ring_config)