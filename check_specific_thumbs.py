import sqlite3
import os

db_path = r"backend\streamos.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

ids = (198, 240, 241, 242, 2, 3, 5, 1, 4, 6)
print(f"--- Checking IDs: {ids} ---")
cursor.execute(f"SELECT id, title, thumbnail_path FROM videos WHERE id IN {ids}")
for row in cursor.fetchall():
    path = row[2]
    exists = os.path.exists(path) if path else False
    print(f"ID: {row[0]}, Title: {row[1]}, Path: {path}, Exists: {exists}")

print("\n--- Checking Series IDs ---")
cursor.execute(f"SELECT id, title, poster_path FROM series WHERE id IN {ids}")
for row in cursor.fetchall():
    path = row[2]
    exists = os.path.exists(path) if path and not path.startswith('http') else (True if path and path.startswith('http') else False)
    print(f"ID: {row[0]}, Title: {row[1]}, Path: {path}, Exists/URL: {exists}")

conn.close()
