from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..database import models
from ..schemas import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.ActivityResponse])
def get_activities(db: Session = Depends(get_db), limit: int = 50):
    return db.query(models.Activity).order_by(models.Activity.id.desc()).limit(limit).all()
