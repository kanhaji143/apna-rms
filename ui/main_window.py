import os
import customtkinter as ctk
from core.config import (
    COLOR_NAVY_DARK, COLOR_LIGHT_BG, load_config, APP_NAME, APP_FULL_NAME
)
from core.translations import t
from core.mail_service import MailService
from ui.components.header import AppHeader
from ui.components.sidebar import AppSidebar
from ui.views.dashboard_view import DashboardView
from ui.views.admission_view import AdmissionView
from ui.views.records_view import RecordsView
from ui.views.activation_view import ActivationView
from ui.views.timetable_view import TimetableView
from ui.views.staff_view import StaffView
from ui.views.expenses_view import ExpensesView
from ui.views.reports_view import ReportsView
from ui.views.settings_view import SettingsView

class MainWindow(ctk.CTk):
    def __init__(self, current_user, on_logout_callback):
        super().__init__()
        self.current_user = current_user
        self.on_logout_callback = on_logout_callback
        self.config = load_config()

        self.title(f"{APP_NAME} - {APP_FULL_NAME}")
        
        # Responsive Resolution Adaptation (Fit any Laptop / Desktop)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(1280, max(850, int(screen_w * 0.94)))
        win_h = min(800, max(550, int(screen_h * 0.88)))
        self.geometry(f"{win_w}x{win_h}")
        self.minsize(800, 480) # Guaranteed to fit even low-res 1366x768 screens with 125% scaling

        # Auto-maximize cleanly so it fits the screen seamlessly on launch
        try:
            self.after(100, lambda: self.state('zoomed'))
        except Exception:
            pass

        theme = self.config.get("theme", "dark")
        ctk.set_appearance_mode(theme)

        # Intercept Close Window Event for EOD Mail Safety Check
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)

        self.current_view = None
        self.views_cache = {}
        self.setup_ui()
        role = self.current_user.get("role", "caller").lower()
        default_view = "admission" if role == "caller" else "dashboard"
        self.navigate_to(default_view)

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        self.configure(fg_color=COLOR_NAVY_DARK if is_dark else COLOR_LIGHT_BG)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = AppHeader(
            self,
            current_user=self.current_user,
            on_theme_change=self.handle_theme_change,
            on_lang_change=self.handle_lang_change,
            on_logout=self.handle_logout
        )
        self.header.grid(row=0, column=0, sticky="ew")

        # Main Body (Sidebar + Content Container)
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.body_frame.grid(row=1, column=0, sticky="nsew")

        # Sidebar
        self.sidebar = AppSidebar(
            self.body_frame,
            current_user=self.current_user,
            on_nav_select=self.navigate_to
        )
        self.sidebar.pack(side="left", fill="y")

        # Content View Frame
        self.content_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent", corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def navigate_to(self, view_name):
        if self.current_view:
            self.current_view.pack_forget()

        if view_name not in self.views_cache:
            if view_name == "dashboard":
                self.views_cache[view_name] = DashboardView(self.content_frame, self.current_user, on_navigate=self.navigate_to)
            elif view_name == "admission":
                self.views_cache[view_name] = AdmissionView(self.content_frame, self.current_user, on_record_saved_callback=self.on_data_updated)
            elif view_name == "records":
                self.views_cache[view_name] = RecordsView(self.content_frame, self.current_user, on_refresh_callback=self.on_data_updated)
            elif view_name == "activations":
                self.views_cache[view_name] = ActivationView(self.content_frame, self.current_user, on_refresh_callback=self.on_data_updated)
            elif view_name == "timetable":
                self.views_cache[view_name] = TimetableView(self.content_frame, self.current_user)
            elif view_name == "staff":
                self.views_cache[view_name] = StaffView(self.content_frame, self.current_user)
            elif view_name == "expenses":
                self.views_cache[view_name] = ExpensesView(self.content_frame, self.current_user)
            elif view_name == "reports":
                self.views_cache[view_name] = ReportsView(self.content_frame, self.current_user)
            elif view_name == "settings":
                self.views_cache[view_name] = SettingsView(self.content_frame, self.current_user, on_config_updated_callback=self.on_config_updated)

        self.current_view = self.views_cache[view_name]
        self.current_view.pack(fill="both", expand=True)

        # Lightning fast data reload
        if hasattr(self.current_view, "load_records"):
            self.current_view.load_records()
        elif hasattr(self.current_view, "load_staff_data"):
            self.current_view.load_staff_data()
        elif hasattr(self.current_view, "load_queue"):
            self.current_view.load_queue()
        elif hasattr(self.current_view, "load_expenses"):
            self.current_view.load_expenses()
        elif hasattr(self.current_view, "load_schedule"):
            self.current_view.load_schedule()

        self.sidebar.refresh_badges()

    def on_data_updated(self):
        self.sidebar.refresh_badges()
        # Invalidate dashboard so metrics re-compute next time it is visited
        if "dashboard" in self.views_cache:
            try:
                self.views_cache["dashboard"].destroy()
                del self.views_cache["dashboard"]
            except Exception:
                pass

    def on_config_updated(self):
        # Refresh header branding if logo/name updated
        self.header.destroy()
        self.header = AppHeader(
            self,
            current_user=self.current_user,
            on_theme_change=self.handle_theme_change,
            on_lang_change=self.handle_lang_change,
            on_logout=self.handle_logout
        )
        self.header.grid(row=0, column=0, sticky="ew")

    def handle_theme_change(self, new_theme):
        self.configure(fg_color=COLOR_NAVY_DARK if new_theme == "dark" else COLOR_LIGHT_BG)
        # Clear cached views so they re-render in new theme colors
        for v in self.views_cache.values():
            try:
                v.destroy()
            except Exception:
                pass
        self.views_cache.clear()
        self.current_view = None

        current_tab = self.sidebar.active_tab
        self.sidebar.destroy()
        self.sidebar = AppSidebar(
            self.body_frame,
            current_user=self.current_user,
            on_nav_select=self.navigate_to
        )
        self.sidebar.pack(side="left", fill="y")
        self.navigate_to(current_tab)

    def handle_lang_change(self, new_lang):
        # Clear cached views so they re-render in new language strings
        for v in self.views_cache.values():
            try:
                v.destroy()
            except Exception:
                pass
        self.views_cache.clear()
        self.current_view = None

        current_tab = self.sidebar.active_tab
        self.header.destroy()
        self.header = AppHeader(
            self,
            current_user=self.current_user,
            on_theme_change=self.handle_theme_change,
            on_lang_change=self.handle_lang_change,
            on_logout=self.handle_logout
        )
        self.header.grid(row=0, column=0, sticky="ew")

        self.sidebar.destroy()
        self.sidebar = AppSidebar(
            self.body_frame,
            current_user=self.current_user,
            on_nav_select=self.navigate_to
        )
        self.sidebar.pack(side="left", fill="y")
        self.navigate_to(current_tab)

    def handle_logout(self):
        self.destroy()
        self.on_logout_callback()

    def on_close_app(self):
        # EOD Backup Safety Prompt
        d = ctk.CTkToplevel(self)
        d.title("Exit Confirmation")
        d.geometry("450x220")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text="⚠️ शाम की डेली रिपोर्ट चेक (Daily EOD Backup Check)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F59E0B"
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            d,
            text="क्या आपने आज की रिपोर्ट व स्क्रीनशॉट्स एडमिन ईमेल पर भेज दिए हैं?\n(Have you sent today's report & backup?)",
            font=ctk.CTkFont(size=11),
            text_color=("#334155", "#CBD5E1"),
            justify="center"
        ).pack(pady=(0, 16))

        btn_box = ctk.CTkFrame(d, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=10)

        def send_and_exit():
            d.destroy()
            caller = self.current_user.get("full_name", "Staff")
            MailService.send_daily_eod_report(caller_name=caller)
            self.destroy()

        def exit_without_sending():
            d.destroy()
            self.destroy()

        ctk.CTkButton(
            btn_box,
            text="📧 भेजें और बंद करें (Send & Exit)",
            height=38,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=send_and_exit
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_box,
            text="सीधे बंद करें (Exit)",
            height=38,
            width=110,
            fg_color="#64748B",
            hover_color="#475569",
            text_color="#FFFFFF",
            command=exit_without_sending
        ).pack(side="right")
