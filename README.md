# Cloud-Computing-HW-2

### Intructions for Running the Program for Client-Side Consistent Hashing with Docker:

- Make sure to have the dependencies installed. We have a Pipfile/requirements.txt file that can be used to install necessary depdencies with the relevant pip/pipenv commands.
- Then run the following commands:
  - docker build -t docker-kv-store .
  - docker run -d -p 8070:80 docker-kv-store
  - docker run -d -p 8080:80 docker-kv-store
  - docker run -d -p 8090:80 docker-kv-store
  - python3 client.py
- Note: Use the client.py file by us as it's compatible with the server we have
