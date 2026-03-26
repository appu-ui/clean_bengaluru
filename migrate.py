import sqlite3

try:
    conn = sqlite3.connect('database.db')
    conn.execute('ALTER TABLE report ADD COLUMN area TEXT')
    conn.commit()
    print('Added area column successfully')
except sqlite3.OperationalError as e:
    print('Error or existing column:', e)
finally:
    conn.close()
