import requests

url = "http://localhost:8080"
key = 'asd'
value = 'qwe'

res = requests.put(f"{url}/store", params={"key": key}, data={"value": value})
print(res.json())

res = requests.get(f"{url}/retrieve", params={"key": key})
print(res.json())