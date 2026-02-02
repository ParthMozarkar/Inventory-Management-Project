import sqlite3
import os

# Get absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "IEEE_Shop.db")

def update_database():
    print(f"Updating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(inventory)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add category if missing
    if 'category' not in columns:
        print("Adding 'category' column...")
        cursor.execute("ALTER TABLE inventory ADD COLUMN category TEXT")
        
    # Add supplier if missing
    if 'supplier' not in columns:
        print("Adding 'supplier' column...")
        cursor.execute("ALTER TABLE inventory ADD COLUMN supplier TEXT")
    
    # Also fix timestamp if it's missing (unlikely but good to check)
    if 'timestamp' not in columns:
        print("Adding 'timestamp' column...")
        cursor.execute("ALTER TABLE inventory ADD COLUMN timestamp TEXT")
        
    conn.commit()
    conn.close()
    print("Database updated successfully!")

if __name__ == "__main__":
    update_database()
