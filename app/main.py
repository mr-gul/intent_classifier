from fastapi import FastAPI

from app.schemas import PredictionRequest
from app.model import predict_intent


app = FastAPI(
    title="Intent Classification API",
    description="ML API for classifying user intents",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Intent Classification API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/predict")
def predict(request: PredictionRequest):

    intent, confidence = predict_intent(request.text)

    return {
        "text": request.text,
        "intent": intent,
        "confidence": round(float(confidence), 4)
    }