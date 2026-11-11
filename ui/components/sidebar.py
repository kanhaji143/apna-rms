import customtkinter as ctk
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_DARK, COLOR_NAVY_SURFACE,
    COLOR_NAVY_CARD, COLOR_LIGHT_BG, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, load_config
)
from core.translations import t
from core.database import DatabaseManager

class AppSidebar(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_nav_select):
        super().__init__(parent, width=210, corner_radius=0)
        self.current_user = current_user
        self.on_nav_select = on_nav_select
        self.config = load_config()
        self.buttons = {}
        self.active_tab = "dashboard"

        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        self.configure(fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE)
        lang = self.config.get("language", "hi")
        role = self.current_user.get("role", "caller").lower()

        # Navigation Items (Key, Label Key, Icon, Roles allowed)
        nav_items = [
            ("dashboard", "nav_dashboard", "📊", ["admin", "accountant"]),
            ("admission", "nav_new_admission", "📝", ["admin", "caller", "coordinator"]),
            ("records", "nav_records", "📋", ["admin", "caller", "accountant", "coordinator"]),
            ("activations", "nav_activations", "🚩", ["admin", "caller", "coordinator"]),
            ("timetable", "nav_timetable", "📅", ["admin", "caller", "accountant", "coordinator"]),
            ("staff", "nav_staff", "👥", ["admin", "accountant"]),
            ("expenses", "nav_expenses", "💰", ["admin", "accountant"]),
            ("reports", "nav_reports", "📈", ["admin"]),
            ("settings", "nav_settings", "⚙️", ["admin"])
        ]

        title_lbl = ctk.CTkLabel(
            self,
            text="NAVIGATION MENU",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#64748B"
        )
        title_lbl.pack(anchor="w", padx=20, pady=(20, 10))

        # Check pending activations count for badge
        db = DatabaseManager.get_instance()
        metrics = db.get_dashboard_metrics()
        pending_count = metrics.get("pending_activations", 0)

        for key, text_key, icon, roles in nav_items:
            if role not in roles:
                continue

            btn_text = f"{icon}  {t(text_key, lang)}"
            if key == "activations" and pending_count > 0:
                btn_text += f" ({pending_count})"

            btn = ctk.CTkButton(
                self,
                text=btn_text,
                height=42,
                corner_radius=8,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color=COLOR_CYAN if key == self.active_tab else "transparent",
                text_color="#001633" if key == self.active_tab else (COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK),
                hover_color=COLOR_CYAN_HOVER if key == self.active_tab else (COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD),
                command=lambda k=key: self.select_tab(k)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.buttons[key] = btn

        # Bottom Version & Offline Status
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=16, pady=16)

        status_lbl = ctk.CTkLabel(
            bottom_frame,
            text="🟢 100% Offline Secured",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#10B981"
        )
        status_lbl.pack(anchor="w")

        ver_lbl = ctk.CTkLabel(
            bottom_frame,
            text="v1.0.0 • Local DB Active",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#94A3B8"
        )
        ver_lbl.pack(anchor="w")

    def select_tab(self, tab_key):
        self.active_tab = tab_key
        is_dark = self.config.get("theme", "dark") == "dark"

        for k, btn in self.buttons.items():
            if k == tab_key:
                btn.configure(
                    fg_color=COLOR_CYAN,
                    text_color="#001633",
                    hover_color=COLOR_CYAN_HOVER
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK,
                    hover_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD
                )

        self.on_nav_select(tab_key)

    def refresh_badges(self):
        db = DatabaseManager.get_instance()
        metrics = db.get_dashboard_metrics()
        pending = metrics.get("pending_activations", 0)
        lang = self.config.get("language", "hi")
        if "activations" in self.buttons:
            text = f"🚩  {t('nav_activations', lang)}"
            if pending > 0:
                text += f" ({pending})"
            self.buttons["activations"].configure(text=text)
