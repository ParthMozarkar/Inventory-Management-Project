import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from datetime import datetime
import sqlite3
import os
import sys

# Paths
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

# Sub-module imports
from core.inventory_window import InventoryHub
from core.checkout_window import checkoutWindowClass # Will update this next
from core.brand import BrandClass
from core.supplier import SupplierClass
from core.analytics import AnalyticsClass

class IMS:
    def __init__(self, root, role="Admin", user="Admin"):
        self.root = root
        self.role = role
        self.user = user
        self.root.geometry("1350x750+0+0")
        self.root.title(f"VJ BEER SHOPE - COMMAND CENTER")
        self.root.config(bg="#0f172a")

        # DESIGN TOKENS
        self.clr_bg = "#0f172a"
        self.clr_sidebar = "#1e293b"
        self.clr_accent = "#10b981"
        self.clr_text = "#f8fafc"

        # --- SOPHISTICATED SIDEBAR ---
        self.sidebar = tk.Frame(self.root, bg=self.clr_sidebar, width=280)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Brand Identity
        brand_frame = tk.Frame(self.sidebar, bg=self.clr_sidebar, pady=30)
        brand_frame.pack(fill="x")
        tk.Label(brand_frame, text="VJ", font=("Century Gothic", 36, "bold"), bg=self.clr_sidebar, fg=self.clr_accent).pack()
        tk.Label(brand_frame, text="BEER SHOPE", font=("Century Gothic", 12, "bold"), bg=self.clr_sidebar, fg="#94a3b8").pack()

        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=30, pady=20)

        # Navigation Buttons (Role-Based Access)
        if self.role == "Admin":
            self.create_nav_btn("📊  Live Dashboard", self.show_home)
            self.create_nav_btn("📦  Warehouse Stock", self.load_inventory)
            self.create_nav_btn("🏷️  Brand Manager", self.load_brands)
            self.create_nav_btn("🤝  Partners/Suppliers", self.load_suppliers)
            self.create_nav_btn("📈  Sales Reports", self.load_analytics)
            tk.Frame(self.sidebar, bg=self.clr_sidebar, height=40).pack()
        else:
            # For Seller, explicitly mention limited access
            tk.Label(self.sidebar, text="STAFF ACCESS", font=("Helvetica", 8, "bold"), bg=self.clr_sidebar, fg="#475569").pack(pady=(20, 10))

        # POS is always available for everyone
        self.btn_pos = tk.Button(self.sidebar, text="⚡ TERMINAL (POS)", font=("Helvetica", 11, "bold"),
                           bg=self.clr_accent, fg=self.clr_bg, bd=0, cursor="hand2", command=self.load_checkout)
        self.btn_pos.pack(fill="x", padx=25, ipady=15)

        # --- DYNAMIC WORKSPACE ---
        self.workspace = tk.Frame(self.root, bg=self.clr_bg, padx=20, pady=20)
        self.workspace.pack(side=tk.LEFT, fill="both", expand=True)

        # STATUS BLOCK
        self.footer = tk.Label(self.root, text="SYSTEM STATUS: ONLINE", font=("Helvetica", 9), bg="#020617", fg="#475569", pady=5)
        self.footer.pack(side="bottom", fill="x")

        # Global Styles for consistent Premium Look
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure Table
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", borderwidth=0)
        style.map("Treeview", background=[('selected', '#10b981')])
        
        # Configure Entry & Combobox for Flat Modern Look with Contrast
        style.configure("TCombobox", fieldbackground="#2d3748", background="#4a5568", foreground="white", 
                        arrowcolor="white", bordercolor="#475569", lightcolor="#475569", darkcolor="#475569", 
                        shiftrelief=0, padding=10)
        style.map("TCombobox", 
                  fieldbackground=[('readonly', "#2d3748"), ('focus', "#334155")], 
                  foreground=[('readonly', "white"), ('focus', "white")])

        # Dropdown Listbox Styling (Global)
        self.root.option_add('*TCombobox*Listbox.background', '#1e293b')
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#10b981')
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#0f172a')
        self.root.option_add('*TCombobox*Listbox.font', ("Helvetica", 11))
        self.root.option_add('*TCombobox*Listbox.borderwidth', 1)
        self.root.option_add('*TCombobox*Listbox.relief', 'flat')

        self.root.title("VJ BEER SHOPE - COMMAND CENTER")

        self.show_home()
        self.update_clock()
        self.bind_keys()

    def bind_keys(self):
        # Keyboard shortcuts for Sidebar
        self.root.bind("<Alt-Key-1>", lambda e: self.show_home())
        if self.role == "Admin":
            self.root.bind("<Alt-Key-2>", lambda e: self.load_inventory())
            self.root.bind("<Alt-Key-3>", lambda e: self.load_brands())
            self.root.bind("<Alt-Key-4>", lambda e: self.load_suppliers())
            self.root.bind("<Alt-Key-5>", lambda e: self.load_analytics())
        
        # POS is always Alt+0 or Alt+P
        self.root.bind("<Alt-Key-0>", lambda e: self.load_checkout())
        self.root.bind("<Alt-p>", lambda e: self.load_checkout())
        self.root.bind("<Alt-P>", lambda e: self.load_checkout())

    def create_nav_btn(self, text, cmd):
        btn = tk.Button(self.sidebar, text=f"   {text}", font=("Helvetica", 11), bg=self.clr_sidebar, fg="#94a3b8", 
                        anchor="w", bd=0, cursor="hand2", command=cmd)
        btn.pack(fill="x", padx=15, pady=2, ipady=12)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1e293b", fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.clr_sidebar, fg="#94a3b8"))

    def clear_workspace(self):
        for widget in self.workspace.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_workspace()
        
        tk.Label(self.workspace, text="OPERATIONAL OVERVIEW", font=("Helvetica", 22, "bold"), bg=self.clr_bg, fg="white").pack(anchor="w")
        
        cards = tk.Frame(self.workspace, bg=self.clr_bg)
        cards.pack(fill="x", pady=20)

        # Home Action Cards
        stock_cmd = self.load_inventory if self.role == "Admin" else lambda: messagebox.showwarning("Restricted", "Admins Only")
        stock_col = "#3b82f6" if self.role == "Admin" else "#475569"
        self.create_home_card(cards, "MANAGE STOCK", "Update beer levels and arrivals." if self.role == "Admin" else "Restricted Access", stock_col, stock_cmd)
        
        self.create_home_card(cards, "BILLING TERMINAL", "Scan bottles and sell to customers.", self.clr_accent, self.load_checkout)

        # --- STOCK ALERTS SECTION ---
        alert_frame = tk.Frame(self.workspace, bg="#1e293b", bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        alert_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(alert_frame, text="⚠️ CRITICAL STOCK ALERTS", font=("Helvetica", 12, "bold"), bg="#1e293b", fg="#f59e0b").pack(anchor="w", pady=(0, 15))
        
        try:
            conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
            cur.execute("SELECT brand, name, quantity FROM inventory WHERE quantity < 10 ORDER BY quantity ASC")
            low_stock = cur.fetchall()
            conn.close()
            
            if not low_stock:
                tk.Label(alert_frame, text="✅ All stock levels are healthy.", font=("Helvetica", 10), bg="#1e293b", fg="#94a3b8").pack(anchor="w")
            else:
                # Scrollable area for alerts if many
                alert_scroll = tk.Frame(alert_frame, bg="#1e293b")
                alert_scroll.pack(fill="both", expand=True)
                
                for item in low_stock[:5]: # Show top 5 alerts
                    brand, name, qty = item
                    color = "#ef4444" if qty == 0 else "#f59e0b"
                    status = "OUT OF STOCK" if qty == 0 else f"LOW STOCK: {qty} left"
                    tk.Label(alert_scroll, text=f"• {brand} {name} → {status}", font=("Helvetica", 11), bg="#1e293b", fg=color).pack(anchor="w", pady=2)
                
                if len(low_stock) > 5:
                    tk.Label(alert_scroll, text=f"... and {len(low_stock)-5} more alerts. Check Warehouse Stock.", font=("Helvetica", 9, "italic"), bg="#1e293b", fg="#475569").pack(anchor="w", pady=5)
        except:
            tk.Label(alert_frame, text="Unable to load stock alerts.", font=("Helvetica", 10), bg="#1e293b", fg="#475569").pack(anchor="w")

    def create_home_card(self, parent, title, desc, col, cmd):
        card = tk.Frame(parent, bg="#1e293b", width=300, height=200, highlightthickness=1, highlightbackground="#334155")
        card.pack(side="left", padx=(0, 30))
        card.pack_propagate(False)
        tk.Label(card, text=title, font=("Helvetica", 12, "bold"), bg="#1e293b", fg=col).pack(pady=(30, 10))
        tk.Label(card, text=desc, font=("Helvetica", 9), bg="#1e293b", fg="#94a3b8", wraplength=250).pack()
        btn = tk.Button(card, text="OPEN HUB", font=("Helvetica", 9, "bold"), bg=col, fg="white" if col!="#10b981" else "#0f172a", 
                       bd=0, cursor="hand2", command=cmd)
        btn.pack(side="bottom", pady=25, ipady=8, padx=60, fill="x")

    # SUB-MODULE LOADERS (Same-window navigation with roll security)
    def load_inventory(self):
        if self.role != "Admin": return
        self.clear_workspace()
        InventoryHub(self.workspace, self.show_home)

    def load_checkout(self):
        self.clear_workspace()
        # Sellers see POS immediately; backing up refreshes POS for them
        back_cmd = self.show_home if self.role == "Admin" else self.load_checkout
        checkoutWindowClass(self.workspace, back_cmd)

    def load_brands(self):
        if self.role != "Admin": return
        self.clear_workspace()
        BrandClass(self.workspace, self.show_home)

    def load_suppliers(self):
        if self.role != "Admin": return
        self.clear_workspace()
        SupplierClass(self.workspace, self.show_home)

    def load_analytics(self):
        if self.role != "Admin": return
        self.clear_workspace()
        AnalyticsClass(self.workspace, self.show_home)

    def update_clock(self):
        self.footer.config(text=f"VJ BEER SHOPE SYSTEM  |  SESSION: {self.user.upper()}  |  {datetime.now().strftime('%d %b %Y %I:%M %p')}")
        self.root.after(30000, self.update_clock)

    def logout(self):
        self.root.destroy()
        os.system(f'python "{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")}"')

if __name__ == "__main__":
    root = tk.Tk()
    IMS(root)
    root.mainloop()