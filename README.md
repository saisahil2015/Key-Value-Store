# Cloud-Computing-HW-1

Intructions for Running the Program:

- Make sure to have the dependencies installed. We have a Pipfile/requirements.txt file that can be used to install necessary depdencies with the relevant pip/pipenv commands.
- Use the client.py file by us and make any modifications to it if necessary as it's been made compatible with Flask

Instructions for Containerization:

- Make sure the docker daemon is open and running
- Run the following commands:
  - docker build -t docker-kv-store .
  - docker run -d -p 80:80 docker-kv-store
  - python3 client.py
