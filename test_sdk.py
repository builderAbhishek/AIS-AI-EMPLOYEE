import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

print("====================================")
print("TEST 1 - SDK CONNECTION")
print("====================================")
r0 = requests.post(f"{BASE_URL}/chats/")
chat_id = r0.json()["id"]
msg0 = {"content": "Hello AIS"}
r0_res = requests.post(f"{BASE_URL}/chats/{chat_id}/messages", json=msg0)
print("AI:", r0_res.json().get('text', '').encode('utf-8'))
print("Actions Taken:", r0_res.json().get('actions'))

print("\n====================================")
print("TEST 2 - CRM CONTEXT")
print("====================================")
msg1 = {"content": "Sharma Sweets ka status kya hai?"}
r1_res = requests.post(f"{BASE_URL}/chats/{chat_id}/messages", json=msg1)
print("AI:", r1_res.json().get('text', '').encode('utf-8'))
print("Actions Taken:", r1_res.json().get('actions'))

print("\n====================================")
print("TEST 3 - PLANNING")
print("====================================")
tasks_before = requests.get(f"{BASE_URL}/tasks/").json()
msg2 = {"content": "Sharma Sweets ke overdue task ka execution plan banao."}
r2_res = requests.post(f"{BASE_URL}/chats/{chat_id}/messages", json=msg2)
print("AI:", r2_res.json().get('text', '').encode('utf-8'))
print("Actions Taken:", r2_res.json().get('actions'))
tasks_after = requests.get(f"{BASE_URL}/tasks/").json()
print("Tasks Before:", len(tasks_before), "Tasks After:", len(tasks_after))

print("\n====================================")
print("TEST 4 - EXPLICIT ACTION")
print("====================================")
msg3 = {"content": "Is plan ke 3 tasks create karo. Project: Sharma Sweets E-commerce Priority: High"}
r3_res = requests.post(f"{BASE_URL}/chats/{chat_id}/messages", json=msg3)
print("AI:", r3_res.json().get('text', '').encode('utf-8'))
print("Actions Taken:", r3_res.json().get('actions'))
tasks_final = requests.get(f"{BASE_URL}/tasks/").json()
print("Tasks After Action:", len(tasks_final))

print("\n====================================")
print("TEST 5 - HEALTH ENDPOINT")
print("====================================")
health = requests.get(f"{BASE_URL}/ai/health")
print("Health:", health.json())
