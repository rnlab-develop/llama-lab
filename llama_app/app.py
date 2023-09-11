from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import os

from llama_app.llm import GCPLlamaService, MockLLMService, Prompt, VertexConfig

app = FastAPI()

app.mount("/static", StaticFiles(directory="./llama_app/static"), name="static")

PROJECT_ID = os.environ.get("PROJECT_ID")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
REGION = os.environ.get("REGION")

if not (PROJECT_ID and ENDPOINT_ID and REGION):
    raise Exception(
        "PROJECT_ID, ENDPOINT_ID, and REGION must be set as environment variables"
    )


if os.getenv("LLM_TYPE") == "mock":
    llm = MockLLMService()
else:
    config = VertexConfig(project_id=PROJECT_ID, endpoint_id=ENDPOINT_ID, region=REGION)
    llm = GCPLlamaService(config)


@app.post("/predict")
async def predict(prompt: Prompt):
    try:
        response = llm.predict({"instances": [prompt]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


@app.get("/liveness")
def liveness():
    return True


# at root redirect to /static/index.html
@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
