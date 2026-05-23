import sqlite3
import os

db_path = r"backend\streamos.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Series Posters ---")
cursor.execute("SELECT id, title, poster_path FROM series LIMIT 10")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Title: {row[1]}, Path: {row[2]}")

print("\n--- Video Thumbnails ---")
cursor.execute("SELECT id, title, thumbnail_path FROM videos LIMIT 10")
for row in cursor.fetchall():
    path = row[2]
    exists = os.path.exists(path) if path else False
    print(f"ID: {row[0]}, Title: {row[1]}, Path: {path}, Exists: {exists}")

conn.close()
