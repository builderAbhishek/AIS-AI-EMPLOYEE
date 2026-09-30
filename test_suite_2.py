import urllib.request
import json

def test_query(prompt, name):
    print(f"\\n--- {name} ---")
    c = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/chats/', method='POST')).read().decode())
    chat_id = c["id"]
    
    data = json.dumps({'content': prompt})
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/chats/{chat_id}/messages', data=data.encode(), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=300).read().decode())
        print("Response:", res.get("text")[:200].replace('\\n', ' '))
        if res.get("actions"):
            print("Actions:", res.get("actions"))
    except Exception as e:
        print("Error:", e)

test_query("Global Traders ke project ka status aur task kya hai?", "TEST 5 - CRM READ")
test_query("Task #20 ki details batao", "TEST 6 - TASK LOOKUP")
test_query("Metro Hospital ke liye execution plan banao.", "TEST 7 - PLANNING")
test_query("Is plan ko 3 tasks me create karo.", "TEST 8 - EXPLICIT ACTION")
