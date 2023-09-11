import requests
from google.auth import default
from google.auth.transport import requests as grequests

import pytest

PROJECT_ID = 108524135261

def get_gcs_token():
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
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

@pytest.mark.integration
def test_list_gcs_buckets():
    response = list_gcs_buckets()
    assert response.status_code == 200, f"Failed to list buckets: {response.status_code} - {response.text}"
    assert 'items' in response.json(), "Response JSON does not contain 'items'"