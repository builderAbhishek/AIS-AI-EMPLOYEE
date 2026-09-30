import sqlite3
for dbname in ["ais.db", "ais_crm.db"]:
    print(f"\n=== {dbname} ===")
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f"Tables: {tables}")
    if "task" in tables:
        c.execute("SELECT id, title, status FROM task LIMIT 3")
        print("task rows:", c.fetchall())
    if "tasks" in tables:
        c.execute("SELECT id, title, status FROM tasks LIMIT 3")
        print("tasks rows:", c.fetchall())
    if "project" in tables:
        c.execute("SELECT id, project_name, status FROM project LIMIT 3")
        print("project rows:", c.fetchall())
    if "projects" in tables:
        c.execute("SELECT id, project_name, status FROM projects LIMIT 3")
        print("projects rows:", c.fetchall())
    conn.close()
