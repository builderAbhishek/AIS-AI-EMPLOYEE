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
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.OLLAMA_THINKING_MODE = os.getenv("OLLAMA_THINKING_MODE", "false")
        self.COMPANY_NAME = os.getenv("COMPANY_NAME", "Alag Innovative Solutions")
        self.FOUNDER_NAME = os.getenv("FOUNDER_NAME", "Founder")
        
        # Load overrides from DB
        db: Session = SessionLocal()
        try:
            settings = db.query(models.Setting).all()
            for setting in settings:
                if setting.key == "AI_PROVIDER": self.AI_PROVIDER = setting.value
                elif setting.key == "OLLAMA_MODEL": self.OLLAMA_MODEL = setting.value
                elif setting.key == "OLLAMA_BASE_URL": self.OLLAMA_BASE_URL = setting.value
                elif setting.key == "OLLAMA_THINKING_MODE": self.OLLAMA_THINKING_MODE = setting.value
                elif setting.key == "COMPANY_NAME": self.COMPANY_NAME = setting.value
                elif setting.key == "FOUNDER_NAME": self.FOUNDER_NAME = setting.value
        except Exception:
            pass
        finally:
            db.close()

settings = Config()
