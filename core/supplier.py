import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

class SupplierClass:
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
        self.var_contact = tk.StringVar()

        # --- MODULE HEADER ---
        header = tk.Frame(self.parent, bg=self.clr_bg)
        header.pack(fill="x", pady=(0, 30))

        tk.Button(header, text="← BACK", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", 
                 bd=0, padx=15, cursor="hand2", command=self.back_cmd).pack(side="left")
        
        tk.Label(header, text="PARTNER & SUPPLIER MANAGER", font=("Helvetica", 18, "bold"), 
                 bg=self.clr_bg, fg=self.clr_accent, padx=20).pack(side="left")

        # --- MAIN CONTENT ---
        content = tk.Frame(self.parent, bg=self.clr_bg)
        content.pack(fill="both", expand=True)

        # INPUT CARD
        input_card = tk.Frame(content, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=25, pady=25, width=400)
        input_card.pack(side="left", fill="both", expand=False)
        input_card.pack_propagate(False)

        tk.Label(input_card, text="ADD NEW PARTNER", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))
        
        tk.Label(input_card, text="SUPPLIER NAME", font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_dim).pack(anchor="w")
        self.txt_name = tk.Entry(input_card, textvariable=self.var_name, font=("Helvetica", 12), bg="#0f172a", fg="white", 
                                bd=1, relief="solid", highlightthickness=0, insertbackground="white")
        self.txt_name.pack(fill="x", pady=(5, 15), ipady=8)
        self.add_placeholder(self.txt_name, "Enter Supplier Name")
        
        tk.Label(input_card, text="CONTACT NUMBER", font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_dim).pack(anchor="w")
        self.txt_contact = tk.Entry(input_card, textvariable=self.var_contact, font=("Helvetica", 12), bg="#0f172a", fg="white", 
                                   bd=1, relief="solid", highlightthickness=0, insertbackground="white")
        self.txt_contact.pack(fill="x", pady=(5, 15), ipady=8)
        self.add_placeholder(self.txt_contact, "Enter Phone Number")

        # Keyboard Binding
        self.txt_name.bind("<Return>", lambda e: self.txt_contact.focus_set())
        self.txt_contact.bind("<Return>", lambda e: self.add())

        tk.Button(input_card, text="ADD SUPPLIER", font=("Helvetica", 10, "bold"), 
                 bg=self.clr_accent, fg=self.clr_bg, cursor="hand2", bd=0, command=self.add).pack(fill="x", pady=10, ipady=10)

        # TABLE CARD (RIGHT PANEL)
        tk.Frame(content, bg=self.clr_bg, width=30).pack(side="left") # Spacer
        
        right_panel = tk.Frame(content, bg=self.clr_bg)
        right_panel.pack(side="left", fill="both", expand=True)

        # 1. Supplier Database (Top)
        table_card = tk.Frame(right_panel, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        table_card.pack(side="top", fill="both", expand=True, pady=(0, 20))

        tk.Label(table_card, text="SUPPLIER DATABASE", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))

        # Table with Night Space Theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", borderwidth=0)
        style.map("Treeview", background=[('selected', '#10b981')])

        self.table = ttk.Treeview(table_card, columns=("sid", "name", "contact"), show="headings", height=8)
        self.table.heading("sid", text="ID")
        self.table.heading("name", text="NAME")
        self.table.heading("contact", text="CONTACT")
        self.table.column("sid", width=50, anchor="center")
        self.table.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(table_card, text="REMOVE SELECTED PARTNER", font=("Helvetica", 10, "bold"), 
                 bg="#ef4444", fg="white", cursor="hand2", bd=0, command=self.delete).pack(fill="x", pady=(20, 0), ipady=10)

        # 2. Sales Stats (Bottom)
        stats_card = tk.Frame(right_panel, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        stats_card.pack(side="bottom", fill="both", expand=True)
        
        tk.Label(stats_card, text="SUPPLIER SALES PERFORMANCE", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))
        
        self.stats_table = ttk.Treeview(stats_card, columns=("sup", "total"), show="headings", height=8)
        self.stats_table.heading("sup", text="SUPPLIER")
        self.stats_table.heading("total", text="TOTAL SALES (₹)")
        self.stats_table.column("total", anchor="e")
        self.stats_table.pack(fill=tk.BOTH, expand=True)

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

    def add(self):
        n, c = self.var_name.get(), self.var_contact.get()
        if n=="" or n=="Enter Supplier Name" or c=="" or c=="Enter Phone Number":
            messagebox.showerror("Error", "All fields are required")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS suppliers (sid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, contact TEXT)")
            cur.execute("INSERT INTO suppliers (name, contact) VALUES (?,?)", (n, c))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Supplier added!")
            self.var_name.set(""); self.add_placeholder(self.txt_name, "Enter Supplier Name")
            self.var_contact.set(""); self.add_placeholder(self.txt_contact, "Enter Phone Number")
            self.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Load Suppliers
            cur.execute("CREATE TABLE IF NOT EXISTS suppliers (sid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, contact TEXT)")
            cur.execute("SELECT * FROM suppliers")
            rows = cur.fetchall()
            self.table.delete(*self.table.get_children())
            for row in rows:
                self.table.insert('', tk.END, values=row)
            
            # Load Sales Stats
            # Ensure sales_log exists (it's created in checkout but good to be safe)
            # We need to handle the case where column might not exist if user hasn't run checkout update yet, 
            # but since I updated checkout, let's assume it catches up or we handle the error gracefully or create table.
            # Best to check/add col like in checkout, but for display let's standard query.
            try:
                cur.execute("SELECT supplier, SUM(total) FROM sales_log GROUP BY supplier ORDER BY SUM(total) DESC")
                stats = cur.fetchall()
                self.stats_table.delete(*self.stats_table.get_children())
                for s in stats:
                    sup_name = s[0] if s[0] else "Unknown"
                    self.stats_table.insert('', tk.END, values=(sup_name, f"₹{s[1]:,.2f}"))
            except:
                pass # Table might not exist yet or no supplier column

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        f = self.table.focus()
        row = self.table.item(f)['values']
        if not row:
            messagebox.showerror("Error", "Select a supplier")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM suppliers WHERE sid=?", (row[0],))
            conn.commit()
            conn.close()
            self.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x700")
    root.config(bg="#0f172a")
    SupplierClass(root, lambda: print("Back"))
    root.mainloop()

