import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

class InventoryHub:
    def __init__(self, parent, back_cmd):
        self.parent = parent
        self.back_cmd = back_cmd
        
        # UI Colors
        self.clr_bg = "#0f172a"
        self.clr_card = "#1e293b"
        self.clr_accent = "#10b981"
        self.clr_field_bg = "#2d3748"  # Slate Steel - High Visibility
        self.clr_text = "#f8fafc"
        self.clr_dim = "#94a3b8"
        self.clr_warning = "#f59e0b"
        self.clr_danger = "#ef4444"

        # Variables
        self.var_barcode = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_size = tk.StringVar()
        self.var_price = tk.StringVar()
        self.var_qty = tk.StringVar()
        self.var_category = tk.StringVar() 
        self.var_brand = tk.StringVar()    
        self.var_sup = tk.StringVar()      
        self.var_search = tk.StringVar()
        self.var_arrival_date = tk.StringVar()

        # --- MODULE HEADER ---
        header = tk.Frame(self.parent, bg=self.clr_bg)
        header.pack(fill="x", pady=(0, 20))

        tk.Button(header, text="← BACK", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", 
                 bd=0, padx=15, cursor="hand2", command=self.back_cmd).pack(side="left")
        
        tk.Label(header, text="VJ WAREHOUSE INVENTORY", font=("Helvetica", 18, "bold"), 
                 bg=self.clr_bg, fg=self.clr_accent, padx=20).pack(side="left")

        # --- MAIN CONTENT ---
        content = tk.Frame(self.parent, bg=self.clr_bg)
        content.pack(fill="both", expand=True)

        # 1. LEFT PANEL (FORM) WITH ROBUST SCROLLBAR
        left_wrap = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", width=400)
        left_wrap.pack(side="left", fill="both", expand=False)
        left_wrap.pack_propagate(False)

        canvas = tk.Canvas(left_wrap, bg=self.clr_card, highlightthickness=0)
        v_scroll = ttk.Scrollbar(left_wrap, orient="vertical", command=canvas.yview)
        col_left = tk.Frame(canvas, bg=self.clr_card, padx=20, pady=20)

        canvas.create_window((0, 0), window=col_left, anchor="nw", tags="frame")
        canvas.configure(yscrollcommand=v_scroll.set)

        def resize_canvas(e):
            canvas.itemconfig("frame", width=e.width)
        canvas.bind("<Configure>", resize_canvas)

        def update_scroll(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        col_left.bind("<Configure>", update_scroll)

        def on_mousewheel(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # --- FORM FIELDS ---
        l_style = {"bg": self.clr_card, "fg": self.clr_accent, "font": ("Helvetica", 10, "bold")}
        
        tk.Label(col_left, text="STOCK REGISTRATION", font=("Helvetica", 15, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))

        # Date Picker
        tk.Label(col_left, text="📅 ARRIVAL DATE", **l_style).pack(anchor="w", pady=(10, 0))
        if DateEntry:
            self.txt_date = DateEntry(col_left, textvariable=self.var_arrival_date, font=("Helvetica", 11), 
                                     background=self.clr_bg, foreground='white', borderwidth=1, 
                                     headersbackground=self.clr_bg, headersforeground=self.clr_accent,
                                     selectbackground=self.clr_accent, selectforeground=self.clr_bg,
                                     date_pattern='yyyy-mm-dd')
            self.txt_date.pack(fill="x", pady=5, ipady=5)
        else:
            self.add_field(col_left, None, self.var_arrival_date, "YYYY-MM-DD")

        # Dropdowns - Custom Styled
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#2d3748", background="#4a5568", foreground="white", padding=5)

        self.add_dropdown(col_left, "🤝 SUPPLIER / PARTNER", self.var_sup, "var_sup_widget")
        self.add_dropdown(col_left, "📂 CATEGORY", self.var_category, "var_cat_widget")
        self.var_category.trace('w', lambda *args: self.update_brands_from_cat())
        
        self.add_dropdown(col_left, "🏷️ BRAND NAME", self.var_brand, "var_brand_widget")
        self.add_dropdown(col_left, "⚖️ BOTTLE SIZE", self.var_size, "var_size_widget", ["650ML", "500ML", "330ML", "180ML"])

        self.add_field(col_left, "💰 RATE PER BOTTLE (₹)", self.var_price, "0.00")
        self.add_field(col_left, "📦 QUANTITY (CURRENT)", self.var_qty, "0")
        self.add_field(col_left, "🔍 SCAN BARCODE", self.var_barcode, "Scan Bottle Now")

        # Buttons
        btn_f = tk.Frame(col_left, bg=self.clr_card, pady=20)
        btn_f.pack(fill="x")
        
        tk.Button(btn_f, text="REGISTER STOCK", font=("Helvetica", 11, "bold"), 
                 bg=self.clr_accent, fg=self.clr_bg, bd=0, cursor="hand2", command=self.add_stock).pack(fill="x", pady=5, ipady=12)
        
        tk.Button(btn_f, text="UPDATE RATE ONLY", font=("Helvetica", 11, "bold"), 
                 bg="#3b82f6", fg="white", bd=0, cursor="hand2", command=self.update_price).pack(fill="x", pady=5, ipady=12)
        
        tk.Button(btn_f, text="🗑️ DELETE STOCK", font=("Helvetica", 11, "bold"), 
                 bg=self.clr_danger, fg="white", bd=0, cursor="hand2", command=self.delete_stock).pack(fill="x", pady=5, ipady=12)

        # 2. RIGHT PANEL (TABLE)
        tk.Frame(content, bg=self.clr_bg, width=20).pack(side="left")
        right_wrap = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        right_wrap.pack(side="left", fill="both", expand=True)

        self.add_table(right_wrap)

        self.db_migration()
        self.refresh_lists()
        self.refresh_table()

    def add_field(self, parent, label, var, p=""):
        if label:
            tk.Label(parent, text=label, font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_accent).pack(anchor="w", pady=(10, 0))
        e = tk.Entry(parent, textvariable=var, font=("Helvetica", 12), bg=self.clr_field_bg, fg="white", 
                    bd=1, relief="solid", insertbackground="white")
        e.pack(fill="x", pady=5, ipady=10)
        if p:
            def on_in(ev):
                if e.get() == p: e.delete(0, tk.END); e.config(fg="white")
            def on_out(ev):
                if not e.get(): e.insert(0, p); e.config(fg="#a0aec0")
            e.insert(0, p); e.config(fg="#a0aec0")
            e.bind("<FocusIn>", on_in); e.bind("<FocusOut>", on_out)

    def add_dropdown(self, parent, label, var, widget_name, vals=[]):
        tk.Label(parent, text=label, font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_accent).pack(anchor="w", pady=(10, 0))
        cb = ttk.Combobox(parent, textvariable=var, values=vals, font=("Helvetica", 11), state="readonly")
        cb.pack(fill="x", pady=5, ipady=10)
        setattr(self, widget_name, cb)

    def add_table(self, parent):
        t_frame = tk.Frame(parent, bg=self.clr_card)
        t_frame.pack(fill="x", pady=(0, 15))
        
        tk.Entry(t_frame, textvariable=self.var_search, font=("Helvetica", 11), bg=self.clr_bg, fg="white", bd=1, relief="solid").pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(t_frame, text="SEARCH", bg="#334155", fg="white", bd=0, padx=20, command=self.search).pack(side="left", padx=10, ipady=8)

        cols = ("b", "c", "br", "s", "p", "q", "sup", "d")
        head = ("BARCODE", "CATEGORY", "BRAND", "SIZE", "RATE", "QTY", "SUPPLIER", "LATEST ENTRY")
        self.table = ttk.Treeview(parent, columns=cols, show="headings")
        
        # Optimized Fluid Sizing: Compacted to fit 100% width without horizontal scroll
        config = {
            "b": 60, "c": 70, "br": 90, "s": 60, "p": 60, "q": 50, "sup": 80, "d": 110
        }
        
        for c, h in zip(cols, head):
            self.table.heading(c, text=h)
            # Force ALL columns to stretch so they fit within the screen width perfectly
            self.table.column(c, width=config[c], minwidth=40, stretch=True, anchor="center")
        self.table.pack(fill="both", expand=True)
        self.table.tag_configure('low', foreground=self.clr_warning)
        self.table.tag_configure('empty', foreground=self.clr_danger)
        self.table.bind("<<TreeviewSelect>>", self.get_data)

    def db_migration(self):
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            # Ensure table exists first
            cur.execute("CREATE TABLE IF NOT EXISTS inventory (barcode TEXT PRIMARY KEY, name TEXT, price REAL, quantity INTEGER, category TEXT, supplier TEXT, timestamp TEXT)")
            
            # Now Check for missing columns
            cur.execute("PRAGMA table_info(inventory)")
            cols = [col[1] for col in cur.fetchall()]
            
            if 'brand' not in cols:
                print("Adding brand column...")
                cur.execute("ALTER TABLE inventory ADD COLUMN brand TEXT")
            if 'size' not in cols:
                print("Adding size column...")
                cur.execute("ALTER TABLE inventory ADD COLUMN size TEXT")
            
            cur.execute("CREATE TABLE IF NOT EXISTS stock_history (id INTEGER PRIMARY KEY AUTOINCREMENT, supplier TEXT, brand TEXT, size TEXT, qty INTEGER, date TEXT)")
            conn.commit(); conn.close()
        except Exception as e: print(f"DB Error: {e}")

    def refresh_lists(self):
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("SELECT name FROM suppliers"); self.var_sup_widget['values'] = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT name FROM categories"); cats = [r[0] for r in cur.fetchall()]
            self.var_cat_widget['values'] = cats if cats else ["Beer", "Wine"]
            conn.close()
        except: pass

    def update_brands_from_cat(self):
        cat = self.var_category.get()
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("SELECT name FROM brands WHERE category=?", (cat,))
            self.var_brand_widget['values'] = [r[0] for r in cur.fetchall()]
            conn.close()
        except: pass

    def add_stock(self):
        b = self.var_barcode.get()
        if not b or b == "Scan Bottle Now":
            messagebox.showerror("Error", "Barcode is required")
            return
        
        # Auto-name logic
        n = f"{self.var_brand.get()} {self.var_size.get()}"
        self.var_name.set(n)
        
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("SELECT quantity FROM inventory WHERE barcode=?", (b,))
            res = cur.fetchone()
            q = int(self.var_qty.get() or 0)
            p = float(self.var_price.get() or 0)
            d = self.var_arrival_date.get() or datetime.now().strftime("%Y-%m-%d")
            
            if res:
                cur.execute("""UPDATE inventory SET 
                            quantity=quantity+?, 
                            name=?, 
                            price=?, 
                            category=?, 
                            brand=?, 
                            size=?, 
                            supplier=?, 
                            timestamp=? 
                            WHERE barcode=?""", 
                           (q, n, p, self.var_category.get(), self.var_brand.get(), self.var_size.get(), self.var_sup.get(), d, b))
            else:
                cur.execute("""INSERT INTO inventory 
                            (barcode, name, price, quantity, category, brand, size, supplier, timestamp) 
                            VALUES (?,?,?,?,?,?,?,?,?)""", 
                           (b, n, p, q, self.var_category.get(), self.var_brand.get(), self.var_size.get(), self.var_sup.get(), d))
            
            cur.execute("INSERT INTO stock_history (supplier, brand, size, qty, date) VALUES (?,?,?,?,?)", 
                       (self.var_sup.get(), self.var_brand.get(), self.var_size.get(), q, d))
            
            conn.commit(); conn.close()
            messagebox.showinfo("Success", "Stock updated successfully")
            self.refresh_table()
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_price(self):
        b = self.var_barcode.get()
        p = self.var_price.get()
        if not b or not p: return
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("UPDATE inventory SET price=? WHERE barcode=?", (p, b))
        conn.commit(); conn.close(); self.refresh_table()

    def delete_stock(self):
        b = self.var_barcode.get()
        if not b or b == "Scan Bottle Now":
            messagebox.showerror("Error", "Please select a product to delete (scan or click from table)")
            return
        
        # Confirm deletion
        brand = self.var_brand.get()
        size = self.var_size.get()
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to DELETE this product?\n\n"
                                      f"Barcode: {b}\n"
                                      f"Brand: {brand}\n"
                                      f"Size: {size}\n\n"
                                      f"This action cannot be undone!")
        if not confirm:
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM inventory WHERE barcode=?", (b,))
            conn.commit()
            conn.close()
            
            # Clear form fields
            self.var_barcode.set("")
            self.var_brand.set("")
            self.var_size.set("")
            self.var_price.set("")
            self.var_qty.set("")
            self.var_category.set("")
            self.var_sup.set("")
            
            messagebox.showinfo("Success", f"Product '{brand} {size}' deleted successfully!")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {str(e)}")

    def refresh_table(self):
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            # Explicit order: 0:barcode, 1:category, 2:brand, 3:size, 4:price, 5:quantity, 6:supplier, 7:timestamp
            cur.execute("SELECT barcode, category, brand, size, price, quantity, supplier, timestamp FROM inventory")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for r in rows:
                tag = ''
                try:
                    qty = int(r[5]) if r[5] is not None else 0
                    if qty == 0: tag = 'empty'
                    elif qty < 10: tag = 'low'
                except:
                    qty = 0
                self.table.insert('', 'end', values=r, tags=(tag,))
            conn.close()
        except Exception as e:
            print(f"Refresh Error: {e}")

    def get_data(self, ev):
        f = self.table.focus()
        d = self.table.item(f)['values']
        if d:
            # Matches SELECT order: barcode(0), category(1), brand(2), size(3), price(4), qty(5), sup(6), date(7)
            self.var_barcode.set(d[0])
            self.var_category.set(d[1])
            self.var_brand.set(d[2])
            self.var_size.set(d[3])
            self.var_price.set(d[4])
            # When selecting, we default qty to 1 for adding more stock
            self.var_qty.set("1") 
            self.var_sup.set(d[6])
            self.var_arrival_date.set(d[7])

    def search(self):
        q = f"%{self.var_search.get()}%"
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("SELECT barcode, category, brand, size, price, quantity, supplier, timestamp FROM inventory WHERE category LIKE ? OR brand LIKE ? OR name LIKE ?", (q,q,q))
        rows = cur.fetchall(); self.table.delete(*self.table.get_children())
        for r in rows: self.table.insert('', 'end', values=r)
        conn.close()

if __name__ == "__main__":
    root = tk.Tk(); root.geometry("1300x700"); InventoryHub(root, lambda: print("X")); root.mainloop()