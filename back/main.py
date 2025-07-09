from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from data.diagnosis_assistant import extract_symptoms, generate_diagnosis, follow_up_map
from models import DiagnosisRequest
from data.condition_info_loader import condition_database
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exception_handlers import request_validation_exception_handler



app = FastAPI(
    title="Smart AI Medical Assistant Backend",
    description="FastAPI backend to extract symptoms and generate diagnosis using RAG + LLM",
    version="1.0.0"
)

# Allow frontend to call the backend (update origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Request Schema --------------------
class SymptomInput(BaseModel):
    text: str

class ConditionQuery(BaseModel):
    conditions: List[str]



# -------------------- Endpoints --------------------
@app.get("/")
def root():
    return {"message": "Smart AI Medical Assistant backend is running."}

@app.post("/extract_symptoms")
def extract(payload: SymptomInput):
    extracted = extract_symptoms(payload.text)
    return {"extracted_symptoms": extracted}

@app.post("/get_followups")
def get_followups(symptoms: List[str] = Body(...)):
    result = {}
    for symptom in symptoms:
        qs = follow_up_map.get(symptom.lower(), [])
        result[symptom] = [q for q in qs if isinstance(q, str) and q.strip()]
    return result


@app.post("/diagnose")
def diagnose(payload: DiagnosisRequest):
    print("🔍 Received diagnosis request:", payload)
    extracted = extract_symptoms(payload.symptoms)
    result = generate_diagnosis(
        extracted,
        payload.followup_answers,
        payload.extra_input,
        age=payload.age,
        gender=payload.gender,
        country=payload.country
    )
    return {"diagnosis": result}

@app.get("/routes")
def list_routes():
    return [route.path for route in app.routes]

@app.post("/condition_info")
def get_condition_info(query: ConditionQuery):
    results = []

    for cond in query.conditions:
        key = cond.lower().strip()
        if key in condition_database:
            data = condition_database[key]
            results.append({
                "name": cond,
                "description": data.get("description", ""),
                "symptoms": data.get("symptoms", []),
                "treatments": data.get("treatments", []),
                "risks": data.get("risks", []),
            })
        else:
            results.append({
                "name": cond,
                "description": "No information available.",
                "symptoms": [],
                "treatments": ["Information not available."],
                "risks": ["Information not available."]
            })
    return results



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ Validation error:", exc.errors())
    return await request_validation_exception_handler(request, exc)
