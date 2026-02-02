import sqlite3
import os

DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\core\IEEE_Shop.db"

def fix():
    if not os.path.exists(DB_PATH): 
        print("Not found")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", [t[0] for t in cur.fetchall()])
    cur.execute("SELECT brand, barcode FROM sales_log LIMIT 5")
    print("Data:", cur.fetchall())
    conn.close()

if __name__ == "__main__":
    fix()
