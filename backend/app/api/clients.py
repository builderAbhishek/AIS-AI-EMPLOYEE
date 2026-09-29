from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..database import models
from ..schemas import schemas
from .leads import log_activity

router = APIRouter()

@router.get("/", response_model=List[schemas.ClientResponse])
def get_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).order_by(models.Client.id.desc()).all()

@router.post("/", response_model=schemas.ClientResponse)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    log_activity(db, "CREATED", "CLIENT", db_client.id, f"Created new client: {db_client.business_name}")
    return db_client

@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_client(client_id: int, client_data: schemas.ClientCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    for key, value in client_data.dict(exclude_unset=True).items():
        setattr(client, key, value)
        
    db.commit()
    db.refresh(client)
    log_activity(db, "UPDATED", "CLIENT", client.id, f"Updated client: {client.business_name}")
    return client

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    log_activity(db, "DELETED", "CLIENT", client_id, f"Deleted client: {client.business_name}")
    return {"ok": True}
