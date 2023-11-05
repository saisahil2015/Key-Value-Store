# Cloud-Computing-HW-1

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

- Run 3 key value store containers

  ```bash
  docker run -d --name kv1 -p 8070:80 docker-kv-store
  docker run -d --name kv2 -p 8080:80 docker-kv-store
  docker run -d --name kv3 -p 8090:80 docker-kv-store
  ```

- Make sure the Nginx configuration file specify 3 connections on the port the docker containers are using. For example in the code below, port `8070`, `8080`, `8090` are used as 3 key value stores.

  ```
    upstream loadbalance {
      hash $arg_key consistent;
      server localhost:8070;
      server localhost:8080;
      server localhost:8090;
    }
  ```

  - To test with fewer key value store, comment out the unused connection

- Make sure to specify the location of the log to `access_log` in the Nginx configuration, for example:

  ```
  access_log /Users/jingxian/code/5980/kv-store/access.log upstreamlog;
  ```

- Optional: stop the docker containers and stop Nginx
  ```
  docker stop kv1 kv2 kv3
  docker rm kv1 kv2 kv3
  nginx -s quit
  ```
