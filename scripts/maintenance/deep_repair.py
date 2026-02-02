import sqlite3
import os

DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db"

def deep_repair():
    if not os.path.exists(DB_PATH): return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Repairing inventory data types...")
    # Any row where quantity is not a number, we reset it to 0
    cur.execute("SELECT barcode, quantity, price FROM inventory")
    rows = cur.fetchall()
    
    for barcode, qty, price in rows:
        try:
            int(qty)
        except:
            print(f"Fixing corrupted quantity for {barcode} (was {qty})")
            cur.execute("UPDATE inventory SET quantity=0 WHERE barcode=?", (barcode,))
            
        try:
            float(price)
        except:
            print(f"Fixing corrupted price for {barcode} (was {price})")
            cur.execute("UPDATE inventory SET price=0.0 WHERE barcode=?", (barcode,))
    
    # Also clean up sales_log just in case
    cur.execute("DELETE FROM sales_log")
    cur.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='sales_log'")
    
    conn.commit()
    conn.close()
    print("Repair complete.")

if __name__ == "__main__":
    deep_repair()
