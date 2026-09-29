from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import models
from datetime import datetime

router = APIRouter()

@router.get("/")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_leads = db.query(models.Lead).count()
    new_leads = db.query(models.Lead).filter(models.Lead.status == "NEW").count()
    qualified_leads = db.query(models.Lead).filter(models.Lead.status.in_(["INTERESTED", "MEETING", "PROPOSAL"])).count()
    
    active_clients = db.query(models.Client).filter(models.Client.status == "ACTIVE").count()
    active_projects = db.query(models.Project).filter(models.Project.status == "IN_PROGRESS").count()
    
    pending_tasks = db.query(models.Task).filter(models.Task.status != "DONE").count()
    
    # Overdue tasks
    now = datetime.now()
    overdue_tasks = db.query(models.Task).filter(
        models.Task.status != "DONE",
        models.Task.deadline < now
    ).count()
    
    # Top 5 actions
    top_tasks = db.query(models.Task).filter(
        models.Task.status != "DONE"
    ).order_by(models.Task.priority.desc(), models.Task.deadline.asc()).limit(5).all()
    
    return {
        "overview": {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "qualified_leads": qualified_leads,
            "active_clients": active_clients,
            "active_projects": active_projects,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks
        },
        "top_actions": [{"id": t.id, "title": t.title, "priority": t.priority} for t in top_tasks]
    }
