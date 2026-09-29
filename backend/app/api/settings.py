from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import models
from ..core.config import settings
from pydantic import BaseModel
from typing import List

router = APIRouter()

class SettingItem(BaseModel):
    key: str
    value: str

class SettingsUpdate(BaseModel):
    settings: List[SettingItem]

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    db_settings = db.query(models.Setting).all()
    setting_dict = {s.key: s.value for s in db_settings}
    
    # Defaults if missing in DB
    result = {
        "AI_PROVIDER": setting_dict.get("AI_PROVIDER", settings.AI_PROVIDER),
        "GEMINI_MODEL": setting_dict.get("GEMINI_MODEL", settings.GEMINI_MODEL),
        "GEMINI_API_BASE_URL": setting_dict.get("GEMINI_API_BASE_URL", settings.GEMINI_API_BASE_URL),
        "COMPANY_NAME": setting_dict.get("COMPANY_NAME", settings.COMPANY_NAME),
        "FOUNDER_NAME": setting_dict.get("FOUNDER_NAME", settings.FOUNDER_NAME),
    }
    
    api_key = setting_dict.get("GEMINI_API_KEY", settings.GEMINI_API_KEY)
    if api_key:
        result["GEMINI_API_KEY_MASKED"] = "Configured" 
    else:
        result["GEMINI_API_KEY_MASKED"] = ""
        
    return result

@router.post("/")
def update_settings(updates: SettingsUpdate, db: Session = Depends(get_db)):
    for item in updates.settings:
        # Ignore masked key submissions
        if item.key == "GEMINI_API_KEY" and item.value == "Configured":
            continue
            
        db_setting = db.query(models.Setting).filter(models.Setting.key == item.key).first()
        if db_setting:
            db_setting.value = item.value
        else:
            db_setting = models.Setting(key=item.key, value=item.value)
            db.add(db_setting)
            
    db.commit()
    settings.reload()
    return {"ok": True}
