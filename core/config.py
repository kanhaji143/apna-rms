import os
import json
from pathlib import Path

APP_NAME = "APNA Computer RMS"
APP_FULL_NAME = "अपना कंप्यूटर रिकॉर्ड मैनेजमेंट सॉफ्टवेयर (Apna Computer Record Management Software)"
APP_VERSION = "1.0.0"

# Brand Colors sampled directly from Logo.png
COLOR_CYAN = "#03F9FD"          # Electric Brand Cyan / Neon Teal
COLOR_CYAN_HOVER = "#00D2D6"    # Darker Cyan for button hover
COLOR_NAVY_DARK = "#001026"     # Deep Midnight Navy (Dark mode background)
COLOR_NAVY_SURFACE = "#00183A"  # Midnight Navy Card / Surface
COLOR_NAVY_CARD = "#06224D"     # Elevated Card / Input background
COLOR_NAVY_BORDER = "#0B3673"   # Elegant border color

# Light Mode Palette
COLOR_LIGHT_BG = "#F4F7FC"       # Clean Ice White/Blue Background
COLOR_LIGHT_SURFACE = "#FFFFFF"  # Pure White Cards
COLOR_LIGHT_CARD = "#EBF1FA"     # Subtle card background
COLOR_LIGHT_BORDER = "#CFDCF0"   # Light border
COLOR_TEXT_DARK = "#001633"      # High contrast dark text for light theme
COLOR_TEXT_LIGHT = "#E2F1FF"     # High contrast light text for dark theme

# Status Colors
COLOR_SUCCESS = "#10B981"        # Emerald Green (Activated)
COLOR_WARNING = "#F59E0B"        # Amber Warning (Duplicate / UTR alert)
COLOR_DANGER = "#EF4444"         # Red Flag (Pending Activation)
COLOR_INFO = "#0284C7"           # Informational Blue

# Default Config File (lives next to the app executable/script)
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "app_config.json"

DEFAULT_COURSES = [
    "DCA (Diploma in Computer Applications)",
    "ADCA (Advanced Diploma in Computer Applications)",
    "CCC (Course on Computer Concepts)",
    "Python & AI Masterclass",
    "Full-Stack Web Development",
    "Spoken English & Communication",
    "Tally Prime with GST & Accounting",
    "Graphic Designing (Photoshop & Illustrator)",
    "Data Analytics & Advanced Excel",
    "SSC & Competitive Exams Foundation"
]

DEFAULT_EXPENSE_CATEGORIES = [
    "👨‍🏫 Teacher Salary / मानदेय",
    "🏢 Rent / सेंटर किराया",
    "⚡ Electricity, Water & Internet / बिजली बिल",
    "📢 Marketing & Online Ads / विज्ञापन",
    "🖨️ Books, Notes & Stationery / प्रिंटिंग",
    "☕ Tea, Refreshment & Office Misc / मेंटेनेंस",
    "💻 Software, Hardware & Lab Equipment / लैब"
]

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "is_setup_completed": False,
        "storage_path": "",
        "institute_name": "APNA COMPUTER",
        "institute_tagline": "कंप्यूटर और कौशल प्रशिक्षण संस्थान",
        "institute_phone": "",
        "institute_email": "",
        "institute_address": "",
        "logo_path": str(BASE_DIR / "Logo.png"),
        "theme": "dark",
        "language": "hi",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_email": "",
        "smtp_password": "",
        "admin_backup_email": "",
        "youtube_link": "",
        "instagram_link": "",
        "telegram_link": ""
    }

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
