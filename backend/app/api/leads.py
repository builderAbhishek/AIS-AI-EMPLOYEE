from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..database import models
from ..schemas import schemas

router = APIRouter()

def log_activity(db: Session, action: str, entity_type: str, entity_id: int, description: str):
    activity = models.Activity(action=action, entity_type=entity_type, entity_id=entity_id, description=description)
    db.add(activity)
    db.commit()

@router.get("/", response_model=List[schemas.LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    return db.query(models.Lead).order_by(models.Lead.id.desc()).all()

@router.post("/", response_model=schemas.LeadResponse)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    log_activity(db, "CREATED", "LEAD", db_lead.id, f"Created new lead: {db_lead.business_name}")
    return db_lead

@router.get("/{lead_id}", response_model=schemas.LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=schemas.LeadResponse)
def update_lead(lead_id: int, lead_data: schemas.LeadCreate, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    for key, value in lead_data.dict(exclude_unset=True).items():
        setattr(lead, key, value)
        
    db.commit()
    db.refresh(lead)
    log_activity(db, "UPDATED", "LEAD", lead.id, f"Updated lead: {lead.business_name}")
    return lead

@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    log_activity(db, "DELETED", "LEAD", lead_id, f"Deleted lead: {lead.business_name}")
    return {"ok": True}
