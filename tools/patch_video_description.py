import sqlite3

db_path = r"backend\streamos.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding 'description' column to 'videos' table...")
    cursor.execute("ALTER TABLE videos ADD COLUMN description TEXT;")
    conn.commit()
    print("Column added successfully.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'description' already exists.")
    else:
        print(f"Error: {e}")
finally:
    conn.close()
