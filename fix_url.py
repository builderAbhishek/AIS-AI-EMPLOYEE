import re

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

payload_definition = """
        url = settings.OLLAMA_BASE_URL.rstrip('/') + "/api/chat"
        
        payload = {
"""

content = content.replace('        payload = {', payload_definition, 1)

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Restored url definition.")
