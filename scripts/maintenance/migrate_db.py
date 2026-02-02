import sqlite3
import os
import sys

# Setup Paths
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

def migrate():
    print(f"Starting migration on: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found. Nothing to migrate.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # 1. Check inventory table columns
        cur.execute("PRAGMA table_info(inventory)")
        columns = [col[1] for col in cur.fetchall()]
        print(f"Existing columns in inventory: {columns}")

        required_columns = [
            ('brand', 'TEXT'),
            ('size', 'TEXT'),
            ('category', 'TEXT'),
            ('supplier', 'TEXT'),
            ('timestamp', 'TEXT')
        ]

        for col_name, col_type in required_columns:
            if col_name not in columns:
                print(f"Adding missing column: {col_name}")
                try:
                    cur.execute(f"ALTER TABLE inventory ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")

        # 2. Check sales_log table columns
        cur.execute("PRAGMA table_info(sales_log)")
        log_columns = [col[1] for col in cur.fetchall()]
        if log_columns:
            print(f"Existing columns in sales_log: {log_columns}")
            if 'supplier' not in log_columns:
                print("Adding missing column 'supplier' to sales_log")
                cur.execute("ALTER TABLE sales_log ADD COLUMN supplier TEXT")

        # 3. Ensure other tables exist (as a safety measure)
        cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS categories (cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS suppliers (sid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, contact TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS transactions (tid INTEGER PRIMARY KEY AUTOINCREMENT, items TEXT, total REAL, date TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS stock_history (id INTEGER PRIMARY KEY AUTOINCREMENT, supplier TEXT, brand TEXT, size TEXT, qty INTEGER, date TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS sales_log (sid INTEGER PRIMARY KEY AUTOINCREMENT, barcode TEXT, brand TEXT, supplier TEXT, qty INTEGER, total REAL, date TEXT)")

        conn.commit()
        conn.close()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
