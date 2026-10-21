from pydantic import BaseModel
class PredictionRequest(BaseModel):
    text: str