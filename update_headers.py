import os
import glob

FRONTEND_DIR = r"f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\frontend"
JS_FILE = os.path.join(FRONTEND_DIR, "assets", "js", "app.js")

# 1. Update all HTML headers
html_files = glob.glob(os.path.join(FRONTEND_DIR, "*.html"))
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the old static header
    content = content.replace('<div>Demo Mode Active</div>', '<div id="mode-indicator" style="font-weight: bold;">Loading...</div>')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

# 2. Add loadModeIndicator and global dropdown helpers to app.js
with open(JS_FILE, 'r', encoding='utf-8') as f:
    js_content = f.read()

if "loadModeIndicator" not in js_content:
    js_append = """
async function loadModeIndicator() {
    const ind = document.getElementById('mode-indicator');
    if(!ind) return;
    try {
        const res = await apiCall('/ai/status');
        if(res.provider === 'gemini') {
            ind.innerHTML = '🟢 Gemini Live';
            ind.className = 'badge badge-active';
        } else {
            ind.innerHTML = '🟡 Demo Mode';
            ind.className = 'badge badge-new';
        }
    } catch(e) {
        ind.innerHTML = '🔴 Offline';
    }
}
document.addEventListener('DOMContentLoaded', loadModeIndicator);

async function loadDropdown(endpoint, selectId, labelField, valueField) {
    const select = document.getElementById(selectId);
    if (!select) return;
    try {
        const data = await apiCall(endpoint);
        let options = '<option value="">-- Select --</option>';
        data.forEach(item => {
            options += `<option value="${item[valueField]}">${item[labelField]}</option>`;
        });
        select.innerHTML = options;
    } catch(e) {
        console.error("Error loading dropdown", selectId, e);
    }
}
"""
    with open(JS_FILE, 'a', encoding='utf-8') as f:
        f.write(js_append)

print("Headers and JS updated.")
