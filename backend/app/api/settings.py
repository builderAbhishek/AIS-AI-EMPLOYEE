from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import models
from pydantic import BaseModel

router = APIRouter()

class SettingItem(BaseModel):
    key: str
    value: str

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(models.Setting).all()
    return {s.key: s.value for s in settings}

@router.post("/")
def update_setting(setting: SettingItem, db: Session = Depends(get_db)):
    db_setting = db.query(models.Setting).filter(models.Setting.key == setting.key).first()
    if db_setting:
        db_setting.value = setting.value
    else:
        db_setting = models.Setting(key=setting.key, value=setting.value)
        db.add(db_setting)
    db.commit()
    return {"ok": True}
