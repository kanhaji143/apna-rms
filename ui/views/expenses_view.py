import os
from pathlib import Path
from datetime import datetime
import tkinter.filedialog as fd
import customtkinter as ctk
import openpyxl
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    DEFAULT_EXPENSE_CATEGORIES, load_config
)
from core.translations import t
from core.database import DatabaseManager
from core.image_utils import ImageOptimizer

class ExpensesView(ctk.CTkFrame):
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.config = load_config()
        self.selected_voucher_path = ""

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")
        db = DatabaseManager.get_instance()
        metrics = db.get_dashboard_metrics()

        # Profit & Loss Overview Banner
        banner = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        banner.pack(fill="x", padx=16, pady=(12, 12))

        b_left = ctk.CTkFrame(banner, fg_color="transparent")
        b_left.pack(side="left", padx=20, pady=14)

        ctk.CTkLabel(
            b_left,
            text=f"💰 {t('exp_title', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w")

        p_l_text = f"🟢 कुल फीस: ₹{metrics['total_revenue']:,.0f}  |  🔴 कुल खर्चे: ₹{metrics['total_expenses']:,.0f}  |  💼 शुद्ध बचत (Net Profit): ₹{metrics['net_profit']:,.0f}"
        ctk.CTkLabel(
            b_left,
            text=p_l_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#CBD5E1" if is_dark else "#334155"
        ).pack(anchor="w")

        # Top Action Button
        b_right = ctk.CTkFrame(banner, fg_color="transparent")
        b_right.pack(side="right", padx=16, pady=14)

        btn_new = ctk.CTkButton(
            b_right,
            text=t("btn_add_expense", lang),
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.show_add_expense_dialog
        )
        btn_new.pack(side="left", padx=4)

        btn_exp_excel = ctk.CTkButton(
            b_right,
            text="📊 Export Expenses Excel",
            height=36,
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_expenses_excel
        )
        btn_exp_excel.pack(side="left", padx=4)

        # Main Table Card
        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Table Header
        th = ctk.CTkFrame(card, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, height=36, corner_radius=6)
        th.pack(fill="x", padx=12, pady=(12, 6))

        cols = [
            ("Date", 90), ("Expense Title", 180), ("Category", 180), ("Amount (₹)", 100),
            ("Payment Mode", 110), ("Paid To", 140), ("Recorded By", 110)
        ]
        for title, w in cols:
            ctk.CTkLabel(
                th,
                text=title,
                width=w,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#CBD5E1" if is_dark else "#334155"
            ).pack(side="left", padx=4)

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.load_expenses()

    def load_expenses(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        db = DatabaseManager.get_instance()
        expenses = db.get_expenses()

        if not expenses:
            ctk.CTkLabel(
                self.scroll,
                text="कोई खर्च दर्ज नहीं है। ऊपर '+ नया खर्चा दर्ज करें' बटन दबाएं।",
                font=ctk.CTkFont(size=12),
                text_color="#94A3B8"
            ).pack(pady=40)
            return

        for exp in expenses:
            tr = ctk.CTkFrame(self.scroll, fg_color="transparent", height=36)
            tr.pack(fill="x", pady=2)

            ctk.CTkLabel(tr, text=exp["expense_date"], width=90, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=exp["title"][:22], width=180, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=exp["category"][:22], width=180, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=f"₹{exp['amount']:,.0f}", width=100, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F87171").pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=exp["payment_mode"][:12], width=110, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=exp["paid_to"][:16], width=140, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=exp.get("recorded_by", "")[:12], width=110, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)

    def show_add_expense_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Record New Expense")
        d.geometry("460x500")
        d.grab_set()

        ctk.CTkLabel(d, text="💸 नया खर्चा दर्ज करें (Record Expense)", font=ctk.CTkFont(size=15, weight="bold"), text_color=COLOR_CYAN).pack(pady=(16, 12))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=24)

        ctk.CTkLabel(f, text="खर्च का विवरण (Title) *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        t_entry = ctk.CTkEntry(f, height=34, placeholder_text="उदा: मार्च महीने का बिजली बिल")
        t_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="खर्च की श्रेणी (Category) - चुनें या नया नाम टाइप करें *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        cat_box = ctk.CTkComboBox(
            f,
            values=DEFAULT_EXPENSE_CATEGORIES,
            height=34,
            font=ctk.CTkFont(size=11)
        )
        cat_box.set(DEFAULT_EXPENSE_CATEGORIES[0])
        cat_box.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="राशि (Amount ₹) *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        amt_entry = ctk.CTkEntry(f, height=34, placeholder_text="0")
        amt_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="तारीख (Date) *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        dt_entry = ctk.CTkEntry(f, height=34)
        dt_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        dt_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="किसे भुगतान किया (Paid To) *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        pt_entry = ctk.CTkEntry(f, height=34, placeholder_text="दुकान / व्यक्ति का नाम")
        pt_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="भुगतान मोड (Payment Mode):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        mode_opt = ctk.CTkOptionMenu(f, values=["Cash / नकद", "UPI / Online", "Cheque", "Bank Transfer"], height=34)
        mode_opt.pack(fill="x", pady=(0, 10))

        err_lbl = ctk.CTkLabel(d, text="", font=ctk.CTkFont(size=11), text_color="#EF4444")
        err_lbl.pack(pady=2)

        def save():
            t_val = t_entry.get().strip()
            cat_val = cat_box.get().strip()
            amt_str = amt_entry.get().strip()
            pt = pt_entry.get().strip()
            dt = dt_entry.get().strip()
            if not t_val or not cat_val or not amt_str or not pt or not dt:
                err_lbl.configure(text="कृपया सभी आवश्यक फील्ड्स भरें!")
                return
            try:
                valid_date = datetime.strptime(dt, "%Y-%m-%d")
                if valid_date.year < 2000 or valid_date.year > 2050:
                    raise ValueError()
            except ValueError:
                err_lbl.configure(text="अमान्य तारीख! सही प्रारूप (YYYY-MM-DD) दर्ज करें (उदा: 2026-11-10)")
                return

            try:
                amt = float(amt_str)
                if amt <= 0:
                    err_lbl.configure(text="अमाउंट 0 से अधिक होना चाहिए!")
                    return
            except ValueError:
                err_lbl.configure(text="अमाउंट में सिर्फ संख्या दर्ज करें!")
                return

            if cat_val not in DEFAULT_EXPENSE_CATEGORIES:
                DEFAULT_EXPENSE_CATEGORIES.append(cat_val)

            db = DatabaseManager.get_instance()
            db.add_expense(t_val, cat_val, amt, mode_opt.get(), dt, pt, "", self.current_user.get("full_name", "Accountant"))
            db.log_activity(
                self.current_user.get("id", 1),
                self.current_user.get("username", "accountant"),
                self.current_user.get("role", "accountant"),
                "EXPENSE_RECORDED",
                f"Added expense '{t_val}' ({cat_val}) of ₹{amt}"
            )
            d.destroy()
            self.load_expenses()

        ctk.CTkButton(d, text="सेव करें (Save Expense)", height=38, fg_color=COLOR_CYAN, text_color="#001633", font=ctk.CTkFont(weight="bold"), command=save).pack(fill="x", padx=24, pady=10)

    def export_expenses_excel(self):
        file_path = fd.asksaveasfilename(
            title="Save Expenses Report",
            defaultextension=".xlsx",
            initialfile=f"Expenses_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            db = DatabaseManager.get_instance()
            expenses = db.get_expenses()
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Expenses_Report"
            ws.append(["Date", "Title", "Category", "Amount (₹)", "Payment Mode", "Paid To", "Recorded By"])
            for e in expenses:
                ws.append([e["expense_date"], e["title"], e["category"], e["amount"], e["payment_mode"], e["paid_to"], e.get("recorded_by", "")])
            wb.save(file_path)
            os.startfile(file_path)
