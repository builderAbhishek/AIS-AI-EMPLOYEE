from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import models
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .ai import build_ais_context
from ..core.ai_provider import AIProvider
from ..core.config import settings
import json

router = APIRouter()
ai = AIProvider()

class MessageCreate(BaseModel):
    content: str

@router.post("/")
def create_chat(db: Session = Depends(get_db)):
    chat = models.ChatConversation(title="New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("/")
def list_chats(db: Session = Depends(get_db)):
    return db.query(models.ChatConversation).filter(models.ChatConversation.is_archived == False).order_by(models.ChatConversation.updated_at.desc()).all()

@router.get("/{chat_id}")
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.ChatConversation).filter(models.ChatConversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.conversation_id == chat_id).order_by(models.ChatMessage.created_at.asc()).all()
    return {"chat": chat, "messages": messages}

@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.ChatConversation).filter(models.ChatConversation.id == chat_id).first()
    if chat:
        chat.is_archived = True
        db.commit()
    return {"success": True}

@router.post("/{chat_id}/messages")
def send_message(chat_id: int, msg: MessageCreate, db: Session = Depends(get_db)):
    chat = db.query(models.ChatConversation).filter(models.ChatConversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    # Save user message
    user_msg = models.ChatMessage(conversation_id=chat_id, role="user", content=msg.content)
    db.add(user_msg)
    
    # Load history
    history_records = db.query(models.ChatMessage).filter(models.ChatMessage.conversation_id == chat_id).order_by(models.ChatMessage.created_at.asc()).all()
    history = [{"role": m.role, "text": m.content} for m in history_records]
    
    system_prompt = build_ais_context(db)
    if chat.current_plan:
        system_prompt += f"\n\nCURRENT PLAN IN MEMORY (for this conversation only):\n{chat.current_plan}"
    
    # Process with Ollama
    # Ensure current_plan update is passed to ai_provider
    response = ai.generate_response(msg.content, system_prompt, history, db, chat_id)
    
    # Save assistant message
    ai_msg_metadata = json.dumps({
        "provider": "ollama",
        "model": response.get("model", settings.OLLAMA_MODEL)
    })
    ai_msg = models.ChatMessage(conversation_id=chat_id, role="model", content=response["text"], metadata_json=ai_msg_metadata)
    db.add(ai_msg)
    
    # Generate title if New Chat
    if chat.title == "New Chat":
        try:
            prompt = f"Generate a short title (max 50 chars) for a conversation that starts with: '{msg.content}'. Return ONLY the title text, nothing else."
            title_res = ai.generate_response(prompt, "You are a title generator. Be concise.", [], None, None)
            new_title = title_res["text"].strip().replace('"', '')
            if len(new_title) > 60: new_title = new_title[:60]
            if new_title: chat.title = new_title
        except:
            chat.title = msg.content[:40] + "..."

    chat.updated_at = datetime.utcnow()
    db.commit()
    
    return response

@router.patch("/{chat_id}")
def update_chat(chat_id: int, data: dict, db: Session = Depends(get_db)):
    chat = db.query(models.ChatConversation).filter(models.ChatConversation.id == chat_id).first()
    if chat and "title" in data:
        chat.title = data["title"]
        db.commit()
    return {"success": True}
