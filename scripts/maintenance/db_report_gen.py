import sqlite3
import os

PATHS = [
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db",
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\core\IEEE_Shop.db",
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\dist\VJ_Beer_Inventory\db\IEEE_Shop.db"
]

with open("db_report.txt", "w") as f:
    for db in PATHS:
        if os.path.exists(db):
            f.write(f"\n--- {db} ---\n")
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cur.fetchall()]
            f.write(f"Tables: {tables}\n")
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    f.write(f"  {table}: {cur.fetchone()[0]} rows\n")
                    if table == "sales_log":
                        cur.execute("SELECT brand, total FROM sales_log LIMIT 3")
                        f.write(f"    Sample: {cur.fetchall()}\n")
                except Exception as e:
                    f.write(f"  {table}: Error {e}\n")
            conn.close()
        else:
            f.write(f"\n--- {db} NOT FOUND ---\n")
