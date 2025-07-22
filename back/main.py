# main.py

from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from data.diagnosis_assistant import extract_symptoms, generate_diagnosis, follow_up_map
from models import DiagnosisRequest
from data.condition_info_loader import condition_database
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from chatbot import query_gemini_from_messages, reset_session_memory


# -------------------- App Setup --------------------
app = FastAPI(
    title="Smart AI Medical Assistant Backend",
    description="FastAPI backend to extract symptoms and generate diagnosis using RAG + LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Request Schemas --------------------
class SymptomInput(BaseModel):
    text: str

class ConditionQuery(BaseModel):
    conditions: List[str]

class ChatMessage(BaseModel):
    role: str
    content: str
 
class ChatRequest(BaseModel):
    session_id: str
    messages: List[ChatMessage]

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

@app.get("/routes")
def list_routes():
    return [route.path for route in app.routes]

from chatbot import query_gemini_from_messages, reset_session_memory

 
class ChatMessage(BaseModel):

    role: str

    content: str
 
class ChatRequest(BaseModel):

    session_id: str

    messages: List[ChatMessage]
 
@app.post("/chat_llm")

def chat_with_llm(chat: ChatRequest):

    print("📥 Incoming chat payload:", chat)

    try:

        messages = [{"role": msg.role, "content": msg.content} for msg in chat.messages]

        reply_text = query_gemini_from_messages(messages, chat.session_id)

        return {"reply": reply_text}

    except Exception as e:

        print("⚠️ Error in Gemini chat:", e)

        return JSONResponse(status_code=500, content={"error": "LLM processing failed."})
 
@app.post("/reset_session")

def reset(chat: dict = Body(...)):

    session_id = chat.get("session_id")

    if not session_id:

        return JSONResponse(status_code=400, content={"error": "Missing session_id"})

    reset_session_memory(session_id)

    return {"message": f"Session '{session_id}' reset successfully."}

 
 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ Validation error:", exc.errors())
    return await request_validation_exception_handler(request, exc)
