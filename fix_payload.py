import re

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

payload_definition = """
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [],
            "stream": False,
            "options": {
                "temperature": 0.3
            },
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_crm",
                        "description": "READ-ONLY TOOL: Search the CRM for clients, projects, or tasks by name or ID.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The name or ID to search for"}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_task",
                        "description": "WRITE TOOL: Create a new task.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "priority": {"type": "string"},
                                "status": {"type": "string"},
                                "description": {"type": "string"},
                                "project_id": {"type": "integer"},
                                "client_id": {"type": "integer"}
                            },
                            "required": ["title", "priority", "status"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "save_current_plan",
                        "description": "WRITE TOOL: Save a generated execution plan.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "client_name": {"type": "string"},
                                "project_name": {"type": "string"},
                                "tasks": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "priority": {"type": "string"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            },
                            "required": ["tasks"]
                        }
                    }
                }
            ]
        }
"""

content = content.replace('        messages = [{"role": "system", "content": system_context}]', payload_definition + '\n        messages = [{"role": "system", "content": system_context}]')

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored payload definition.")
