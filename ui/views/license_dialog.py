# -*- coding: utf-8 -*-
"""
================================================================================
APNA COMPUTER RMS — LICENSE & TRIAL ACTIVATION MODAL DIALOG
Developed for: APNA Computer (कृष्णा जी) | Helpline: 8504985149
================================================================================
"""

import os
import shutil
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mbox
import customtkinter as ctk
from pathlib import Path
from datetime import datetime

from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_DARK, COLOR_NAVY_SURFACE,
    COLOR_NAVY_CARD, COLOR_LIGHT_BG, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    load_config
)
from core.license_manager import LicenseManager


class LicenseActivationDialog(ctk.CTkToplevel):
    """Modern modal dialog for entering license/extension keys, viewing installation ID, and exporting safety backups."""

    def __init__(self, parent, on_activated_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_activated_callback = on_activated_callback
        self.config = load_config()
        self.lm = LicenseManager.get_instance()
        self.lic_info = self.lm.get_license_info()

        self.title("🛡️ लाइसेंस एवं ट्रायल प्रबंधन — APNA Computer RMS")
        self.geometry("540x620")
        self.resizable(False, False)

        # Modal behavior
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = 540
        h = 620
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        bg_col = COLOR_NAVY_DARK if is_dark else COLOR_LIGHT_BG
        card_col = COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD
        self.configure(fg_color=bg_col)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=24, pady=20)

        # 1. Header Banner
        header_card = ctk.CTkFrame(main_frame, fg_color=card_col, corner_radius=12, border_width=1, border_color="#1E3A8A" if is_dark else "#CBD5E1")
        header_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            header_card,
            text="🛡️ APNA Computer RMS — अधिकृत लाइसेंस नियंत्रण",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38BDF8" if is_dark else "#0284C7"
        ).pack(pady=(12, 2), padx=14)

        ctk.CTkLabel(
            header_card,
            text="100% ऑफ़लाइन सुरक्षित • हार्डवेयर बाउंड क्रिप्टोग्राफिक सिस्टम",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(pady=(0, 12), padx=14)

        # 2. Status & Hardware Installation ID Card
        status_card = ctk.CTkFrame(main_frame, fg_color=card_col, corner_radius=12, border_width=1, border_color="#F59E0B" if self.lic_info["is_locked"] else ("#334155" if is_dark else "#E2E8F0"))
        status_card.pack(fill="x", pady=(0, 14))

        st_inner = ctk.CTkFrame(status_card, fg_color="transparent")
        st_inner.pack(fill="x", padx=16, pady=12)

        # Installation ID with Copy button
        id_row = ctk.CTkFrame(st_inner, fg_color="transparent")
        id_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            id_row,
            text="कंप्यूटर Installation ID:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK
        ).pack(side="left")

        self.lbl_id = ctk.CTkLabel(
            id_row,
            text=f"  {self.lic_info['installation_id']}  ",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            fg_color="#0F2942" if is_dark else "#E0F2FE",
            corner_radius=6,
            text_color="#38BDF8" if is_dark else "#0369A1"
        )
        self.lbl_id.pack(side="left", padx=8)

        ctk.CTkButton(
            id_row,
            text="📋 कॉपी करें",
            width=80,
            height=26,
            corner_radius=6,
            fg_color="#334155" if is_dark else "#E2E8F0",
            hover_color="#475569" if is_dark else "#CBD5E1",
            text_color="#FFFFFF" if is_dark else "#1E293B",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.copy_installation_id
        ).pack(side="left", padx=4)

        # Status badge row
        status_row = ctk.CTkFrame(st_inner, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            status_row,
            text="वर्तमान स्थिति (Status):",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(side="left")

        ctk.CTkLabel(
            status_row,
            text=f" {self.lic_info['display_text']}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#F87171" if self.lic_info["is_locked"] else ("#FBBF24" if self.lic_info["status"] in ("trial", "trial_extended") else "#34D399")
        ).pack(side="left", padx=6)

        # Expiry Date Row
        exp_row = ctk.CTkFrame(st_inner, fg_color="transparent")
        exp_row.pack(fill="x")

        ctk.CTkLabel(
            exp_row,
            text=f"वैधता समाप्ति: {self.lic_info['expiry_date']} ({self.lic_info['days_left']} दिन शेष)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(side="left")

        # 3. Activation Key Input Section
        act_card = ctk.CTkFrame(main_frame, fg_color=card_col, corner_radius=12)
        act_card.pack(fill="x", pady=(0, 14))

        act_inner = ctk.CTkFrame(act_card, fg_color="transparent")
        act_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            act_inner,
            text="🔑 लाइसेंस अथवा एक्सटेंशन की (Key) दर्ज करें:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK
        ).pack(anchor="w", pady=(0, 6))

        input_row = ctk.CTkFrame(act_inner, fg_color="transparent")
        input_row.pack(fill="x", pady=(0, 8))

        self.key_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="APNA-XXXX-XXXX-XXXX या मास्टर कोड",
            height=38,
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold")
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_activate = ctk.CTkButton(
            input_row,
            text="सक्रिय करें (Activate)",
            height=38,
            width=140,
            corner_radius=8,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.handle_activation
        )
        self.btn_activate.pack(side="right")

        self.lbl_msg = ctk.CTkLabel(
            act_inner,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            wraplength=460,
            justify="left"
        )
        self.lbl_msg.pack(anchor="w")

        # 4. Helpline & Support Card
        help_card = ctk.CTkFrame(main_frame, fg_color="#0C2540" if is_dark else "#F0F9FF", corner_radius=10, border_width=1, border_color="#0284C7")
        help_card.pack(fill="x", pady=(0, 14))

        h_inner = ctk.CTkFrame(help_card, fg_color="transparent")
        h_inner.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(
            h_inner,
            text=f"📞 आधिकारिक सहायता व रिन्यूअल हेल्पलाइन:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#38BDF8" if is_dark else "#0369A1"
        ).pack(anchor="w")

        ctk.CTkLabel(
            h_inner,
            text="• डेवलपर / वेंडर: APNA Computer (कृष्णा जी)\n• हेल्पलाइन / WhatsApp: +91 8504985149\n• 10-15 दिन ट्रायल एक्सटेंशन अथवा वार्षिक लाइसेंस हेतु कॉल करें।",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1" if is_dark else "#334155",
            justify="left"
        ).pack(anchor="w", pady=(2, 0))

        # 5. Bottom Action Buttons (Backup & Close)
        btn_bar = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_bar.pack(fill="x", side="bottom")

        ctk.CTkButton(
            btn_bar,
            text="💾 डेटाबेस बैकअप डाउनलोड करें",
            height=32,
            corner_radius=6,
            fg_color="#059669",
            hover_color="#047857",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.handle_emergency_backup
        ).pack(side="left")

        ctk.CTkButton(
            btn_bar,
            text="बंद करें (Close)",
            height=32,
            width=90,
            corner_radius=6,
            fg_color="#475569" if is_dark else "#94A3B8",
            hover_color="#334155" if is_dark else "#64748B",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.destroy
        ).pack(side="right")

    def copy_installation_id(self):
        install_id = self.lic_info["installation_id"]
        self.clipboard_clear()
        self.clipboard_append(install_id)
        self.lbl_msg.configure(text=f"✅ Installation ID '{install_id}' क्लिपबोर्ड पर कॉपी हो गई है! इसे WhatsApp पर भेजें।", text_color="#10B981")

    def handle_activation(self):
        key = self.key_entry.get().strip()
        if not key:
            self.lbl_msg.configure(text="❌ कृपया लाइसेंस की (License Key) दर्ज करें!", text_color="#EF4444")
            return

        success, message = self.lm.activate_key(key)
        if success:
            self.lbl_msg.configure(text=f"🎉 {message}", text_color="#10B981")
            self.lic_info = self.lm.get_license_info()
            # Refresh dialog state
            mbox.showinfo("सफलता", message, parent=self)
            if self.on_activated_callback:
                self.on_activated_callback()
            self.destroy()
        else:
            self.lbl_msg.configure(text=f"❌ {message}", text_color="#EF4444")

    def handle_emergency_backup(self):
        """Export current database so client has 100% confidence their data is secure."""
        from core.database import DatabaseManager
        db = DatabaseManager.get_instance()
        src_db = db.db_path

        if not os.path.exists(src_db):
            mbox.showerror("त्रुटि", "मुख्य डेटाबेस फ़ाइल नहीं मिली!", parent=self)
            return

        default_name = f"APNA_RMS_Data_Backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db"
        dest_file = fd.asksaveasfilename(
            parent=self,
            title="इमरजेंसी डेटाबेस बैकअप सुरक्षित करें",
            initialfile=default_name,
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )

        if dest_file:
            try:
                shutil.copy2(src_db, dest_file)
                mbox.showinfo("बैकअप सफल", f"डेटाबेस सुरक्षित सेव हो गया है:\n{dest_file}", parent=self)
            except Exception as e:
                mbox.showerror("त्रुटि", f"बैकअप बनाने में त्रुटि: {str(e)}", parent=self)
