import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

class CategoryClass:
    def __init__(self, parent, back_cmd=None):
        self.parent = parent
        self.back_cmd = back_cmd
        
        # Colors
        self.clr_bg = "#0f172a"
        self.clr_card = "#1e293b"
        self.clr_accent = "#10b981"
        self.clr_dim = "#94a3b8"

        # Variables
        self.var_name = tk.StringVar()

        # Title
        header = tk.Frame(self.parent, bg=self.clr_bg)
        header.pack(fill="x", pady=(0, 20))

        if self.back_cmd:
            tk.Button(header, text="← BACK", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", 
                     bd=0, padx=15, cursor="hand2", command=self.back_cmd).pack(side="left")

        tk.Label(header, text="MANAGE CATEGORIES", font=("Helvetica", 18, "bold"), 
                 bg=self.clr_bg, fg=self.clr_accent, padx=20).pack(side="left")

        # Content
        entry_frame = tk.Frame(self.parent, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        entry_frame.pack(fill=tk.X, pady=10)

        tk.Label(entry_frame, text="Category Name", font=("Helvetica", 10, "bold"), bg=self.clr_card, fg=self.clr_dim).pack(side=tk.LEFT)
        self.txt_name = tk.Entry(entry_frame, textvariable=self.var_name, font=("Helvetica", 12), bg="#0f172a", fg="white", bd=0, insertbackground="white")
        self.txt_name.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True, ipady=8)
        self.add_placeholder(self.txt_name, "Enter Category (e.g., Beer, Wine, Soda)")
        
        btn_add = tk.Button(entry_frame, text="ADD CATEGORY", font=("Helvetica", 10, "bold"), bg=self.clr_accent, fg=self.clr_bg, cursor="hand2", command=self.add, bd=0)
        btn_add.pack(side=tk.LEFT, padx=5, ipadx=15, ipady=8)

        # Keyboard Binding
        self.txt_name.bind("<Return>", lambda e: self.add())

        # Table
        table_frame = tk.Frame(self.parent, bg=self.clr_bg, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", borderwidth=0)
        style.map("Treeview", background=[('selected', '#10b981')])

        self.categoryTable = ttk.Treeview(table_frame, columns=("cid", "name"), show="headings")
        self.categoryTable.heading("cid", text="ID")
        self.categoryTable.heading("name", text="Name")
        self.categoryTable.column("cid", width=80, anchor="center")
        self.categoryTable.pack(fill=tk.BOTH, expand=True)
        self.categoryTable.bind("<ButtonRelease-1>", self.get_data)

        # Delete Button
        btn_del = tk.Button(self.parent, text="DELETE SELECTED CATEGORY", font=("Helvetica", 10, "bold"), bg="#ef4444", fg="white", cursor="hand2", command=self.delete, bd=0)
        btn_del.pack(fill="x", pady=10, ipady=12)

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
        name = self.var_name.get()
        if name == "" or name == "Enter Category (e.g., Beer, Wine, Soda)":
            messagebox.showerror("Error", "Category name is required")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS categories (cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
            cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Category added!")
            self.var_name.set(""); self.add_placeholder(self.txt_name, "Enter Category (e.g., Beer, Wine, Soda)")
            self.show()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS categories (cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
            cur.execute("SELECT * FROM categories")
            rows = cur.fetchall()
            self.categoryTable.delete(*self.categoryTable.get_children())
            for row in rows:
                self.categoryTable.insert('', tk.END, values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_data(self, ev):
        f = self.categoryTable.focus()
        content = self.categoryTable.item(f)
        row = content['values']
        if row:
            self.var_name.set(row[1])
            self.txt_name.config(fg="white")

    def delete(self):
        f = self.categoryTable.focus()
        content = self.categoryTable.item(f)
        row = content['values']
        if not row:
            messagebox.showerror("Error", "Select a category to delete")
            return
        
        if messagebox.askyesno("Confirm", "Do you really want to delete?"):
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("DELETE FROM categories WHERE cid=?", (row[0],))
                conn.commit()
                conn.close()
                self.show()
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.config(bg="#0f172a")
    obj = CategoryClass(root)
    root.mainloop()
