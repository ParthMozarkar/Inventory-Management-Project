import sqlite3
import os

DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db"

def reset_db_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Clear current corrupted sales data
    print("Clearing corrupted sales data...")
    cur.execute("DELETE FROM sales_log")
    cur.execute("DELETE FROM transactions")
    
    # 2. Reset ID auto-increment to 1
    print("Resetting ID sequence...")
    cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'sales_log'")
    cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'transactions'")
    
    conn.commit()
    conn.close()
    print("Database cleanup complete. IDs will start from 1.")

if __name__ == "__main__":
    reset_db_data()
