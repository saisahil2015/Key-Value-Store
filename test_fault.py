# get all keys and values
# shut down the container (dont relaunch it)
# test all the key value it got (this should be success from replica node)

import requests
import argparse
import docker
import time

if __name__ == "__main__":
    docker_client = docker.from_env()

    parser = argparse.ArgumentParser()
    parser.add_argument("--p", help="port", type=int, default=8080)
    parser.add_argument("--name", help="container anem", type=str)

    args = parser.parse_args()
    port = args.p
    container_name = args.name

    # get all keys and values
    all_kvs = None
    response = requests.get(f"http://localhost:{port}/get_all", params={"mode": "primary"})
    if response.status_code == 200:
        all_kvs = response.json()
        print(f"Received {len(all_kvs.keys())} keys value pairs")

        for key, value in all_kvs.items():
            print(f"{key} {value}")
    else:
        print("Error getting all keys and values")
        exit(1)

    print("Stopping container")
    container = docker_client.containers.get(container_name)
    container.stop()

    while True:
        user_input = input("Enter 'y' to start testing: ")
        if user_input == "y":
            break
        else:
            print("Invalid input")
    
    # test all the key value
    print("testing all keys and values")
    success_count = 0 
    error_count = 0
    for key, value in all_kvs.items():
        response = requests.get(f"http://localhost:{port}/retrieve", params={"key": key})
        if response.status_code == 200 and response.json()["value"] == value:
            print(f"Success: {key} {value}")
            success_count += 1
        else:
            print(f"Error: {key} {value}, {response.status_code}, {response.json()}")
            error_count += 1

    print(f"Success: {success_count}, Error: {error_count}")
    print("Test complete")