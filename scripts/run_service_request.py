import requests

# URL of the FastAPI endpoint
url = "http://127.0.0.1:8000/predict"

# JSON payload that needs to be sent
payload = {"prompt": "What are marge simpson's husband's name?"}

# Headers
headers = {"Content-Type": "application/json"}

# Sending a POST request to the FastAPI endpoint
response = requests.post(url, json=payload, headers=headers)

# Checking if the request was successful
if response.status_code == 200:
    print("Request was successful!")
    print("Response JSON: ")
    print(response.json())
else:
    print(response.text)
    print(f"Failed to make request, status code: {response.status_code}")
