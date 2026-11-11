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
    load_config
)
from core.translations import t
from core.database import DatabaseManager

class ActivationView(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.on_refresh_callback = on_refresh_callback
        self.config = load_config()

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")
        db = DatabaseManager.get_instance()
        metrics = db.get_dashboard_metrics()
        pending_count = metrics.get("pending_activations", 0)

        # Header Banner
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

        title_lbl = ctk.CTkLabel(
            b_left,
            text=f"🚩 {t('act_title', lang)} ({pending_count} Pending)",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_DANGER if pending_count > 0 else COLOR_SUCCESS
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            b_left,
            text="बैकएंड टीम के लिए कोर्स एक्टिवेशन एवं मिलान कतार (1-Click & Bulk Sync)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        )
        sub_lbl.pack(anchor="w")

        # Action Buttons on Right
        b_right = ctk.CTkFrame(banner, fg_color="transparent")
        b_right.pack(side="right", padx=16, pady=14)

        btn_exp_pending = ctk.CTkButton(
            b_right,
            text=t("btn_export_pending", lang),
            height=36,
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_pending_sheet
        )
        btn_exp_pending.pack(side="left", padx=4)

        btn_sync = ctk.CTkButton(
            b_right,
            text=t("btn_upload_sync_activations", lang),
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.upload_activation_sheet
        )
        btn_sync.pack(side="left", padx=4)

        # Tab Selector: [ 🚩 Pending Activations | ✅ Completed History ]
        tab_box = ctk.CTkFrame(self, fg_color="transparent")
        tab_box.pack(fill="x", padx=16, pady=(0, 8))

        self.active_subtab = "pending"
        self.btn_tab_pen = ctk.CTkButton(
            tab_box,
            text=f"🚩 पेंडिंग कोर्स ({pending_count})",
            width=150,
            height=32,
            fg_color=COLOR_DANGER if pending_count > 0 else COLOR_CYAN,
            text_color="#FFFFFF" if pending_count > 0 else "#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.switch_subtab("pending")
        )
        self.btn_tab_pen.pack(side="left", padx=(0, 6))

        self.btn_tab_comp = ctk.CTkButton(
            tab_box,
            text="✅ पूर्ण एक्टिवेशन इतिहास (Completed)",
            width=200,
            height=32,
            fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD,
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.switch_subtab("completed")
        )
        self.btn_tab_comp.pack(side="left")

        # Container Card
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        self.card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Table Header
        self.th = ctk.CTkFrame(self.card, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, height=36, corner_radius=6)
        self.th.pack(fill="x", padx=12, pady=(12, 6))

        headers = [
            ("Adm No", 85), ("Date", 75), ("Student Name", 120), ("Phone", 85),
            ("Email", 130), ("Courses Enrolled", 150), ("Amount", 70), ("Action / Status", 130)
        ]
        for title, w in headers:
            ctk.CTkLabel(
                self.th,
                text=title,
                width=w,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#CBD5E1" if is_dark else "#334155"
            ).pack(side="left", padx=3)

        # Scrollable Rows
        self.scroll = ctk.CTkScrollableFrame(self.card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.load_list()

    def switch_subtab(self, subtab):
        self.active_subtab = subtab
        is_dark = self.config.get("theme", "dark") == "dark"
        if subtab == "pending":
            self.btn_tab_pen.configure(fg_color=COLOR_DANGER, text_color="#FFFFFF")
            self.btn_tab_comp.configure(fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK)
        else:
            self.btn_tab_comp.configure(fg_color=COLOR_SUCCESS, text_color="#FFFFFF")
            self.btn_tab_pen.configure(fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK)
        self.load_list()

    def load_list(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        is_dark = self.config.get("theme", "dark") == "dark"
        status_filter = "Pending" if self.active_subtab == "pending" else "Activated"

        db = DatabaseManager.get_instance()
        admissions = db.get_admissions(status=status_filter)

        if not admissions:
            msg = "🎉 कोई भी कोर्स एक्टिवेशन पेंडिंग नहीं है! (All caught up!)" if self.active_subtab == "pending" else "अभी कोई एक्टिवेटेड रिकॉर्ड नहीं है।"
            ctk.CTkLabel(
                self.scroll,
                text=msg,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLOR_SUCCESS if self.active_subtab == "pending" else "#94A3B8"
            ).pack(pady=50)
            return

        for a in admissions:
            tr = ctk.CTkFrame(self.scroll, fg_color="transparent", height=40)
            tr.pack(fill="x", pady=2)

            ctk.CTkLabel(tr, text=a["admission_no"], width=85, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["payment_date"], width=75, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["student_name"][:16], width=120, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["phone"], width=85, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["email"][:16], width=130, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["courses_taken"][:20], width=150, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=f"₹{a['final_amount']:,.0f}", width=70, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_SUCCESS).pack(side="left", padx=3)

            # Action / Status Button
            act_box = ctk.CTkFrame(tr, fg_color="transparent", width=130)
            act_box.pack(side="left", padx=3)

            if self.active_subtab == "pending":
                btn_act = ctk.CTkButton(
                    act_box,
                    text="✅ Activate Now",
                    height=28,
                    width=115,
                    fg_color=COLOR_SUCCESS,
                    hover_color="#059669",
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda rec_id=a["id"]: self.mark_activated(rec_id)
                )
                btn_act.pack(side="left")
            else:
                act_time = a.get("activated_at", "")[:17]
                ctk.CTkLabel(
                    act_box,
                    text=f"✅ {act_time}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=COLOR_SUCCESS
                ).pack(side="left")

    def mark_activated(self, admission_id):
        db = DatabaseManager.get_instance()
        user_name = self.current_user.get("full_name", "Staff")
        db.update_activation_status(admission_id, "Activated", user_name)
        db.log_activity(
            self.current_user.get("id", 1),
            self.current_user.get("username", "staff"),
            self.current_user.get("role", "staff"),
            "COURSE_ACTIVATED",
            f"Activated admission ID {admission_id}"
        )
        self.load_list()
        if self.on_refresh_callback:
            self.on_refresh_callback()

    def export_pending_sheet(self):
        file_path = fd.asksaveasfilename(
            title="Pending Activations Export",
            defaultextension=".xlsx",
            initialfile=f"Pending_Activations_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            db = DatabaseManager.get_instance()
            pending = db.get_admissions(status="Pending")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Pending_Activations"
            ws.append(["Admission No*", "Student Name", "Phone", "Email", "Courses Enrolled", "Paid Amount", "Activation Status (Set to 'Activated')"])
            for a in pending:
                ws.append([a["admission_no"], a["student_name"], a["phone"], a["email"], a["courses_taken"], a["final_amount"], "Pending"])
            wb.save(file_path)
            os.startfile(file_path)

    def upload_activation_sheet(self):
        file_path = fd.askopenfilename(
            title="Select Verified Activation Sheet",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if not file_path:
            return

        db = DatabaseManager.get_instance()
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active
        updated_count = 0

        user_name = self.current_user.get("full_name", "Bulk Sync")
        rows = list(ws.iter_rows(values_only=True))

        for row in rows[1:]:
            if not row or not row[0]:
                continue
            adm_no = str(row[0]).strip()
            # If 7th column says Activated or Yes
            status_val = str(row[6] or "").strip().lower() if len(row) > 6 else "activated"
            if "act" in status_val or "yes" in status_val or "done" in status_val:
                with db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id FROM admissions WHERE admission_no = ?", (adm_no,))
                    res = cur.fetchone()
                    if res:
                        db.update_activation_status(res[0], "Activated", user_name)
                        updated_count += 1

        self.load_list()
        if self.on_refresh_callback:
            self.on_refresh_callback()

        # Show alert
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sync Complete")
        dialog.geometry("380x180")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"✅ {updated_count} कोर्स सफलतापूर्वक एक्टिवेट कर दिए गए!",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_SUCCESS
        ).pack(pady=(30, 10))

        ctk.CTkButton(
            dialog,
            text="ठीक है (OK)",
            command=dialog.destroy
        ).pack(pady=10)
