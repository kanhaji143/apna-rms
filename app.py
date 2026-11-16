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
        self.next_screen = None
        self.screen_data = None

    def start(self):
        is_setup_done = self.config.get("is_setup_completed", False)
        storage_path = self.config.get("storage_path", "")

        # Auto-detect missing drive (e.g. PC has no D: drive) and fallback to C: or User Profile
        if storage_path:
            drive = os.path.splitdrive(storage_path)[0]
            if drive and not os.path.exists(drive + "\\"):
                storage_path = "C:\\APNA_RMS_DATA" if os.path.exists("C:\\") else str(Path.home() / "APNA_RMS_DATA")
                self.config["storage_path"] = storage_path
                from core.config import save_config
                save_config(self.config)

        if is_setup_done and storage_path:
            try:
                os.makedirs(storage_path, exist_ok=True)
            except Exception:
                # If configured drive does not exist on this machine, fallback to user home directory
                storage_path = str(Path.home() / "APNA_RMS_DATA")
                try:
                    os.makedirs(storage_path, exist_ok=True)
                    self.config["storage_path"] = storage_path
                    from core.config import save_config
                    save_config(self.config)
                except Exception:
                    pass

            # Trigger DatabaseManager to perform Self-Healing check and restore from Shadow Vault if folder was deleted!
            try:
                DatabaseManager.get_instance()
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

        self.next_screen = "wizard" if needs_setup else "login"

        # Robust State Machine: completely eliminates nested mainloop recursion and timer collision
        while self.next_screen:
            target = self.next_screen
            data = self.screen_data
            self.next_screen = None
            self.screen_data = None

            if target == "wizard":
                w = SetupWizard(
                    on_complete_callback=lambda: self._set_next("login"),
                    on_demo_callback=lambda u: self._set_next("main", u)
                )
                w.mainloop()
                import tkinter
                tkinter._default_root = None
            elif target == "login":
                self.config = load_config()
                try:
                    AuthManager.ensure_default_staff_roles()
                except Exception:
                    pass
                w = LoginWindow(on_login_success=lambda u: self._set_next("main", u))
                w.mainloop()
                import tkinter
                tkinter._default_root = None
            elif target == "main":
                w = MainWindow(current_user=data, on_logout_callback=lambda: self._set_next("login"))
                w.mainloop()
                import tkinter
                tkinter._default_root = None

    def _set_next(self, screen, data=None):
        self.next_screen = screen
        self.screen_data = data

if __name__ == "__main__":
    app = ApplicationController()
    app.start()
