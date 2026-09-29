from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..core.ai_provider import AIProvider
from .leads import log_activity
from pathlib import Path

router = APIRouter()
ai = AIProvider()

class ChatRequest(BaseModel):
    message: str
    
def get_ais_brain():
    brain_path = Path("knowledge/company/ais_brain.md")
    if brain_path.exists():
        with open(brain_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an AI assistant for AIS."

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    system_prompt = get_ais_brain()
    response = ai.generate_response(request.message, system_prompt)
    log_activity(db, "AI_CHAT", "SYSTEM", 0, f"AI Chat query: {request.message[:50]}...")
    return response

@router.post("/lead-score")
def lead_score(data: dict, db: Session = Depends(get_db)):
    prompt = f"Analyze lead and provide a score 0-100: {data}"
    res = ai.generate_response(prompt, get_ais_brain())
    return res

@router.post("/pitch")
def generate_pitch(data: dict, db: Session = Depends(get_db)):
    prompt = f"Generate a short sales pitch for {data.get('business_name')} interested in {data.get('service_interest')}"
    res = ai.generate_response(prompt, get_ais_brain())
    return res

@router.post("/task-breakdown")
def task_breakdown(data: dict, db: Session = Depends(get_db)):
    prompt = f"Break down this project into small executable tasks: {data.get('project_name')} - {data.get('description')}"
    res = ai.generate_response(prompt, get_ais_brain())
    return res

@router.get("/daily-brief")
def daily_brief(db: Session = Depends(get_db)):
    prompt = "Generate today's daily brief based on priority tasks and new leads."
    res = ai.generate_response(prompt, get_ais_brain())
    log_activity(db, "AI_DAILY_BRIEF", "SYSTEM", 0, "Generated Daily Brief")
    return res
