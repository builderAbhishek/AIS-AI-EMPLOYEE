from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..database import models
from ..schemas import schemas
from .leads import log_activity

router = APIRouter()

@router.get("/", response_model=List[schemas.KnowledgeResponse])
def get_knowledge(db: Session = Depends(get_db)):
    return db.query(models.Knowledge).order_by(models.Knowledge.id.desc()).all()

@router.post("/", response_model=schemas.KnowledgeResponse)
def create_knowledge(knowledge: schemas.KnowledgeCreate, db: Session = Depends(get_db)):
    db_knowledge = models.Knowledge(**knowledge.dict())
    db.add(db_knowledge)
    db.commit()
    db.refresh(db_knowledge)
    log_activity(db, "CREATED", "KNOWLEDGE", db_knowledge.id, f"Added knowledge: {db_knowledge.title}")
    return db_knowledge

@router.put("/{knowledge_id}", response_model=schemas.KnowledgeResponse)
def update_knowledge(knowledge_id: int, knowledge_data: schemas.KnowledgeCreate, db: Session = Depends(get_db)):
    knowledge = db.query(models.Knowledge).filter(models.Knowledge.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    
    for key, value in knowledge_data.dict(exclude_unset=True).items():
        setattr(knowledge, key, value)
        
    db.commit()
    db.refresh(knowledge)
    log_activity(db, "UPDATED", "KNOWLEDGE", knowledge.id, f"Updated knowledge: {knowledge.title}")
    return knowledge

@router.delete("/{knowledge_id}")
def delete_knowledge(knowledge_id: int, db: Session = Depends(get_db)):
    knowledge = db.query(models.Knowledge).filter(models.Knowledge.id == knowledge_id).first()
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    
    db.delete(knowledge)
    db.commit()
    log_activity(db, "DELETED", "KNOWLEDGE", knowledge_id, f"Deleted knowledge: {knowledge.title}")
    return {"ok": True}
