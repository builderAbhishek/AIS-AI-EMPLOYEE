import urllib.request
import json
import sys
# Set console to print utf-8 safely
sys.stdout.reconfigure(encoding='utf-8')

def read_chat():
    try:
        # Just grab the last chat or create one
        chats = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/chats/', method='GET')).read().decode())
        if chats:
            chat_id = chats[0]["id"]
            data = json.loads(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:8000/api/chats/{chat_id}', method='GET')).read().decode())
            for msg in data["messages"]:
                print(f"[{msg['role']}] {msg['content']}")
    except Exception as e:
        print("Error:", e)

read_chat()
