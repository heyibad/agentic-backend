from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Agentic Backend")


class PredictRequest(BaseModel):
    prompt: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(req: PredictRequest):
    # Placeholder implementation: echo the prompt back as a fake "prediction".
    # Replace this with real agent logic.
    return {"input": req.prompt, "output": f"Echo: {req.prompt}"}
