import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

import sys

# New Pathing
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

class checkoutWindowClass:
    def __init__(self, parent, back_cmd):
        self.parent = parent
        self.back_cmd = back_cmd
        
        # UI Colors
        self.clr_bg = "#0f172a"
        self.clr_card = "#1e293b"
        self.clr_accent = "#10b981"
        self.clr_text = "#f8fafc"
        self.clr_dim = "#94a3b8"

        # --- MODULE HEADER ---
        header = tk.Frame(self.parent, bg=self.clr_bg)
        header.pack(fill="x", pady=(0, 30))

        tk.Button(header, text="← BACK", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", 
                 bd=0, padx=15, cursor="hand2", command=self.back_cmd).pack(side="left")
        
        tk.Label(header, text="TERMINAL (POS) - PREMIUM BILLING", font=("Helvetica", 18, "bold"), 
                 bg=self.clr_bg, fg=self.clr_accent, padx=20).pack(side="left")

        # --- MAIN CONTENT ---
        content = tk.Frame(self.parent, bg=self.clr_bg)
        content.pack(fill="both", expand=True)

        # Left Panel (Scanner Card)
        left = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=25, pady=25, width=400)
        left.pack(side="left", fill="both", expand=False)
        left.pack_propagate(False)

        tk.Label(left, text="BOTTLE SCANNER", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 25))

        self.create_field(left, "BARCODE ID", "barcode", focus=True)
        self.create_field(left, "QUANTITY", "qty", default="1")

        self.lbl_msg = tk.Label(left, text="", font=("Helvetica", 10), bg=self.clr_card)
        self.lbl_msg.pack(pady=15)

        tk.Button(left, text="ADD TO TRANSACTION", font=("Helvetica", 11, "bold"), 
                 bg=self.clr_accent, fg=self.clr_bg, cursor="hand2", bd=0, command=self.add).pack(fill="x", pady=20, ipady=15)

        # Right Panel (Transaction Card)
        tk.Frame(content, bg=self.clr_bg, width=30).pack(side="left") # Spacer
        
        right = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=25, pady=25)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="BILLING SUMMARY", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))

        # Table Structure as per User Request
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", borderwidth=0)
        style.map("Treeview", background=[('selected', '#10b981')])

        cols = ("Barcode", "Category", "Brand", "Size", "Rate", "Qty", "Total")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        
        # Optimized widths for POS table (Supplier removed)
        w_map = {"Barcode": 70, "Category": 80, "Brand": 120, "Size": 60, "Rate": 60, "Qty": 40, "Total": 70}
        
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=w_map[col], anchor="center", stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bottom Finish Area
        footer = tk.Frame(right, bg=self.clr_card, pady=20)
        footer.pack(fill="x")

        self.lbl_total = tk.Label(footer, text="GRAND TOTAL: ₹0.00", font=("Helvetica", 16, "bold"), 
                                 bg=self.clr_card, fg="white")
        self.lbl_total.pack(side="left")

        tk.Button(footer, text="BILL", font=("Helvetica", 11, "bold"), 
                 bg="#3b82f6", fg="white", cursor="hand2", bd=0, padx=30, 
                 command=self.finish_sale).pack(side="right", ipady=10)

        # Scanner Binding
        self.barcode_ent.bind("<Return>", self.on_barcode_enter)
        self.qty_ent.bind("<Return>", self.on_qty_enter)
        self.parent.bind("<F12>", lambda e: self.finish_sale())

    def create_field(self, parent, label, attr, default="", focus=False):
        tk.Label(parent, text=label, font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_dim).pack(anchor="w", pady=(15, 0))
        ent = tk.Entry(parent, font=("Helvetica", 12), bg="#0f172a", fg="white", bd=0, insertbackground="white")
        ent.pack(fill="x", pady=5, ipady=10)
        
        if attr == "barcode":
            self.set_placeholder(ent, "Scan or Type Barcode")
        
        if default: 
            ent.delete(0, tk.END)
            ent.insert(0, default)
            ent.config(fg="white") # Ensure default is white
            
        if focus: ent.focus()
        setattr(self, f"{attr}_ent", ent)

    def set_placeholder(self, entry, placeholder):
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="white")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="#94a3b8")

        entry.insert(0, placeholder)
        entry.config(fg="#94a3b8")
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def on_barcode_enter(self, event):
        # If placeholder is active, clear it before processing? 
        # Actually .get() will return placeholder text if we aren't careful.
        # But add() strips and checks. Logic in add() needs to handle placeholder text if it's there?
        # Ideally focus in/out handles it. If user types nothing and hits enter, it might send placeholder.
        # Let's handle this in add()
        self.barcode_ent.focus() # Ensure focus stays 
        self.add()

    def on_qty_enter(self, event):
        self.add()

    def add(self):
        b, q = self.barcode_ent.get().strip(), self.qty_ent.get().strip()
        # Ignore placeholder if somehow submitted
        if b == "Scan or Type Barcode": return
        if not b or not q: return

        try:
            q = int(q)
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            # Fetch Supplier, Barcode, Category, Brand, Size, Rate, Stock
            cur.execute("SELECT supplier, barcode, category, brand, size, price, quantity FROM inventory WHERE barcode=?", (b,))
            row = cur.fetchone()
            conn.close()

            if not row:
                # If product not found (row is None), show clearer error
                self.msg(f"❌ Product Not Found: {b}", "#f43f5e")
                # Optional: Clear field to allow retry
                self.barcode_ent.delete(0, tk.END)
                return

            sup, barcode, cat, brand, size, rate, stock = row
            current_cart_qty = 0
            if self.tree.exists(b):
                curr = self.tree.item(b)["values"]
                current_cart_qty = int(curr[5])

            if stock < (q + current_cart_qty):
                self.msg(f"❌ Shortage: Only {stock}", "#f43f5e")
                messagebox.showwarning("Out of Stock", f"No stock for {brand}\nAvailable Quantity: {stock}")
                return

            total = rate * q
            if self.tree.exists(b):
                curr = self.tree.item(b)["values"]
                new_q = int(curr[5]) + q # Qty is at index 5 now (Barcode[0], Cat[1], Brand[2], Size[3], Rate[4], Qty[5])
                self.tree.item(b, values=(barcode, cat, brand, size, rate, new_q, rate * new_q))
            else:
                self.tree.insert("", "end", iid=b, values=(barcode, cat, brand, size, rate, q, total))

            self.update_total()
            self.barcode_ent.delete(0, tk.END) # This triggers focus out -> placeholder? No, focus is still in.
            # If focus is still in, we want empty field, not placeholder.
            # My logic in on_focus_out puts placeholder back if empty.
            # Since focus is effectively still here (we didn't move it), we just want empty.
            # But wait, self.barcode_ent.focus() is called at end.
            
            self.qty_ent.delete(0, tk.END); self.qty_ent.insert(0, "1")
            self.barcode_ent.focus()
            self.msg("✅ Added Item", "#10b981")

        except ValueError: self.msg("❌ Quantity must be a number", "#f43f5e")

    def msg(self, text, color):
        self.lbl_msg.config(text=text, fg=color)

    def update_total(self):
        total = sum(float(self.tree.item(item)["values"][6]) for item in self.tree.get_children())
        self.lbl_total.config(text=f"GRAND TOTAL: ₹{total:,.2f}")

    def finish_sale(self):
        if not self.tree.get_children(): return
        if messagebox.askyesno("Confirm", "Process Payment & Finalize?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS transactions (tid INTEGER PRIMARY KEY AUTOINCREMENT, items TEXT, total REAL, date TEXT)")
                cur.execute("CREATE TABLE IF NOT EXISTS sales_log (sid INTEGER PRIMARY KEY AUTOINCREMENT, barcode TEXT, brand TEXT, supplier TEXT, qty INTEGER, total REAL, date TEXT)")
                
                bill_items = []
                for child in self.tree.get_children():
                    v = self.tree.item(child)["values"] # Barcode, Cat, Brand, Size, Rate, Qty, Total
                    bill_items.append(f"{v[2]} {v[3]} x{v[5]}")
                    
                    # We need supplier for sales_log, let's fetch it one last time to be sure
                    cur.execute("SELECT supplier FROM inventory WHERE barcode=?", (v[0],))
                    db_sup = cur.fetchone()[0]
                    
                    cur.execute("INSERT INTO sales_log (barcode, brand, supplier, qty, total, date) VALUES (?, ?, ?, ?, ?, ?)",
                               (v[0], v[2], db_sup, v[5], v[6], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    # Update Stock - v[0] is barcode, v[5] is qty
                    cur.execute("UPDATE inventory SET quantity = quantity - ? WHERE barcode = ?", (v[5], v[0]))
                
                total_text = self.lbl_total.cget("text")
                total_val = float(total_text.split("₹")[1].replace(",", ""))
                cur.execute("INSERT INTO transactions (items, total, date) VALUES (?, ?, ?)", 
                           (", ".join(bill_items), total_val, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit(); conn.close()
                messagebox.showinfo("Success", "Transaction Complete. Stock Adjusted.")
                self.tree.delete(*self.tree.get_children()); self.update_total()
            except Exception as e: messagebox.showerror("System Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x700")
    root.config(bg="#0f172a")
    checkoutWindowClass(root, lambda: print("Back"))
    root.mainloop()
