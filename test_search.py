import urllib.request
import json

def search_test():
    c = json.loads(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/api/chats/', method='POST')).read().decode())
    chat_id = c["id"]
    
    data = json.dumps({'content': 'Global Traders ke project ka status aur task kya hai?'})
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/chats/{chat_id}/messages', data=data.encode(), headers={'Content-Type': 'application/json'}, method='POST')
    
    print("Testing Global Traders request...")
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=300).read().decode())
        print("Actions taken:", res.get("actions"))
        # we can't print hindi easily but we can see actions
    except Exception as e:
        print("Error:", e)

search_test()
