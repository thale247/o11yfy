import time
import random
import requests

BASE_URL = "http://localhost:8000"

endpoints = [
    "/fast",
    "/slow",
    "/spiky",
    "/error",
    "/mixed"
]

def hit():
    endpoint = random.choice(endpoints)
    url = BASE_URL + endpoint

    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        duration = time.time() - start

        print(f"{endpoint} -> {r.status_code} ({duration:.2f}s)")
    except Exception as e:
        print(f"{endpoint} -> ERROR ({e})")

if __name__ == "__main__":
    while True:
        hit()

        # variable load
        time.sleep(random.uniform(0.1, 0.5))