import os
import shutil
from pathlib import Path
import tkinter.filedialog as fd
import customtkinter as ctk
from PIL import Image
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_DARK, COLOR_NAVY_SURFACE,
    COLOR_NAVY_CARD, COLOR_NAVY_BORDER, load_config, save_config, APP_NAME, APP_FULL_NAME
)
from core.database import DatabaseManager
from core.auth import AuthManager

class SetupWizard(ctk.CTk):
    def __init__(self, on_complete_callback, on_demo_callback=None):
        super().__init__()
        self.on_complete_callback = on_complete_callback
        self.on_demo_callback = on_demo_callback
        self.title(f"{APP_NAME} - Initial Setup Wizard (प्रारंभिक सेटअप)")
        self.geometry("840x700")
        self.minsize(800, 650)
        ctk.set_appearance_mode("dark")

        self.storage_path = ""
        self.generated_master_key = AuthManager.generate_master_recovery_key()

        self.setup_ui()

    def setup_ui(self):
        self.configure(fg_color=COLOR_NAVY_DARK)

        # Header banner
        header = ctk.CTkFrame(self, height=80, fg_color=COLOR_NAVY_SURFACE, corner_radius=0)
        header.pack(fill="x")

        title = ctk.CTkLabel(
            header,
            text=f"🚀 Welcome to {APP_NAME} - Setup Wizard",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLOR_CYAN
        )
        title.pack(anchor="w", padx=24, pady=(16, 2))

        subtitle = ctk.CTkLabel(
            header,
            text="सिस्टम को पहली बार कॉन्फ़िगर करें: स्टोरेज लोकेशन, एडमिन खाता व रिकवरी कुंजी",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 14))

        # --- 1-CLICK INSTANT DEMO BANNER (Zero Form Filling) ---
        demo_card = ctk.CTkFrame(
            self,
            fg_color="#064E3B",
            corner_radius=12,
            border_width=2,
            border_color="#10B981"
        )
        demo_card.pack(fill="x", padx=24, pady=(12, 0))

        dc_left = ctk.CTkFrame(demo_card, fg_color="transparent")
        dc_left.pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(
            dc_left,
            text="🌟 केवल सॉफ्टवेयर का डेमो देखना है? बिना किसी फॉर्म भरे तुरंत शुरू करें!",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#A7F3D0"
        ).pack(anchor="w")

        ctk.CTkLabel(
            dc_left,
            text="1-क्लिक में 10 सैंपल छात्र, फीस रसीदें, टाइम-टेबल, स्टाफ और पूरा P&L डैशबोर्ड लाइव लोड हो जाएगा।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#D1FAE5"
        ).pack(anchor="w")

        btn_demo = ctk.CTkButton(
            demo_card,
            text="🎮 1-क्लिक लाइव डेमो (Explore Live Demo)",
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.launch_instant_demo
        )
        btn_demo.pack(side="right", padx=16, pady=10)

        # Main Scrollable Form Container
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=24, pady=12)

        # --- STEP 1: Custom Storage Directory (No Forced C: Drive) ---
        step1_card = ctk.CTkFrame(self.container, fg_color=COLOR_NAVY_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_NAVY_BORDER)
        step1_card.pack(fill="x", pady=(0, 16), padx=4)

        s1_title = ctk.CTkLabel(
            step1_card,
            text="📁 1. डेटा स्टोरेज डायरेक्टरी चुनें (Select Storage Location - Not Forced to C:)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN
        )
        s1_title.pack(anchor="w", padx=16, pady=(14, 4))

        s1_desc = ctk.CTkLabel(
            step1_card,
            text="डेटाबेस और सभी पेमेंट स्क्रीनशॉट्स इसी चुने हुए सुरक्षित स्थान (जैसे D: या E: ड्राइव) में रहेंगे।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1"
        )
        s1_desc.pack(anchor="w", padx=16, pady=(0, 10))

        path_box = ctk.CTkFrame(step1_card, fg_color="transparent")
        path_box.pack(fill="x", padx=16, pady=(0, 16))

        # Suggest a safe non-C path if available, or app directory
        default_dir = "D:\\APNA_RMS_Data" if os.path.exists("D:\\") else str(Path(__file__).resolve().parent.parent / "local_storage")
        self.path_entry = ctk.CTkEntry(
            path_box,
            placeholder_text="जैसे: D:\\APNA_Institute_Data",
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.path_entry.insert(0, default_dir)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = ctk.CTkButton(
            path_box,
            text="📂 Browse Folder...",
            width=130,
            height=38,
            fg_color=COLOR_CYAN,
            text_color="#001633",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            hover_color=COLOR_CYAN_HOVER,
            command=self.browse_storage_path
        )
        btn_browse.pack(side="right")

        # --- STEP 2: Create Admin Account ---
        step2_card = ctk.CTkFrame(self.container, fg_color=COLOR_NAVY_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_NAVY_BORDER)
        step2_card.pack(fill="x", pady=(0, 16), padx=4)

        s2_title = ctk.CTkLabel(
            step2_card,
            text="👤 2. मुख्य एडमिन खाता बनाएं (Create Admin Account)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN
        )
        s2_title.pack(anchor="w", padx=16, pady=(14, 4))

        form_grid = ctk.CTkFrame(step2_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=16, pady=(0, 16))

        # Admin Full Name
        lbl_fn = ctk.CTkLabel(form_grid, text="पूरा नाम (Full Name):", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_fn.grid(row=0, column=0, sticky="w", pady=4, padx=4)
        self.admin_name = ctk.CTkEntry(form_grid, height=36, placeholder_text="उदा: Director / Admin Name")
        self.admin_name.insert(0, "Director Admin")
        self.admin_name.grid(row=0, column=1, sticky="ew", pady=4, padx=4)

        # Admin Username
        lbl_un = ctk.CTkLabel(form_grid, text="यूज़रनेम (Username):", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_un.grid(row=1, column=0, sticky="w", pady=4, padx=4)
        self.admin_user = ctk.CTkEntry(form_grid, height=36, placeholder_text="admin")
        self.admin_user.insert(0, "admin")
        self.admin_user.grid(row=1, column=1, sticky="ew", pady=4, padx=4)

        # Password
        lbl_pw = ctk.CTkLabel(form_grid, text="पासवर्ड (Password):", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_pw.grid(row=2, column=0, sticky="w", pady=4, padx=4)
        self.admin_pass = ctk.CTkEntry(form_grid, height=36, show="•", placeholder_text="मजबूत पासवर्ड दर्ज करें")
        self.admin_pass.grid(row=2, column=1, sticky="ew", pady=4, padx=4)

        # Confirm Password
        lbl_cpw = ctk.CTkLabel(form_grid, text="कन्फर्म पासवर्ड (Confirm):", font=ctk.CTkFont(size=11, weight="bold"))
        lbl_cpw.grid(row=3, column=0, sticky="w", pady=4, padx=4)
        self.admin_cpass = ctk.CTkEntry(form_grid, height=36, show="•", placeholder_text="पासवर्ड दोबारा दर्ज करें")
        self.admin_cpass.grid(row=3, column=1, sticky="ew", pady=4, padx=4)

        form_grid.grid_columnconfigure(1, weight=1)

        # --- STEP 3: Master Recovery Key ---
        step3_card = ctk.CTkFrame(self.container, fg_color=COLOR_NAVY_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_NAVY_BORDER)
        step3_card.pack(fill="x", pady=(0, 16), padx=4)

        s3_title = ctk.CTkLabel(
            step3_card,
            text="🔑 3. मास्टर रिकवरी कुंजी (Master Password Recovery Key)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLOR_CYAN
        )
        s3_title.pack(anchor="w", padx=16, pady=(14, 4))

        s3_desc = ctk.CTkLabel(
            step3_card,
            text="⚠️ महत्वपूर्ण: यदि आप कभी एडमिन पासवर्ड भूल जाते हैं, तो केवल यह कुंजी आपका पासवर्ड रीसेट कर सकती है। इसे लिखकर सुरक्षित रख लें!",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#F59E0B"
        )
        s3_desc.pack(anchor="w", padx=16, pady=(0, 8))

        key_box = ctk.CTkFrame(step3_card, fg_color=COLOR_NAVY_CARD, corner_radius=8)
        key_box.pack(fill="x", padx=16, pady=(0, 16))

        self.key_lbl = ctk.CTkLabel(
            key_box,
            text=self.generated_master_key,
            font=ctk.CTkFont(family="Courier New", size=16, weight="bold"),
            text_color=COLOR_CYAN
        )
        self.key_lbl.pack(side="left", padx=16, pady=10)

        btn_copy = ctk.CTkButton(
            key_box,
            text="📋 Copy Key",
            width=90,
            height=30,
            fg_color="#0284C7",
            hover_color="#0369A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.copy_recovery_key
        )
        btn_copy.pack(side="right", padx=16)

        # Error / Validation Label
        self.error_label = ctk.CTkLabel(
            self.container,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#EF4444"
        )
        self.error_label.pack(pady=4)

        # Bottom Finish Button
        btn_finish = ctk.CTkButton(
            self.container,
            text="✅ Save & Complete Setup (सेटअप पूरा करें)",
            height=46,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self.complete_setup
        )
        btn_finish.pack(fill="x", pady=(10, 20), padx=4)

    def browse_storage_path(self):
        chosen = fd.askdirectory(title="डेटा स्टोरेज फ़ोल्डर चुनें")
        if chosen:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, chosen)

    def copy_recovery_key(self):
        self.clipboard_clear()
        self.clipboard_append(self.generated_master_key)
        self.error_label.configure(text="✅ Master Recovery Key copied to clipboard! (सुरक्षित जगह सेव करें)", text_color="#10B981")

    def complete_setup(self):
        path = self.path_entry.get().strip()
        name = self.admin_name.get().strip()
        username = self.admin_user.get().strip()
        pwd = self.admin_pass.get()
        cpwd = self.admin_cpass.get()

        if not path:
            self.error_label.configure(text="कृपया स्टोरेज पाथ चुनें! / Please choose a storage path!")
            return
        if not name or not username or not pwd:
            self.error_label.configure(text="कृपया एडमिन का नाम, यूज़रनेम और पासवर्ड भरें!")
            return
        if len(pwd) < 4:
            self.error_label.configure(text="पासवर्ड कम से कम 4 अक्षरों का होना चाहिए!")
            return
        if pwd != cpwd:
            self.error_label.configure(text="पासवर्ड और कन्फर्म पासवर्ड मैच नहीं हो रहे हैं!")
            return

        try:
            # Create storage path
            os.makedirs(path, exist_ok=True)
            db = DatabaseManager.get_instance(os.path.join(path, "apna_records.db"))

            # Save Master Recovery Key
            AuthManager.save_master_recovery_key(self.generated_master_key)

            # Register Admin User
            AuthManager.register_user(username, pwd, "admin", name)

            # Save App Config
            config = load_config()
            config["is_setup_completed"] = True
            config["storage_path"] = path
            save_config(config)

            self.destroy()
            self.on_complete_callback()
        except Exception as e:
            self.error_label.configure(text=f"सेटअप एरर: {str(e)}")

    def launch_instant_demo(self):
        """Instant demo bypass: seeds sample database and launches main app immediately as demo user."""
        try:
            if os.path.exists("D:\\"):
                demo_dir = Path("D:\\APNA_RMS_DATA")
            else:
                demo_dir = Path.home() / "APNA_RMS_DATA"
            demo_dir.mkdir(parents=True, exist_ok=True)

            config = load_config()
            config["is_setup_completed"] = True
            config["storage_path"] = str(demo_dir)
            save_config(config)

            db = DatabaseManager.get_instance(str(demo_dir / "apna_records.db"))
            AuthManager.ensure_default_staff_roles()
            db.reset_to_demo_data()

            demo_user = AuthManager.get_demo_user()

            self.destroy()
            if self.on_demo_callback:
                self.on_demo_callback(demo_user)
            else:
                self.on_complete_callback()
        except Exception as e:
            self.error_label.configure(text=f"डेमो एरर: {str(e)}")
