import sys
import os
import customtkinter as ctk

# Initialize CTk root hidden
app = ctk.CTk()
app.withdraw()

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import DatabaseManager
from core.auth import AuthManager
from core.config import load_config
import ui.views.dashboard_view as dv
import ui.views.admission_view as av
import ui.views.records_view as rv
import ui.views.activation_view as actv
import ui.views.timetable_view as tv
import ui.views.staff_view as sv
import ui.views.expenses_view as ev
import ui.views.reports_view as repv
import ui.views.settings_view as setv
from ui.components.header import AppHeader
from ui.components.sidebar import AppSidebar
from ui.login_window import LoginWindow

print("Imports successful!")

DatabaseManager.get_instance().init_database()
AuthManager.ensure_default_staff_roles()

roles = [
    {"username": "hanuganeshan", "role": "super_admin", "full_name": "Hanu Ganeshan"},
    {"username": "admin", "role": "admin", "full_name": "Founder"},
    {"username": "counselor", "role": "counselor", "full_name": "Counselor"},
    {"username": "accountant", "role": "accountant", "full_name": "Accountant"},
    {"username": "demo", "role": "admin", "is_demo": True, "full_name": "Live Demo Director"}
]

parent = ctk.CTkFrame(app)

for r in roles:
    uname = r["username"]
    role = r["role"]
    print(f"Testing role: {uname} ({role})")
    
    # Test Header
    h = AppHeader(parent, current_user=r, on_theme_change=lambda x: None, on_lang_change=lambda x: None, on_logout=lambda: None)
    h.destroy()
    
    # Test Sidebar
    s = AppSidebar(parent, current_user=r, on_nav_select=lambda x: None)
    s.destroy()
    
    # Test all views
    views = [
        ("dashboard", dv.DashboardView(parent, r, on_navigate=lambda x: None)),
        ("admission", av.AdmissionView(parent, r)),
        ("records", rv.RecordsView(parent, r)),
        ("activations", actv.ActivationView(parent, r)),
        ("timetable", tv.TimetableView(parent, r)),
        ("staff", sv.StaffView(parent, r)),
        ("expenses", ev.ExpensesView(parent, r)),
        ("reports", repv.ReportsView(parent, r)),
        ("settings", setv.SettingsView(parent, r))
    ]
    for vname, v in views:
        if hasattr(v, "load_records"): v.load_records()
        if hasattr(v, "load_staff_data"): v.load_staff_data()
        if hasattr(v, "load_queue"): v.load_queue()
        if hasattr(v, "load_expenses"): v.load_expenses()
        if hasattr(v, "load_schedule"): v.load_schedule()
        v.destroy()

print("ALL 9 VIEWS ACROSS ALL 5 ROLES TESTED SUCCESSFULLY!")

# Test Login Window
lw = LoginWindow(on_login_success=lambda u: None)
# Check placeholders
assert lw.user_entry.get() == "", f"user_entry not empty: {lw.user_entry.get()}"
assert lw.pass_entry.get() == "", f"pass_entry not empty: {lw.pass_entry.get()}"
lw.destroy()
print("Login window placeholders verified!")

# Test Auth Manager
assert AuthManager.verify_super_admin_credentials("Admin@123") == True
assert AuthManager.authenticate("hanuganeshan", "Admin@123") is not None
assert AuthManager.authenticate("admin", "admin123") is not None
assert AuthManager.authenticate("counselor", "staff@123") is not None
assert AuthManager.authenticate("accountant", "accountant@123") is not None
print("Auth Manager role credentials verified!")

app.destroy()
print("=== ALL SYSTEM AUDITS PASSED 100% ===")
