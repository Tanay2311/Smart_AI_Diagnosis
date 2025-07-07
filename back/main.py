from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from data.diagnosis_assistant import extract_symptoms, generate_diagnosis

app = FastAPI(
    title="Smart AI Medical Assistant Backend",
    description="FastAPI backend to extract symptoms and generate diagnosis using RAG + LLM",
    version="1.0.0"
)

# Allow frontend to call the backend (update origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Request Schema --------------------
class DiagnosisRequest(BaseModel):
    symptoms: str
    extra_input: Optional[str] = ""
    followup_answers: Dict[str, List[str]]

# -------------------- Endpoints --------------------
@app.get("/")
def root():
    return {"message": "Smart AI Medical Assistant backend is running."}

@app.post("/extract_symptoms")
def extract(symptom_text: str):
    extracted = extract_symptoms(symptom_text)
    return {"extracted_symptoms": extracted}

@app.post("/diagnose")
def diagnose(payload: DiagnosisRequest):
    extracted = extract_symptoms(payload.symptoms)
    result = generate_diagnosis(extracted, payload.followup_answers, payload.extra_input)
    return result
