import glob
import time
import re

timestamp = str(int(time.time()))
for file in glob.glob('frontend/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Also fix the anonymous function in ai.html if it exists
    content = content.replace('(() => {\n        loadChats();\n    });', 'loadChats();')
    
    # Replace any existing app.js with app.js?v=TIMESTAMP
    content = re.sub(r'src="assets/js/app\.js(\?v=\d+)?"', f'src="assets/js/app.js?v={timestamp}"', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Cache busting and anonymous function fixes applied.")
