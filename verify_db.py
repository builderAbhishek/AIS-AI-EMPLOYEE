import sqlite3

conn = sqlite3.connect('data/ais_employee.db')
c = conn.cursor()
c.execute("SELECT id, business_name, status, project_count FROM clients WHERE business_name='abhishekl'")
print('CLIENT IN DB:', c.fetchall())

c.execute("SELECT id, project_name, client_id, deadline, status, progress FROM projects WHERE project_name='School Website'")
print('PROJECT IN DB:', c.fetchall())

c.execute("SELECT id, action, entity_type, entity_id, description FROM activities WHERE entity_type IN ('CLIENT', 'PROJECT') ORDER BY id DESC LIMIT 5")
print('\nACTIVITIES LOGGED IN DB:')
for r in c.fetchall():
    print(' ', r)

conn.close()
