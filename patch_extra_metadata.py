import sqlite3

db_path = r"backend\streamos.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_columns(table, columns):
    for col, data_type in columns.items():
        try:
            print(f"Adding column '{col}' to table '{table}'...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {data_type};")
            conn.commit()
            print(f"Column '{col}' added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column '{col}' already exists in '{table}'.")
            else:
                print(f"Error adding '{col}' to '{table}': {e}")

new_cols = {
    "cast": "TEXT",
    "director": "TEXT",
    "trailer_url": "TEXT"
}

add_columns("series", new_cols)
add_columns("videos", new_cols)

conn.close()
