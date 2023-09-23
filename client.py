import requests


def getValue():
    key = "Sahil"
    response = requests.get(f"http://127.0.0.1:5000/get/{key}", timeout=20)
    print(response.text)


if __name__ == "__main__":
    getValue()
