import requests
import threading
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1/transfer/"


AUTH_URL = "http://127.0.0.1:8000/api/token/"
LOGIN_DATA = {
    "email": "admin@cc.ru",
    "password": "123"
}

key = str(uuid.uuid4())


resp = requests.post(AUTH_URL, json=LOGIN_DATA)
resp.raise_for_status()
access_token = resp.json()["access"]

TO_USER_ID = 2
AMOUNT = "5.00"

def send_transfer():
    data = {
        "to_user_id": TO_USER_ID,
        "amount": AMOUNT,
        "idempotency_key": key
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(BASE_URL, json=data, headers=headers)
    
    print("Status code:", response.status_code)
    try:
        print("JSON:", response.json())
    except Exception as e:
        print("JSON decode error:", e)

threads = []
for _ in range(10):
    t = threading.Thread(target=send_transfer)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
