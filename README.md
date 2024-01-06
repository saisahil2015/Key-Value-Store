# Key-Value Store Projects

This repository contains two projects that are thematically related as they focus on experimenting with the Key Value Store.

## Project 1: Performance Optimization with Fixed Containers (Python, Go, Rust)

**Objective**: Improved the key-value store's performance, particularly throughput and latency, when operating with a fixed configuration of three containers.

**Evolution**:
- Initial Version: Implemented in Python (tag: `v.1.0`)
- Final Version: Reimplemented and optimized using Go and Rust for enhanced performance

**Final Version Branch**: `main`

## Instructions for Running the Go Programs for Client-Side Consistent Hashing:

- Navigate to the kv-store folder
- Run the files using the following command: go run "file name" "port"
  - The primary file is the main2.go file
- Make sure to activate the virtual environment using "pipenv shell" and then run the following command to install all dependencies in the environment: "pipenv install"
- Run python3 client.py then

## Intructions for Rust version

- Make sure rust and cargo is installed, if not, here is the guide to install
  https://doc.rust-lang.org/book/ch01-01-installation.html

### Rust with in-memory storage

```shell
cd rust-kv
cargo build
cargo run
```

### Rust with sleb db

```shell
cd rust-kv-sleb
cargo build
cargo run
```

### Run the client file

```shell
python3 client.py
```

### Results

When we ran this project in the same lab environment as the other teams in the class, we achieved an overall **throughput of 25,588 operations per second and a latency of 2.9 ms, ranking us third amongst the eight teams.**

## Project 2: Autoscaling vs. Non-Autoscaling Experiment (Python)

**Objective**: Devised and implemented various autoscaling algorithms, along with integrated failure prevention mechanisms, for our key-value store and experimented with their performance. We rigorously tested and compared these autoscaling solutions against the non-autoscaling algorithm to understand their impact on handling workloads effectively.

**Final Version Branch**: `autoscaling_fixes`

**[Final Project Report](https://drive.google.com/file/d/1oHDnzIs7KBM8oSlmksqgZfMUVVDrQd7g/view?usp=sharing)**

**Timeline of Both the Projects:** September 2023 - December 2023

**Contributors for both the projects:** Sahil Raina, Jingxian Chai, Shunichi Sawamura

