import os
from pathlib import Path
import customtkinter as ctk
from PIL import Image
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_DARK, COLOR_NAVY_SURFACE,
    COLOR_NAVY_CARD, COLOR_LIGHT_BG, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, load_config, save_config, APP_NAME
)
from core.translations import t

class AppHeader(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_theme_change, on_lang_change, on_logout):
        super().__init__(parent, height=68, corner_radius=0)
        self.current_user = current_user
        self.on_theme_change = on_theme_change
        self.on_lang_change = on_lang_change
        self.on_logout = on_logout
        self.config = load_config()

        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        # Configure colors based on current theme
        is_dark = self.config.get("theme", "dark") == "dark"
        self.configure(fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE)

        # Left: Logo + Brand Name
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", padx=16, fill="y")

        logo_path = self.config.get("logo_path", "")
        if logo_path and os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                # Keep aspect ratio inside 48x48 box
                pil_img.thumbnail((48, 48), Image.Resampling.LANCZOS)
                self.logo_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                self.logo_label = ctk.CTkLabel(left_frame, image=self.logo_ctk, text="")
                self.logo_label.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", pady=8)

        self.title_label = ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            title_frame,
            text=t("app_subtitle", self.config.get("language", "hi")),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        )
        self.subtitle_label.pack(anchor="w")

        # Center: Live Demo Banner (if in demo mode)
        if self.current_user.get("username") == "demo" or self.current_user.get("is_demo"):
            demo_frame = ctk.CTkFrame(self, fg_color="#064E3B", corner_radius=10, border_width=1, border_color="#10B981")
            demo_frame.pack(side="left", padx=16, pady=12)

            ctk.CTkLabel(
                demo_frame,
                text="🌟 लाइव डेमो मोड (Live Demo)",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#6EE7B7"
            ).pack(side="left", padx=(10, 8))

            ctk.CTkButton(
                demo_frame,
                text="🔄 रीसेट डेमो डेटा",
                height=26,
                width=110,
                corner_radius=6,
                fg_color="#10B981",
                hover_color="#059669",
                text_color="#FFFFFF",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                command=self.handle_demo_reset
            ).pack(side="left", padx=(0, 6), pady=4)

        # Center: License & VIP Trial Status Pill
        try:
            from core.license_manager import LicenseManager
            self.lm = LicenseManager.get_instance()
            self.lic_info = self.lm.get_license_info()

            is_locked = self.lic_info.get("is_locked")
            status = self.lic_info.get("status")
            badge_text = self.lic_info.get("display_text", "")

            if is_locked:
                b_fg = "#7F1D1D"
                b_border = "#EF4444"
                b_text = "#FCA5A5"
            elif status in ("trial", "trial_extended"):
                b_fg = "#451A03"
                b_border = "#F59E0B"
                b_text = "#FDE68A"
            else:
                b_fg = "#064E3B"
                b_border = "#10B981"
                b_text = "#6EE7B7"

            self.lic_btn = ctk.CTkButton(
                self,
                text=badge_text,
                height=30,
                corner_radius=15,
                border_width=1,
                border_color=b_border,
                fg_color=b_fg,
                text_color=b_text,
                hover_color=b_border,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                command=self.open_license_dialog
            )
            self.lic_btn.pack(side="left", padx=14, pady=12)
        except Exception as e:
            print(f"[Header License] Error initializing license pill: {e}")

        # Right Frame: Controls & User Info
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", padx=16, fill="y")

        # Side-by-side Segmented Theme Toggle Pill: [ ☀️ Light | 🌙 Dark ]
        theme_frame = ctk.CTkFrame(right_frame, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, corner_radius=18)
        theme_frame.pack(side="left", padx=8, pady=14)

        self.btn_light = ctk.CTkButton(
            theme_frame,
            text="☀️ Light",
            width=70,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLOR_CYAN if not is_dark else "transparent",
            text_color="#001633" if not is_dark else "#94A3B8",
            hover_color=COLOR_CYAN_HOVER if not is_dark else "#1E293B",
            command=lambda: self.switch_theme("light")
        )
        self.btn_light.pack(side="left", padx=2, pady=2)

        self.btn_dark = ctk.CTkButton(
            theme_frame,
            text="🌙 Dark",
            width=70,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLOR_CYAN if is_dark else "transparent",
            text_color="#001633" if is_dark else "#64748B",
            hover_color=COLOR_CYAN_HOVER if is_dark else "#E2E8F0",
            command=lambda: self.switch_theme("dark")
        )
        self.btn_dark.pack(side="left", padx=2, pady=2)

        # Side-by-side Segmented Language Toggle Pill: [ हिंदी | English ]
        current_lang = self.config.get("language", "hi")
        lang_frame = ctk.CTkFrame(right_frame, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, corner_radius=18)
        lang_frame.pack(side="left", padx=8, pady=14)

        self.btn_hi = ctk.CTkButton(
            lang_frame,
            text="हिंदी",
            width=60,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLOR_CYAN if current_lang == "hi" else "transparent",
            text_color="#001633" if current_lang == "hi" else ("#94A3B8" if is_dark else "#64748B"),
            hover_color=COLOR_CYAN_HOVER if current_lang == "hi" else "#1E293B",
            command=lambda: self.switch_lang("hi")
        )
        self.btn_hi.pack(side="left", padx=2, pady=2)

        self.btn_en = ctk.CTkButton(
            lang_frame,
            text="English",
            width=65,
            height=28,
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLOR_CYAN if current_lang == "en" else "transparent",
            text_color="#001633" if current_lang == "en" else ("#94A3B8" if is_dark else "#64748B"),
            hover_color=COLOR_CYAN_HOVER if current_lang == "en" else "#1E293B",
            command=lambda: self.switch_lang("en")
        )
        self.btn_en.pack(side="left", padx=2, pady=2)

        # User Badge
        role_raw = self.current_user.get("role", "staff").lower()
        is_super = role_raw == "super_admin" or self.current_user.get("username") == "hanuganeshan"
        user_name = self.current_user.get("full_name", self.current_user.get("username", "User"))

        user_card_kwargs = {
            "fg_color": "#0F2942" if is_super else (COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD),
            "corner_radius": 10
        }
        if is_super:
            user_card_kwargs["border_width"] = 1
            user_card_kwargs["border_color"] = "#F59E0B"

        user_card = ctk.CTkFrame(right_frame, **user_card_kwargs)
        user_card.pack(side="left", padx=10, pady=12)

        if is_super:
            user_text = f"👑 {user_name} [SUPER ADMIN]"
            text_col = "#FDE68A" if is_dark else "#B45309"
        else:
            role_title = role_raw.capitalize()
            user_text = f"👤 {user_name} ({role_title})"
            text_col = COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK

        self.user_lbl = ctk.CTkLabel(
            user_card,
            text=user_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=text_col
        )
        self.user_lbl.pack(padx=10, pady=4)

        # Logout Button
        self.logout_btn = ctk.CTkButton(
            right_frame,
            text="🚪 " + t("logout", current_lang),
            width=80,
            height=32,
            corner_radius=8,
            fg_color="#EF4444",
            hover_color="#DC2626",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.on_logout
        )
        self.logout_btn.pack(side="left", padx=4, pady=16)

    def switch_theme(self, new_theme):
        if self.config.get("theme") != new_theme:
            self.config["theme"] = new_theme
            save_config(self.config)
            ctk.set_appearance_mode(new_theme)
            self.on_theme_change(new_theme)

    def switch_lang(self, new_lang):
        if self.config.get("language") != new_lang:
            self.config["language"] = new_lang
            save_config(self.config)
            self.on_lang_change(new_lang)

    def handle_demo_reset(self):
        from core.database import DatabaseManager
        import tkinter.messagebox as mbox
        DatabaseManager.get_instance().reset_to_demo_data()
        mbox.showinfo("Demo Data Reset", "डेमो डेटा सफलतापूर्वक रीसेट हो गया है!\n(10 स्टूडेंट्स व 5 खर्चे पुनः लोड हो गए हैं)")
        # Notify parent main window to refresh current view
        if hasattr(self.master, "on_data_updated"):
            self.master.on_data_updated()
        if hasattr(self.master, "navigate_to"):
            current_tab = getattr(self.master.sidebar, "active_tab", "dashboard")
            self.master.navigate_to(current_tab)

    def open_license_dialog(self):
        try:
            from ui.views.license_dialog import LicenseActivationDialog
            LicenseActivationDialog(self.winfo_toplevel(), on_activated_callback=self.on_license_updated)
        except Exception as e:
            print(f"[Header License] Error opening dialog: {e}")

    def on_license_updated(self):
        try:
            self.lic_info = self.lm.get_license_info()
            is_locked = self.lic_info.get("is_locked")
            status = self.lic_info.get("status")
            badge_text = self.lic_info.get("display_text", "")

            if is_locked:
                b_fg = "#7F1D1D"
                b_border = "#EF4444"
                b_text = "#FCA5A5"
            elif status in ("trial", "trial_extended"):
                b_fg = "#451A03"
                b_border = "#F59E0B"
                b_text = "#FDE68A"
            else:
                b_fg = "#064E3B"
                b_border = "#10B981"
                b_text = "#6EE7B7"

            if hasattr(self, "lic_btn"):
                self.lic_btn.configure(
                    text=badge_text,
                    fg_color=b_fg,
                    border_color=b_border,
                    text_color=b_text,
                    hover_color=b_border
                )
        except Exception as e:
            print(f"[Header License] Error updating badge: {e}")

