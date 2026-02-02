import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

class BrandClass:
    def __init__(self, parent, back_cmd):
        self.parent = parent
        self.back_cmd = back_cmd
        
        # UI Colors
        self.clr_bg = "#0f172a"
        self.clr_card = "#1e293b"
        self.clr_accent = "#10b981"
        self.clr_text = "#f8fafc"
        self.clr_dim = "#94a3b8"

        # Variables
        self.var_name = tk.StringVar()
        self.var_cat = tk.StringVar()

        # Variables
        self.var_name = tk.StringVar()
        self.var_cat = tk.StringVar()

        # Local Style Tweak (Override default spacing if needed)
        style = ttk.Style()
        # Ensure focus colors are premium
        style.map("TCombobox", 
                  fieldbackground=[('readonly', "#0f172a"), ('focus', "#1e293b")],
                  foreground=[('readonly', "white"), ('focus', "white")])

        # --- MODULE HEADER ---
        header = tk.Frame(self.parent, bg=self.clr_bg)
        header.pack(fill="x", pady=(0, 30))

        tk.Button(header, text="← BACK", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", 
                 bd=0, padx=15, cursor="hand2", command=self.back_cmd).pack(side="left")
        
        tk.Label(header, text="BRAND MANAGER", font=("Helvetica", 18, "bold"), 
                 bg=self.clr_bg, fg=self.clr_accent, padx=20).pack(side="left")

        # --- MAIN CONTENT ---
        content = tk.Frame(self.parent, bg=self.clr_bg)
        content.pack(fill="both", expand=True)

        # INPUT CARD
        input_card = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=25, pady=25, width=400)
        input_card.pack(side="left", fill="both", expand=False)
        input_card.pack_propagate(False)

        tk.Label(input_card, text="ADD NEW BRAND", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))
        
        tk.Label(input_card, text="SELECT CATEGORY", font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_dim).pack(anchor="w")
        self.txt_cat = ttk.Combobox(input_card, textvariable=self.var_cat, values=[], font=("Helvetica", 11), state="readonly")
        self.txt_cat.pack(fill="x", pady=(5, 20), ipady=5)
        self.txt_cat.set("Select Category")

        tk.Label(input_card, text="BRAND NAME", font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_dim).pack(anchor="w")
        self.txt_name = tk.Entry(input_card, textvariable=self.var_name, font=("Helvetica", 12), bg="#0f172a", fg="white", 
                                bd=1, relief="solid", highlightthickness=0, insertbackground="white")
        self.txt_name.pack(fill="x", pady=(5, 30), ipady=10)
        self.add_placeholder(self.txt_name, "Enter Brand Name")
        
        # Keyboard Binding
        self.txt_name.bind("<Return>", lambda e: self.add())

        btn_frame = tk.Frame(input_card, bg=self.clr_card)
        btn_frame.pack(fill="x", pady=20)

        tk.Button(btn_frame, text="REGISTER BRAND", font=("Helvetica", 10, "bold"), 
                 bg=self.clr_accent, fg=self.clr_bg, cursor="hand2", bd=0, command=self.add).pack(fill="x", ipady=12)

        # Initialize Data
        self.setup_table(content)
        self.db_migration()
        self.load_categories()
        self.show()

    def add_placeholder(self, entry, placeholder):
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

    def load_categories(self):
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS categories (cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
            cur.execute("SELECT name FROM categories")
            cats = [r[0] for r in cur.fetchall()]
            if not cats: cats = ["Beer", "Wine"]
            self.txt_cat['values'] = cats
            # Set Beer as default if available
            if "Beer" in cats:
                self.txt_cat.set("Beer")
            elif cats:
                self.txt_cat.set(cats[0])
            conn.close()
        except: pass

    def setup_table(self, content):
        tk.Frame(content, bg=self.clr_bg, width=30).pack(side="left") # Spacer
        
        table_card = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        table_card.pack(side="left", fill="both", expand=True)

        tk.Label(table_card, text="REGISTERED BRANDS", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))

        self.brandTable = ttk.Treeview(table_card, columns=("bid", "name", "cat"), show="headings")
        self.brandTable.heading("bid", text="ID")
        self.brandTable.heading("name", text="BRAND NAME")
        self.brandTable.heading("cat", text="CATEGORY")
        self.brandTable.column("bid", width=60, anchor="center")
        self.brandTable.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(table_card, text="DELETE SELECTED BRAND", font=("Helvetica", 10, "bold"), 
                 bg="#ef4444", fg="white", cursor="hand2", bd=0, command=self.delete).pack(fill="x", pady=(20, 0), ipady=10)

    def db_migration(self):
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            # Migration: Ensure table exists and has the category column
            cur.execute("CREATE TABLE IF NOT EXISTS brands (bid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
            cols = [c[1] for c in cur.execute("PRAGMA table_info(brands)").fetchall()]
            if 'category' not in cols: 
                cur.execute("ALTER TABLE brands ADD COLUMN category TEXT")
            conn.commit(); conn.close()
        except Exception as e: print(f"Migration Error: {e}")

    def add(self):
        name = self.var_name.get()
        if name == "" or name == "Enter Brand Name":
            messagebox.showerror("Error", "Brand name is required")
            return
            
        cat = self.var_cat.get()
        if cat == "Select Category":
            cat = "" # Fallback or error

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO brands (name, category) VALUES (?, ?)", (name, cat))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Brand registered!")
            self.var_name.set(""); self.add_placeholder(self.txt_name, "Enter Brand Name")
            self.var_cat.set("Select Category")
            self.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT bid, name, category FROM brands")
            rows = cur.fetchall()
            self.brandTable.delete(*self.brandTable.get_children())
            for row in rows:
                self.brandTable.insert('', tk.END, values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        f = self.brandTable.focus()
        content = self.brandTable.item(f)
        row = content['values']
        if not row:
            messagebox.showerror("Error", "Select a brand to delete")
            return
        
        if messagebox.askyesno("Confirm", "Do you really want to delete this brand?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM brands WHERE bid=?", (row[0],))
                conn.commit()
                conn.close()
                self.show()
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x700")
    root.config(bg="#0f172a")
    BrandClass(root, lambda: print("Back"))
    root.mainloop()

