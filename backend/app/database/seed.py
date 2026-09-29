from sqlalchemy.orm import Session
from .database import engine, Base
from . import models
from datetime import datetime, timedelta

def seed_db(db: Session):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Check if we already seeded
    if db.query(models.Setting).first() is not None:
        return
        
    print("Seeding database with demo data...")
    
    # Settings
    db.add(models.Setting(key="COMPANY_NAME", value="Alag Innovative Solutions"))
    db.add(models.Setting(key="FOUNDER_NAME", value="Founder"))
    db.add(models.Setting(key="AI_PROVIDER", value="demo"))
    
    # Leads
    demo_leads = [
        {"business_name": "ABC Restaurant", "contact_person": "Rahul Sharma", "phone": "+91 98765 43210", "email": "rahul@abcrestaurant.in", "business_type": "Restaurant", "status": "NEW", "priority": "HIGH"},
        {"business_name": "XYZ School", "contact_person": "Anita Desai", "phone": "+91 87654 32109", "email": "admin@xyzschool.edu", "business_type": "School", "status": "CONTACTED", "priority": "MEDIUM"},
        {"business_name": "Success Coaching Institute", "contact_person": "Vikram Singh", "phone": "+91 76543 21098", "business_type": "Education", "status": "INTERESTED", "priority": "HIGH"},
        {"business_name": "City Medical Store", "contact_person": "Dr. Gupta", "phone": "+91 65432 10987", "business_type": "Pharmacy", "status": "MEETING", "priority": "MEDIUM"},
        {"business_name": "Tech Mobile Shop", "contact_person": "Amit Kumar", "phone": "+91 54321 09876", "business_type": "Retail", "status": "PROPOSAL", "priority": "LOW"},
        {"business_name": "Fashion Clothing Store", "contact_person": "Neha Kapoor", "phone": "+91 43210 98765", "business_type": "Retail", "status": "NEW", "priority": "MEDIUM"},
        {"business_name": "Fresh Grocery", "contact_person": "Raju Bhai", "phone": "+91 32109 87654", "business_type": "Retail", "status": "NEW", "priority": "LOW"},
        {"business_name": "Elite Gym", "contact_person": "Priya Singh", "phone": "+91 21098 76543", "business_type": "Fitness", "status": "CONTACTED", "priority": "HIGH"},
        {"business_name": "Royal Palace Hotel", "contact_person": "Vijay M", "phone": "+91 10987 65432", "business_type": "Hospitality", "status": "INTERESTED", "priority": "HIGH"},
        {"business_name": "Smart Solutions Pvt Ltd", "contact_person": "Sanjay V", "phone": "+91 99887 76655", "business_type": "IT", "status": "MEETING", "priority": "MEDIUM"}
    ]
    for ld in demo_leads:
        db.add(models.Lead(**ld))
        
    # Clients
    demo_clients = [
        {"business_name": "Sharma Sweets", "contact_person": "Ramesh Sharma", "phone": "+91 99999 88888", "services": "Website, CRM", "status": "ACTIVE"},
        {"business_name": "Metro Hospital", "contact_person": "Dr. Reddy", "phone": "+91 77777 66666", "services": "App Development", "status": "ACTIVE"},
        {"business_name": "Global Traders", "contact_person": "Ajay Singh", "phone": "+91 55555 44444", "services": "Marketing", "status": "COMPLETED"}
    ]
    for cl in demo_clients:
        db.add(models.Client(**cl))
        
    db.commit() # Commit to get IDs
    
    # Projects
    demo_projects = [
        {"project_name": "Sharma Sweets E-commerce", "client_id": 1, "status": "IN_PROGRESS", "priority": "HIGH", "progress": 45},
        {"project_name": "Metro Hospital Booking App", "client_id": 2, "status": "PLANNING", "priority": "HIGH", "progress": 10},
        {"project_name": "Global Traders SEO", "client_id": 3, "status": "COMPLETED", "priority": "MEDIUM", "progress": 100},
        {"project_name": "Internal AIS CRM Update", "client_id": None, "status": "IN_PROGRESS", "priority": "MEDIUM", "progress": 60}
    ]
    for pr in demo_projects:
        db.add(models.Project(**pr))
        
    # Tasks
    now = datetime.now()
    demo_tasks = [
        {"title": "Follow up with ABC Restaurant", "status": "TODO", "priority": "HIGH", "deadline": now + timedelta(days=1)},
        {"title": "Prepare proposal for XYZ School", "status": "TODO", "priority": "MEDIUM", "deadline": now + timedelta(days=2)},
        {"title": "Review Sharma Sweets design", "project_id": 1, "status": "IN_PROGRESS", "priority": "HIGH", "deadline": now},
        {"title": "Call Success Coaching Institute", "status": "TODO", "priority": "HIGH", "deadline": now - timedelta(days=1)}, # Overdue
        {"title": "Setup database for Metro Hospital", "project_id": 2, "status": "BACKLOG", "priority": "MEDIUM", "deadline": now + timedelta(days=5)},
        {"title": "Send invoice to Global Traders", "client_id": 3, "status": "TODO", "priority": "MEDIUM", "deadline": now},
        {"title": "Publish today's content", "status": "TODO", "priority": "MEDIUM", "deadline": now},
        {"title": "Update CRM lead status", "status": "DONE", "priority": "LOW", "completed_at": now - timedelta(days=1)},
        {"title": "Client meeting with Dr. Gupta", "status": "TODO", "priority": "HIGH", "deadline": now},
        {"title": "Draft contract for Tech Mobile Shop", "status": "TODO", "priority": "MEDIUM", "deadline": now + timedelta(days=3)},
        {"title": "Hire new developer", "status": "BACKLOG", "priority": "LOW"},
        {"title": "Monthly tax filing", "status": "TODO", "priority": "HIGH", "deadline": now + timedelta(days=10)},
        {"title": "Fix bug in internal tool", "status": "IN_PROGRESS", "priority": "MEDIUM"},
        {"title": "Reply to support emails", "status": "TODO", "priority": "LOW", "deadline": now},
        {"title": "Plan marketing campaign for next month", "status": "PLANNING", "priority": "MEDIUM", "deadline": now + timedelta(days=15)}
    ]
    for tk in demo_tasks:
        db.add(models.Task(**tk))
        
    # Knowledge
    demo_knowledge = [
        {"title": "Sales Pitch Script", "category": "Sales", "content": "Hi, I am calling from AIS. We help businesses automate their workflows..."},
        {"title": "Target Audience", "category": "Marketing", "content": "Our target audience includes small to medium local businesses in India."},
        {"title": "Onboarding Process", "category": "Operations", "content": "1. Send welcome email. 2. Setup kick-off meeting. 3. Gather requirements."}
    ]
    for kn in demo_knowledge:
        db.add(models.Knowledge(**kn))

    db.commit()
    print("Database seeded successfully.")
