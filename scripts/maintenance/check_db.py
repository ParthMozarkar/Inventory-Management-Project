import sqlite3
import os

conn = sqlite3.connect('IEEE_Shop.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Check product count
cursor.execute('SELECT COUNT(*) FROM inventory')
count = cursor.fetchone()[0]
print(f"\nProducts in inventory: {count}")

# Show sample products
if count > 0:
    cursor.execute('SELECT barcode, name, price, quantity FROM inventory LIMIT 5')
    products = cursor.fetchall()
    print("\nSample products:")
    for p in products:
        print(f"  {p[0]} - {p[1]} - ${p[2]} - Qty: {p[3]}")

conn.close()
