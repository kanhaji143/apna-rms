# -*- coding: utf-8 -*-
"""
================================================================================
APNA COMPUTER RMS — LICENSING & TRIAL MANAGEMENT UNIT TEST SUITE
================================================================================
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.database import DatabaseManager
from core.license_manager import LicenseManager, generate_license_key, MASTER_BYPASS_KEYS, VALID_DURATIONS


class TestLicensingSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager.get_instance()
        cls.lm = LicenseManager.get_instance()

    def setUp(self):
        # Reset to clean 30-day trial state before each test
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        exp_30 = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        
        self.db.set_setting("license_status", "trial")
        self.db.set_setting("license_type", "30-Day VIP Trial")
        self.db.set_setting("license_expiry_date", exp_30)
        self.db.set_setting("last_known_date", today_str)

    def tearDown(self):
        # Clean up any tampered date
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.db.set_setting("last_known_date", today_str)

    def test_01_installation_id_format(self):
        """Test installation ID is consistent and starts with ACR-."""
        install_id = self.lm.get_installation_id()
        self.assertTrue(install_id.startswith("ACR-"), f"ID must start with ACR-, got: {install_id}")
        self.assertEqual(len(install_id), 8, f"ID must be 8 characters (ACR-XXXX), got: {install_id}")

    def test_02_initial_30_day_trial(self):
        """Test default fresh state has 30 days trial and is not locked."""
        info = self.lm.get_license_info()
        self.assertEqual(info["status"], "trial")
        self.assertFalse(info["is_locked"])
        self.assertGreaterEqual(info["days_left"], 29)
        self.assertIn("30-दिवसीय VIP मुफ़्त ट्रायल", info["display_text"])

    def test_03_extension_15_days(self):
        """Test generating and activating a 15-day extension key."""
        install_id = self.lm.get_installation_id()
        key_15 = generate_license_key(install_id, 15)
        self.assertTrue(key_15.startswith("APNA-"))

        success, msg = self.lm.activate_key(key_15)
        self.assertTrue(success)
        self.assertIn("सफलतापूर्वक", msg)
        self.assertIn("15 दिन", msg)

        info = self.lm.get_license_info()
        self.assertFalse(info["is_locked"])
        # Extended from 30 days to 45 days
        self.assertGreaterEqual(info["days_left"], 44)

    def test_04_extension_10_days(self):
        """Test generating and activating a 10-day extension key."""
        install_id = self.lm.get_installation_id()
        key_10 = generate_license_key(install_id, 10)

        success, msg = self.lm.activate_key(key_10)
        self.assertTrue(success)
        self.assertIn("10 दिन", msg)

    def test_05_annual_license_activation(self):
        """Test activating a 1-year (365 days) commercial license."""
        install_id = self.lm.get_installation_id()
        key_365 = generate_license_key(install_id, 365)

        success, msg = self.lm.activate_key(key_365)
        self.assertTrue(success)

        info = self.lm.get_license_info()
        self.assertEqual(info["status"], "active")
        self.assertFalse(info["is_locked"])
        self.assertGreaterEqual(info["days_left"], 364)
        self.assertIn("अधिकृत लाइसेंस सक्रिय", info["display_text"])

    def test_06_master_bypass_keys(self):
        """Test universal vendor master code unlocks lifetime."""
        success, msg = self.lm.activate_key("APNA8504985149")
        self.assertTrue(success)
        self.assertIn("आजीवन", msg)

        info = self.lm.get_license_info()
        self.assertEqual(info["status"], "active")
        self.assertFalse(info["is_locked"])
        self.assertGreater(info["days_left"], 3000)
        self.assertIn("आजीवन लाइसेंस", info["display_text"])

    def test_07_invalid_key_rejected(self):
        """Test fraudulent or corrupted key is rejected."""
        success, msg = self.lm.activate_key("APNA-FAKE-1234-9999")
        self.assertFalse(success)
        self.assertIn("अमान्य लाइसेंस की", msg)

    def test_08_lockout_on_expiry(self):
        """Test software locks write access when trial expiry date has passed."""
        yesterday_str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        self.db.set_setting("license_expiry_date", yesterday_str)
        self.db.set_setting("last_known_date", yesterday_str)

        info = self.lm.get_license_info()
        self.assertTrue(info["is_locked"])
        self.assertEqual(info["days_left"], 0)
        self.assertIn("मुफ़्त ट्रायल समाप्त", info["display_text"])

        # Recover by activating 15-day extension key
        install_id = self.lm.get_installation_id()
        key_15 = generate_license_key(install_id, 15)
        success, _ = self.lm.activate_key(key_15)
        self.assertTrue(success)

        info_recovered = self.lm.get_license_info()
        self.assertFalse(info_recovered["is_locked"])
        self.assertGreaterEqual(info_recovered["days_left"], 14)

    def test_09_anti_clock_tampering(self):
        """Test clock tampering backwards triggers security lock."""
        # Set last_known_date to 2027-01-01 (future date)
        self.db.set_setting("last_known_date", "2027-01-01")

        info = self.lm.get_license_info()
        self.assertTrue(info["is_locked"])
        self.assertEqual(info["status"], "tampered")
        self.assertIn("सिस्टम घड़ी में गड़बड़ी", info["display_text"])


if __name__ == "__main__":
    unittest.main()
