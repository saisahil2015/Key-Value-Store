# Auto Scaling Key-Value Stores with Integrated Failure Prevention Mechanisms

**Objective:** Devised and implemented various autoscaling algorithms, along with integrated failure prevention mechanisms, for our key-value store and experimented with their performance. We rigorously tested and compared these autoscaling solutions against the non-autoscaling algorithm to understand their impact on handling workloads effectively.

# Instructions for Testing Autoscaling and Non-Autoscaling Algorithms

- Run `test.py` to test the autoscaling, without fault-prevention mechanism, and non-autoscaling algorithms using different types of workloads.
- To test the autoscaling algorithm with integrated fault prevention mechanism, need to first run `test_autoscaling_with_fault_recovery.py` and then run `test_fault.py` 
- **Note:** Make sure to have docker engine installed and build the docker image before testing using the following command: `docker build -t docker-kv-store .`


**[Final Project Report](https://drive.google.com/file/d/1oHDnzIs7KBM8oSlmksqgZfMUVVDrQd7g/view?usp=sharing)**

**Timeline of the Project:** September 2023 - December 2023

**Contributors for the project:** Sahil Raina, Jingxian Chai, Shunichi Sawamura
