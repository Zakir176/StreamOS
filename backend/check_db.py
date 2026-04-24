import sqlite3
import os

db_path = os.path.join(os.getcwd(), "streamos.db")

def check_db():
    if not os.path.exists(db_path):
        print("DB not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Videos ---")
    cursor.execute("SELECT title, thumbnail_path, thumbnail_placeholder FROM videos LIMIT 10")
    for row in cursor.fetchall():
        print(f"Title: {row[0]}, Path: {row[1]}, HasPlaceholder: {bool(row[2])}")
        
    print("\n--- Series ---")
    cursor.execute("SELECT title, poster_path, thumbnail_placeholder FROM series LIMIT 5")
    for row in cursor.fetchall():
        print(f"Title: {row[0]}, Path: {row[1]}, HasPlaceholder: {bool(row[2])}")
        
    conn.close()

if __name__ == "__main__":
    check_db()
