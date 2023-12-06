# this file is for generating workloads for actually testing the autoscaling vs non-autoscaling
# new_client.py used for generating generating workloads and related metrics for training the models used for autoscaling

import random

combinations = ["RI", "WI", "B"]


def generate_workload(n=100):
    arr = []

    for _ in range(n):
        combination = random.choice(combinations)
        NUM_REQUESTS = random.randint(150, 10000)
        NUM_WRITE_REQUESTS, NUM_READ_REQUESTS = 0, 0

        if combination == "RI":
            NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.9)
            NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
        elif combination == "WI":
            NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.1)
            NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS
        elif combination == "B":
            NUM_READ_REQUESTS = round(NUM_REQUESTS * 0.5)
            NUM_WRITE_REQUESTS = NUM_REQUESTS - NUM_READ_REQUESTS

        arr.append(
            (
                NUM_WRITE_REQUESTS,
                NUM_READ_REQUESTS,
                NUM_READ_REQUESTS / NUM_WRITE_REQUESTS,
            )
        )

    return arr


if __name__ == "__main__":
    workload = generate_workload()

    # output on file
    with open("new_workload.txt", "w") as f:
        for n_write, n_read, rw_ratio in workload:
            f.write(f"{n_write} {n_read} {rw_ratio}\n")
