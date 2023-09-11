Experiment with llama2 in gcp.

Scripts currently here assume you save the 7b llama2 model from the model garden to model registry in GCP
with the name llama2-7b-chat-001

To create an endpoint update relevant variables and run 

you need to be authenticated to your gcp account
```bash
gcloud auth application-default login
```


```bash
pip install -r requirements.local.txt
python ./scripts/create_llama_endpoint.py
```

To run the app locally with a mock llm

```bash
pip install -r requirements.xt
LLM_TYPE=mock python -m uvicorn llama_app.app:app
```

To run the app locally with llama hosted in Vertex AI you must be authenticated to gcp (see above) and set GCP configs
```bash
export PROJECT_ID=${PROJECT_ID:-108524135261}
export ENDPOINT_ID=${ENDPOINT_ID:-8443336706668625920}
export REGION=${REGION:-us-central1}
python -m uvicorn llama_app.app:app

```

To run integration tests

```bash
export PROJECT_ID=${PROJECT_ID:-108524135261}
export ENDPOINT_ID=${ENDPOINT_ID:-8443336706668625920}
export REGION=${REGION:-us-central1}
python -m pytest llama_app/tests/ --integration
```


Infrastructure

You can deploy the infrastructure with terraform, use terraform 1.5.7.
Using https://github.com/robertpeteuil/terraform-installer

./terraform-installer.sh -i 1.5.7