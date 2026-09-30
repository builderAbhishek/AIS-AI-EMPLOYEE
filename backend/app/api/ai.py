from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.database import get_db
from ..database import models
from ..core.ai_provider import AIProvider
from ..core.config import settings
from .leads import log_activity
from pathlib import Path
from datetime import datetime

router = APIRouter()
ai = AIProvider()

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

def get_ais_brain():
    brain_path = Path("knowledge/company/ais_brain.md")
    if brain_path.exists():
        with open(brain_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are an AI assistant for AIS."

def build_ais_context(db: Session):
    brain = get_ais_brain()
    
    context = (
        "You are AIS AI Employee.\n\n"
        f"Company: Alag Innovative Solutions\n"
        f"Operating principles:\n{brain}\n\n"
        "Current live business data from SQLite Database:\n"
    )
    
    context += "You MUST use the 'search_crm' tool to find details about specific clients, projects, or tasks by their name.\n"

    
    context += "\nIMPORTANT RULES:\n"
    context += "1. Prioritize execution over generic advice.\n"
    context += "2. Use ACTUAL AIS data. Do not invent leads, projects, tasks, or revenue.\n"
    context += "3. Always use 'search_crm' tool when asked about a client or project to get their actual Status, Progress, and Tasks. Never assume or hallucinate a status.\n"
    context += "4. If you have an explicit action request (like 'create 3 tasks'), USE the create_task tool.\n"
    context += "5. Break large goals into actionable tasks.\n"
    context += "6. Always provide a concrete next action based on the live data.\n"
    context += "7. Keep answers concise, structure with SITUATION, PRIORITIES, ACTIONS, EXPECTED OUTCOME, NEXT ACTION.\n"
    context += "8. After successful tool execution, confirm the action and DO NOT claim creation unless it succeeded.\n"
    context += "9. Planning requests are read-only. Do NOT create tasks when asked to 'plan' or 'suggest'. Use save_current_plan instead.\n"
    context += "10. Other external actions (email, WhatsApp) require approval and are not available yet.\n"

    return context

@router.get("/status")
def ai_status():
    settings.reload()
    return {
        "provider": "ollama",
        "mode": "live",
        "model": settings.OLLAMA_MODEL,
        "configured": True,
        "connection": "connected",
        "thinking_mode": getattr(settings, "OLLAMA_THINKING_MODE", "false")
    }

@router.get("/models")
def get_models():
    settings.reload()
    try:
        import urllib.request
        import json
        url = settings.OLLAMA_BASE_URL.rstrip('/') + "/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            models = []
            for m in data.get("models", []):
                models.append({
                    "name": m.get("name"),
                    "provider": "ollama",
                    "available": True
                })
            return models
    except Exception as e:
        return {
            "provider": "ollama",
            "available": False,
            "error": "Ollama is not running"
        }

@router.get("/health")
def ai_health():
    settings.reload()
    try:
        import urllib.request
        url = settings.OLLAMA_BASE_URL.rstrip('/') + "/"
        urllib.request.urlopen(url, timeout=2)
        return {
            "provider": "ollama",
            "model": settings.OLLAMA_MODEL,
            "status": "connected"
        }
    except Exception:
        return {
            "provider": "ollama",
            "model": settings.OLLAMA_MODEL,
            "status": "offline"
        }

@router.post("/test-connection")
def test_connection():
    return ai.test_connection()

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    history = [h.dict() for h in request.history] if request.history else []
    response = ai.generate_response(request.message, system_prompt, history, db)
    log_activity(db, "AI_CHAT", "SYSTEM", 0, f"AI Chat query: {request.message[:50]}...")
    return response

@router.post("/lead-score")
def lead_score(data: dict, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = f"Analyze this lead and provide a score 0-100 based on AIS priorities:\n{data}"
    res = ai.generate_response(prompt, system_prompt, [], db)
    return res

@router.post("/pitch")
def generate_pitch(data: dict, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = f"Generate a short, personalized sales pitch for this specific lead:\nBusiness: {data.get('business_name')}\nService Interest: {data.get('service_interest')}\nStatus: {data.get('status')}"
    res = ai.generate_response(prompt, system_prompt, [], db)
    return res

@router.post("/task-breakdown")
def task_breakdown(data: dict, db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = f"Break down this project into small executable tasks:\nProject: {data.get('project_name')}\nDescription: {data.get('description')}"
    res = ai.generate_response(prompt, system_prompt, [], db)
    return res

@router.get("/daily-brief")
def daily_brief(db: Session = Depends(get_db)):
    system_prompt = build_ais_context(db)
    prompt = "Generate today's daily brief analyzing the provided SQLite business data. Output MUST include: Business Status, Top Priorities, Overdue Items, Sales Opportunities, Project Risks, Today's 3 Most Important Actions, Next Action."
    res = ai.generate_response(prompt, system_prompt, [], db)
    log_activity(db, "AI_DAILY_BRIEF", "SYSTEM", 0, "Generated Daily Brief")
    return res
