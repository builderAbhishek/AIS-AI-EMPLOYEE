import re

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('        final_text = ""\n        try:', '        final_text = ""\n        url = settings.OLLAMA_BASE_URL.rstrip(\'/\') + "/api/chat"\n        try:')

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected url inside generate_response.")
