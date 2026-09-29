from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Leads
class LeadBase(BaseModel):
    business_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    business_type: Optional[str] = None
    source: Optional[str] = None
    service_interest: Optional[str] = None
    status: Optional[str] = "NEW"
    priority: Optional[str] = "MEDIUM"
    estimated_value: Optional[float] = 0.0
    notes: Optional[str] = None
    last_contacted: Optional[datetime] = None
    next_followup: Optional[datetime] = None

class LeadCreate(LeadBase):
    pass

class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

# Clients
class ClientBase(BaseModel):
    business_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    services: Optional[str] = None
    project_count: Optional[int] = 0
    status: Optional[str] = "ACTIVE"
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

# Projects
class ProjectBase(BaseModel):
    project_name: str
    client_id: Optional[int] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = "PLANNING"
    priority: Optional[str] = "MEDIUM"
    progress: Optional[int] = 0
    budget: Optional[float] = 0.0
    notes: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

# Tasks
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    client_id: Optional[int] = None
    assigned_to: Optional[str] = "Founder"
    priority: Optional[str] = "MEDIUM"
    status: Optional[str] = "TODO"
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    class Config:
        orm_mode = True

# Knowledge
class KnowledgeBase(BaseModel):
    title: str
    category: str
    content: str
    tags: Optional[str] = None

class KnowledgeCreate(KnowledgeBase):
    pass

class KnowledgeResponse(KnowledgeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

# Activity
class ActivityBase(BaseModel):
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str

class ActivityResponse(ActivityBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
