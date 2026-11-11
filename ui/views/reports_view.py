import os
import threading
import urllib.parse
import webbrowser
import zipfile
from pathlib import Path
from datetime import datetime
import tkinter.filedialog as fd
import customtkinter as ctk
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    load_config
)
from core.translations import t
from core.database import DatabaseManager
from core.excel_service import ExcelService
from core.mail_service import MailService

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.config = load_config()

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        # Header Banner
        banner = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        banner.pack(fill="x", padx=4, pady=(0, 16))

        b_left = ctk.CTkFrame(banner, fg_color="transparent")
        b_left.pack(side="left", padx=20, pady=16)

        ctk.CTkLabel(
            b_left,
            text=f"📈 {t('rep_title', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_left,
            text="दैनिक रिपोर्ट ईमेल, AI/LLM ऑडिट एक्सेल एक्सपोर्ट व बल्क स्टूडेंट इम्पोर्ट",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(anchor="w")

        # --- MODULE 1: ONE-CLICK DAILY EOD EMAIL TO ADMIN ---
        card_mail = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        card_mail.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            card_mail,
            text="📧 दैनिक रिपोर्ट व बैकअप ईमेल (Daily EOD Backup & Email)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 4))

        admin_email = self.config.get("admin_backup_email", "सेटिंग्स में सेट नहीं है")
        ctk.CTkLabel(
            card_mail,
            text=f"शाम को काम समाप्त होने पर यह बटन दबाएं। आज के सभी एडमिशन की Excel और सभी स्क्रीनशॉट्स की Zip सुरक्षित रूप से मालिक/एडमिन के ईमेल ({admin_email}) पर भेज दी जाएगी।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#475569",
            wraplength=700
        ).pack(anchor="w", padx=20, pady=(0, 12))

        mail_action_row = ctk.CTkFrame(card_mail, fg_color="transparent")
        mail_action_row.pack(fill="x", padx=20, pady=(0, 16))

        # 1-Click Direct Gmail Button (No Password, No SMTP setup required)
        self.btn_gmail_compose = ctk.CTkButton(
            mail_action_row,
            text="🌐 1-क्लिक जीमेल में भेजें (Open in Gmail - No Password!)",
            height=42,
            fg_color="#EA4335",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.open_direct_gmail_compose
        )
        self.btn_gmail_compose.pack(side="left", padx=(0, 10))

        self.btn_send_mail = ctk.CTkButton(
            mail_action_row,
            text="🚀 ऑटो-मेल (SMTP)",
            height=42,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.trigger_eod_mail
        )
        self.btn_send_mail.pack(side="left")

        self.mail_status_lbl = ctk.CTkLabel(
            mail_action_row,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.mail_status_lbl.pack(side="left", padx=16)

        # --- MODULE 2: AI / LLM & TAX AUDIT EXCEL EXPORT ---
        card_excel = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        card_excel.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            card_excel,
            text="📊 AI / LLM व टैक्स ऑडिट रेडी एक्सेल एक्सपोर्ट (Date-Wise Audit Report)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            card_excel,
            text="तारीख चुनकर Excel (.xlsx) डाउनलोड करें। इस फाइल को सीधे ChatGPT या Gemini में अपलोड करके वित्तीय विश्लेषण प्राप्त कर सकते हैं।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#475569"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        filter_row = ctk.CTkFrame(card_excel, fg_color="transparent")
        filter_row.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(filter_row, text="From Date:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 4))
        self.start_dt = ctk.CTkEntry(filter_row, width=110, height=34)
        self.start_dt.insert(0, datetime.now().strftime("%Y-%m-01"))
        self.start_dt.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_row, text="To Date:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 4))
        self.end_dt = ctk.CTkEntry(filter_row, width=110, height=34)
        self.end_dt.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_dt.pack(side="left", padx=(0, 16))

        btn_dl_excel = ctk.CTkButton(
            filter_row,
            text="📥 " + t("btn_export_excel", lang),
            height=36,
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_audit_excel
        )
        btn_dl_excel.pack(side="left")

        # --- MODULE 3: BULK IMPORT EXISTING STUDENT EXCEL ---
        card_import = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        card_import.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            card_import,
            text="📥 पुराने छात्रों का बल्क डेटा इम्पोर्ट (Bulk Student Onboarding)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            card_import,
            text="यदि कोचिंग के पास पहले से Excel में छात्रों का डेटा है, तो 1-क्लिक में पूरा डेटा सॉफ्टवेयर में लोड करें (बिना दोबारा हाथ से टाइप किए)।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#475569"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        import_row = ctk.CTkFrame(card_import, fg_color="transparent")
        import_row.pack(fill="x", padx=20, pady=(0, 16))

        btn_template = ctk.CTkButton(
            import_row,
            text="📄 डाउनलोड Excel टेम्पलेट",
            height=36,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.download_template
        )
        btn_template.pack(side="left", padx=(0, 10))

        btn_upload = ctk.CTkButton(
            import_row,
            text="📤 " + t("btn_bulk_import", lang),
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.import_existing_excel
        )
        btn_upload.pack(side="left")

        self.import_status_lbl = ctk.CTkLabel(
            card_import,
            text="",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.import_status_lbl.pack(anchor="w", padx=20, pady=(0, 12))

    def open_direct_gmail_compose(self):
        admin_email = self.config.get("admin_backup_email", "krishnaskb143@gmail.com")
        inst_name = self.config.get("institute_name", "APNA Computer")
        today_str = datetime.now().strftime("%Y-%m-%d")
        display_date = datetime.now().strftime("%d-%b-%Y")

        db = DatabaseManager.get_instance()
        today_admissions = db.get_admissions(start_date=today_str, end_date=today_str)
        total_count = len(today_admissions)
        total_rev = sum(a["final_amount"] for a in today_admissions)

        # Folder to store today's files
        export_dir = db.db_dir / "today_report_for_mail"
        export_dir.mkdir(parents=True, exist_ok=True)

        # 1. Export Today's Excel
        excel_file = export_dir / f"Daily_Report_{today_str}.xlsx"
        ExcelService.export_admissions_to_excel(str(excel_file), start_date=today_str, end_date=today_str)

        # 2. Export Today's Screenshots Zip
        zip_file = export_dir / f"Screenshots_{today_str}.zip"
        with zipfile.ZipFile(str(zip_file), "w", zipfile.ZIP_DEFLATED) as zipf:
            for a in today_admissions:
                s_path = a.get("screenshot_path", "")
                if s_path and os.path.exists(s_path):
                    zipf.write(s_path, arcname=Path(s_path).name)

        # Open the folder with the files highlighted
        try:
            os.startfile(str(export_dir))
        except Exception:
            pass

        # Open Gmail in default browser with pre-filled fields
        subject = f"📊 Daily EOD Admission Report ({display_date}) - {inst_name} [{total_count} Adm - ₹{total_rev:,.0f}]"
        body = (
            f"नमस्ते सर,\n\n"
            f"आज ({display_date}) की दैनिक एडमिशन रिपोर्ट व स्क्रीनशॉट्स की फ़ाइलें आपके कंप्यूटर पर स्वतः तैयार होकर खुल चुकी हैं।\n\n"
            f"• आज के कुल एडमिशन: {total_count}\n"
            f"• आज का कुल कलेक्शन: ₹{total_rev:,.2f}\n\n"
            f"कृपया खुली हुई विंडो से दोनों फ़ाइलें (Excel व Zip) यहां अटैच कर लें।\n\n"
            f"धन्यवाद,\n"
            f"{self.current_user.get('full_name', 'Office Staff')}"
        )
        enc_sub = urllib.parse.quote(subject)
        enc_body = urllib.parse.quote(body)
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={admin_email}&su={enc_sub}&body={enc_body}"
        webbrowser.open(gmail_url)

        self.mail_status_lbl.configure(
            text="✅ जीमेल विंडो और रिपोर्ट फोल्डर खुल चुका है! फ़ाइलें अटैच करके Send दबाएं।",
            text_color=COLOR_SUCCESS
        )

    def trigger_eod_mail(self):
        self.btn_send_mail.configure(state="disabled", text="⏳ ईमेल भेजा जा रहा है...")
        self.mail_status_lbl.configure(text="Creating report & compressing screenshots...", text_color=COLOR_CYAN)

        def worker():
            caller = self.current_user.get("full_name", "Staff")
            success, msg = MailService.send_daily_eod_report(caller_name=caller)
            self.after(0, lambda: self.on_mail_complete(success, msg))

        threading.Thread(target=worker, daemon=True).start()

    def on_mail_complete(self, success, msg):
        self.btn_send_mail.configure(state="normal", text="🚀 आज की रिपोर्ट व बैकअप Admin मेल पर भेजें")
        if success:
            self.mail_status_lbl.configure(text=f"✅ {msg}", text_color=COLOR_SUCCESS)
        else:
            self.mail_status_lbl.configure(text=f"❌ {msg}", text_color=COLOR_DANGER)

    def export_audit_excel(self):
        s_date = self.start_dt.get().strip()
        e_date = self.end_dt.get().strip()
        file_path = fd.asksaveasfilename(
            title="Export AI & Tax Audit Excel",
            defaultextension=".xlsx",
            initialfile=f"APNA_RMS_Audit_{s_date}_to_{e_date}.xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            ExcelService.export_admissions_to_excel(file_path, start_date=s_date, end_date=e_date)
            os.startfile(file_path)

    def download_template(self):
        file_path = fd.asksaveasfilename(
            title="Download Import Template",
            defaultextension=".xlsx",
            initialfile="Student_Import_Template.xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            ExcelService.generate_import_template(file_path)
            os.startfile(file_path)

    def import_existing_excel(self):
        file_path = fd.askopenfilename(
            title="Select Existing Student Excel",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if not file_path:
            return

        caller = self.current_user.get("full_name", "Excel Import")
        count, errors = ExcelService.bulk_import_from_excel(file_path, default_caller=caller)

        if count > 0:
            err_msg = f" (त्रुटियां: {len(errors)})" if errors else ""
            self.import_status_lbl.configure(text=f"✅ {count} छात्रों का डेटा सफलतापूर्वक लोड हो गया!{err_msg}", text_color=COLOR_SUCCESS)
        else:
            first_err = errors[0] if errors else "फाइल में कोई रिकॉर्ड नहीं मिला।"
            self.import_status_lbl.configure(text=f"❌ इम्पोर्ट विफल: {first_err}", text_color=COLOR_DANGER)
