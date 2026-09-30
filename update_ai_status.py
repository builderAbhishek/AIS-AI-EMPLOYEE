import re
with open('frontend/ai.html', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''async function loadStatus() {
            try {
                const status = await apiCall('/ai/status');
                const indicator = document.getElementById('mode-indicator');
                if (status.connection === 'connected') {
                    const thinkingStr = status.thinking_mode === 'true' ? 'ON' : 'OFF';
                    indicator.innerHTML = `🟢 Ollama Live <br><span style="font-size:0.8em;font-weight:normal;">Model: ${status.model}<br>Thinking: ${thinkingStr}</span>`;
                    indicator.style.color = '#166534';
                } else {
                    indicator.innerHTML = `🔴 Ollama Offline`;
                    indicator.style.color = '#991b1b';
                }
            } catch(e) {
                document.getElementById('mode-indicator').innerText = 'Status Unknown';
            }
        }'''

text = re.sub(r'async function loadStatus\(\) \{.*?\}(?=\n\n\s*loadChats\(\);)', replacement, text, flags=re.DOTALL)

with open('frontend/ai.html', 'w', encoding='utf-8') as f:
    f.write(text)
