import re

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the indentation of tools_map and the rest of the execution block
fixed_content = re.sub(
    r'                tools_map = \{',
    r'        tools_map = {',
    content
)

with open(r'f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\backend\app\core\ai_provider.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)
print("Indentation fixed.")
