import os
import tkinter.messagebox as mbox
import customtkinter as ctk
from datetime import datetime
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    load_config
)
from core.database import DatabaseManager
from ui.components.tooltip import CTkTooltip

class StaffView(ctk.CTkFrame):
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.config = load_config()
        self.db = DatabaseManager.get_instance()

        self.setup_ui()
        self.load_staff_data()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"

        # Top Header Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(12, 8))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="👥 Staff & Faculty Directory (स्टाफ व फैकल्टी प्रबंधन)",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="टीचर्स, डायरेक्टर्स व सब-स्टाफ का मासिक वेतन, एडवांस और बकाया हिसाब-किताब",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(anchor="w")

        # Top Buttons
        btn_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_box.pack(side="right")

        btn_add = ctk.CTkButton(
            btn_box,
            text="➕ नया स्टाफ जोड़ें",
            height=36,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.open_add_staff_dialog
        )
        btn_add.pack(side="left", padx=4)
        CTkTooltip(btn_add, "नया टीचर या स्टाफ सदस्य जोड़ें")

        btn_refresh = ctk.CTkButton(
            btn_box,
            text="🔄 Refresh",
            width=80,
            height=36,
            fg_color="#0284C7",
            hover_color="#0369A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.load_staff_data
        )
        btn_refresh.pack(side="left", padx=4)
        CTkTooltip(btn_refresh, "स्टाफ सूची रिफ्रेश करें")

        # KPI Summary Cards (Total Staff, Monthly Liability, Total Advance)
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=16, pady=(0, 10))

        # Main Table Card
        self.table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        self.table_card.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Table Header
        th = ctk.CTkFrame(self.table_card, fg_color=COLOR_NAVY_CARD if is_dark else "#E2E8F0", height=38, corner_radius=8)
        th.pack(fill="x", padx=8, pady=8)

        cols = [
            ("नाम व पद (Name & Designation)", 210),
            ("श्रेणी (Category)", 125),
            ("फोन नंबर", 95),
            ("मासिक वेतन (₹)", 105),
            ("एडवांस बैलेंस (₹)", 115),
            ("एक्शन (Actions)", 160)
        ]
        for name, w in cols:
            ctk.CTkLabel(
                th,
                text=name,
                width=w,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLOR_CYAN if is_dark else "#0F172A"
            ).pack(side="left", padx=5)

        # Scrollable rows container
        self.rows_frame = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))

    def load_staff_data(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        for w in self.kpi_frame.winfo_children():
            w.destroy()
        for w in self.rows_frame.winfo_children():
            w.destroy()

        staff_list = self.db.get_all_staff()

        # Calculate KPIs
        total_staff = len(staff_list)
        total_sal_liability = sum(float(s["monthly_salary"]) for s in staff_list)
        total_adv_out = sum(float(s["advance_balance"]) for s in staff_list)

        # Render KPI Cards
        kpi_data = [
            ("कुल स्टाफ / फैकल्टी", str(total_staff), "#0284C7"),
            ("मासिक वेतन देयता", f"₹{total_sal_liability:,.0f}", "#10B981"),
            ("कुल बकाया एडवांस", f"₹{total_adv_out:,.0f}", "#F59E0B" if total_adv_out > 0 else "#64748B")
        ]
        for title, val, col in kpi_data:
            c = ctk.CTkFrame(self.kpi_frame, fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE, corner_radius=10, height=64)
            c.pack(side="left", fill="x", expand=True, padx=4)
            ctk.CTkLabel(c, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=12, pady=(6, 0))
            ctk.CTkLabel(c, text=val, font=ctk.CTkFont(size=17, weight="bold"), text_color=col).pack(anchor="w", padx=12, pady=(0, 6))

        if not staff_list:
            ctk.CTkLabel(self.rows_frame, text="कोई स्टाफ रिकॉर्ड नहीं मिला। ऊपर दिए गए बटन से नया स्टाफ जोड़ें।", font=ctk.CTkFont(size=12)).pack(pady=30)
            return

        for idx, s in enumerate(staff_list):
            bg = COLOR_NAVY_CARD if is_dark else "#F8FAFC"
            if idx % 2 == 1:
                bg = "#0B1F3B" if is_dark else "#EFF6FF"

            row = ctk.CTkFrame(self.rows_frame, fg_color=bg, corner_radius=6, height=44)
            row.pack(fill="x", pady=2)

            # Name & Designation
            name_box = ctk.CTkFrame(row, fg_color="transparent", width=210)
            name_box.pack(side="left", padx=5)
            ctk.CTkLabel(name_box, text=s["name"], font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(name_box, text=s["designation"][:28], font=ctk.CTkFont(size=9.5), text_color="#94A3B8", anchor="w").pack(anchor="w")

            # Category Badge
            cat_col = "#0284C7" if "Teacher" in s["category"] else ("#8B5CF6" if "Director" in s["category"] else "#64748B")
            cat_box = ctk.CTkFrame(row, fg_color=cat_col, corner_radius=4, width=125, height=24)
            cat_box.pack(side="left", padx=5)
            ctk.CTkLabel(cat_box, text=s["category"].split("/")[0].strip(), font=ctk.CTkFont(size=10, weight="bold"), text_color="#FFFFFF").pack(padx=6, pady=2)

            # Phone
            ctk.CTkLabel(row, text=s["phone"] or "—", width=95, anchor="w", font=ctk.CTkFont(size=10.5)).pack(side="left", padx=5)

            # Monthly Salary
            ctk.CTkLabel(row, text=f"₹{float(s['monthly_salary']):,.0f}", width=105, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#10B981").pack(side="left", padx=5)

            # Advance Balance
            adv = float(s["advance_balance"])
            adv_color = "#F59E0B" if adv > 0 else "#64748B"
            adv_text = f"₹{adv:,.0f} (बाकी)" if adv > 0 else "₹0 (क्लियर)"
            ctk.CTkLabel(row, text=adv_text, width=115, anchor="w", font=ctk.CTkFont(size=10.5, weight="bold"), text_color=adv_color).pack(side="left", padx=5)

            # Actions Box
            act_box = ctk.CTkFrame(row, fg_color="transparent", width=160)
            act_box.pack(side="left", padx=5)

            # Pay / Advance Button
            btn_pay = ctk.CTkButton(
                act_box,
                text="💸 वेतन / एडवांस",
                width=95,
                height=26,
                fg_color="#10B981",
                hover_color="#059669",
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda st=s: self.open_payment_modal(st)
            )
            btn_pay.pack(side="left", padx=2)
            CTkTooltip(btn_pay, f"{s['name']} को वेतन या एडवांस का भुगतान दर्ज करें")

            # Ledger / History Button
            btn_hist = ctk.CTkButton(
                act_box,
                text="📜",
                width=28,
                height=26,
                fg_color="#4F46E5",
                hover_color="#4338CA",
                font=ctk.CTkFont(size=11),
                command=lambda st=s: self.open_history_modal(st)
            )
            btn_hist.pack(side="left", padx=2)
            CTkTooltip(btn_hist, f"{s['name']} का पिछला भुगतान व एडवांस इतिहास देखें")

    def open_add_staff_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Add New Staff / Faculty")
        d.geometry("450x420")
        d.grab_set()

        ctk.CTkLabel(d, text="➕ नया स्टाफ या फैकल्टी सदस्य जोड़ें", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=COLOR_CYAN).pack(pady=(16, 12))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=30)

        ctk.CTkLabel(f, text="स्टाफ / टीचर का पूरा नाम:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_name = ctk.CTkEntry(f, height=36, placeholder_text="उदा: Prof. Rohit Verma")
        ent_name.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="श्रेणी (Category):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        opt_cat = ctk.CTkOptionMenu(f, values=["Teacher / Faculty", "Director / Management", "Sub-staff / Office"], height=36)
        opt_cat.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="पद या विषय (Designation / Subject):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_desig = ctk.CTkEntry(f, height=36, placeholder_text="उदा: Tally Prime & Accounting Lead")
        ent_desig.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="मोबाइल नंबर (10 अंक):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_ph = ctk.CTkEntry(f, height=36, placeholder_text="उदा: 9812345678")
        ent_ph.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="तय मासिक वेतन (Monthly Salary ₹):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_sal = ctk.CTkEntry(f, height=36, placeholder_text="उदा: 20000")
        ent_sal.pack(fill="x", pady=(2, 14))

        def save():
            name = ent_name.get().strip()
            if len(name) < 2:
                mbox.showwarning("Incomplete", "कृपया पूरा नाम दर्ज करें!")
                return
            try:
                sal = float(ent_sal.get().strip() or "0")
            except ValueError:
                mbox.showwarning("Invalid", "वेतन संख्या (numeric) में होना चाहिए!")
                return

            self.db.add_staff_member(name, opt_cat.get(), ent_desig.get().strip(), ent_ph.get().strip(), sal)
            mbox.showinfo("Success", f"{name} को स्टाफ डायरेक्टरी में सफलतापूर्वक जोड़ दिया गया!")
            d.destroy()
            self.load_staff_data()

        ctk.CTkButton(d, text="💾 स्टाफ सुरक्षित करें", height=38, fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=save).pack(fill="x", padx=30, pady=6)

    def open_payment_modal(self, staff):
        d = ctk.CTkToplevel(self)
        d.title(f"Pay Salary / Advance - {staff['name']}")
        d.geometry("480x480")
        d.grab_set()

        ctk.CTkLabel(d, text=f"💸 वेतन व एडवांस भुगतान: {staff['name']}", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLOR_CYAN).pack(pady=(14, 4))
        adv = float(staff["advance_balance"])
        adv_info = f"वर्तमान बकाया एडवांस: ₹{adv:,.0f} | तय मासिक वेतन: ₹{float(staff['monthly_salary']):,.0f}"
        ctk.CTkLabel(d, text=adv_info, font=ctk.CTkFont(size=10.5), text_color="#F59E0B" if adv > 0 else "#94A3B8").pack(pady=(0, 10))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=30)

        ctk.CTkLabel(f, text="भुगतान का प्रकार (Payment Type):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        opt_type = ctk.CTkOptionMenu(
            f,
            values=[
                "Salary Paid (मासिक वेतन)",
                "Advance Given (एडवांस दिया)",
                "Advance Settled (एडवांस काटा/समायोजित)",
                "Due Salary Paid (देर से / पिछला वेतन)"
            ],
            height=34
        )
        opt_type.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="भुगतान राशि (Amount ₹):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_amt = ctk.CTkEntry(f, height=34)
        ent_amt.insert(0, str(int(staff["monthly_salary"])))
        ent_amt.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="किस माह हेतु (Month / Purpose):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_month = ctk.CTkEntry(f, height=34)
        curr_m = datetime.now().strftime("%B %Y")
        ent_month.insert(0, curr_m)
        ent_month.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="भुगतान माध्यम (Payment Mode):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        opt_mode = ctk.CTkOptionMenu(f, values=["Bank Transfer", "Cash / नकद", "UPI / QR"], height=34)
        opt_mode.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="टिप्पणी / विवरण (Notes):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ent_notes = ctk.CTkEntry(f, height=34, placeholder_text="उदा: सैलरी में से ₹2,000 एडवांस काटा गया")
        ent_notes.pack(fill="x", pady=(2, 12))

        def record():
            try:
                amt = float(ent_amt.get().strip())
                if amt <= 0:
                    raise ValueError()
            except ValueError:
                mbox.showwarning("Invalid", "कृपया सही राशि दर्ज करें!")
                return

            p_type = opt_type.get()
            caller = self.current_user.get("full_name", "Admin")
            today_date = datetime.now().strftime("%Y-%m-%d")

            success, msg = self.db.record_staff_payment(
                staff["id"], p_type, amt, today_date, opt_mode.get(),
                ent_month.get().strip(), ent_notes.get().strip(), caller
            )
            if success:
                mbox.showinfo("Success", f"{staff['name']} का भुगतान सफलतापूर्वक दर्ज हो गया!\n(संस्थान के खर्च व P&L में स्वतः अपडेट हो गया है)")
                d.destroy()
                self.load_staff_data()
            else:
                mbox.showerror("Error", msg)

        ctk.CTkButton(d, text="✅ भुगतान दर्ज करें", height=38, fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=record).pack(fill="x", padx=30, pady=8)

    def open_history_modal(self, staff):
        d = ctk.CTkToplevel(self)
        d.title(f"Payment History - {staff['name']}")
        d.geometry("620x460")
        d.grab_set()

        ctk.CTkLabel(d, text=f"📜 भुगतान व एडवांस इतिहास: {staff['name']}", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLOR_CYAN).pack(pady=(14, 4))
        
        history = self.db.get_staff_ledger(staff["id"])
        
        scr = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scr.pack(fill="both", expand=True, padx=16, pady=10)

        if not history:
            ctk.CTkLabel(scr, text="अभी तक इस स्टाफ का कोई पिछला भुगतान रिकॉर्ड नहीं है।", font=ctk.CTkFont(size=12)).pack(pady=40)
            return

        for h in history:
            card = ctk.CTkFrame(scr, fg_color=COLOR_NAVY_CARD, corner_radius=8)
            card.pack(fill="x", pady=4, padx=4)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(6, 2))
            ctk.CTkLabel(top, text=f"{h['entry_type']} ({h['month_cycle']})", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_CYAN).pack(side="left")
            ctk.CTkLabel(top, text=f"₹{float(h['amount']):,.0f}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#10B981").pack(side="right")

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=10, pady=(0, 6))
            sub = f"तारीख: {h['payment_date']} | मोड: {h['payment_mode']} | दर्जकर्ता: {h['recorded_by']}"
            if h.get("notes"):
                sub += f" | नोट: {h['notes']}"
            ctk.CTkLabel(bot, text=sub, font=ctk.CTkFont(size=9.5), text_color="#94A3B8").pack(side="left")
