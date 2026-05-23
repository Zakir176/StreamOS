import sqlite3
import os

db_path = os.path.join(os.getcwd(), "streamos.db")

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. No migration needed.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["videos", "series"]
    
    columns_to_add = ["dominant_color", "thumbnail_placeholder"]
    
    for table in tables:
        try:
            print(f"Checking table: {table}")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in cursor.fetchall()]
            
            for col in columns_to_add:
                if col not in columns:
                    print(f"Adding {col} column to {table}...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT")
                    print(f"Successfully added {col} to {table}.")
                else:
                    print(f"Column {col} already exists in {table}.")
        except Exception as e:
            print(f"Error updating {table}: {e}")

    conn.commit()
    conn.close()
    print("Migration finished!")

if __name__ == "__main__":
    migrate()
