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

To run the app

```
pip install -r requirements.xt
python ./llama_app/app.py
```
