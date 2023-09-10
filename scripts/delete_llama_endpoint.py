from google.cloud import aiplatform

if __name__ == "__main__":

    endpoint = aiplatform.Endpoint(endpoint_name="llama2")

    print("Deleting Llama Endpoint...")
    endpoint.delete()
    print("Llama Endpoint deleted.")