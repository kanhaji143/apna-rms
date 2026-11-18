import os
import customtkinter as ctk
from PIL import Image
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_DARK, COLOR_NAVY_SURFACE,
    COLOR_NAVY_CARD, COLOR_NAVY_BORDER, load_config, APP_NAME, APP_FULL_NAME
)
from core.auth import AuthManager

class LoginWindow(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.on_login_success = on_login_success
        self.config = load_config()
        self.setup_ui()

    def setup_ui(self):
        # Center Card (placed in the center of the viewport for responsive look on any screen)
        card = ctk.CTkFrame(self, width=460, height=590, fg_color=COLOR_NAVY_SURFACE, corner_radius=16, border_width=1, border_color=COLOR_NAVY_BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        logo_path = self.config.get("logo_path", "")
        if logo_path and os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                pil_img.thumbnail((72, 72), Image.Resampling.LANCZOS)
                self.logo_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                logo_lbl = ctk.CTkLabel(card, image=self.logo_ctk, text="")
                logo_lbl.pack(pady=(24, 8))
            except Exception:
                pass

        title_lbl = ctk.CTkLabel(
            card,
            text=APP_NAME,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLOR_CYAN
        )
        title_lbl.pack(pady=(0, 2))

        sub_lbl = ctk.CTkLabel(
            card,
            text="सुरक्षित ऑफलाइन लॉगिन (Secure Offline Portal)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        sub_lbl.pack(pady=(0, 20))

        # Form Inputs
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="x", padx=36)

        lbl_user = ctk.CTkLabel(form_frame, text="यूज़रनेम (Username):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_user.pack(anchor="w", pady=(0, 4))
        self.user_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="यूज़रनेम दर्ज करें (Username)...",
            font=ctk.CTkFont(size=13)
        )
        self.user_entry.pack(fill="x", pady=(0, 14))

        lbl_pass = ctk.CTkLabel(form_frame, text="पासवर्ड (Password):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_pass.pack(anchor="w", pady=(0, 4))
        self.pass_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            show="•",
            placeholder_text="पासवर्ड दर्ज करें (Password)...",
            font=ctk.CTkFont(size=13)
        )
        self.pass_entry.pack(fill="x", pady=(0, 8))

        # Enter key triggers login
        self.pass_entry.bind("<Return>", lambda e: self.do_login())
        self.user_entry.bind("<Return>", lambda e: self.do_login())

        # Error / Status Label
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#EF4444"
        )
        self.error_label.pack(pady=4)

        # Login Button
        btn_login = ctk.CTkButton(
            card,
            text="🔒 सुरक्षित लॉगिन करें (Login)",
            height=44,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.do_login
        )
        btn_login.pack(fill="x", padx=36, pady=(6, 8))

        # Divider / OR
        or_frame = ctk.CTkFrame(card, fg_color="transparent")
        or_frame.pack(fill="x", padx=36, pady=(2, 6))
        ctk.CTkLabel(
            or_frame,
            text="─── अथवा सीधे बिना पासवर्ड के देखें ───",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        ).pack()

        # Quick 1-Click Live Demo Button
        btn_demo = ctk.CTkButton(
            card,
            text="🎮 1-क्लिक लाइव डेमो (Explore Live Demo)",
            height=42,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.do_quick_demo
        )
        btn_demo.pack(fill="x", padx=36, pady=(0, 10))

        # Forgot Password / Reset with Master Key
        btn_forgot = ctk.CTkButton(
            card,
            text="🔑 पासवर्ड भूल गए? मास्टर की से रीसेट करें",
            fg_color="transparent",
            hover_color=COLOR_NAVY_CARD,
            text_color="#94A3B8",
            font=ctk.CTkFont(size=11),
            command=self.show_recovery_dialog
        )
        btn_forgot.pack(pady=(0, 16))

    def do_quick_demo(self):
        try:
            from core.database import DatabaseManager
            db = DatabaseManager.get_instance()
            # If database has 0 students, populate demo data so the demo is lively and functional
            metrics = db.get_dashboard_metrics()
            if metrics.get("total_admissions", 0) == 0:
                db.reset_to_demo_data()
        except Exception as e:
            print(f"Demo auto-seed notice: {e}")

        try:
            user = AuthManager.get_demo_user()
        except Exception as e:
            print(f"Demo get user notice: {e}")
            user = None

        if not user:
            user = {
                "id": 9999,
                "username": "demo",
                "role": "admin",
                "full_name": "🌟 लाइव डेमो डायरेक्टर (Demo Mode)"
            }
        if callable(self.on_login_success):
            self.on_login_success(user)

    def do_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            self.error_label.configure(text="कृपया यूज़रनेम और पासवर्ड दोनों दर्ज करें!")
            return

        try:
            # Self-healing: ensure default accounts exist before checking
            AuthManager.ensure_default_staff_roles()
            user = AuthManager.authenticate(username, password)
            if user:
                self.error_label.configure(text="")
                if callable(self.on_login_success):
                    self.on_login_success(user)
            else:
                self.error_label.configure(text="गलत यूज़रनेम या पासवर्ड! (Invalid Credentials)")
                self.pass_entry.delete(0, "end")
                self.pass_entry.focus()
        except Exception as e:
            self.error_label.configure(text=f"लॉगिन एरर: {str(e)}")

    def show_recovery_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Master Key Password Reset")
        dialog.geometry("440x360")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="🔑 Master Key Password Reset",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLOR_CYAN
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            dialog,
            text="मास्टर रिकवरी की (Master Key) दर्ज करके नया पासवर्ड बनाएं:",
            font=ctk.CTkFont(size=11),
            text_color="#CBD5E1"
        ).pack(pady=(0, 14))

        f = ctk.CTkFrame(dialog, fg_color="transparent")
        f.pack(fill="x", padx=24)

        ctk.CTkLabel(f, text="यूज़रनेम:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        u_ent = ctk.CTkEntry(f, height=34)
        u_ent.insert(0, self.user_entry.get().strip() or "admin")
        u_ent.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(f, text="मास्टर रिकवरी की (Master Key):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        k_ent = ctk.CTkEntry(f, height=34, placeholder_text="जैसे: APNA-XXXX-XXXX-XXXX")
        k_ent.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(f, text="नया पासवर्ड (New Password):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        p_ent = ctk.CTkEntry(f, height=34, show="•")
        p_ent.pack(fill="x", pady=(0, 10))

        err_lbl = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444")
        err_lbl.pack(pady=2)

        def do_reset():
            u = u_ent.get().strip()
            k = k_ent.get().strip()
            p = p_ent.get()
            if not u or not k or not p:
                err_lbl.configure(text="सभी फील्ड्स भरना अनिवार्य है!")
                return
            success, msg = AuthManager.reset_password_with_master_key(u, k, p)
            if success:
                err_lbl.configure(text=msg, text_color="#10B981")
                self.after(1500, dialog.destroy)
            else:
                err_lbl.configure(text=msg, text_color="#EF4444")

        ctk.CTkButton(
            dialog,
            text="रीसेट करें (Confirm Reset)",
            fg_color=COLOR_CYAN,
            text_color="#001633",
            font=ctk.CTkFont(weight="bold"),
            command=do_reset
        ).pack(fill="x", padx=24, pady=10)
