import sqlite3
import os

PATHS = [
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\db\IEEE_Shop.db",
    r"d:\inverntory manegmenet\Simple-Inventory-Management-System-by-Barcode-Scanner\dist\VJ_Beer_Inventory\db\IEEE_Shop.db"
]

def force_migrate():
    for db in PATHS:
        if not os.path.exists(db):
            print(f"Skipping {db} - not found.")
            continue
            
        print(f"Migrating brands in {db}...")
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        # Ensure brand column exists first (just in case)
        try:
            cur.execute("ALTER TABLE sales_log ADD COLUMN brand TEXT")
        except: pass # already exists
        
        try:
            # Update sales_log brand from inventory based on barcode
            cur.execute('''
                UPDATE sales_log 
                SET brand = (
                    SELECT brand 
                    FROM inventory 
                    WHERE inventory.barcode = sales_log.barcode
                )
                WHERE EXISTS (
                    SELECT 1 
                    FROM inventory 
                    WHERE inventory.barcode = sales_log.barcode
                )
            ''')
            
            # If inventory is empty or brand is missing there, try to use Category if Brand is "Beer/Wine"
            # Actually, the user wants the real brand name.
            
            conn.commit()
            count = cur.execute('SELECT COUNT(*) FROM sales_log').fetchone()[0]
            print(f"Migration complete for {db}. Rows: {count}")
            
            # Sanity check: show some data
            cur.execute("SELECT brand FROM sales_log LIMIT 5")
            print("Sample brands:", cur.fetchall())
        except Exception as e:
            print(f"Error migrating {db}: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    force_migrate()
