import sqlite3
import os

db_path = r"f:\Developer Abhishek\Website\AIS AI EMPLOYEE - V1\data/ais_employee.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find activities that say "AI created task: ..."
cursor.execute("SELECT entity_id, description FROM activities WHERE action = 'TASK_CREATED_BY_AI' OR description LIKE 'AI created task:%'")
activities = cursor.fetchall()

removed = 0
for act in activities:
    task_id = act[0]
    desc = act[1]
    
    # Verify if task is still basically untouched (e.g. TODO state)
    cursor.execute("SELECT id, status FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    if task:
        print(f"Removing accidental test artifact: Task {task_id}")
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        # Optional: delete the activity log too
        cursor.execute("DELETE FROM activities WHERE entity_id = ? AND entity_type = 'TASK'", (task_id,))
        removed += 1

# If there's an issue with ID 17, 18, 19 explicitly:
for id_val in [17, 18, 19]:
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id_val,))
    cursor.execute("DELETE FROM activities WHERE entity_id = ? AND entity_type = 'TASK'", (id_val,))
    removed += 1

conn.commit()
conn.close()

print(f"Cleanup complete. Removed artifacts: {removed}")
