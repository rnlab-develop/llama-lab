from google.cloud import aiplatform

if __name__ == "__main__":

    endpoints = aiplatform.Endpoint.list(filter="display_name=llama2-7b-chat-001_endpoint")
    endpoint = endpoints[0]

    print("Deleting Llama Endpoint...")
    endpoint.delete(force=True)
    print("Llama Endpoint deleted.")