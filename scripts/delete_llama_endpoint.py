from google.cloud import aiplatform

if __name__ == "__main__":

    endpoint = aiplatform.Endpoint(
        project="sandbox-378304",
        location="us-central1",
        endpoint_name="llama2-70b-chat-001_endpoint"
    )

    print("Deleting Llama Endpoint...")
    endpoint.delete()
    print("Llama Endpoint deleted.")