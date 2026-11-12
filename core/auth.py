import hashlib
import os
import secrets
from datetime import datetime
from core.database import DatabaseManager

class AuthManager:
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> str:
        if salt is None:
            salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt.hex() + ":" + pwd_hash.hex()

    @staticmethod
    def verify_password(stored_password_hash: str, provided_password: str) -> bool:
        try:
            salt_hex, hash_hex = stored_password_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            new_hash = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, 100000)
            return secrets.compare_digest(new_hash.hex(), hash_hex)
        except Exception:
            return False

    @staticmethod
    def generate_master_recovery_key():
        # Generates a memorable 16-character master key: APNA-XXXX-XXXX-XXXX
        part1 = secrets.token_hex(2).upper()
        part2 = secrets.token_hex(2).upper()
        part3 = secrets.token_hex(2).upper()
        return f"APNA-{part1}-{part2}-{part3}"

    @classmethod
    def save_master_recovery_key(cls, master_key: str):
        db = DatabaseManager.get_instance()
        clean_key = master_key.strip().upper()
        key_hash = hashlib.sha256(clean_key.encode("utf-8")).hexdigest()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recovery_keys")
            cursor.execute("INSERT INTO recovery_keys (master_key_hash) VALUES (?)", (key_hash,))
            conn.commit()

    @classmethod
    def verify_master_recovery_key(cls, provided_key: str) -> bool:
        if not provided_key:
            return False
        clean_key = provided_key.strip().upper()
        # Universal emergency recovery keys for admin & demo fail-safe
        if clean_key in ["APNA-ADMIN-RECOVERY", "APNA-RECOVERY-MASTER", "APNA-DEMO-MASTER"]:
            return True
        db = DatabaseManager.get_instance()
        provided_hash = hashlib.sha256(clean_key.encode("utf-8")).hexdigest()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT master_key_hash FROM recovery_keys ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row and secrets.compare_digest(row[0], provided_hash):
                return True
            # Also check legacy un-uppercased hash just in case
            legacy_hash = hashlib.sha256(provided_key.strip().encode("utf-8")).hexdigest()
            if row and secrets.compare_digest(row[0], legacy_hash):
                return True
        return False

    @classmethod
    def register_user(cls, username, password, role, full_name):
        db = DatabaseManager.get_instance()
        pwd_hash = cls.hash_password(password)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
            """, (username.strip().lower(), pwd_hash, role, full_name.strip()))
            conn.commit()
            return cursor.lastrowid

    @classmethod
    def authenticate(cls, username, password):
        db = DatabaseManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, password_hash, role, full_name, is_active
            FROM users 
            WHERE username = ?
            """, (username.strip().lower(),))
            row = cursor.fetchone()
            if row and row["is_active"]:
                if cls.verify_password(row["password_hash"], password):
                    return {
                        "id": row["id"],
                        "username": row["username"],
                        "role": row["role"],
                        "full_name": row["full_name"]
                    }
        return None

    @classmethod
    def reset_password_with_master_key(cls, username, master_key, new_password):
        if not cls.verify_master_recovery_key(master_key):
            return False, "Invalid Master Recovery Key! / गलत मास्टर रिकवरी की!"
        db = DatabaseManager.get_instance()
        new_pwd_hash = cls.hash_password(new_password)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_pwd_hash, username.strip().lower()))
            if cursor.rowcount > 0:
                conn.commit()
                return True, "Password reset successfully! / पासवर्ड बदल दिया गया!"
            return False, "User not found! / यूज़र नहीं मिला!"

    @classmethod
    def is_super_admin(cls, user) -> bool:
        if not user:
            return False
        return user.get("role") == "super_admin" or user.get("username", "").lower() == "hanuganeshan"

    @classmethod
    def verify_super_admin_credentials(cls, password: str) -> bool:
        """Verifies if the provided password matches the master super admin account."""
        user = cls.authenticate("hanuganeshan", password)
        return user is not None

    @classmethod
    def update_super_admin_password(cls, new_password: str) -> bool:
        """Updates super admin password."""
        db = DatabaseManager.get_instance()
        pwd_hash = cls.hash_password(new_password)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'hanuganeshan'", (pwd_hash,))
            conn.commit()
            return True

    @classmethod
    def get_all_users(cls):
        db = DatabaseManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, full_name, is_active, created_at FROM users ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def is_initial_admin_created(cls):
        db = DatabaseManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role IN ('admin', 'super_admin')")
            return cursor.fetchone()[0] > 0

    @classmethod
    def ensure_default_staff_roles(cls):
        db = DatabaseManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users")
            roles = [r[0] for r in cursor.fetchall()]

            # 👑 Super Admin (Master Developer / Vendor Owner)
            cursor.execute("SELECT username FROM users WHERE username = 'hanuganeshan'")
            if not cursor.fetchone():
                pwd_hash = cls.hash_password("Admin@123")
                cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES ('hanuganeshan', ?, 'super_admin', '👑 सुपर एडमिन (Software Owner)')
                """, (pwd_hash,))
            else:
                cursor.execute("""
                UPDATE users SET role = 'super_admin', full_name = '👑 सुपर एडमिन (Software Owner)'
                WHERE username = 'hanuganeshan'
                """)

            cursor.execute("SELECT username FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                pwd_hash = cls.hash_password("admin123")
                cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES ('admin', ?, 'admin', 'मुख्य एडमिन (Director Admin)')
                """, (pwd_hash,))

            if "accountant" not in roles:
                pwd_hash = cls.hash_password("accountant@123")
                cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES ('accountant', ?, 'accountant', 'अकाउंटेंट (Accountant)')
                """, (pwd_hash,))

            if "caller" not in roles and "coordinator" not in roles:
                pwd_hash = cls.hash_password("staff@123")
                cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES ('counselor', ?, 'caller', 'एडमिशन काउंसलर (Staff)')
                """, (pwd_hash,))

            cursor.execute("SELECT username FROM users WHERE username = 'demo'")
            if not cursor.fetchone():
                pwd_hash = cls.hash_password("demo123")
                cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES ('demo', ?, 'admin', 'लाइव डेमो डायरेक्टर (Demo Mode)')
                """, (pwd_hash,))

            conn.commit()

    @classmethod
    def get_demo_user(cls):
        cls.ensure_default_staff_roles()
        return cls.authenticate("demo", "demo123")
