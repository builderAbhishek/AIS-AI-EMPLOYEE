from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, index=True)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    location = Column(String)
    business_type = Column(String)
    source = Column(String)
    service_interest = Column(String)
    status = Column(String, default="NEW")
    priority = Column(String, default="MEDIUM")
    estimated_value = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    last_contacted = Column(DateTime, nullable=True)
    next_followup = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, index=True)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    services = Column(String)
    project_count = Column(Integer, default=0)
    status = Column(String, default="ACTIVE")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    projects = relationship("Project", back_populates="client")
    tasks = relationship("Task", back_populates="client")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String, default="PLANNING")
    priority = Column(String, default="MEDIUM")
    progress = Column(Integer, default=0)
    budget = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    client = relationship("Client", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    assigned_to = Column(String, default="Founder")
    priority = Column(String, default="MEDIUM")
    status = Column(String, default="TODO")
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="tasks")
    client = relationship("Client", back_populates="tasks")

class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)
    content = Column(Text)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Memory(Base):
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    title = Column(String)
    content = Column(Text)
    importance = Column(String, default="NORMAL")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer, nullable=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Chat")
    current_plan = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"))
    role = Column(String)
    content = Column(Text)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

