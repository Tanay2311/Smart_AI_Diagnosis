# models.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class DiagnosisRequest(BaseModel):
    symptoms: str
    extra_input: Optional[str] = ""
    followup_answers: Dict[str, List[str]]
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None


class DiagnosisResponse(BaseModel):
    disease: str
    description: str
    treatment: str
    risk_factors: str
