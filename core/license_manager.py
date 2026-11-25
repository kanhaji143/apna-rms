# -*- coding: utf-8 -*-
"""
================================================================================
APNA COMPUTER RMS — ENTERPRISE OFFLINE LICENSE & TRIAL MANAGEMENT SYSTEM
Developed & Authorized for: APNA Computer (कृष्णा जी) | Helpline: 8504985149
================================================================================
Architecture:
- 100% Offline-First Hardware-Locked Cryptographic Licensing
- Auto 30-Day VIP Free Trial for all new installations
- 10-Day & 15-Day Trial Extensions for hot prospective clients
- Annual, Multi-Year & Lifetime Commercial Licenses
- Anti-Clock Tampering Engine (Tracks last_known_date)
- Universal Master Bypass Keys for Platform Owner (Krishna ji)
================================================================================
"""

import os
import sys
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger("APNA_RMS.LicenseManager")

SALT = "APNA_COMPUTER_RMS_8504985149"

# Supported valid license durations (days: display label)
VALID_DURATIONS = {
    10: "10 दिन एक्सटेंशन (Re-check Extension)",
    15: "15 दिन एक्सटेंशन (New Batch Demo Extension)",
    30: "30 दिन एक्सटेंशन (VIP Trial Extension)",
    90: "3 महीने (Quarterly License)",
    180: "6 महीने (Half-Yearly License)",
    365: "1 वर्ष (365 दिन - वार्षिक लाइसेंस)",
    730: "2 वर्ष (730 दिन)",
    1095: "3 वर्ष (1095 दिन)",
    3650: "आजीवन (Lifetime Enterprise License - 10 वर्ष)"
}

# Master Universal Bypass Keys (Direct offline activation by Krishna ji)
MASTER_BYPASS_KEYS = {
    "APNA8504985149",
    "MASTER@2026",
    "8504985149",
    "APNA-MASTER-OVERRIDE",
    "HANUGANESHAN-MASTER"
}


def _get_hardware_fingerprint() -> str:
    """Generate a consistent machine fingerprint based on MAC and ComputerName."""
    try:
        node = str(uuid.getnode())
        comp_name = os.environ.get('COMPUTERNAME', '')
        proc_id = os.environ.get('PROCESSOR_IDENTIFIER', '')
        raw = f"{node}_{comp_name}_{proc_id}_APNA_RMS"
        h = hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()
        # 4-character clean alphanumeric ID (e.g. ACR-8542)
        digits = ''.join([c for c in h if c.isdigit()])[:4]
        if len(digits) < 4:
            digits = (digits + "8504")[:4]
        return f"ACR-{digits}"
    except Exception as e:
        logger.warning(f"Error computing hardware fingerprint: {e}")
        return "ACR-8504"


def generate_license_key(installation_id: str, validity_days: int = 365) -> str:
    """
    Cryptographic key generator used by Krishna ji to generate activation & extension keys.
    Format: APNA-XXXX-XXXX-XXXX
    """
    clean_id = installation_id.strip().upper()
    raw = f"{clean_id}_{validity_days}_{SALT}"
    h = hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()
    return f"APNA-{h[:4]}-{h[4:8]}-{h[8:12]}"


class LicenseManager:
    """Enterprise offline license & trial enforcement engine for APNA Computer RMS."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        from core.database import DatabaseManager
        self.db = DatabaseManager.get_instance()
        self._init_license_settings()

    def _init_license_settings(self):
        """Initialize installation ID and 30-day VIP trial if fresh install."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 1. Ensure installation ID exists
        install_id = self.db.get_setting("installation_id")
        if not install_id:
            install_id = _get_hardware_fingerprint()
            self.db.set_setting("installation_id", install_id)
            logger.info(f"Initialized new Installation ID: {install_id}")

        # 2. Ensure initial 30-day trial is configured
        installed_date = self.db.get_setting("license_installed_date")
        if not installed_date:
            self.db.set_setting("license_installed_date", today_str)
            expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            self.db.set_setting("license_expiry_date", expiry_date)
            self.db.set_setting("license_status", "trial")
            self.db.set_setting("license_type", "30-Day VIP Trial")
            self.db.set_setting("last_known_date", today_str)
            logger.info(f"Initialized 30-Day VIP Trial expiring on {expiry_date}")

        # 3. Ensure last_known_date exists
        if not self.db.get_setting("last_known_date"):
            self.db.set_setting("last_known_date", today_str)

    def get_installation_id(self) -> str:
        """Returns the hardware-bound installation ID."""
        return self.db.get_setting("installation_id", "ACR-8504")

    def get_license_info(self) -> Dict[str, Any]:
        """
        Evaluate and return full license status, days remaining, and display badges.
        """
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        install_id = self.get_installation_id()
        status = self.db.get_setting("license_status", "trial")
        lic_type = self.db.get_setting("license_type", "30-Day VIP Trial")
        expiry_str = self.db.get_setting("license_expiry_date", today_str)
        last_known = self.db.get_setting("last_known_date", today_str)

        # Anti-Clock Tampering Check: If system clock was turned backwards
        if today_str < last_known:
            logger.warning(f"Clock tampering detected! Today: {today_str} < Last Known: {last_known}")
            return {
                "installation_id": install_id,
                "status": "tampered",
                "is_locked": True,
                "days_left": 0,
                "expiry_date": expiry_str,
                "display_text": "⚠️ सिस्टम घड़ी में गड़बड़ी (Time Tampered) - लॉक",
                "lock_title": "सुरक्षा लॉक (Security Lock - Time Tampering)",
                "lock_message": "कंप्यूटर की दिनांक में हेराफेरी पाई गई है। कृपया सिस्टम का सही दिनांक व समय सेट करें या हेल्पलाइन पर संपर्क करें।",
                "helpline": "8504985149",
                "developer": "APNA Computer (कृष्णा जी)",
                "license_type": lic_type
            }

        # Update last_known_date
        self.db.set_setting("last_known_date", today_str)

        # Calculate days left
        try:
            expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d")
            delta = (expiry_dt.date() - now.date()).days
        except Exception:
            delta = 0

        is_locked = delta < 0

        # Construct status display text
        if is_locked:
            display_text = "🔒 मुफ़्त ट्रायल समाप्त (Expired)" if status == "trial" else "🔒 लाइसेंस समाप्त (License Expired)"
            lock_title = "🔒 30-दिवसीय निःशुल्क ट्रायल समाप्त हो चुका है" if status == "trial" else "🔒 वार्षिक लाइसेंस नवीनीकरण आवश्यक है"
            lock_message = (
                "सॉफ्टवेयर में नया एडमिशन, फीस रसीद व दैनिक काम जारी रखने के लिए कृपया लाइसेंस की दर्ज करें। "
                "ट्रायल अवधि 10-15 दिन बढ़वाने अथवा वार्षिक लाइसेंस हेतु आधिकारिक हेल्पलाइन पर संपर्क करें।"
            )
        elif status == "trial":
            display_text = f"⭐ 30-दिवसीय VIP मुफ़्त ट्रायल ({delta} दिन शेष)"
            lock_title = ""
            lock_message = ""
        elif status == "trial_extended":
            display_text = f"⏳ VIP ट्रायल एक्सटेंशन ({delta} दिन शेष)"
            lock_title = ""
            lock_message = ""
        else:
            if delta > 3000:
                display_text = "⭐ अधिकृत आजीवन लाइसेंस (Lifetime Active)"
            else:
                display_text = f"⭐ अधिकृत लाइसेंस सक्रिय ({delta} दिन शेष)"
            lock_title = ""
            lock_message = ""

        return {
            "installation_id": install_id,
            "status": "expired" if is_locked else status,
            "is_locked": is_locked,
            "days_left": max(0, delta),
            "expiry_date": expiry_str,
            "display_text": display_text,
            "lock_title": lock_title,
            "lock_message": lock_message,
            "helpline": "8504985149",
            "developer": "APNA Computer (कृष्णा जी)",
            "license_type": lic_type
        }

    def activate_key(self, entered_key: str) -> Tuple[bool, str]:
        """
        Validate and activate entered license key or extension key.
        Returns: (success: bool, message: str)
        """
        clean_key = entered_key.strip().upper()
        if not clean_key:
            return False, "कृपया मान्य लाइसेंस की (License Key) दर्ज करें।"

        install_id = self.get_installation_id()
        now = datetime.now()
        today = now.date()

        # 1. Check Master Universal Bypass Keys (Immediate Lifetime 10-Year Unlock)
        if clean_key in MASTER_BYPASS_KEYS:
            new_expiry = (now + timedelta(days=3650)).strftime("%Y-%m-%d")
            self.db.set_setting("license_expiry_date", new_expiry)
            self.db.set_setting("license_status", "active")
            self.db.set_setting("license_type", "आजीवन लाइसेंस (Master Bypass Active)")
            self.db.set_setting("last_known_date", today.strftime("%Y-%m-%d"))
            self.db.log_activity(1, "System", "Super_Admin", "LICENSE_ACTIVATED", "Master Bypass Key applied. Activated for 10 Years.")
            return True, f"सॉफ्टवेयर सफलतापूर्वक सक्रिय हुआ! (आजीवन अधिकृत लाइसेंस - वैधता: 2036 तक)"

        # 2. Check Standard Duration Cryptographic Keys
        for days, label in VALID_DURATIONS.items():
            expected = generate_license_key(install_id, days)
            if clean_key == expected:
                # Calculate new expiry: extend from current expiry if not yet expired, or from today
                cur_exp_str = self.db.get_setting("license_expiry_date")
                try:
                    cur_exp = datetime.strptime(cur_exp_str, "%Y-%m-%d").date()
                    base_date = max(cur_exp, today)
                except Exception:
                    base_date = today

                new_expiry_date = base_date + timedelta(days=days)
                new_expiry_str = new_expiry_date.strftime("%Y-%m-%d")

                # Update database
                self.db.set_setting("license_expiry_date", new_expiry_str)
                self.db.set_setting("license_status", "active" if days >= 90 else "trial_extended")
                self.db.set_setting("license_type", label)
                self.db.set_setting("last_known_date", today.strftime("%Y-%m-%d"))
                
                # Log audit
                self.db.log_activity(1, "System", "Super_Admin", "LICENSE_ACTIVATED", f"Activated: {label} (Key: {clean_key[:8]}...) until {new_expiry_str}")
                
                formatted_date = new_expiry_date.strftime("%d-%m-%Y")
                return True, f"लाइसेंस सफलतापूर्वक सक्रिय हुआ!\n\nवैधता: {formatted_date} तक ({label})"

        return False, "अमान्य लाइसेंस की (Invalid Key)! कृपया हेल्पलाइन 8504985149 पर संपर्क करें।"
