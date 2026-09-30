import sqlite3, glob
# Find the DB file
for f in glob.glob("*.db"):
    print(f"DB: {f}")
    conn = sqlite3.connect(f)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for row in c.fetchall():
        print(f"  Table: {row[0]}")
    conn.close()
