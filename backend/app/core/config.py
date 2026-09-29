import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..database import models

load_dotenv()

class Config:
    def __init__(self):
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "demo")
        self.API_KEY = os.getenv("API_KEY", "")
        self.API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        self.MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
        self.COMPANY_NAME = os.getenv("COMPANY_NAME", "Alag Innovative Solutions")
        self.FOUNDER_NAME = os.getenv("FOUNDER_NAME", "Founder")
        
        # Load overrides from DB
        db: Session = SessionLocal()
        try:
            settings = db.query(models.Setting).all()
            for setting in settings:
                if setting.key == "AI_PROVIDER": self.AI_PROVIDER = setting.value
                elif setting.key == "API_KEY": self.API_KEY = setting.value
                elif setting.key == "API_BASE_URL": self.API_BASE_URL = setting.value
                elif setting.key == "MODEL": self.MODEL = setting.value
                elif setting.key == "COMPANY_NAME": self.COMPANY_NAME = setting.value
                elif setting.key == "FOUNDER_NAME": self.FOUNDER_NAME = setting.value
        except Exception:
            pass
        finally:
            db.close()

settings = Config()
