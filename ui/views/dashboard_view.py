import customtkinter as ctk
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    load_config
)
from core.translations import t
from core.database import DatabaseManager

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_navigate):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.on_navigate = on_navigate
        self.config = load_config()

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")
        db = DatabaseManager.get_instance()
        metrics = db.get_dashboard_metrics()

        # Welcome & Action Banner
        banner = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        banner.pack(fill="x", padx=16, pady=(12, 16))

        user_name = self.current_user.get("full_name", "User")
        role = self.current_user.get("role", "Staff").capitalize()

        left_b = ctk.CTkFrame(banner, fg_color="transparent")
        left_b.pack(side="left", padx=20, pady=16)

        greeting = ctk.CTkLabel(
            left_b,
            text=f"नमस्ते, {user_name}! 👋 ({role})",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        )
        greeting.pack(anchor="w")

        sub_greeting = ctk.CTkLabel(
            left_b,
            text="अपना कंप्यूटर RMS - ऑफलाइन एडमिशन व वित्तीय नियंत्रण केंद्र",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8" if is_dark else "#64748B"
        )
        sub_greeting.pack(anchor="w")

        right_b = ctk.CTkFrame(banner, fg_color="transparent")
        right_b.pack(side="right", padx=20, pady=12)

        from datetime import datetime
        now_dt = datetime.now()
        date_time_str = now_dt.strftime("📅 %d-%b-%Y  •  ⏰ %I:%M %p")

        # License & Trial Countdown Info
        try:
            from core.license_manager import LicenseManager
            lm = LicenseManager.get_instance()
            lic_info = lm.get_license_info()
            days_left = lic_info.get("days_left", 0)
            is_locked = lic_info.get("is_locked", False)
            status = lic_info.get("status", "trial")

            if is_locked:
                pill_text = f"🔒 ट्रायल समाप्त (0 दिन शेष) — अभी सक्रिय करें"
                pill_fg = "#7F1D1D"
                pill_border = "#EF4444"
                pill_txt_col = "#FCA5A5"
            elif status == "trial":
                pill_text = f"⏳ 30-दिन VIP मुफ़्त ट्रायल: {days_left} दिन शेष"
                pill_fg = "#451A03"
                pill_border = "#F59E0B"
                pill_txt_col = "#FDE68A"
            elif status == "trial_extended":
                pill_text = f"⏳ VIP ट्रायल एक्सटेंशन: {days_left} दिन शेष"
                pill_fg = "#78350F"
                pill_border = "#F59E0B"
                pill_txt_col = "#FEF3C7"
            elif status == "active":
                if days_left > 1000:
                    pill_text = "⭐ आजीवन अधिकृत लाइसेंस (Lifetime Active)"
                else:
                    pill_text = f"⭐ वार्षिक लाइसेंस सक्रिय: {days_left} दिन शेष"
                pill_fg = "#064E3B"
                pill_border = "#10B981"
                pill_txt_col = "#6EE7B7"
            else:
                pill_text = f"⭐ लाइसेंस स्थिति: {days_left} दिन शेष"
                pill_fg = "#0F2240"
                pill_border = "#38BDF8"
                pill_txt_col = "#E0F2FE"
        except Exception:
            pill_text = "🟢 लोकल डेटाबेस सक्रिय"
            pill_fg = "#064E3B"
            pill_border = "#10B981"
            pill_txt_col = "#6EE7B7"

        info_col = ctk.CTkFrame(right_b, fg_color="transparent")
        info_col.pack(side="right", fill="y")

        dt_lbl = ctk.CTkLabel(
            info_col,
            text=date_time_str,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8" if is_dark else "#475569",
            justify="right"
        )
        dt_lbl.pack(anchor="e", pady=(0, 4))

        lic_btn = ctk.CTkButton(
            info_col,
            text=pill_text,
            height=28,
            corner_radius=14,
            border_width=1.5,
            border_color=pill_border,
            fg_color=pill_fg,
            text_color=pill_txt_col,
            hover_color=pill_border,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.open_license_dialog
        )
        lic_btn.pack(anchor="e")

        # 6 KPI Cards Grid
        kpi_grid = ctk.CTkFrame(self, fg_color="transparent")
        kpi_grid.pack(fill="x", padx=12, pady=(0, 16))

        cards_data = [
            (t("dash_total_admissions", lang), f"{metrics['total_admissions']}", "📋", COLOR_CYAN if is_dark else "#0284C7"),
            (t("dash_today_admissions", lang), f"{metrics['today_admissions']}", "📅", "#38BDF8"),
            (t("dash_pending_activations", lang), f"{metrics['pending_activations']}", "🚩", COLOR_DANGER if metrics['pending_activations'] > 0 else COLOR_SUCCESS),
            (t("dash_total_revenue", lang), f"₹{metrics['total_revenue']:,.0f}", "💵", COLOR_SUCCESS),
            (t("dash_total_expenses", lang), f"₹{metrics['total_expenses']:,.0f}", "📉", "#F87171"),
            (t("dash_net_profit", lang), f"₹{metrics['net_profit']:,.0f}", "💼", COLOR_CYAN if metrics['net_profit'] >= 0 else COLOR_DANGER)
        ]

        for i, (label, val, icon, color) in enumerate(cards_data):
            col = i % 3
            row = i // 3
            card = ctk.CTkFrame(
                kpi_grid,
                fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
                corner_radius=12,
                border_width=1,
                border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            kpi_grid.grid_columnconfigure(col, weight=1)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(14, 4))

            ctk.CTkLabel(
                top_row,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#94A3B8" if is_dark else "#64748B"
            ).pack(side="left")

            ctk.CTkLabel(
                top_row,
                text=icon,
                font=ctk.CTkFont(size=18)
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=val,
                font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                text_color=color
            ).pack(anchor="w", padx=16, pady=(0, 14))

        # Due Fees Warning & Reminder Banner
        due_val = metrics.get("total_due_fee", 0.0)
        due_count = metrics.get("due_students_count", 0)
        if due_val > 0:
            due_banner = ctk.CTkFrame(
                self,
                fg_color="#381E05" if is_dark else "#FEF3C7",
                corner_radius=10,
                border_width=1,
                border_color="#F59E0B"
            )
            due_banner.pack(fill="x", padx=16, pady=(0, 14))

            db_left = ctk.CTkFrame(due_banner, fg_color="transparent")
            db_left.pack(side="left", padx=16, pady=10)

            ctk.CTkLabel(
                db_left,
                text=f"💳 बकाया फीस अलर्ट (Pending Fee Alert): कुल {due_count} छात्रों की ₹{due_val:,.0f} फीस किस्त बकाया है।",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#FDE68A" if is_dark else "#92400E"
            ).pack(side="left")

            btn_go_due = ctk.CTkButton(
                due_banner,
                text="बकाया छात्र देखें व WhatsApp रिमाइंडर भेजें ➡️",
                height=30,
                fg_color="#D97706",
                hover_color="#B45309",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda: self.on_navigate("records")
            )
            btn_go_due.pack(side="right", padx=16, pady=8)

        # Quick Navigation Bar
        quick_bar = ctk.CTkFrame(self, fg_color="transparent")
        quick_bar.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            quick_bar,
            text="⚡ त्वरित कार्य (Quick Actions):",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            quick_bar,
            text="📝 नया Admission",
            height=30,
            fg_color="#0284C7",
            hover_color="#0369A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.on_navigate("admission")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            quick_bar,
            text="👥 स्टाफ व फैकल्टी प्रबंधन",
            height=30,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.on_navigate("staff")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            quick_bar,
            text="📅 Time-Table",
            height=30,
            fg_color="#6366F1",
            hover_color="#4F46E5",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.on_navigate("timetable")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            quick_bar,
            text="💰 दैनिक खर्च दर्ज करें",
            height=30,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.on_navigate("expenses")
        ).pack(side="left", padx=4)

        # Recent Admissions Table Card
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        table_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        h_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        h_frame.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            h_frame,
            text=f"⚡ {t('dash_recent_admissions', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK
        ).pack(side="left")

        ctk.CTkButton(
            h_frame,
            text="सभी रिकॉर्ड्स देखें →",
            width=140,
            height=28,
            fg_color="transparent",
            hover_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD,
            text_color=COLOR_CYAN if is_dark else "#0284C7",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.on_navigate("records")
        ).pack(side="right")

        # Scrollable table container
        table_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        table_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Recent admissions
        admissions = db.get_admissions()[:8]
        if not admissions:
            ctk.CTkLabel(
                table_scroll,
                text="अभी कोई एडमिशन दर्ज नहीं हुआ है। ऊपर '+ नया Admission दर्ज करें' बटन दबाएं।",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#94A3B8"
            ).pack(pady=40)
        else:
            # Table Header
            th = ctk.CTkFrame(table_scroll, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, height=32, corner_radius=6)
            th.pack(fill="x", pady=2)

            cols = [("Adm No", 100), ("Date", 90), ("Student Name", 180), ("Course", 200), ("Amount", 90), ("Status", 120)]
            for title, width in cols:
                ctk.CTkLabel(
                    th,
                    text=title,
                    width=width,
                    anchor="w",
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color="#CBD5E1" if is_dark else "#475569"
                ).pack(side="left", padx=6)

            for a in admissions:
                tr = ctk.CTkFrame(table_scroll, fg_color="transparent", height=34)
                tr.pack(fill="x", pady=1)

                is_act = a["activation_status"] == "Activated"
                status_color = COLOR_SUCCESS if is_act else COLOR_DANGER
                status_badge = "✅ Activated" if is_act else "🚩 Pending"

                vals = [
                    (a["admission_no"], 100, None),
                    (a["payment_date"], 90, None),
                    (a["student_name"], 180, None),
                    (a["courses_taken"], 200, None),
                    (f"₹{a['final_amount']:,.0f}", 90, COLOR_SUCCESS),
                    (status_badge, 120, status_color)
                ]

                for val, width, clr in vals:
                    ctk.CTkLabel(
                        tr,
                        text=str(val)[:28],
                        width=width,
                        anchor="w",
                        font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold" if clr else "normal"),
                        text_color=clr if clr else (COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK)
                    ).pack(side="left", padx=6)

    def open_license_dialog(self):
        """Open license activation dialog and refresh dashboard if state changes."""
        from ui.views.license_dialog import LicenseDialog
        d = LicenseDialog(self)
        self.wait_window(d)
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
