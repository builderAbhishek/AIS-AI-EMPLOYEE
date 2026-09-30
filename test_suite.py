import urllib.request
import json
import time

def test_config(think_mode):
    # Set settings
    print(f"\n--- Testing Thinking Mode: {think_mode} ---")
    data = json.dumps({'settings': [{'key': 'OLLAMA_MODEL', 'value': 'ais-qwen-hindi:latest'}, {'key': 'OLLAMA_THINKING_MODE', 'value': str(think_mode).lower()}]})
    req = urllib.request.Request('http://127.0.0.1:8000/api/settings/', data=data.encode(), headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req).read()

    # Create Chat
    c = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/chats/', method='POST')).read().decode())
    chat_id = c["id"]
    
    # Send message
    data = json.dumps({'content': 'hello ji'})
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/chats/{chat_id}/messages', data=data.encode(), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=300).read().decode())
        print("Response:", res.get("text")[:100].replace('\n', ' '))
    except Exception as e:
        print("Error:", e)

test_config(False)
test_config(True)
