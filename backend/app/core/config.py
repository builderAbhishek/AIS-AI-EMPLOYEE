import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..database import models

load_dotenv()

class Config:
    def __init__(self):
        self.reload()

    def reload(self):
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "demo")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_API_BASE_URL = os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        self.COMPANY_NAME = os.getenv("COMPANY_NAME", "Alag Innovative Solutions")
        self.FOUNDER_NAME = os.getenv("FOUNDER_NAME", "Founder")
        
        # Load overrides from DB
        db: Session = SessionLocal()
        try:
            settings = db.query(models.Setting).all()
            for setting in settings:
                if setting.key == "AI_PROVIDER": self.AI_PROVIDER = setting.value
                elif setting.key == "GEMINI_API_KEY": self.GEMINI_API_KEY = setting.value
                elif setting.key == "GEMINI_API_BASE_URL": self.GEMINI_API_BASE_URL = setting.value
                elif setting.key == "GEMINI_MODEL": self.GEMINI_MODEL = setting.value
                elif setting.key == "COMPANY_NAME": self.COMPANY_NAME = setting.value
                elif setting.key == "FOUNDER_NAME": self.FOUNDER_NAME = setting.value
        except Exception:
            pass
        finally:
            db.close()

settings = Config()
