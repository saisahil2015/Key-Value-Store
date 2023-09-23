import requests

url = "http://127.0.0.1:5000"


response = requests.get("{}/retrieve".format(url), data={'key':3})
print(response.json())

response = requests.put("{}/store".format(url), data={'key':3, 'value':30})
print(response.json())

response = requests.put("{}/store".format(url), data={'key':1, 'value':10})
print(response.json())

response = requests.put("{}/store".format(url), data={'key':1, 'value':100})
print(response.json())

response = requests.get("{}/retrieve".format(url), data={'key':1})
print(response.json())

response = requests.delete("{}/remove".format(url), data={'key':1})
print(response.json())


response = requests.delete("{}/remove".format(url), data={'key':1})
print(response.json())


response = requests.get("{}/retrieve".format(url), data={'key':1})
print(response.json())
