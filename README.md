# Cloud-Computing-HW-2

### Intructions for Running the Program:

- Make sure to have the dependencies installed. We have a Pipfile/requirements.txt file that can be used to install necessary depdencies with the relevant pip/pipenv commands.
- Use the client.py file by us and make any modifications to it if necessary as it's been made compatible with Flask

### Instructions for Containerization:

- Make sure the docker daemon is open and running
- Run the following commands:
  - docker build -t docker-kv-store .
  - docker run -d -p 80:80 docker-kv-store
  - python3 client.py

### Instructions for Nginx:

- Make sure Nginx is installed
- To start Nginx, run the following commands

  ```bash
  nginx -c <configuration file location>
  ```

  - Replace **configuration file location** with your own configuration file location.
  - Make sure that you pull the `consistent_hashing.conf` file from this repository, and use that to start Nginx.

- To stop Nginx,
  ```bash
  nginx -s quit
  ```

### Instructions for testing (coding assignment 2):

- `in-memory-kv.py` - in-memory key value store

  to start the key value store run the following command, and provide the port and a log file location

  ```
  python3 in-memory-kv.py --port 8080 --log app-8080.log
  ```

- `new_client.py` - client test

  to test multiple settings all at once and output the collected data into a json file, run

  ```
  python3 new_client.py --filename 3kv-nginx-fix-op-var-proc.json
  ```

  to run one setting, run the following command, and provide number of request and number of processes

  ```
  python3 client_new.py --n_ops 100 --n_proc 2
  ```

- Make sure the Nginx configuration file specify 3 connections on the port the docker containers are using. For example in the code below, port `8080`, `8081`, `8082` are used as 3 key value stores.

  ```
    upstream loadbalance {
      hash $arg_key consistent;
      server localhost:8080;
      server localhost:8081;
      server localhost:8082;
    }
  ```

  - To test with fewer key value store, comment out the unused connection

- Make sure to specify the location of the log to `access_log` in the Nginx configuration, for example:

  ```
  access_log /Users/jingxian/code/5980/kv-store/access.log upstreamlog;
  ```

  or optionally turn off the log

  ```
  access_log off;
  ```
