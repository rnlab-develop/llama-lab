from google.auth import default
import requests
from google.auth.transport import requests as grequests
import os

PROJECT_ID = os.environ.get("PROJECT_ID")

def get_gcs_token():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"], quota_project_id=PROJECT_ID)
    auth_request = grequests.Request()
    creds.refresh(auth_request)
    return creds.token

def list_gcs_buckets():
    project_id = PROJECT_ID  # Replace with your actual GCP project ID
    url = f"https://storage.googleapis.com/storage/v1/b?project={project_id}"
    headers = {
        "Authorization": f"Bearer {get_gcs_token()}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    return response

if __name__ == "__main__":
    response = list_gcs_buckets()
    print(response)