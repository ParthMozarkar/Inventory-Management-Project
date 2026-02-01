import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
import sys

# Setup Paths for reorganized structure
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")
# Create db folder if missing for distribution
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Auto-initialize database if missing
from core.create_db import init_db
init_db() # This will create tables and default users if not present
    
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "core"))

class PremiumLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("VJ BEER SHOPE - SECURE ACCESS")
        
        # Center Window
        w, h = 450, 600
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        # Initial State: Hidden (Transparent) for smooth entry
        self.root.attributes('-alpha', 0.0)
        
        self.root.config(bg="#0f172a") # Deep Space Blue
        self.root.resizable(True, True) # Allow resizing for device friendliness

        # Decorative Glow
        glow_frame = tk.Frame(self.root, bg="#10b981", height=2) # Emerald Line
        glow_frame.pack(fill="x")

        # --- LOGO AREA ---
        content = tk.Frame(self.root, bg="#0f172a", padx=40)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="VJ", font=("Century Gothic", 42, "bold"), 
                 bg="#0f172a", fg="#10b981").pack(pady=(60, 0))
        tk.Label(content, text="BEER SHOPE", font=("Century Gothic", 12, "bold"), 
                 bg="#0f172a", fg="#94a3b8").pack(pady=(0, 40))

        tk.Label(content, text="ACCESS PORTAL", font=("Helvetica", 18, "bold"), 
                 bg="#0f172a", fg="white").pack(pady=(0, 30))

        # --- INPUTS ---
        self.create_entry(content, "USERNAME", "user_icon")
        self.username = tk.Entry(content, font=("Helvetica", 14), bg="#1e293b", fg="#94a3b8", 
                                bd=0, insertbackground="white")
        self.username.pack(fill="x", pady=(5, 20), ipady=12)
        self.add_placeholder(self.username, "Enter your username")
        # Bind Return to jump to password
        self.username.bind('<Return>', lambda e: self.password.focus_set())

        self.create_entry(content, "PASSWORD", "lock_icon")
        self.password = tk.Entry(content, font=("Helvetica", 14), bg="#1e293b", fg="#94a3b8", 
                                bd=0, insertbackground="white") # show="*" handled in placeholder logic
        self.password.pack(fill="x", pady=(5, 30), ipady=12)
        self.add_placeholder(self.password, "Enter your password", is_password=True)
        # Bind Return to Submit/Login
        self.password.bind('<Return>', lambda e: self.login())

        # --- BUTTON ---
        # Store button as self.btn_login so we can flash it or reference it if needed
        self.btn_login = tk.Button(content, text="UNLOCK SYSTEM", font=("Helvetica", 12, "bold"), 
                             bg="#10b981", fg="#0f172a", cursor="hand2", bd=0, 
                             activebackground="#34d399", activeforeground="#0f172a",
                             command=self.login)
        self.btn_login.pack(fill="x", ipady=15)

        tk.Label(content, text="PRIVATE ENTERPRISE EDITION", font=("Helvetica", 8), 
                 bg="#0f172a", fg="#334155").pack(side="bottom", pady=20)
        
        # --- ACCESSIBILITY FOCUS ---
        self.username.focus_set()
        
        # Start Animation
        self.fade_in()

    def fade_in(self):
        """Smooth fade-in animation"""
        alpha = self.root.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.08
            self.root.attributes("-alpha", alpha)
            # Adjust speed: 10ms for very smooth fast entry
            self.root.after(10, self.fade_in)
        else:
            self.root.attributes("-alpha", 1.0) # Ensure full visibility

    def add_placeholder(self, entry, placeholder, is_password=False):
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="white")
                if is_password:
                    entry.config(show="●")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="#94a3b8")
                if is_password:
                    entry.config(show="")

        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def create_entry(self, parent, label_text, icon):
        tk.Label(parent, text=label_text, font=("Helvetica", 9, "bold"), 
                 bg="#0f172a", fg="#475569").pack(anchor="w")

    def login(self):
        u, p = self.username.get(), self.password.get()
        # Handle placeholder values as empty
        if u == "Enter your username": u = ""
        if p == "Enter your password": p = ""

        if not u or not p:
            messagebox.showerror("Security", "Identity Verification Required")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p))
            user = cur.fetchone()
            conn.close()

            if user:
                role = user[0]
                self.root.destroy()
                from core.dashboard import IMS
                new_root = tk.Tk()
                # Center the dashboard window too
                w, h = 1350, 750
                ws = new_root.winfo_screenwidth()
                hs = new_root.winfo_screenheight()
                x = (ws/2) - (w/2)
                y = (hs/2) - (h/2)
                new_root.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
                
                IMS(new_root, role, u)
                new_root.mainloop()
            else:
                messagebox.showerror("Denied", "Access Revoked: Invalid Credentials")
        except Exception as e:
            messagebox.showerror("System Error", f"Database Link Failure: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    PremiumLogin(root)
    root.mainloop()
