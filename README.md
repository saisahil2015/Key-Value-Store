# Instructions for Testing Autoscaling and Non-Autoscaling Algorithms

- Run `test.py` to test the autoscaling, without fault-prevention mechanism, and non-autoscaling algorithms using different types of workloads.
- To test the autoscaling algorithm with integrated fault prevention mechanism, need to first run `test_autoscaling_with_fault_recovery.py` and then run `test_fault.py` 
- **Note:** Make sure to have docker engine installed and build the docker image before testing using the following command: `docker build -t docker-kv-store .`
