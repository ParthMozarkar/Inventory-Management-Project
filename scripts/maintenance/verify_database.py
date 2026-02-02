"""
Database Verification Script
This script checks if your database is set up correctly for permanent product storage.
"""

import sqlite3
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

def verify_database():
    print("=" * 60)
    print("DATABASE VERIFICATION SCRIPT")
    print("=" * 60)
    print(f"\nDatabase Path: {DB_PATH}")
    print(f"Database Exists: {os.path.exists(DB_PATH)}")
    
    if not os.path.exists(DB_PATH):
        print("\n❌ Database does not exist!")
        print("Please run 'create_db.py' first to create the database.")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if inventory table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='inventory'
        """)
        
        if cursor.fetchone():
            print("\n✅ Inventory table exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(inventory)")
            columns = cursor.fetchall()
            
            print("\nTable Schema:")
            print("-" * 60)
            for col in columns:
                print(f"  {col[1]:12} {col[2]:10}")
            
            # Count products
            cursor.execute("SELECT COUNT(*) FROM inventory")
            count = cursor.fetchone()[0]
            print("-" * 60)
            print(f"\nTotal Products in Database: {count}")
            
            if count > 0:
                print("\nSample Products:")
                print("-" * 60)
                cursor.execute("SELECT barcode, name, price, quantity FROM inventory LIMIT 5")
                products = cursor.fetchall()
                for product in products:
                    print(f"  Barcode: {product[0]:15} | Name: {product[1]:20} | Price: ₹{product[2]:6.2f} | Qty: {product[3]:3}")
            else:
                print("\n⚠️  No products in database yet.")
                print("   Add products using: Dashboard → Products → Add Record")
        else:
            print("\n❌ Inventory table does not exist!")
            print("Please run 'create_db.py' to create the table.")
        
        # Check transactions table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='transactions'
        """)
        
        if cursor.fetchone():
            print("\n✅ Transactions table exists")
            cursor.execute("SELECT COUNT(*) FROM transactions")
            trans_count = cursor.fetchone()[0]
            print(f"   Total Transactions: {trans_count}")
        else:
            print("\n⚠️  Transactions table does not exist")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)
        
        if count == 0:
            print("\n💡 TIP: Add your first product:")
            print("   1. Run dashboard.py")
            print("   2. Click 'Products' in the left menu")
            print("   3. Fill in product details and click 'Add Record to Database'")
        else:
            print(f"\n✅ Your system is ready! You have {count} product(s) in the database.")
            print("   These products will be recognized when scanning barcodes.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    verify_database()
    input("\nPress Enter to exit...")
