from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database.database import get_db
from ..database import models
from ..schemas import schemas
from .leads import log_activity

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).order_by(models.Task.id.desc()).all()

@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"found": False, "message": f"Task #{task_id} was not found in the current database."}
    
    project_name = None
    if task.project_id:
        project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
        if project:
            project_name = project.project_name

    return {
        "found": True,
        "id": task.id,
        "title": task.title,
        "project_id": task.project_id,
        "project_name": project_name,
        "priority": task.priority,
        "status": task.status,
        "due_date": str(task.deadline) if task.deadline else "Not set",
        "created_at": str(task.created_at) if task.created_at else "Not set",
        "description": task.description
    }

@router.post("/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    log_activity(db, "CREATED", "TASK", db_task.id, f"Created new task: {db_task.title}")
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_data: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
        
    if task.status == "DONE" and not task.completed_at:
        task.completed_at = datetime.now()
        
    db.commit()
    db.refresh(task)
    log_activity(db, "UPDATED", "TASK", task.id, f"Updated task: {task.title}")
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    log_activity(db, "DELETED", "TASK", task_id, f"Deleted task: {task.title}")
    return {"ok": True}
