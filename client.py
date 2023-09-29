import requests
import time
import threading

HOST, PORT = "127.0.0.1", 5000
BASE_URL = f"http://{HOST}:{PORT}"
NUM_REQUESTS = 1000  # Number of requests to send per client
NUM_CLIENTS = 10  # Number of concurrent clients

throughputs = []
latencies = []


def client_thread(client_id):
    # Start time
    start_time = time.time()

    for i in range(NUM_REQUESTS):
        key = f"key-{client_id}-{i}"
        value = f"value-{client_id}-{i}"

        # PUT request
        requests.put(f"{BASE_URL}/store", data={"key": key, "value": value})

        # GET request
        requests.get(f"{BASE_URL}/retrieve", data={"key": key})

        # DEL request
        requests.delete(f"{BASE_URL}/remove", data={"key": key})

    # End time
    end_time = time.time()

    elapsed_time = end_time - start_time
    throughput = NUM_REQUESTS * 3 / elapsed_time  # Multiply by 3 for PUT, GET, DEL
    throughputs.append(throughput)
    latency = elapsed_time / (NUM_REQUESTS * 3)  # Average latency per request
    latencies.append(latency)

    print(
        f"Client-{client_id} | Throughput: {throughput:.2f} req/s | Average Latency: {latency:.6f} seconds"
    )


if __name__ == "__main__":
    clients = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_thread, args=(i,))
        clients.append(t)
        t.start()

    for t in clients:
        t.join()

    print("Overall Throughput: ", sum(throughputs) / NUM_CLIENTS)
    print("Overall Latency: ", sum(latencies) / NUM_CLIENTS)

    print("Testing completed.")
