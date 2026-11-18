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

class MainWindow(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_logout_callback):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.current_user = current_user
        self.on_logout_callback = on_logout_callback
        self.config = load_config()

        self.current_view = None
        self.views_cache = {}
        self.setup_ui()
        self.bind_global_shortcuts()
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

    def bind_global_shortcuts(self):
        try:
            top = self.winfo_toplevel()
            role = self.current_user.get("role", "caller").lower()

            # Global Navigation Shortcuts
            top.bind("<Control-Key-1>", lambda e: self.navigate_to("dashboard") if role in ["admin", "super_admin", "accountant"] else None)
            top.bind("<Control-Key-2>", lambda e: self.navigate_to("admission"))
            top.bind("<F2>", lambda e: self.navigate_to("admission"))
            top.bind("<Control-Key-3>", lambda e: self.navigate_to("records"))
            top.bind("<Control-Key-4>", lambda e: self.navigate_to("activations"))
            top.bind("<Control-Key-5>", lambda e: self.navigate_to("timetable"))
            top.bind("<Control-Key-6>", lambda e: self.navigate_to("staff") if role in ["admin", "super_admin", "accountant"] else None)
            top.bind("<Control-Key-7>", lambda e: self.navigate_to("expenses") if role in ["admin", "super_admin", "accountant"] else None)
            top.bind("<Control-Key-8>", lambda e: self.navigate_to("reports") if role in ["admin", "super_admin"] else None)
            top.bind("<Control-Key-9>", lambda e: self.navigate_to("settings") if role in ["admin", "super_admin"] else None)
            top.bind("<F5>", lambda e: self.refresh_current_view())
        except Exception:
            pass

    def refresh_current_view(self):
        if self.current_view:
            if hasattr(self.current_view, "load_records"):
                self.current_view.load_records()
            elif hasattr(self.current_view, "load_staff_data"):
                self.current_view.load_staff_data()
            elif hasattr(self.current_view, "load_expenses"):
                self.current_view.load_expenses()
            elif hasattr(self.current_view, "load_schedule"):
                self.current_view.load_schedule()
            elif hasattr(self.current_view, "load_queue"):
                self.current_view.load_queue()
        self.sidebar.refresh_badges()

    def navigate_to(self, view_name):
        if self.current_view:
            self.current_view.pack_forget()

        try:
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

        except Exception as e:
            # Bulletproof: Never leave the viewport blank!
            err_box = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            err_box.pack(fill="both", expand=True, padx=40, pady=40)
            ctk.CTkLabel(err_box, text="⚠️ व्यू लोड करने में समस्या आई", font=ctk.CTkFont(size=18, weight="bold"), text_color="#EF4444").pack(pady=(30, 8))
            ctk.CTkLabel(err_box, text=f"विवरण (Error): {str(e)}", font=ctk.CTkFont(size=12), text_color="#CBD5E1").pack(pady=4)
            ctk.CTkButton(
                err_box,
                text="📊 डैशबोर्ड पर वापस जाएं",
                command=lambda: self.navigate_to("dashboard"),
                fg_color="#03F9FD",
                hover_color="#00D2D6",
                text_color="#001633",
                font=ctk.CTkFont(weight="bold")
            ).pack(pady=16)
            self.current_view = err_box

        self.sidebar.active_tab = view_name
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
        if callable(self.on_logout_callback):
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
            try:
                MailService.send_daily_eod_report(caller_name=caller)
            except Exception:
                pass
            root = self.winfo_toplevel()
            root.destroy()

        def exit_without_sending():
            d.destroy()
            root = self.winfo_toplevel()
            root.destroy()

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
