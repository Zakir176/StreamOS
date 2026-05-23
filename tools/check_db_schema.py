import sqlite3

db_path = r"backend\streamos.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(profiles);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Columns in 'profiles' table: {column_names}")
    if "theme" in column_names:
        print("SUCCESS: 'theme' column exists.")
    else:
        print("FAILURE: 'theme' column is missing!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
