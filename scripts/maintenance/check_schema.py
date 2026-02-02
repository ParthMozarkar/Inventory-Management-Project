import sqlite3
import os

DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db"

def check_schema():
    with open("schema_output.txt", "w") as f:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        tables = ["sales_log", "transactions", "stock_history", "inventory"]
        for table in tables:
            f.write(f"--- {table} ---\n")
            cur.execute(f"PRAGMA table_info({table})")
            for col in cur.fetchall():
                f.write(f"{col}\n")
            f.write("\n")
            
        conn.close()

if __name__ == "__main__":
    check_schema()
