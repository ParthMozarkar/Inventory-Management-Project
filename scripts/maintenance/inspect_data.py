import sqlite3
import os

DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db"

def inspect_and_fix():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("--- Inspecting sales_log ---")
    cur.execute("SELECT * FROM sales_log")
    rows = cur.fetchall()
    print(f"Total rows: {len(rows)}")
    for r in rows:
        print(r)
        
    print("\n--- Inspecting inventory ---")
    cur.execute("SELECT * FROM inventory")
    inv_rows = cur.fetchall()
    print(f"Total inventory items: {len(inv_rows)}")
    for r in inv_rows[:5]:
        print(r)

    # If rows exist and contain strings in numeric columns, they are likely shifted.
    # The user reported '650ML' and 'Parth' in int() errors.
    # Let's check where 'Parth' and '650ML' are.
    
    # If the user wants to start over or clean up:
    # cur.execute("DELETE FROM sales_log")
    # cur.execute("DELETE FROM transactions")
    # cur.execute("UPDATE sqlite_sequence SET seq=0 WHERE name IN ('sales_log', 'transactions')")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inspect_and_fix()
