import sqlite3
import os

DB_PATH = r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db"

def fix():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Check current data
    cur.execute("SELECT brand, barcode FROM sales_log LIMIT 5")
    print("Before fix:", cur.fetchall())
    
    # 2. Force update brands from inventory
    cur.execute('''
        UPDATE sales_log 
        SET brand = (
            SELECT brand FROM inventory WHERE inventory.barcode = sales_log.barcode
        )
        WHERE EXISTS (
            SELECT 1 FROM inventory WHERE inventory.barcode = sales_log.barcode
        )
    ''')
    
    # 3. If brand is "Beer" or "Wine" or empty, and we have a name in inventory, use part of the name
    # But usually 'brand' in inventory is correct.
    
    conn.commit()
    
    cur.execute("SELECT brand, barcode FROM sales_log LIMIT 5")
    print("After fix:", cur.fetchall())
    
    conn.close()

if __name__ == "__main__":
    fix()
