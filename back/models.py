# backend/models.py
from pydantic import BaseModel
from typing import List, Optional

class DiagnosisRequest(BaseModel):
    symptoms_text: str
    age: int
    gender: str
    followup_answers: Optional[List[str]] = []

class DiagnosisResponse(BaseModel):
    disease: str
    description: str
    treatment: str
    risk_factors: str
