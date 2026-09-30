import glob
import re

for file in glob.glob('frontend/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace the exact pattern:
    # (() => {
    #     some code
    # });
    # with:
    # (() => {
    #     some code
    # })();
    
    # We can use regex to safely find and replace this.
    content = re.sub(r'\(\(\) => \{([\s\S]*?)\}\);', r'(() => {\1})();', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed anonymous function execution in all HTML files.")
