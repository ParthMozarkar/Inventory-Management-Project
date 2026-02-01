import sqlite3
import os

# Unified Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # if running from project root
# Actually, let's just use the absolute path we know
DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db"

def reset_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # List of tables to clear
        tables = [
            'inventory',
            'sales_log',
            'transactions',
            'brands',
            'categories',
            'stock_history',
            'suppliers'
        ]

        print("--- DATA RESET START ---")
        for table in tables:
            try:
                cur.execute(f"DELETE FROM {table}")
                print(f"✓ Cleared table: {table}")
            except sqlite3.OperationalError:
                print(f"⚠ Table {table} does not exist yet. Skipping.")

        conn.commit()
        conn.close()
        print("--- DATA RESET COMPLETE (Users preserved) ---")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    reset_data()
