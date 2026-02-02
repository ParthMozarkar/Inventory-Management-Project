import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
import os
from datetime import datetime, timedelta
from tkinter import filedialog
import sys
from fpdf import FPDF
from tkcalendar import DateEntry

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "db", "IEEE_Shop.db")

class AnalyticsClass:
    def __init__(self, parent, back_cmd):
        self.parent = parent
        self.back_cmd = back_cmd
        
        # UI Colors
        self.clr_bg = "#0f172a"
        self.clr_card = "#1e293b"
        self.clr_accent = "#10b981"
        self.clr_text = "#f8fafc"
        self.clr_dim = "#94a3b8"
        
        # State for custom range
        self.custom_start = None
        self.custom_end = None

        # --- MODULE HEADER ---
        header = tk.Frame(self.parent, bg=self.clr_bg)
        header.pack(fill="x", pady=(0, 20))

        tk.Button(header, text="← BACK", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", 
                 bd=0, padx=15, cursor="hand2", command=self.back_cmd).pack(side="left")
        
        tk.Label(header, text="VJ SALES ANALYTICS", font=("Helvetica", 18, "bold"), 
                 bg=self.clr_bg, fg=self.clr_accent, padx=20).pack(side="left")
        
        # Filter Control
        self.filter_var = tk.StringVar(value="Today")
        
        tk.Label(header, text="FILTER:", font=("Helvetica", 10, "bold"), bg=self.clr_bg, fg=self.clr_dim).pack(side="right", padx=(20, 0))
        self.filter_cb = ttk.Combobox(header, textvariable=self.filter_var, values=["Today", "Yesterday", "Weekly", "Monthly", "Yearly", "Custom Range"], 
                                state="readonly", font=("Helvetica", 10), width=15)
        self.filter_cb.pack(side="right", padx=10)
        self.filter_cb.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        tk.Button(header, text="📥 SALES REPORT", font=("Helvetica", 9, "bold"), bg=self.clr_accent, fg=self.clr_bg,
                 bd=0, padx=10, pady=5, cursor="hand2", command=self.download_sales_chart_pdf).pack(side="right", padx=10)
        
        # Style Combobox for dark theme
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground="#0f172a", background="#1e293b", foreground="white")

        # --- MAIN CONTENT ---
        main_frame = tk.Frame(self.parent, bg=self.clr_bg)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Overview Stats
        stats_frame = tk.Frame(main_frame, bg=self.clr_bg)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        self.total_rev = tk.StringVar(value="₹0.00")
        
        # Stat Box
        self.stat_box = tk.Frame(stats_frame, bg=self.clr_card, width=300, height=120, bd=0, highlightbackground="#334155", highlightthickness=1)
        self.stat_box.pack(side=tk.LEFT, padx=(0, 20))
        self.stat_box.pack_propagate(False)
        self.lbl_stat_title = tk.Label(self.stat_box, text=f"REVENUE ({self.filter_var.get().upper()})", font=("Helvetica", 9, "bold"), bg=self.clr_card, fg=self.clr_dim)
        self.lbl_stat_title.pack(pady=(25, 5))
        tk.Label(self.stat_box, textvariable=self.total_rev, font=("Helvetica", 22, "bold"), bg=self.clr_card, fg=self.clr_accent).pack()

        # Data Layout Top Row
        data_frame = tk.Frame(main_frame, bg=self.clr_bg)
        data_frame.pack(fill=tk.BOTH, expand=True)
 
        # 1. Revenue Per Brand Table (Top Left)
        brand_card = tk.Frame(data_frame, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        brand_card.pack(side="left", fill="both", expand=True)
        tk.Label(brand_card, text="REVENUE PER BRAND", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))
        
        self.brand_table = ttk.Treeview(brand_card, columns=("brand", "total"), show="headings")
        self.brand_table.heading("brand", text="BRAND NAME")
        self.brand_table.heading("total", text="TOTAL SALES (₹)")
        self.brand_table.pack(fill=tk.BOTH, expand=True)

        tk.Frame(data_frame, bg=self.clr_bg, width=30).pack(side="left") # Spacer
        
        # 2. Live Transaction Report (Top Right)
        history_card = tk.Frame(data_frame, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        history_card.pack(side="left", fill="both", expand=True)
        
        hist_header = tk.Frame(history_card, bg=self.clr_card)
        hist_header.pack(fill="x", pady=(0, 15))
        
        tk.Label(hist_header, text="LIVE TRANSACTION REPORT", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(side="left")
        
        tk.Button(hist_header, text="📥 DETAILED LOG", font=("Helvetica", 8, "bold"), bg=self.clr_accent, fg=self.clr_bg,
                 bd=0, padx=8, pady=2, cursor="hand2", command=self.download_detailed_report).pack(side="right")
        
        table_frame = tk.Frame(history_card, bg=self.clr_card)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.hist_table = ttk.Treeview(table_frame, columns=("date", "cat", "br", "qty", "pr", "total"), show="headings")
        cols_info = [
            ("date", "TIME", 110, True), 
            ("cat", "CAT", 55, False), 
            ("br", "BRAND", 100, True), 
            ("qty", "QTY", 35, False), 
            ("pr", "PRICE", 55, False), 
            ("total", "TOTAL", 65, False)
        ]
        for col, head, w, s in cols_info:
            self.hist_table.heading(col, text=head)
            self.hist_table.column(col, width=w, minwidth=w, stretch=s, anchor="center")
        
        scrolly = ttk.Scrollbar(table_frame, orient="vertical", command=self.hist_table.yview)
        self.hist_table.configure(yscrollcommand=scrolly.set)
        scrolly.pack(side="right", fill="y")
        self.hist_table.pack(fill=tk.BOTH, expand=True)

        # 3. Brand Performance Graph (Bottom Full Width)
        graph_log_frame = tk.Frame(main_frame, bg=self.clr_bg)
        graph_log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        graph_card = tk.Frame(graph_log_frame, bg=self.clr_card, bd=0, highlightthickness=1, highlightbackground="#334155", padx=20, pady=20)
        graph_card.pack(fill="both", expand=True)
        tk.Label(graph_card, text="BRAND SALES PERFORMANCE GRAPH", font=("Helvetica", 12, "bold"), bg=self.clr_card, fg="white").pack(anchor="w", pady=(0, 15))

        self.canvas_frame = tk.Frame(graph_card, bg=self.clr_card)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.clr_card, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.load_analytics()
        # Auto-refresh every 60 seconds
        self.parent.after(60000, self.auto_refresh)

    def auto_refresh(self):
        try:
            self.load_analytics()
            self.parent.after(60000, self.auto_refresh)
        except: pass
        
    def on_filter_change(self, event):
        if self.filter_var.get() == "Custom Range":
            self.open_date_selector()
        else:
            self.custom_start = None
            self.custom_end = None
            self.load_analytics()

    def open_date_selector(self):
        # Create a simple dialog for start and end date
        dialog = tk.Toplevel(self.parent)
        dialog.title("Select Date Range")
        dialog.geometry("300x200")
        dialog.config(bg="#1e293b")
        dialog.grab_set() # Modal
        
        tk.Label(dialog, text="Start Date:", bg="#1e293b", fg="white").pack(pady=(20, 5))
        start_cal = DateEntry(dialog, width=12, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        start_cal.pack(pady=5)
        
        tk.Label(dialog, text="End Date:", bg="#1e293b", fg="white").pack(pady=5)
        end_cal = DateEntry(dialog, width=12, background='darkblue',
                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        end_cal.pack(pady=5)
        
        def set_dates():
            self.custom_start = start_cal.get_date()
            self.custom_end = end_cal.get_date()
            if self.custom_start > self.custom_end:
                messagebox.showerror("Error", "Start date cannot be after end date.")
                return
            dialog.destroy()
            self.load_analytics()
            
        tk.Button(dialog, text="Apply Filter", command=set_dates, bg="#10b981", fg="white").pack(pady=20)
        self.parent.wait_window(dialog)

    def draw_revenue_graph(self, data):
        self.canvas.delete("all")
        if not data:
            self.canvas.create_text(200, 100, text="No Data Available for this period", fill=self.clr_dim, font=("Helvetica", 10))
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100: w = 800 # Default if hidden
        if h < 100: h = 250

        padding = 50
        graph_h = h - padding * 2
        graph_w = w - padding * 2
        
        max_val = max([d[1] for d in data]) if data else 1
        if max_val == 0: max_val = 1
        
        bar_w = graph_w / (len(data) * 2)
        colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f43f5e", "#10b981", "#3b82f6", "#f59e0b"]
        
        for i, (brand, val) in enumerate(data):
            # Calculate bar dimensions
            bar_h = (val / max_val) * graph_h
            x0 = padding + (i * 2 * bar_w) + (bar_w / 2)
            y0 = h - padding - bar_h
            x1 = x0 + bar_w
            y1 = h - padding
            
            # Draw Bar
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color, width=0)
            
            # Label
            label = brand[:12] + ".." if len(brand) > 12 else brand
            self.canvas.create_text(x0 + bar_w/2, y1 + 15, text=label, fill="white", font=("Helvetica", 8, "bold"))
            
            # Value on top
            self.canvas.create_text(x0 + bar_w/2, y0 - 15, text=f"₹{val:,.0f}", fill=color, font=("Helvetica", 8, "bold"))

    def load_analytics(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            period = self.filter_var.get()
            title_text = f"REVENUE ({period.upper()})"
            if period == "Custom Range" and self.custom_start and self.custom_end:
                 title_text = f"REV ({self.custom_start.strftime('%d/%m')} - {self.custom_end.strftime('%d/%m')})"
            self.lbl_stat_title.config(text=title_text)
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            month_str = datetime.now().strftime("%Y-%m")
            year_str = datetime.now().strftime("%Y")
            
            where_clause = ""
            params = ()
            
            if period == "Today" or period == "Daily": # Daily is now Today
                where_clause = "WHERE s.date LIKE ?"
                params = (f"{today_str}%",)
            elif period == "Yesterday":
                yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date LIKE ?"
                params = (f"{yesterday_str}%",)
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date >= ?"
                params = (start_date,)
            elif period == "Monthly":
                where_clause = "WHERE strftime('%Y-%m', s.date) = ?"
                params = (month_str,)
            elif period == "Yearly":
                where_clause = "WHERE strftime('%Y', s.date) = ?"
                params = (year_str,)
            elif period == "Custom Range" and self.custom_start and self.custom_end:
                # Inclusive range
                 # Assuming s.date is YYYY-MM-DD HH:MM:SS
                s_str = self.custom_start.strftime("%Y-%m-%d")
                e_str = (self.custom_end + timedelta(days=1)).strftime("%Y-%m-%d") # Next day midnight for correct < compare
                where_clause = "WHERE s.date >= ? AND s.date < ?"
                params = (s_str, e_str)

            # Total Revenue
            cur.execute(f"SELECT SUM(s.total) FROM sales_log s {where_clause}", params)
            rev_res = cur.fetchone()
            rev = rev_res[0] if rev_res[0] else 0
            self.total_rev.set(f"₹{rev:,.2f}")

            # 1. Revenue Per Brand Table (Top Left)
            self.brand_table.delete(*self.brand_table.get_children())
            query = f"""
                SELECT COALESCE(i.brand, s.brand), SUM(s.total) 
                FROM sales_log s
                LEFT JOIN inventory i ON s.barcode = i.barcode
                {where_clause} 
                GROUP BY COALESCE(i.brand, s.brand) 
                ORDER BY SUM(s.total) DESC
            """
            cur.execute(query, params)
            brands_data = cur.fetchall()
            for b in brands_data:
                brand_name = b[0] if b[0] else "Unknown"
                self.brand_table.insert('', tk.END, values=(brand_name, f"₹{b[1]:,.2f}"))

            # 2. Brand Sales Graph (Bottom)
            graph_query = f"""
                SELECT COALESCE(i.brand, s.brand), SUM(s.total) 
                FROM sales_log s
                LEFT JOIN inventory i ON s.barcode = i.barcode
                {where_clause} 
                GROUP BY COALESCE(i.brand, s.brand) 
                ORDER BY SUM(s.total) DESC LIMIT 10
            """
            cur.execute(graph_query, params)
            graph_data = cur.fetchall()
            self.draw_revenue_graph(graph_data)

            # 3. Live Transaction History (Top Right)
            self.hist_table.delete(*self.hist_table.get_children())
            query = f"""
                SELECT s.date, 
                       COALESCE(i.category, 'Unknown'), 
                       COALESCE(i.brand, s.brand), 
                       s.qty, s.total 
                FROM sales_log s
                LEFT JOIN inventory i ON s.barcode = i.barcode
                {where_clause} 
                ORDER BY s.sid DESC LIMIT 100
            """
            cur.execute(query, params)
            for r in cur.fetchall(): 
                date, cat, brand, qty, total = r
                try:
                    qty_val = float(qty) if str(qty).replace('.','',1).isdigit() else 0
                    total_val = float(total) if str(total).replace('.','',1).isdigit() else 0
                    price = total_val / qty_val if qty_val > 0 else 0
                except:
                    price = 0
                self.hist_table.insert('', tk.END, values=(date, cat, brand, qty, f"{price:,.2f}", f"{total:,.2f}"))
            
            conn.close()
        except Exception as e:
            print(f"Analytics Error: {e}")

    def download_sales_chart_pdf(self):
        try:
            period = self.filter_var.get()
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf")],
                                                   initialfile=f"VJ_Sale_Chart_{period}_{today_date}.pdf")
            if not file_path: return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            month_str = datetime.now().strftime("%Y-%m")
            year_str = datetime.now().strftime("%Y")
            where_clause = ""
            params = ()
            if period == "Today" or period == "Daily":
                where_clause = "WHERE s.date LIKE ?"; params = (f"{today_str}%",)
            elif period == "Yesterday":
                yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date LIKE ?"; params = (f"{yesterday_str}%",)
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date >= ?"; params = (start_date,)
            elif period == "Monthly":
                where_clause = "WHERE strftime('%Y-%m', s.date) = ?"; params = (month_str,)
            elif period == "Yearly":
                where_clause = "WHERE strftime('%Y', s.date) = ?"; params = (year_str,)
            elif period == "Custom Range" and self.custom_start and self.custom_end:
                s_str = self.custom_start.strftime("%Y-%m-%d")
                e_str = (self.custom_end + timedelta(days=1)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date >= ? AND s.date < ?"
                params = (s_str, e_str)

            if period in ["Today", "Daily", "Yesterday", "Weekly", "Monthly", "Custom Range"]:
                query = f"""
                    SELECT MAX(s.date), COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, '-'), SUM(s.qty) 
                    FROM sales_log s 
                    LEFT JOIN inventory i ON s.barcode = i.barcode 
                    {where_clause} 
                    GROUP BY COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, '-')
                    ORDER BY MAX(s.date) DESC
                """
            else:
                query = f"""
                    SELECT s.date, COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, '-'), s.qty 
                    FROM sales_log s 
                    LEFT JOIN inventory i ON s.barcode = i.barcode 
                    {where_clause} 
                    ORDER BY s.date DESC
                """
            cur.execute(query, params)
            records = cur.fetchall()
            conn.close()

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 5, txt="SHREE GANESHAY NAMAH", ln=True, align='C')
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(190, 10, txt="V J BEER SHOPEE", ln=True, align='C')
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, txt=f"SALE CHART ({period.upper()})", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            
            # Prepare date display for header based on period
            if period == "Today" or period == "Daily":
                header_date = datetime.now().strftime('%d-%m-%Y')
                pdf.cell(190, 8, txt=f"DATE: {header_date}", ln=True, align='R')
            elif period == "Yesterday":
                y_date = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
                pdf.cell(190, 8, txt=f"DATE: {y_date}", ln=True, align='R')
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime('%d-%m')
                end_date = datetime.now().strftime('%d-%m-%Y')
                pdf.cell(190, 8, txt=f"DATE RANGE: {start_date} till {end_date}", ln=True, align='R')
            elif period == "Monthly":
                month_year = datetime.now().strftime('%B %Y')
                pdf.cell(190, 8, txt=f"MONTH: {month_year}", ln=True, align='R')
            elif period == "Custom Range" and self.custom_start and self.custom_end:
                pdf.cell(190, 8, txt=f"DATE RANGE: {self.custom_start.strftime('%d-%m')} till {self.custom_end.strftime('%d-%m-%Y')}", ln=True, align='R')
            else:
                pdf.cell(190, 8, txt=f"GENERATED: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", ln=True, align='R')
            pdf.ln(5)

            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(10, 8, "#", 1, 0, 'C', 1)
            pdf.cell(40, 8, "CATEGORY", 1, 0, 'C', 1)
            pdf.cell(60, 8, "BRAND NAME", 1, 0, 'C', 1)
            pdf.cell(50, 8, "SIZE", 1, 0, 'C', 1)
            pdf.cell(30, 8, "QTY", 1, 1, 'C', 1)
            
            pdf.set_font("Arial", size=9)
            for i, row in enumerate(records):
                # Order number starts from #1
                pdf.cell(10, 7, str(i + 1), 1, 0, 'C')
                # Skip date column - date info is already in the header
                pdf.cell(40, 7, str(row[1]), 1, 0, 'C')  # Category
                pdf.cell(60, 7, str(row[2]), 1, 0, 'L')  # Brand Name
                pdf.cell(50, 7, str(row[3]), 1, 0, 'C')  # Size
                pdf.cell(30, 7, str(row[4]), 1, 1, 'C')  # Qty

            if not records:
                pdf.cell(190, 10, "No sales recorded for this period.", 1, 1, 'C')

            pdf.output(file_path)
            messagebox.showinfo("Success", f"Sale Chart Saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF: {str(e)}")

    def download_detailed_report(self):
        try:
            period = self.filter_var.get()
            
            if period == "Today" or period == "Daily":
                date_suffix = datetime.now().strftime("%d %b")
            elif period == "Yesterday":
                date_suffix = (datetime.now() - timedelta(days=1)).strftime("%d %b")
            elif period == "Weekly":
                start_str = (datetime.now() - timedelta(days=7)).strftime("%d %b")
                end_str = datetime.now().strftime("%d %b")
                date_suffix = f"{start_str} - {end_str}"
            elif period == "Monthly":
                date_suffix = datetime.now().strftime("%B %Y")
            elif period == "Yearly":
                date_suffix = datetime.now().strftime("%Y")
            elif period == "Custom Range" and self.custom_start and self.custom_end:
                 date_suffix = f"{self.custom_start.strftime('%d %b')} - {self.custom_end.strftime('%d %b')}"
            else:
                date_suffix = datetime.now().strftime("%Y-%m-%d")

            file_name = f"detailed transaction report {date_suffix}.pdf"
            
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf")],
                                                   initialfile=file_name)
            if not file_path: return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Helper to create PDF pages
            def create_page_for_date(pdf_obj, target_date_str, filter_type, custom_title=None):
                pdf_obj.add_page()
                pdf_obj.set_font("Arial", 'B', 10)
                pdf_obj.cell(190, 5, txt="SHREE GANESHAY NAMAH", ln=True, align='C')
                pdf_obj.set_font("Arial", 'B', 18)
                pdf_obj.cell(190, 10, txt="V J BEER SHOPEE", ln=True, align='C')
                pdf_obj.set_font("Arial", 'B', 14)
                
                title = custom_title if custom_title else f"DETAILED TRANSACTION REPORT ({filter_type.upper()})"
                pdf_obj.cell(190, 10, txt=title, ln=True, align='C')
                
                pdf_obj.set_font("Arial", size=10)
                # Show the date for this page
                if filter_type == "Custom Range":
                     # Logic to show specific date of this page
                     dt = datetime.strptime(target_date_str, "%Y-%m-%d")
                     pdf_obj.cell(190, 8, txt=f"DATE: {dt.strftime('%d-%m-%Y')}", ln=True, align='R')
                else:
                    if filter_type == "Yesterday":
                        y_date = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
                        pdf_obj.cell(190, 8, txt=f"DATE: {y_date}", ln=True, align='R')
                    elif filter_type == "Today" or filter_type == "Daily":
                        pdf_obj.cell(190, 8, txt=f"DATE: {datetime.now().strftime('%d-%m-%Y')}", ln=True, align='R')
                    else:
                         pdf_obj.cell(190, 8, txt=f"GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
                
                pdf_obj.ln(5)

                pdf_obj.set_fill_color(240, 240, 240)
                pdf_obj.set_font("Arial", 'B', 8)
                pdf_obj.cell(35, 8, "TIME", 1, 0, 'C', 1)
                pdf_obj.cell(25, 8, "CATEGORY", 1, 0, 'C', 1)
                pdf_obj.cell(60, 8, "BRAND", 1, 0, 'C', 1)
                pdf_obj.cell(15, 8, "QTY", 1, 0, 'C', 1)
                pdf_obj.cell(25, 8, "PRICE", 1, 0, 'C', 1)
                pdf_obj.cell(30, 8, "TOTAL", 1, 1, 'C', 1)
                
                pdf_obj.set_font("Arial", size=8)
                
            def fetch_and_print(pdf_obj, where, prms):
                query = f"""
                    SELECT s.date, COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, ''), s.qty, s.total 
                    FROM sales_log s 
                    LEFT JOIN inventory i ON s.barcode = i.barcode 
                    {where} 
                    ORDER BY s.date DESC
                """
                cur.execute(query, prms)
                records = cur.fetchall()
                
                grand_total = 0
                for row in records:
                    s_date, s_cat, s_brand, s_size, s_qty, s_total = row
                    
                    if s_size and s_size != '-' and s_size != '':
                        display_brand = f"{s_brand} ({s_size})"
                    else:
                        display_brand = s_brand

                    try:
                        dt_obj = datetime.strptime(s_date, "%Y-%m-%d %H:%M:%S")
                        display_time = dt_obj.strftime("%d/%m %I:%M %p")
                    except:
                        display_time = str(s_date)

                    try:
                        qty_val = float(s_qty)
                        total_val = float(s_total)
                        brand_price = total_val / qty_val if qty_val > 0 else 0
                        grand_total += total_val
                    except:
                        brand_price = 0
                        total_val = 0

                    pdf_obj.cell(35, 7, display_time, 1, 0, 'C')
                    pdf_obj.cell(25, 7, str(s_cat), 1, 0, 'C')
                    pdf_obj.cell(60, 7, str(display_brand)[:35], 1, 0, 'L')
                    pdf_obj.cell(15, 7, str(s_qty), 1, 0, 'C')
                    pdf_obj.cell(25, 7, f"{brand_price:,.2f}", 1, 0, 'R')
                    pdf_obj.cell(30, 7, f"{total_val:,.2f}", 1, 1, 'R')
                
                pdf_obj.set_font("Arial", 'B', 9)
                pdf_obj.cell(160, 8, "TOTAL FOR PAGE:", 1, 0, 'R', 1)
                pdf_obj.cell(30, 8, f"{grand_total:,.2f}", 1, 1, 'R', 1)
                if not records:
                    pdf_obj.cell(190, 10, "No transactions found.", 1, 1, 'C')

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            if period == "Custom Range" and self.custom_start and self.custom_end:
                # Loop through each day
                delta = (self.custom_end - self.custom_start).days
                for i in range(delta + 1):
                    day = self.custom_start + timedelta(days=i)
                    day_str = day.strftime("%Y-%m-%d")
                    
                    # Create Page
                    create_page_for_date(pdf, day_str, "Custom Range")
                    
                    # Query for this specific day
                    w_clause = "WHERE s.date LIKE ?"
                    pms = (f"{day_str}%",)
                    fetch_and_print(pdf, w_clause, pms)
            else:
                # Standard Logic for other filters
                # Prepare where clause again (re-using logic from load_analytics basically)
                today_str = datetime.now().strftime("%Y-%m-%d")
                month_str = datetime.now().strftime("%Y-%m")
                year_str = datetime.now().strftime("%Y")
                
                where_clause = ""
                params = ()
                if period == "Today" or period == "Daily":
                    where_clause = "WHERE s.date LIKE ?"; params = (f"{today_str}%",)
                elif period == "Yesterday":
                    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    where_clause = "WHERE s.date LIKE ?"; params = (f"{yesterday_str}%",)
                elif period == "Weekly":
                    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                    where_clause = "WHERE s.date >= ?"; params = (start_date,)
                elif period == "Monthly":
                    where_clause = "WHERE strftime('%Y-%m', s.date) = ?"; params = (month_str,)
                elif period == "Yearly":
                    where_clause = "WHERE strftime('%Y', s.date) = ?"; params = (year_str,)
                
                create_page_for_date(pdf, today_str, period)
                fetch_and_print(pdf, where_clause, params)

            conn.close()
            pdf.output(file_path)
            messagebox.showinfo("Success", f"Detailed Report Saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF: {str(e)}")

    def auto_refresh(self):
        try:
            self.load_analytics()
            self.parent.after(60000, self.auto_refresh)
        except: pass

    def draw_revenue_graph(self, data):
        self.canvas.delete("all")
        if not data:
            self.canvas.create_text(200, 100, text="No Data Available for this period", fill=self.clr_dim, font=("Helvetica", 10))
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100: w = 800 # Default if hidden
        if h < 100: h = 250

        padding = 50
        graph_h = h - padding * 2
        graph_w = w - padding * 2
        
        max_val = max([d[1] for d in data]) if data else 1
        if max_val == 0: max_val = 1
        
        bar_w = graph_w / (len(data) * 2)
        colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f43f5e", "#10b981", "#3b82f6", "#f59e0b"]
        
        for i, (brand, val) in enumerate(data):
            # Calculate bar dimensions
            bar_h = (val / max_val) * graph_h
            x0 = padding + (i * 2 * bar_w) + (bar_w / 2)
            y0 = h - padding - bar_h
            x1 = x0 + bar_w
            y1 = h - padding
            
            # Draw Bar
            color = colors[i % len(colors)]
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color, width=0)
            
            # Label
            label = brand[:12] + ".." if len(brand) > 12 else brand
            self.canvas.create_text(x0 + bar_w/2, y1 + 15, text=label, fill="white", font=("Helvetica", 8, "bold"))
            
            # Value on top
            self.canvas.create_text(x0 + bar_w/2, y0 - 15, text=f"₹{val:,.0f}", fill=color, font=("Helvetica", 8, "bold"))

    def load_analytics(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            period = self.filter_var.get()
            self.lbl_stat_title.config(text=f"REVENUE ({period.upper()})")
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            month_str = datetime.now().strftime("%Y-%m")
            year_str = datetime.now().strftime("%Y")
            
            where_clause = ""
            params = ()
            
            if period == "Daily":
                where_clause = "WHERE s.date LIKE ?"
                params = (f"{today_str}%",)
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date >= ?"
                params = (start_date,)
            elif period == "Monthly":
                where_clause = "WHERE strftime('%Y-%m', s.date) = ?"
                params = (month_str,)
            elif period == "Yearly":
                where_clause = "WHERE strftime('%Y', s.date) = ?"
                params = (year_str,)

            # Total Revenue
            cur.execute(f"SELECT SUM(total) FROM transactions", ()) # Keeping simple for now or use filter
            # Re-fetch correct total based on filter
            cur.execute(f"SELECT SUM(s.total) FROM sales_log s {where_clause}", params)
            rev_res = cur.fetchone()
            rev = rev_res[0] if rev_res[0] else 0
            self.total_rev.set(f"₹{rev:,.2f}")

            # 1. Revenue Per Brand Table (Top Left)
            self.brand_table.delete(*self.brand_table.get_children())
            query = f"""
                SELECT COALESCE(i.brand, s.brand), SUM(s.total) 
                FROM sales_log s
                LEFT JOIN inventory i ON s.barcode = i.barcode
                {where_clause} 
                GROUP BY COALESCE(i.brand, s.brand) 
                ORDER BY SUM(s.total) DESC
            """
            cur.execute(query, params)
            brands_data = cur.fetchall()
            for b in brands_data:
                brand_name = b[0] if b[0] else "Unknown"
                self.brand_table.insert('', tk.END, values=(brand_name, f"₹{b[1]:,.2f}"))

            # 2. Brand Sales Graph (Bottom)
            graph_query = f"""
                SELECT COALESCE(i.brand, s.brand), SUM(s.total) 
                FROM sales_log s
                LEFT JOIN inventory i ON s.barcode = i.barcode
                {where_clause} 
                GROUP BY COALESCE(i.brand, s.brand) 
                ORDER BY SUM(s.total) DESC LIMIT 10
            """
            cur.execute(graph_query, params)
            graph_data = cur.fetchall()
            self.draw_revenue_graph(graph_data)

            # 3. Live Transaction History (Top Right)
            self.hist_table.delete(*self.hist_table.get_children())
            query = f"""
                SELECT s.date, 
                       COALESCE(i.category, 'Unknown'), 
                       COALESCE(i.brand, s.brand), 
                       s.qty, s.total 
                FROM sales_log s
                LEFT JOIN inventory i ON s.barcode = i.barcode
                {where_clause} 
                ORDER BY s.sid DESC LIMIT 100
            """
            cur.execute(query, params)
            for r in cur.fetchall(): 
                date, cat, brand, qty, total = r
                try:
                    qty_val = float(qty) if str(qty).replace('.','',1).isdigit() else 0
                    total_val = float(total) if str(total).replace('.','',1).isdigit() else 0
                    price = total_val / qty_val if qty_val > 0 else 0
                except:
                    price = 0
                self.hist_table.insert('', tk.END, values=(date, cat, brand, qty, f"{price:,.2f}", f"{total:,.2f}"))
            
            conn.close()
        except Exception as e:
            print(f"Analytics Error: {e}")

    def download_sales_chart_pdf(self):
        try:
            period = self.filter_var.get()
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf")],
                                                   initialfile=f"VJ_Sale_Chart_{period}_{today_date}.pdf")
            if not file_path: return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            month_str = datetime.now().strftime("%Y-%m")
            year_str = datetime.now().strftime("%Y")
            where_clause = ""
            params = ()
            if period == "Daily":
                where_clause = "WHERE s.date LIKE ?"; params = (f"{today_str}%",)
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date >= ?"; params = (start_date,)
            elif period == "Monthly":
                where_clause = "WHERE strftime('%Y-%m', s.date) = ?"; params = (month_str,)
            elif period == "Yearly":
                where_clause = "WHERE strftime('%Y', s.date) = ?"; params = (year_str,)

            if period in ["Daily", "Weekly", "Monthly"]:
                query = f"""
                    SELECT MAX(s.date), COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, '-'), SUM(s.qty) 
                    FROM sales_log s 
                    LEFT JOIN inventory i ON s.barcode = i.barcode 
                    {where_clause} 
                    GROUP BY COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, '-')
                    ORDER BY MAX(s.date) DESC
                """
            else:
                query = f"""
                    SELECT s.date, COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, '-'), s.qty 
                    FROM sales_log s 
                    LEFT JOIN inventory i ON s.barcode = i.barcode 
                    {where_clause} 
                    ORDER BY s.date DESC
                """
            cur.execute(query, params)
            records = cur.fetchall()
            conn.close()

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 5, txt="SHREE GANESHAY NAMAH", ln=True, align='C')
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(190, 10, txt="V J BEER SHOPEE", ln=True, align='C')
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, txt=f"SALE CHART ({period.upper()})", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            
            # Prepare date display for header based on period
            if period == "Daily":
                header_date = datetime.now().strftime('%d-%m-%Y')
                pdf.cell(190, 8, txt=f"DATE: {header_date}", ln=True, align='R')
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime('%d-%m')
                end_date = datetime.now().strftime('%d-%m-%Y')
                pdf.cell(190, 8, txt=f"DATE RANGE: {start_date} till {end_date}", ln=True, align='R')
            elif period == "Monthly":
                month_year = datetime.now().strftime('%B %Y')
                pdf.cell(190, 8, txt=f"MONTH: {month_year}", ln=True, align='R')
            elif period == "Yearly":
                year_val = datetime.now().strftime('%Y')
                pdf.cell(190, 8, txt=f"YEAR: {year_val}", ln=True, align='R')
            else:
                pdf.cell(190, 8, txt=f"GENERATED: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", ln=True, align='R')
            pdf.ln(5)

            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(10, 8, "#", 1, 0, 'C', 1)
            pdf.cell(40, 8, "CATEGORY", 1, 0, 'C', 1)
            pdf.cell(60, 8, "BRAND NAME", 1, 0, 'C', 1)
            pdf.cell(50, 8, "SIZE", 1, 0, 'C', 1)
            pdf.cell(30, 8, "QTY", 1, 1, 'C', 1)
            
            pdf.set_font("Arial", size=9)
            for i, row in enumerate(records):
                # Order number starts from #1
                pdf.cell(10, 7, str(i + 1), 1, 0, 'C')
                # Skip date column - date info is already in the header
                pdf.cell(40, 7, str(row[1]), 1, 0, 'C')  # Category
                pdf.cell(60, 7, str(row[2]), 1, 0, 'L')  # Brand Name
                pdf.cell(50, 7, str(row[3]), 1, 0, 'C')  # Size
                pdf.cell(30, 7, str(row[4]), 1, 1, 'C')  # Qty

            if not records:
                pdf.cell(190, 10, "No sales recorded for this period.", 1, 1, 'C')

            pdf.output(file_path)
            messagebox.showinfo("Success", f"Sale Chart Saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF: {str(e)}")

    def download_detailed_report(self):
        try:
            period = self.filter_var.get()
            
            if period == "Daily":
                date_suffix = datetime.now().strftime("%d %b")
            elif period == "Weekly":
                start_str = (datetime.now() - timedelta(days=7)).strftime("%d %b")
                end_str = datetime.now().strftime("%d %b")
                date_suffix = f"{start_str} - {end_str}"
            elif period == "Monthly":
                date_suffix = datetime.now().strftime("%B %Y")
            elif period == "Yearly":
                date_suffix = datetime.now().strftime("%Y")
            else:
                date_suffix = datetime.now().strftime("%Y-%m-%d")

            file_name = f"detailed transaction report {date_suffix}.pdf"
            
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf")],
                                                   initialfile=file_name)
            if not file_path: return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            month_str = datetime.now().strftime("%Y-%m")
            year_str = datetime.now().strftime("%Y")
            where_clause = ""
            params = ()
            if period == "Daily":
                where_clause = "WHERE s.date LIKE ?"; params = (f"{today_str}%",)
            elif period == "Weekly":
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                where_clause = "WHERE s.date >= ?"; params = (start_date,)
            elif period == "Monthly":
                where_clause = "WHERE strftime('%Y-%m', s.date) = ?"; params = (month_str,)
            elif period == "Yearly":
                where_clause = "WHERE strftime('%Y', s.date) = ?"; params = (year_str,)

            # Show each individual transaction without grouping
            query = f"""
                SELECT s.date, COALESCE(i.category, 'Other'), COALESCE(i.brand, s.brand), COALESCE(i.size, ''), s.qty, s.total 
                FROM sales_log s 
                LEFT JOIN inventory i ON s.barcode = i.barcode 
                {where_clause} 
                ORDER BY s.date DESC
            """
            cur.execute(query, params)
            records = cur.fetchall()
            conn.close()

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 5, txt="SHREE GANESHAY NAMAH", ln=True, align='C')
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(190, 10, txt="V J BEER SHOPEE", ln=True, align='C')
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, txt=f"DETAILED TRANSACTION REPORT ({period.upper()})", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            if period in ["Daily", "Weekly", "Monthly"]:
                pdf.cell(190, 8, txt=f"GENERATED: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", ln=True, align='R')
            else:
                pdf.cell(190, 8, txt=f"GENERATED: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
            pdf.ln(5)

            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(35, 8, "TIME", 1, 0, 'C', 1)
            pdf.cell(25, 8, "CATEGORY", 1, 0, 'C', 1)
            pdf.cell(60, 8, "BRAND", 1, 0, 'C', 1)
            pdf.cell(15, 8, "QTY", 1, 0, 'C', 1)
            pdf.cell(25, 8, "PRICE", 1, 0, 'C', 1)
            pdf.cell(30, 8, "TOTAL", 1, 1, 'C', 1)
            
            pdf.set_font("Arial", size=8)
            grand_total = 0
            
            for row in records:
                s_date, s_cat, s_brand, s_size, s_qty, s_total = row
                
                # Format Brand with Size
                if s_size and s_size != '-' and s_size != '':
                    display_brand = f"{s_brand} ({s_size})"
                else:
                    display_brand = s_brand

                if period in ["Daily", "Weekly", "Monthly"]:
                    try:
                        dt_obj = datetime.strptime(s_date, "%Y-%m-%d %H:%M:%S")
                        display_time = dt_obj.strftime("%d/%m %I:%M %p")
                    except:
                        display_time = str(s_date)
                else:
                    display_time = str(s_date)

                try:
                    qty_val = float(s_qty)
                    total_val = float(s_total)
                    brand_price = total_val / qty_val if qty_val > 0 else 0
                    grand_total += total_val
                except:
                    brand_price = 0
                    total_val = 0

                pdf.cell(35, 7, display_time, 1, 0, 'C')
                pdf.cell(25, 7, str(s_cat), 1, 0, 'C')
                pdf.cell(60, 7, str(display_brand)[:35], 1, 0, 'L')
                pdf.cell(15, 7, str(s_qty), 1, 0, 'C')
                pdf.cell(25, 7, f"{brand_price:,.2f}", 1, 0, 'R')
                pdf.cell(30, 7, f"{total_val:,.2f}", 1, 1, 'R')

            pdf.set_font("Arial", 'B', 9)
            pdf.cell(160, 8, "GRAND TOTAL:", 1, 0, 'R', 1)
            pdf.cell(30, 8, f"{grand_total:,.2f}", 1, 1, 'R', 1)

            if not records:
                pdf.cell(190, 10, "No transactions found.", 1, 1, 'C')

            pdf.output(file_path)
            messagebox.showinfo("Success", f"Detailed Report Saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x700")
    root.config(bg="#0f172a")
    AnalyticsClass(root, lambda: print("Back"))
    root.mainloop()
