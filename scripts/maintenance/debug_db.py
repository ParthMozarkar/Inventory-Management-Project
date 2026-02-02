import sqlite3
import os

PATHS = [
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db",
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\dist\VJ_Beer_Inventory\db\IEEE_Shop.db"
]

for db in PATHS:
    if os.path.exists(db):
        print(f"\n--- Database: {db} ---")
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cur.fetchall()]
        print("Tables:", tables)
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {cur.fetchone()[0]} rows")
        conn.close()
    else:
        print(f"\n--- Database: {db} NOT FOUND ---")
