import urllib.request
import json
import sqlite3
import sys

BASE = "http://127.0.0.1:8000/api"
DB_PATH = "data/ais_employee.db"

def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())

def get_db_records():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, business_name, status, project_count FROM clients WHERE lower(business_name)='abhishekl'")
    clients = c.fetchall()
    c.execute("SELECT id, project_name, client_id, deadline, status, progress FROM projects WHERE lower(project_name)='school website'")
    projects = c.fetchall()
    c.execute("SELECT action, entity_type, entity_id, description FROM activities WHERE entity_type IN ('CLIENT', 'PROJECT') ORDER BY id DESC LIMIT 5")
    activities = c.fetchall()
    conn.close()
    return clients, projects, activities

def reset_test_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE lower(project_name)='school website'")
    c.execute("DELETE FROM clients WHERE lower(business_name)='abhishekl'")
    conn.commit()
    conn.close()
    print("Test data reset: abhishekl and School Website removed.")

print("=" * 70)
print("RUNNING COMPLETE TEST SUITE FOR CRM ACTION BUG FIX")
print("=" * 70)

# Reset test data first
reset_test_data()

# Create new chat conversation
chat = api("POST", "/chats/")
chat_id = chat["id"]
print(f"Created Test Chat #{chat_id}\n")

# -------------------------------------------------------------
# TEST A: Create Client + Project with Deadline
# -------------------------------------------------------------
print(">>> TEST A: Create Client + Project with Deadline 08/10/2026")
prompt_a = "abhishekl name ke client ka school website banana hai aur deadline 08/10/2026 - add these"
print(f"Prompt: '{prompt_a}'")
res_a = api("POST", f"/chats/{chat_id}/messages", {"content": prompt_a})
print("\nResponse Text:")
print(res_a["text"])
print("Actions Taken:", res_a["actions"])

clients, projects, activities = get_db_records()
print("\nDatabase Verification:")
print(f"  Clients in DB:  {clients}")
print(f"  Projects in DB: {projects}")
print(f"  Latest Activities: {activities[:2]}")

assert len(clients) == 1, f"Expected 1 client, got {len(clients)}"
assert clients[0][1].lower() == "abhishekl"
assert len(projects) == 1, f"Expected 1 project, got {len(projects)}"
assert projects[0][1] == "School Website"
assert projects[0][2] == clients[0][0]
assert "2026-10-08" in str(projects[0][3]), f"Expected 2026-10-08 in deadline, got {projects[0][3]}"
print(">>> TEST A: [PASSED]\n")

# -------------------------------------------------------------
# TEST B: Duplicate Prevention (Exact Same Request)
# -------------------------------------------------------------
print(">>> TEST B: Send exact same request again (Duplicate Prevention)")
prompt_b = "abhishekl name ke client ka school website banana hai aur deadline 08/10/2026 - add these"
print(f"Prompt: '{prompt_b}'")
res_b = api("POST", f"/chats/{chat_id}/messages", {"content": prompt_b})
print("\nResponse Text:")
print(res_b["text"])
print("Actions Taken:", res_b["actions"])

clients, projects, _ = get_db_records()
print("\nDatabase Verification:")
print(f"  Clients in DB:  {clients}")
print(f"  Projects in DB: {projects}")

assert len(clients) == 1, f"Expected exactly 1 client (no duplicate), got {len(clients)}"
assert len(projects) == 1, f"Expected exactly 1 project (no duplicate), got {len(projects)}"
assert "reused" in res_b["text"].lower() or "existing" in res_b["text"].lower()
print(">>> TEST B: [PASSED]\n")

# -------------------------------------------------------------
# TEST C: Update Deadline to 15/10/2026
# -------------------------------------------------------------
print(">>> TEST C: Update deadline to 15/10/2026")
prompt_c = "abhishekl ke school website project ki deadline 15/10/2026 kar do"
print(f"Prompt: '{prompt_c}'")
res_c = api("POST", f"/chats/{chat_id}/messages", {"content": prompt_c})
print("\nResponse Text:")
print(res_c["text"])
print("Actions Taken:", res_c["actions"])

clients, projects, activities = get_db_records()
print("\nDatabase Verification:")
print(f"  Projects in DB: {projects}")
print(f"  Latest Activity: {activities[0] if activities else 'None'}")

assert len(projects) == 1
assert "2026-10-15" in str(projects[0][3]), f"Expected 2026-10-15, got {projects[0][3]}"
print(">>> TEST C: [PASSED]\n")

# -------------------------------------------------------------
# TEST D: Update Project Status to COMPLETED
# -------------------------------------------------------------
print(">>> TEST D: Update project status to COMPLETED")
prompt_d = "abhishekl ke school website project ka status completed kar do"
print(f"Prompt: '{prompt_d}'")
res_d = api("POST", f"/chats/{chat_id}/messages", {"content": prompt_d})
print("\nResponse Text:")
print(res_d["text"])
print("Actions Taken:", res_d["actions"])

clients, projects, activities = get_db_records()
print("\nDatabase Verification:")
print(f"  Projects in DB: {projects}")
print(f"  Latest Activity: {activities[0] if activities else 'None'}")

assert len(projects) == 1
assert projects[0][4] == "COMPLETED", f"Expected COMPLETED status, got {projects[0][4]}"
assert projects[0][5] == 100, f"Expected 100 progress, got {projects[0][5]}"
print(">>> TEST D: [PASSED]\n")

# -------------------------------------------------------------
# TEST E: READ QUERY (Read vs Action separation)
# -------------------------------------------------------------
print(">>> TEST E: Read query - verify database is source of truth")
prompt_e = "abhishekl ka school website project details batao"
print(f"Prompt: '{prompt_e}'")
res_e = api("POST", f"/chats/{chat_id}/messages", {"content": prompt_e})
print("\nResponse Text:")
print(res_e["text"])
print("Actions Taken:", res_e["actions"])

assert "School Website" in res_e["text"] or "school website" in res_e["text"].lower()
assert "COMPLETED" in res_e["text"].upper() or "completed" in res_e["text"].lower()
print(">>> TEST E: [PASSED]\n")

print("=" * 70)
print("ALL TESTS (TEST A, TEST B, TEST C, TEST D, TEST E) PASSED SUCCESSFULLY!")
print("=" * 70)
