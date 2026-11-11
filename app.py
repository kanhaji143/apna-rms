import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import customtkinter as ctk
from core.config import load_config
from core.database import DatabaseManager
from core.auth import AuthManager
from ui.setup_wizard import SetupWizard
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class ApplicationController:
    def __init__(self):
        self.config = load_config()
        self.current_window = None

    def start(self):
        is_setup_done = self.config.get("is_setup_completed", False)
        storage_path = self.config.get("storage_path", "")

        if is_setup_done and storage_path:
            try:
                os.makedirs(storage_path, exist_ok=True)
            except Exception:
                # If configured drive (e.g. D:) does not exist on this machine, fallback to user home directory
                storage_path = str(Path.home() / "APNA_RMS_DATA")
                try:
                    os.makedirs(storage_path, exist_ok=True)
                    self.config["storage_path"] = storage_path
                    from core.config import save_config
                    save_config(self.config)
                except Exception:
                    pass

        # Check if database exists and admin is created
        needs_setup = not is_setup_done or not storage_path or not os.path.exists(storage_path)

        if not needs_setup:
            try:
                db = DatabaseManager.get_instance()
                if not AuthManager.is_initial_admin_created():
                    needs_setup = True
            except Exception:
                needs_setup = True

        if needs_setup:
            self.show_setup_wizard()
        else:
            self.show_login()

    def show_setup_wizard(self):
        self.current_window = SetupWizard(
            on_complete_callback=self.show_login,
            on_demo_callback=self.show_main_app
        )
        self.current_window.mainloop()

    def show_login(self):
        self.config = load_config()
        try:
            AuthManager.ensure_default_staff_roles()
        except Exception:
            pass
        self.current_window = LoginWindow(on_login_success=self.show_main_app)
        self.current_window.mainloop()

    def show_main_app(self, user):
        self.current_window = MainWindow(current_user=user, on_logout_callback=self.show_login)
        self.current_window.mainloop()

if __name__ == "__main__":
    app = ApplicationController()
    app.start()
