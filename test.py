import requests

server_url = "http://127.0.0.1:8080"

key = 'asdfasd'
response = requests.put(f"{server_url}/set/{key}", data={"value": "111"})
print(response.json())

key='as'
response = requests.get(f"{server_url}/get/{key}")
print(response.json())