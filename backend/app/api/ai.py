from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import models
from ..core.ai_provider import AIProvider
from ..core.config import settings
from .leads import log_activity
from pathlib import Path
from datetime import datetime

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

def build_ais_context(db: Session):
    leads = db.query(models.Lead).filter(models.Lead.status != "WON", models.Lead.status != "LOST").all()
    clients = db.query(models.Client).filter(models.Client.status == "ACTIVE").all()
    projects = db.query(models.Project).filter(models.Project.status != "COMPLETED").all()
    tasks = db.query(models.Task).filter(models.Task.status != "DONE").all()
    knowledge_entries = db.query(models.Knowledge).all()
    
    brain = get_ais_brain()
    
    context = (
        "You are AIS AI Employee.\n\n"
        f"Company: Alag Innovative Solutions\n"
        f"Operating principles:\n{brain}\n\n"
        "Current live business data from SQLite Database:\n\n"
    )
    
    context += "LEADS:\n"
    for l in leads:
        context += f"- {l.business_name} (Priority: {l.priority}, Status: {l.status})\n"
        
    context += "\nCLIENTS:\n"
    for c in clients:
        context += f"- {c.business_name} (Services: {c.services})\n"
        
    context += "\nPROJECTS:\n"
    for p in projects:
        context += f"- {p.project_name} (Status: {p.status}, Progress: {p.progress}%)\n"
        
    context += "\nTASKS:\n"
    now = datetime.now()
    for t in tasks:
        overdue = "OVERDUE" if t.deadline and t.deadline < now else "Pending"
        context += f"- {t.title} ({overdue}, Priority: {t.priority})\n"
        
    context += "\nKNOWLEDGE BASE:\n"
    for k in knowledge_entries:
        context += f"- [{k.category}] {k.title}: {k.content}\n"
        
    context += "\nRULES:\n"
    context += "1. Prioritize execution over generic advice.\n"
    context += "2. Use actual AIS data when available. Do not invent leads, projects, tasks, or revenue.\n"
    context += "3. Break large goals into actionable tasks.\n"
    context += "4. Always provide a concrete next action based on the live data.\n"
    context += "5. Keep answers concise, structure with SITUATION, PRIORITIES, ACTIONS, NEXT ACTION.\n"

    return context

@router.get("/status")
def ai_status():
    mode = ai.get_mode()
    settings.reload()
    return {
        "provider": mode,
        "mode": "live" if mode == "gemini" else "demo",
        "model": settings.GEMINI_MODEL,
        "configured": bool(settings.GEMINI_API_KEY),
        "connection": "connected" if mode == "gemini" else "local"
    }

@router.post("/test-connection")
def test_connection():
    return ai.test_connection()

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    response = ai.generate_response(request.message, system_prompt)
    log_activity(db, "AI_CHAT", "SYSTEM", 0, f"AI Chat query: {request.message[:50]}...")
    return response

@router.post("/lead-score")
def lead_score(data: dict, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = f"Analyze this lead and provide a score 0-100 based on AIS priorities:\n{data}"
    res = ai.generate_response(prompt, system_prompt)
    return res

@router.post("/pitch")
def generate_pitch(data: dict, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = f"Generate a short, personalized sales pitch for this specific lead:\nBusiness: {data.get('business_name')}\nService Interest: {data.get('service_interest')}\nStatus: {data.get('status')}"
    res = ai.generate_response(prompt, system_prompt)
    return res

@router.post("/task-breakdown")
def task_breakdown(data: dict, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = f"Break down this project into small executable tasks:\nProject: {data.get('project_name')}\nDescription: {data.get('description')}"
    res = ai.generate_response(prompt, system_prompt)
    return res

@router.get("/daily-brief")
def daily_brief(db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = "Generate today's daily brief analyzing the provided SQLite business data. Output MUST include: Business Status, Top Priorities, Overdue Items, Sales Opportunities, Project Risks, Today's 3 Most Important Actions, Next Action."
    res = ai.generate_response(prompt, system_prompt)
    log_activity(db, "AI_DAILY_BRIEF", "SYSTEM", 0, "Generated Daily Brief")
    return res
