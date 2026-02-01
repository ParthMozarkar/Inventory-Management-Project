import sqlite3
import os

import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Inventory Table
    cur.execute("""CREATE TABLE IF NOT EXISTS inventory (
        barcode TEXT PRIMARY KEY,
        name TEXT,
        price REAL,
        quantity INTEGER,
        category TEXT,
        brand TEXT,
        size TEXT,
        supplier TEXT,
        timestamp TEXT
    )""")

    # Users Table
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
    cur.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'Admin')")
    cur.execute("INSERT OR IGNORE INTO users VALUES ('seller', 'seller123', 'Seller')")

    # Categories Table
    cur.execute("CREATE TABLE IF NOT EXISTS categories (cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")

    # Suppliers Table
    cur.execute("CREATE TABLE IF NOT EXISTS suppliers (sid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, contact TEXT)")

    # Transactions Table
    cur.execute("CREATE TABLE IF NOT EXISTS transactions (tid INTEGER PRIMARY KEY AUTOINCREMENT, items TEXT, total REAL, date TEXT)")

    # Stock History Table
    cur.execute("CREATE TABLE IF NOT EXISTS stock_history (id INTEGER PRIMARY KEY AUTOINCREMENT, supplier TEXT, brand TEXT, size TEXT, qty INTEGER, date TEXT)")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()