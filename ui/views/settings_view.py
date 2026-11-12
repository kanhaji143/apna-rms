import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import tkinter.filedialog as fd
import customtkinter as ctk
from PIL import Image
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    load_config, save_config, APP_NAME
)
from core.translations import t
from core.database import DatabaseManager
from core.auth import AuthManager

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_config_updated_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.on_config_updated = on_config_updated_callback
        self.config = load_config()
        self.is_super = AuthManager.is_super_admin(self.current_user)

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
            text=f"⚙️ {t('set_title', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_left,
            text="व्हाइट-लेबल ब्रांडिंग, लोगो, बैकअप, ईमेल SMTP व स्टाफ प्रबंधन",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(anchor="w")

        # --- SECTION 1: INSTITUTE PROFILE & BRANDING ---
        sec1 = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        sec1.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            sec1,
            text=f"🏢 {t('set_inst_profile', lang)} (कस्टमाइज़ व री-सेल तैयार)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 10))

        grid1 = ctk.CTkFrame(sec1, fg_color="transparent")
        grid1.pack(fill="x", padx=20, pady=(0, 16))

        # Institute Name
        ctk.CTkLabel(grid1, text="संस्थान का नाम (Institute Name):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", pady=4, padx=6)
        self.inst_name_entry = ctk.CTkEntry(grid1, height=36)
        self.inst_name_entry.insert(0, self.config.get("institute_name", "APNA COMPUTER"))
        self.inst_name_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=6)

        # Tagline
        ctk.CTkLabel(grid1, text="टैगलाइन (Tagline):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, sticky="w", pady=4, padx=6)
        self.tagline_entry = ctk.CTkEntry(grid1, height=36)
        self.tagline_entry.insert(0, self.config.get("institute_tagline", "कंप्यूटर और कौशल प्रशिक्षण संस्थान"))
        self.tagline_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=6)

        # Phone
        ctk.CTkLabel(grid1, text="हेल्पलाइन / फोन नंबर:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=1, column=0, sticky="w", pady=4, padx=6)
        self.phone_entry = ctk.CTkEntry(grid1, height=36)
        self.phone_entry.insert(0, self.config.get("institute_phone", ""))
        self.phone_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=6)

        # Email
        ctk.CTkLabel(grid1, text="ऑफिशियल ईमेल:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=1, column=2, sticky="w", pady=4, padx=6)
        self.email_entry = ctk.CTkEntry(grid1, height=36)
        self.email_entry.insert(0, self.config.get("institute_email", ""))
        self.email_entry.grid(row=1, column=3, sticky="ew", pady=4, padx=6)

        # Address
        ctk.CTkLabel(grid1, text="सेंटर का पता (Address):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", pady=4, padx=6)
        self.addr_entry = ctk.CTkEntry(grid1, height=36)
        self.addr_entry.insert(0, self.config.get("institute_address", ""))
        self.addr_entry.grid(row=2, column=1, columnspan=3, sticky="ew", pady=4, padx=6)

        # Optional Social Links (Shown on Fee Receipts)
        ctk.CTkLabel(grid1, text="YouTube चैनल लिंक (वैकल्पिक):", font=ctk.CTkFont(size=11)).grid(row=3, column=0, sticky="w", pady=4, padx=6)
        self.yt_entry = ctk.CTkEntry(grid1, height=36, placeholder_text="https://youtube.com/@YourChannel")
        self.yt_entry.insert(0, self.config.get("youtube_link", ""))
        self.yt_entry.grid(row=3, column=1, sticky="ew", pady=4, padx=6)

        ctk.CTkLabel(grid1, text="Instagram लिंक (वैकल्पिक):", font=ctk.CTkFont(size=11)).grid(row=3, column=2, sticky="w", pady=4, padx=6)
        self.insta_entry = ctk.CTkEntry(grid1, height=36, placeholder_text="https://instagram.com/YourPage")
        self.insta_entry.insert(0, self.config.get("instagram_link", ""))
        self.insta_entry.grid(row=3, column=3, sticky="ew", pady=4, padx=6)

        grid1.grid_columnconfigure((1, 3), weight=1)

        # Logo Change Row
        logo_row = ctk.CTkFrame(sec1, fg_color="transparent")
        logo_row.pack(fill="x", padx=20, pady=(0, 16))

        btn_logo = ctk.CTkButton(
            logo_row,
            text="👑 लोगो बदलें (Change Logo)" if self.is_super else "🔒 लोगो बदलें (Super Admin Only)",
            width=210,
            height=36,
            fg_color="#10B981" if self.is_super else "#334155",
            hover_color="#059669" if self.is_super else "#475569",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.change_logo
        )
        btn_logo.pack(side="left", padx=(0, 12))

        logo_status_text = f"Current Logo: {Path(self.config.get('logo_path', '')).name}"
        if not self.is_super:
            logo_status_text += " [🔒 लॉक - केवल सुपर एडमिन द्वारा परिवर्तनशील]"
        self.logo_path_lbl = ctk.CTkLabel(
            logo_row,
            text=logo_status_text,
            font=ctk.CTkFont(size=11),
            text_color="#10B981" if self.is_super else "#94A3B8"
        )
        self.logo_path_lbl.pack(side="left")

        btn_save_profile = ctk.CTkButton(
            logo_row,
            text="💾 Save Profile (प्रोफाइल सेव करें)",
            width=180,
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.save_institute_profile
        )
        btn_save_profile.pack(side="right")

        # --- SECTION 2: SMTP & ADMIN BACKUP EMAIL ---
        sec2 = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        sec2.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            sec2,
            text="✉️ SMTP व एडमिन बैकअप ईमेल सेटिंग्स (Daily EOD Dispatch Settings)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 10))

        grid2 = ctk.CTkFrame(sec2, fg_color="transparent")
        grid2.pack(fill="x", padx=20, pady=(0, 16))

        # Admin Target Email
        ctk.CTkLabel(grid2, text="मालिक / एडमिन ईमेल (Recipient) *:", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_CYAN).grid(row=0, column=0, sticky="w", pady=4, padx=6)
        self.admin_mail_entry = ctk.CTkEntry(grid2, height=36, placeholder_text="owner@institute.com")
        self.admin_mail_entry.insert(0, self.config.get("admin_backup_email", ""))
        self.admin_mail_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=6)

        # SMTP Server
        ctk.CTkLabel(grid2, text="SMTP Host (जैसे smtp.gmail.com):", font=ctk.CTkFont(size=11)).grid(row=0, column=2, sticky="w", pady=4, padx=6)
        self.smtp_srv_entry = ctk.CTkEntry(grid2, height=36)
        self.smtp_srv_entry.insert(0, self.config.get("smtp_server", "smtp.gmail.com"))
        self.smtp_srv_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=6)

        # Sender Email
        ctk.CTkLabel(grid2, text="भेजने वाला ईमेल (Sender Email):", font=ctk.CTkFont(size=11)).grid(row=1, column=0, sticky="w", pady=4, padx=6)
        self.sender_mail_entry = ctk.CTkEntry(grid2, height=36)
        self.sender_mail_entry.insert(0, self.config.get("smtp_email", ""))
        self.sender_mail_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=6)

        # App Password
        ctk.CTkLabel(grid2, text="App Password (SMTP पासवर्ड):", font=ctk.CTkFont(size=11)).grid(row=1, column=2, sticky="w", pady=4, padx=6)
        self.smtp_pwd_entry = ctk.CTkEntry(grid2, height=36, show="•")
        self.smtp_pwd_entry.insert(0, self.config.get("smtp_password", ""))
        self.smtp_pwd_entry.grid(row=1, column=3, sticky="ew", pady=4, padx=6)

        grid2.grid_columnconfigure((1, 3), weight=1)

        btn_save_smtp = ctk.CTkButton(
            sec2,
            text="💾 Save Email Settings (ईमेल सेटिंग्स सेव करें)",
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.save_smtp_settings
        )
        btn_save_smtp.pack(anchor="e", padx=26, pady=(0, 16))

        # --- SECTION 3: ONE-CLICK DISASTER RECOVERY & BACKUP ---
        sec3 = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        sec3.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            sec3,
            text="💾 डेटा बैकअप व रिस्टोर (Disaster Recovery)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 4))

        db = DatabaseManager.get_instance()
        ctk.CTkLabel(
            sec3,
            text=f"वर्तमान डेटाबेस डायरेक्टरी: {db.db_dir}\n1-क्लिक में पूरा डेटाबेस और सभी स्क्रीनशॉट्स पेनड्राइव या किसी सुरक्षित फोल्डर में ज़िप बनकर सेव हो जाएंगे।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#475569",
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        b_row = ctk.CTkFrame(sec3, fg_color="transparent")
        b_row.pack(fill="x", padx=20, pady=(0, 16))

        btn_backup = ctk.CTkButton(
            b_row,
            text="💾 " + t("btn_one_click_backup", lang),
            height=38,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.create_system_backup
        )
        btn_backup.pack(side="left", padx=(0, 12))

        btn_restore = ctk.CTkButton(
            b_row,
            text="🔄 " + t("btn_restore_backup", lang),
            height=38,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.restore_system_backup
        )
        btn_restore.pack(side="left")

        btn_clear_demo = ctk.CTkButton(
            b_row,
            text="🧹 सभी डेमो डेटा साफ करें",
            height=38,
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.clear_demo_data_prompt
        )
        btn_clear_demo.pack(side="left", padx=(12, 0))

        self.backup_msg = ctk.CTkLabel(sec3, text="", font=ctk.CTkFont(size=11, weight="bold"))
        self.backup_msg.pack(anchor="w", padx=20, pady=(0, 8))

        # --- SUB-SECTION 3B: SMART MULTI-PC AUTO-MERGE ENGINE ---
        merge_box = ctk.CTkFrame(
            sec3,
            fg_color="#091E3A" if is_dark else "#F1F5F9",
            corner_radius=10,
            border_width=1,
            border_color="#0284C7" if is_dark else "#93C5FD"
        )
        merge_box.pack(fill="x", padx=20, pady=(4, 16))

        m_header = ctk.CTkFrame(merge_box, fg_color="transparent")
        m_header.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            m_header,
            text="⚡ स्मार्ट मल्टी-पीसी ऑटो-डेटा मर्ज (Smart Multi-PC Auto-Merge Tool)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(side="left")

        ctk.CTkLabel(
            merge_box,
            text="विभिन्न कंप्यूटरों (जैसे PC-1 रिसेप्शन, PC-2 अकाउंटेंट, PC-3 कॉलिंग टीम) की दिनभर की बैकअप फाइलों (.db या .zip) को 1-क्लिक में मर्ज करें।\n• डुप्लीकेट रहित: छात्र, किस्तें व खर्चे स्वतः जुड़ेंगे   • ऑटो-रिसॉल्यूशन: टकराने वाले एडमिशन नंबर अपने आप री-असाइन होंगे   • ऑटो-बैकअप सुरक्षित रहेगा",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#475569",
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 10))

        m_btn_row = ctk.CTkFrame(merge_box, fg_color="transparent")
        m_btn_row.pack(fill="x", padx=16, pady=(0, 14))

        btn_merge = ctk.CTkButton(
            m_btn_row,
            text="📥 " + t("btn_multi_pc_merge", lang),
            height=38,
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.perform_multi_pc_merge
        )
        btn_merge.pack(side="left", padx=(0, 12))

        # --- SECTION 4: USER & STAFF MANAGEMENT ---
        sec4 = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        sec4.pack(fill="x", padx=4, pady=(0, 16))

        ctk.CTkLabel(
            sec4,
            text="👥 कॉलिंग टीम व स्टाफ खाता प्रबंधन (Staff Users)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=20, pady=(16, 8))

        user_btn_row = ctk.CTkFrame(sec4, fg_color="transparent")
        user_btn_row.pack(fill="x", padx=20, pady=(0, 12))

        btn_new_user = ctk.CTkButton(
            user_btn_row,
            text="+ नया स्टाफ खाता जोड़ें (Add Staff User)",
            height=34,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.show_add_user_dialog
        )
        btn_new_user.pack(side="left", padx=(0, 10))

        btn_view_logs = ctk.CTkButton(
            user_btn_row,
            text="🕵️ सुरक्षा ऑडिट लॉग देखें (View Audit Logs)",
            height=34,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.show_audit_logs_dialog
        )
        btn_view_logs.pack(side="left")

        # Existing Users List
        self.users_box = ctk.CTkFrame(sec4, fg_color="transparent")
        self.users_box.pack(fill="x", padx=20, pady=(0, 16))
        self.load_users_list()

        # --- SECTION 5: SUPER ADMIN & VENDOR MASTER PANEL ---
        sec5 = ctk.CTkFrame(
            scroll,
            fg_color="#061B33" if is_dark else "#F0FDF4",
            corner_radius=12,
            border_width=1,
            border_color="#F59E0B" if is_dark else "#10B981"
        )
        sec5.pack(fill="x", padx=4, pady=(0, 24))

        sec5_hdr = ctk.CTkFrame(sec5, fg_color="transparent")
        sec5_hdr.pack(fill="x", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            sec5_hdr,
            text="👑 सॉफ्टवेयर निर्माता व वेंडर कंट्रोल (Vendor Master Panel)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#F59E0B" if is_dark else "#047857"
        ).pack(side="left")

        ctk.CTkLabel(
            sec5,
            text="यह सॉफ्टवेयर APNA Computer द्वारा अधिकृत रूप से विकसित और लाइसेंस प्राप्त है।\n• सॉफ्टवेयर डेवलपर: APNA Computer (कृष्णा जी)   • हेल्पलाइन: 8504985149   • ईमेल: krishnaskb143@gmail.com\n• सिस्टम लाइसेंस: लाइफटाइम एक्टिवेटेड (Hardware ID: APNA-RMS-HQ-2026)   • लोगो व ब्रांडिंग: सुरक्षित",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#334155",
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 14))

        sec5_btn_row = ctk.CTkFrame(sec5, fg_color="transparent")
        sec5_btn_row.pack(fill="x", padx=20, pady=(0, 16))

        if self.is_super:
            btn_change_super_pwd = ctk.CTkButton(
                sec5_btn_row,
                text="🔑 सुपर एडमिन पासवर्ड बदलें",
                height=34,
                fg_color="#F59E0B",
                hover_color="#D97706",
                text_color="#001633",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=self.show_change_super_admin_password_dialog
            )
            btn_change_super_pwd.pack(side="left", padx=(0, 10))

            btn_super_logo = ctk.CTkButton(
                sec5_btn_row,
                text="🖼️ मास्टर लोगो अपडेट करें",
                height=34,
                fg_color="#10B981",
                hover_color="#059669",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=self.do_change_logo
            )
            btn_super_logo.pack(side="left")
        else:
            ctk.CTkLabel(
                sec5_btn_row,
                text="🔒 सुपर एडमिन टूल्स केवल @hanuganeshan लॉगिन के लिए अधिकृत हैं।",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#94A3B8"
            ).pack(side="left")

    def change_logo(self):
        if not AuthManager.is_super_admin(self.current_user):
            self.prompt_super_admin_for_logo()
        else:
            self.do_change_logo()

    def prompt_super_admin_for_logo(self):
        d = ctk.CTkToplevel(self)
        d.title("Super Admin Authorization")
        d.geometry("440x270")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text="🔒 सुपर एडमिन सत्यापन आवश्यक है",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN
        ).pack(pady=(16, 6))

        ctk.CTkLabel(
            d,
            text="संस्थान का लोगो बदलने का अधिकार केवल सॉफ्टवेयर ओनर के पास है।\nकृपया सुपर एडमिन (@hanuganeshan) पासवर्ड दर्ज करें:",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            justify="center"
        ).pack(pady=(0, 12))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=30)

        pw_ent = ctk.CTkEntry(f, height=36, show="•", placeholder_text="Enter Super Admin Password...")
        pw_ent.pack(fill="x", pady=(0, 6))
        pw_ent.focus_set()

        err_lbl = ctk.CTkLabel(d, text="", font=ctk.CTkFont(size=11), text_color="#EF4444")
        err_lbl.pack(pady=2)

        def verify():
            pw = pw_ent.get()
            if AuthManager.verify_super_admin_credentials(pw):
                d.destroy()
                self.do_change_logo()
            else:
                err_lbl.configure(text="गलत सुपर एडमिन पासवर्ड! आप लोगो नहीं बदल सकते।")

        pw_ent.bind("<Return>", lambda e: verify())

        ctk.CTkButton(
            d,
            text="🔓 अनलॉक व लोगो बदलें",
            height=36,
            fg_color=COLOR_CYAN,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=verify
        ).pack(fill="x", padx=30, pady=10)

    def do_change_logo(self):
        file_path = fd.askopenfilename(
            title="नया लोगो चुनें (Select Logo)",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if file_path:
            self.config["logo_path"] = file_path
            save_config(self.config)
            self.logo_path_lbl.configure(text=f"Selected Logo: {Path(file_path).name}", text_color=COLOR_SUCCESS)
            if self.on_config_updated:
                self.on_config_updated()
            mbox.showinfo("सफल", "संस्थान का लोगो सफलतापूर्वक अपडेट कर दिया गया!")

    def show_change_super_admin_password_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Change Super Admin Password")
        d.geometry("400x300")
        d.grab_set()

        ctk.CTkLabel(d, text="🔑 सुपर एडमिन पासवर्ड बदलें", font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B").pack(pady=(16, 10))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=30)

        ctk.CTkLabel(f, text="नया पासवर्ड (New Password):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        p1 = ctk.CTkEntry(f, height=36, show="•")
        p1.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="कन्फर्म पासवर्ड (Confirm Password):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        p2 = ctk.CTkEntry(f, height=36, show="•")
        p2.pack(fill="x", pady=(2, 10))

        err_lbl = ctk.CTkLabel(d, text="", font=ctk.CTkFont(size=11), text_color="#EF4444")
        err_lbl.pack(pady=2)

        def save_pwd():
            val1 = p1.get()
            val2 = p2.get()
            if not val1 or not val2:
                err_lbl.configure(text="कृपया दोनों फील्ड्स भरें!")
                return
            if val1 != val2:
                err_lbl.configure(text="दोनों पासवर्ड मेल नहीं खाते!")
                return
            AuthManager.update_super_admin_password(val1)
            mbox.showinfo("सफल", "सुपर एडमिन पासवर्ड सफलतापूर्वक अपडेट कर दिया गया!")
            d.destroy()

        ctk.CTkButton(
            d,
            text="💾 पासवर्ड सुरक्षित करें",
            height=38,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=save_pwd
        ).pack(fill="x", padx=30, pady=10)

    def save_institute_profile(self):
        self.config["institute_name"] = self.inst_name_entry.get().strip()
        self.config["institute_tagline"] = self.tagline_entry.get().strip()
        self.config["institute_phone"] = self.phone_entry.get().strip()
        self.config["institute_email"] = self.email_entry.get().strip()
        self.config["institute_address"] = self.addr_entry.get().strip()
        self.config["youtube_link"] = self.yt_entry.get().strip()
        self.config["instagram_link"] = self.insta_entry.get().strip()
        save_config(self.config)
        if self.on_config_updated:
            self.on_config_updated()

    def save_smtp_settings(self):
        self.config["admin_backup_email"] = self.admin_mail_entry.get().strip()
        self.config["smtp_server"] = self.smtp_srv_entry.get().strip()
        self.config["smtp_email"] = self.sender_mail_entry.get().strip()
        self.config["smtp_password"] = self.smtp_pwd_entry.get().strip()
        save_config(self.config)

    def create_system_backup(self):
        db = DatabaseManager.get_instance()
        file_path = fd.asksaveasfilename(
            title="Save Entire System Backup",
            defaultextension=".zip",
            initialfile=f"APNA_RMS_FULL_BACKUP_{datetime.now().strftime('%Y-%m-%d_%H%M')}.zip",
            filetypes=[("ZIP Files", "*.zip")]
        )
        if file_path:
            try:
                with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    # Backup DB
                    if db.db_path.exists():
                        zipf.write(str(db.db_path), arcname="apna_records.db")
                    # Backup Screenshots
                    if db.screenshots_dir.exists():
                        for img in db.screenshots_dir.glob("*.*"):
                            zipf.write(str(img), arcname=f"screenshots/{img.name}")
                self.backup_msg.configure(text=f"✅ संपूर्ण बैकअप सफलतापूर्वक बनाया गया: {Path(file_path).name}", text_color=COLOR_SUCCESS)
            except Exception as e:
                self.backup_msg.configure(text=f"❌ बैकअप त्रुटि: {str(e)}", text_color=COLOR_DANGER)

    def restore_system_backup(self):
        file_path = fd.askopenfilename(
            title="Select Backup ZIP to Restore",
            filetypes=[("ZIP Files", "*.zip")]
        )
        if not file_path:
            return

        db = DatabaseManager.get_instance()
        try:
            with zipfile.ZipFile(file_path, "r") as zipf:
                zipf.extractall(str(db.db_dir))
            self.backup_msg.configure(text="✅ बैकअप सफलतापूर्वक रिस्टोर हो गया! कृपया सॉफ्टवेयर रीस्टार्ट करें।", text_color=COLOR_SUCCESS)
        except Exception as e:
            self.backup_msg.configure(text=f"❌ रिस्टोर त्रुटि: {str(e)}", text_color=COLOR_DANGER)

    def clear_demo_data_prompt(self):
        d = ctk.CTkToplevel(self)
        d.title("Clear Demo Data")
        d.geometry("400x190")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text="🧹 क्या आप सभी डेमो एडमिशन और खर्चे हटाना चाहते हैं?",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#EF4444"
        ).pack(pady=(24, 8))

        ctk.CTkLabel(
            d,
            text="केवल डेमो रिकॉर्ड्स हटाए जाएंगे। आपके वास्तविक रिकॉर्ड सुरक्षित रहेंगे।",
            font=ctk.CTkFont(size=11),
            text_color="#CBD5E1"
        ).pack(pady=(0, 16))

        btn_box = ctk.CTkFrame(d, fg_color="transparent")
        btn_box.pack()

        def do_clear():
            db = DatabaseManager.get_instance()
            count = db.clear_demo_data()
            d.destroy()
            self.backup_msg.configure(text=f"✅ {count} डेमो रिकॉर्ड्स सफलतापूर्वक हटा दिए गए!", text_color=COLOR_SUCCESS)

        ctk.CTkButton(btn_box, text="हाँ, डेमो डेटा हटाएं", fg_color="#EF4444", hover_color="#DC2626", command=do_clear).pack(side="left", padx=6)
        ctk.CTkButton(btn_box, text="रद्द करें", fg_color="#64748B", command=d.destroy).pack(side="left", padx=6)

    def perform_multi_pc_merge(self):
        file_paths = fd.askopenfilenames(
            title="अन्य सिस्टम (PC-1/PC-2) की बैकअप फाइलें (.db या .zip) चुनें",
            filetypes=[
                ("APNA RMS Backup Files (*.db, *.zip)", "*.db;*.zip"),
                ("SQLite Database (*.db)", "*.db"),
                ("ZIP Backup (*.zip)", "*.zip"),
                ("All Files", "*.*")
            ]
        )
        if not file_paths:
            return

        db = DatabaseManager.get_instance()
        results = []
        user_name = self.current_user.get("full_name", "Admin")

        for fp in file_paths:
            res = db.merge_external_data(fp, recorded_by=user_name)
            results.append(res)

        self.show_merge_results_dialog(results)

    def show_merge_results_dialog(self, results):
        is_dark = self.config.get("theme", "dark") == "dark"

        d = ctk.CTkToplevel(self)
        d.title("मल्टी-पीसी डेटा ऑटो-मर्ज रिपोर्ट (Multi-PC Merge Report)")
        d.geometry("640x520")
        d.grab_set()

        # Header
        header = ctk.CTkFrame(d, fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE, corner_radius=10)
        header.pack(fill="x", padx=16, pady=(16, 10))

        total_files = len(results)
        succ_files = sum(1 for r in results if r.get("success"))
        total_admissions = sum(r.get("admissions_added", 0) for r in results if r.get("success"))
        total_updated = sum(r.get("admissions_updated", 0) for r in results if r.get("success"))
        total_installments = sum(r.get("installments_added", 0) for r in results if r.get("success"))
        total_expenses = sum(r.get("expenses_added", 0) for r in results if r.get("success"))
        total_revenue = sum(r.get("total_revenue_added", 0.0) for r in results if r.get("success"))
        total_exp_amt = sum(r.get("total_expenses_added", 0.0) for r in results if r.get("success"))

        ctk.CTkLabel(
            header,
            text="⚡ मल्टी-पीसी डेटा ऑटो-मर्ज संपन्न!",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            header,
            text=f"कुल फ़ाइलें प्रोसेस: {total_files} | सफल: {succ_files} | नए छात्र: +{total_admissions} | नया कलेक्शन: +₹{total_revenue:,.0f} | नए खर्चे: +₹{total_exp_amt:,.0f}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLOR_SUCCESS if succ_files > 0 else COLOR_DANGER
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Scrollable Breakdown
        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        for idx, r in enumerate(results, start=1):
            f_box = ctk.CTkFrame(
                scroll,
                fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD,
                corner_radius=8,
                border_width=1,
                border_color="#0284C7" if r.get("success") else "#EF4444"
            )
            f_box.pack(fill="x", pady=6)

            if r.get("success"):
                ctk.CTkLabel(
                    f_box,
                    text=f"📁 फ़ाइल #{idx}: {r.get('source_file')}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_CYAN if is_dark else "#0284C7"
                ).pack(anchor="w", padx=12, pady=(10, 4))

                detail_text = (
                    f"  • नए छात्र एडमिशन जोड़े गए: +{r.get('admissions_added', 0)}\n"
                    f"  • एक्टिवेशन स्थिति अपडेट: +{r.get('admissions_updated', 0)}\n"
                    f"  • नई किस्तें जोड़ी गईं: +{r.get('installments_added', 0)}\n"
                    f"  • नए खर्चे जोड़े गए: +{r.get('expenses_added', 0)} (₹{r.get('total_expenses_added', 0.0):,.0f})\n"
                    f"  • टाइमटेबल व स्टाफ लेजर: +{r.get('timetable_added', 0)} क्लास, +{r.get('staff_ledger_added', 0)} लेजर एंट्री\n"
                    f"  • सुरक्षा बैकअप: {r.get('safety_backup', 'सुरक्षित')}"
                )
                ctk.CTkLabel(
                    f_box,
                    text=detail_text,
                    font=ctk.CTkFont(size=11),
                    text_color="#CBD5E1" if is_dark else "#475569",
                    justify="left"
                ).pack(anchor="w", padx=12, pady=(0, 10))
            else:
                ctk.CTkLabel(
                    f_box,
                    text=f"❌ फ़ाइल #{idx}: त्रुटि",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#EF4444"
                ).pack(anchor="w", padx=12, pady=(10, 4))

                ctk.CTkLabel(
                    f_box,
                    text=f"  कारण: {r.get('error', 'अज्ञात त्रुटि')}",
                    font=ctk.CTkFont(size=11),
                    text_color="#EF4444",
                    justify="left"
                ).pack(anchor="w", padx=12, pady=(0, 10))

        # Bottom Button
        btn_box = ctk.CTkFrame(d, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(0, 16))

        def on_close():
            d.destroy()
            if self.on_config_updated:
                self.on_config_updated()

        ctk.CTkButton(
            btn_box,
            text="✅ ठीक है (डेटा रिफ्रेश करें)",
            height=38,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=on_close
        ).pack(side="right")

    def load_users_list(self):
        for w in self.users_box.winfo_children():
            w.destroy()

        users = AuthManager.get_all_users()
        is_dark = self.config.get("theme", "dark") == "dark"
        for u in users:
            row = ctk.CTkFrame(self.users_box, fg_color="transparent", height=30)
            row.pack(fill="x", pady=2)
            if u.get("role") == "super_admin" or u.get("username") == "hanuganeshan":
                role_badge = "[👑 SUPER ADMIN - VENDOR]"
                text_col = "#F59E0B"
                lbl_txt = f"👑 {u['full_name']} (@{u['username']}) - {role_badge} (सुरक्षित / Non-deletable)"
            else:
                role_badge = f"[{u['role'].upper()}]"
                text_col = "#CBD5E1" if is_dark else "#1E293B"
                lbl_txt = f"👤 {u['full_name']} (@{u['username']}) - {role_badge}"
            ctk.CTkLabel(row, text=lbl_txt, font=ctk.CTkFont(size=11, weight="bold"), text_color=text_col).pack(side="left")

    def show_add_user_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Add Staff User")
        d.geometry("400x380")
        d.grab_set()

        ctk.CTkLabel(d, text="👤 नया स्टाफ खाता जोड़ें", font=ctk.CTkFont(size=15, weight="bold"), text_color=COLOR_CYAN).pack(pady=(16, 10))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=24)

        ctk.CTkLabel(f, text="पूरा नाम (Full Name):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        fn_entry = ctk.CTkEntry(f, height=34, placeholder_text="उदा: राहुल शर्मा")
        fn_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="यूज़रनेम (Username):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        un_entry = ctk.CTkEntry(f, height=34, placeholder_text="rahul")
        un_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="रोल / भूमिका (Role):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        role_opt = ctk.CTkOptionMenu(f, values=["caller", "coordinator", "accountant", "admin"], height=34)
        role_opt.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="पासवर्ड (Password):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        pw_entry = ctk.CTkEntry(f, height=34, show="•")
        pw_entry.pack(fill="x", pady=(0, 10))

        err_lbl = ctk.CTkLabel(d, text="", font=ctk.CTkFont(size=11), text_color="#EF4444")
        err_lbl.pack(pady=2)

        def save():
            fn = fn_entry.get().strip()
            un = un_entry.get().strip()
            pw = pw_entry.get()
            if not fn or not un or not pw:
                err_lbl.configure(text="सभी फील्ड्स भरना अनिवार्य है!")
                return
            try:
                AuthManager.register_user(un, pw, role_opt.get(), fn)
                d.destroy()
                self.load_users_list()
            except Exception as e:
                err_lbl.configure(text=f"एरर: {str(e)}")

        ctk.CTkButton(d, text="खाता बनाएं (Create User)", height=38, fg_color=COLOR_CYAN, text_color="#001633", font=ctk.CTkFont(weight="bold"), command=save).pack(fill="x", padx=24, pady=10)

    def show_audit_logs_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Security Audit Trail")
        d.geometry("720x500")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text="🛡️ सिस्टम एक्टिविटी व सुरक्षा ऑडिट लॉग (Security Audit Trail)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_CYAN
        ).pack(pady=(16, 8))

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        db = DatabaseManager.get_instance()
        logs = db.get_audit_logs(limit=100)

        if not logs:
            ctk.CTkLabel(scroll, text="अभी तक कोई ऑडिट लॉग दर्ज नहीं है।", text_color="#94A3B8").pack(pady=40)
            return

        for l in logs:
            row = ctk.CTkFrame(scroll, fg_color=COLOR_NAVY_CARD, corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)

            time_str = str(l.get("timestamp", ""))[:19]
            user_info = f"@{l.get('username', 'system')} [{l.get('user_role', '')}]"
            act = l.get("action", "")
            det = l.get("details", "")

            ctk.CTkLabel(row, text=time_str, font=ctk.CTkFont(size=10), text_color="#94A3B8", width=130, anchor="w").pack(side="left", padx=6, pady=4)
            ctk.CTkLabel(row, text=user_info, font=ctk.CTkFont(size=10, weight="bold"), text_color=COLOR_CYAN, width=130, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=act, font=ctk.CTkFont(size=10, weight="bold"), text_color="#F59E0B", width=140, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=det[:45], font=ctk.CTkFont(size=10), text_color="#CBD5E1", anchor="w").pack(side="left", padx=4, fill="x", expand=True)
