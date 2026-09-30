import re
with open('backend/app/core/ai_provider.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add search_crm method definition
search_crm_code = '''
        def search_crm(query: str) -> dict:
            try:
                query_lower = query.lower()
                results = {"clients": [], "projects": [], "tasks": []}
                
                # Search Clients
                clients = db.query(models.Client).all()
                for c in clients:
                    if query_lower in c.business_name.lower() or query_lower in str(c.id):
                        results["clients"].append({
                            "id": c.id, "name": c.business_name, "services": c.services, "status": c.status
                        })
                
                # Search Projects
                projects = db.query(models.Project).all()
                for p in projects:
                    if query_lower in p.project_name.lower() or query_lower in str(p.id) or (p.client_id and any(c["id"] == p.client_id for c in results["clients"])):
                        results["projects"].append({
                            "id": p.id, "name": p.project_name, "client_id": p.client_id,
                            "status": p.status, "progress": p.progress, "priority": p.priority
                        })
                
                # Search Tasks
                tasks = db.query(models.Task).all()
                for t in tasks:
                    if query_lower in t.title.lower() or query_lower in str(t.id) or (t.project_id and any(p["id"] == t.project_id for p in results["projects"])):
                        results["tasks"].append({
                            "id": t.id, "title": t.title, "project_id": t.project_id,
                            "status": t.status, "priority": t.priority, "deadline": str(t.deadline)
                        })
                
                actions_taken.append(f"🔍 Searched CRM for: '{query}'")
                return {"found": bool(results["clients"] or results["projects"] or results["tasks"]), "results": results}
            except Exception as e:
                return {"found": False, "error": str(e)}

        def save_current_plan'''

text = text.replace('        def save_current_plan', search_crm_code)

# 2. Add search_crm to tools_map
tools_map_code = '''        tools_map = {
            "create_task": create_task,
            "get_task": get_task,
            "save_current_plan": save_current_plan,
            "search_crm": search_crm
        }'''
text = re.sub(r'tools_map = \{.*?\}', tools_map_code, text, flags=re.DOTALL)

# 3. Add search_crm to tools array
search_crm_schema = '''            {
                "type": "function",
                "function": {
                    "name": "search_crm",
                    "description": "READ-ONLY TOOL: Search the CRM for clients, projects, or tasks by name or ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The name or ID to search for (e.g., 'Global Traders')"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_task",'''

text = text.replace('            {\n                "type": "function",\n                "function": {\n                    "name": "create_task",', search_crm_schema)

with open('backend/app/core/ai_provider.py', 'w', encoding='utf-8') as f:
    f.write(text)
