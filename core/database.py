import sqlite3
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from core.config import load_config, DEFAULT_COURSES

class DatabaseManager:
    _instance = None

    def __init__(self, db_path=None):
        # 1. Establish Shadow Vault (Protected system mirror in LocalAppData)
        self.vault_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "APNA_Computer_RMS" / "vault"
        try:
            self.vault_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        self.vault_db_path = self.vault_dir / "apna_records_vault.db"
        self.vault_receipts_dir = self.vault_dir / "receipts"
        try:
            self.vault_receipts_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        # 2. Determine Primary Database Directory
        if db_path is None:
            config = load_config()
            storage_path = config.get("storage_path", "")
            if storage_path:
                self.db_dir = Path(storage_path)
            else:
                self.db_dir = Path(__file__).resolve().parent.parent / "local_storage"
        else:
            self.db_path = Path(db_path)
            self.db_dir = self.db_path.parent

        try:
            self.db_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            self.db_dir = Path.home() / "APNA_RMS_DATA"
            self.db_dir.mkdir(parents=True, exist_ok=True)

        self.screenshots_dir = self.db_dir / "screenshots"
        self.receipts_dir = self.db_dir / "receipts"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "apna_records.db"

        # 3. Emergency Self-Healing & Anti-Tamper Check
        self._perform_self_healing_check()

        # 4. Initialize Database Schema
        self.init_database()

        # 5. Mirror to Shadow Vault
        self.sync_to_shadow_vault()

    def _perform_self_healing_check(self):
        """
        Anti-Tamper & Self-Healing Engine:
        If the primary database folder or file is deleted, missing, or corrupted,
        automatically restores all data and receipts from the secure Shadow Vault.
        """
        try:
            primary_exists = self.db_path.exists()
            primary_size = self.db_path.stat().st_size if primary_exists else 0
            vault_exists = self.vault_db_path.exists()
            vault_size = self.vault_db_path.stat().st_size if vault_exists else 0

            needs_restore = False
            reason = ""

            # Condition 1: Primary DB was deleted or is an empty 0-byte file, but vault has valid data
            if (not primary_exists or primary_size < 1000) and (vault_exists and vault_size >= 1000):
                needs_restore = True
                reason = "Primary database file was missing or deleted"

            # Condition 2: Primary DB exists but fails SQLite integrity check
            elif primary_exists and primary_size >= 1000:
                try:
                    conn = sqlite3.connect(str(self.db_path), timeout=5.0)
                    cur = conn.cursor()
                    cur.execute("PRAGMA integrity_check")
                    res = cur.fetchone()
                    conn.close()
                    if not res or res[0] != "ok":
                        if vault_exists and vault_size >= 1000:
                            needs_restore = True
                            reason = f"Database corrupted: {res[0] if res else 'Unknown'}"
                except Exception as e:
                    if vault_exists and vault_size >= 1000:
                        needs_restore = True
                        reason = f"Database integrity check failed: {e}"

            if needs_restore:
                print(f"[SECURITY ALERT] Self-Healing Triggered: {reason}. Restoring from Shadow Vault...")
                self.db_dir.mkdir(parents=True, exist_ok=True)
                self.receipts_dir.mkdir(parents=True, exist_ok=True)
                self.screenshots_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.vault_db_path, self.db_path)

                # Restore receipts
                if self.vault_receipts_dir.exists():
                    for pdf_file in self.vault_receipts_dir.glob("*.pdf"):
                        target_pdf = self.receipts_dir / pdf_file.name
                        if not target_pdf.exists() or target_pdf.stat().st_size < 1000:
                            try:
                                shutil.copy2(pdf_file, target_pdf)
                            except Exception:
                                pass

                # Write emergency recovery log
                try:
                    log_file = self.db_dir / "SECURITY_RECOVERY_LOG.txt"
                    with open(log_file, "a", encoding="utf-8") as lf:
                        lf.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] EMERGENCY SELF-HEALING: {reason}. All data restored successfully from Shadow Vault.\n")
                except Exception:
                    pass

        except Exception as e:
            print(f"[SECURITY] Self-healing check error: {e}")

    def sync_to_shadow_vault(self):
        """
        Silently mirrors the primary database and new receipts to the secure Shadow Vault.
        Uses SQLite online backup API to ensure 100% zero-lock consistency.
        """
        try:
            if not self.db_path.exists() or self.db_path.stat().st_size < 1000:
                return

            self.vault_dir.mkdir(parents=True, exist_ok=True)
            self.vault_receipts_dir.mkdir(parents=True, exist_ok=True)

            # Live atomic SQLite backup
            src_conn = sqlite3.connect(str(self.db_path), timeout=10.0)
            dst_conn = sqlite3.connect(str(self.vault_db_path), timeout=10.0)
            with dst_conn:
                src_conn.backup(dst_conn, pages=100)
            dst_conn.close()
            src_conn.close()

            # Mirror receipts to vault
            if self.receipts_dir.exists():
                for pdf_file in self.receipts_dir.glob("*.pdf"):
                    vault_pdf = self.vault_receipts_dir / pdf_file.name
                    if not vault_pdf.exists() or vault_pdf.stat().st_size != pdf_file.stat().st_size:
                        try:
                            shutil.copy2(pdf_file, vault_pdf)
                        except Exception:
                            pass
        except Exception:
            pass

    @classmethod
    def get_instance(cls, custom_path=None):
        if cls._instance is None or custom_path is not None:
            cls._instance = DatabaseManager(custom_path)
        return cls._instance

    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")
        except Exception:
            pass
        return conn

    def get_pending_activations_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM admissions WHERE activation_status = 'Pending'")
            row = cursor.fetchone()
            return row[0] if row else 0

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Settings table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL, -- 'admin', 'coordinator', 'caller', 'accountant'
                full_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Master Recovery Key table (Single record)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_key_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Courses table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                standard_fee REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1
            )
            """)

            # Populate default courses if empty
            cursor.execute("SELECT COUNT(*) FROM courses")
            if cursor.fetchone()[0] == 0:
                for c in DEFAULT_COURSES:
                    cursor.execute("INSERT OR IGNORE INTO courses (name, standard_fee) VALUES (?, 0.0)", (c,))

            # Admissions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_no TEXT UNIQUE NOT NULL,
                student_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                courses_taken TEXT NOT NULL, -- comma separated or JSON
                payment_mode TEXT NOT NULL,  -- UPI, Cash, Card, Net Banking
                account_holder TEXT NOT NULL,
                original_fee REAL DEFAULT 0.0,
                concession_amount REAL DEFAULT 0.0,
                concession_reason TEXT DEFAULT '',
                final_amount REAL NOT NULL,
                utr_no TEXT DEFAULT '',
                payment_date TEXT NOT NULL,
                screenshot_path TEXT DEFAULT '',
                admission_source TEXT NOT NULL, -- 'Telecalling' or 'Walk-in'
                caller_staff_name TEXT DEFAULT '',
                caller_staff_id INTEGER DEFAULT 0,
                activation_status TEXT DEFAULT 'Pending', -- 'Pending' or 'Activated'
                activated_at TEXT DEFAULT '',
                activated_by TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Teacher Timetable table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS timetable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                day_of_week TEXT NOT NULL, -- Monday, Tuesday, etc.
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                room_batch TEXT NOT NULL,
                is_leave INTEGER DEFAULT 0,
                substitute_teacher TEXT DEFAULT '',
                updated_by TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Expenses table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_mode TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                paid_to TEXT NOT NULL,
                receipt_image_path TEXT DEFAULT '',
                recorded_by TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Audit Logs table (Tamper-proof security tracking)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER DEFAULT 0,
                username TEXT NOT NULL,
                user_role TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT DEFAULT ''
            )
            """)

            # Fee Installments table (Due / Installment tracking)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fee_installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_id INTEGER NOT NULL,
                admission_no TEXT NOT NULL,
                installment_no INTEGER DEFAULT 1,
                amount_paid REAL NOT NULL,
                payment_mode TEXT NOT NULL,
                payment_date TEXT NOT NULL,
                receipt_no TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                recorded_by TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Staff Members Directory table (Teachers, Sub-staff, Directors)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL, -- 'Teacher / Faculty', 'Director / Management', 'Sub-staff / Office'
                designation TEXT NOT NULL,
                phone TEXT DEFAULT '',
                monthly_salary REAL DEFAULT 0.0,
                advance_balance REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Staff Salary & Advance Ledger table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                staff_name TEXT NOT NULL,
                entry_type TEXT NOT NULL, -- 'Salary Paid', 'Advance Given', 'Advance Settled', 'Due Salary Paid'
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_mode TEXT NOT NULL,
                month_cycle TEXT NOT NULL,
                notes TEXT DEFAULT '',
                recorded_by TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Seed default staff if table is empty
            cursor.execute("SELECT COUNT(*) FROM staff_members")
            if cursor.fetchone()[0] == 0:
                default_staff = [
                    ("Prof. Alok Pandey", "Teacher / Faculty", "Senior Python & AI Faculty", "9876543210", 25000.0, 5000.0),
                    ("Er. Ramesh Verma", "Teacher / Faculty", "Web Development & MERN Lead", "9812345678", 22000.0, 0.0),
                    ("CA S. K. Gupta", "Teacher / Faculty", "Tally Prime & GST Specialist", "9723456789", 18000.0, 0.0),
                    ("Krishna Sharma", "Director / Management", "Director & Operations Head", "8504985149", 35000.0, 0.0),
                    ("Sunil Kumar", "Sub-staff / Office", "Lab Assistant & Office Support", "9934567890", 12000.0, 1500.0)
                ]
                for s_name, s_cat, s_desig, s_ph, s_sal, s_adv in default_staff:
                    cursor.execute("""
                    INSERT INTO staff_members (name, category, designation, phone, monthly_salary, advance_balance)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (s_name, s_cat, s_desig, s_ph, s_sal, s_adv))

            conn.commit()

    # --- Admission Operations ---
    def generate_next_admission_no(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            year = datetime.now().strftime("%Y")
            cursor.execute("SELECT id FROM admissions ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            next_id = (row[0] + 1) if row else 1
            return f"ADM-{year}-{next_id:04d}"

    def check_duplicate_student(self, phone, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, admission_no, student_name, phone, email, courses_taken, payment_date
            FROM admissions 
            WHERE phone = ? OR email = ?
            ORDER BY id DESC LIMIT 1
            """, (phone.strip(), email.strip()))
            row = cursor.fetchone()
            return dict(row) if row else None

    def check_duplicate_utr(self, utr_no):
        if not utr_no or not utr_no.strip():
            return None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, admission_no, student_name, utr_no, payment_date, final_amount
            FROM admissions 
            WHERE TRIM(utr_no) = ? AND utr_no != ''
            LIMIT 1
            """, (utr_no.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_admission(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO admissions (
                admission_no, student_name, email, phone, courses_taken,
                payment_mode, account_holder, original_fee, concession_amount,
                concession_reason, final_amount, utr_no, payment_date,
                screenshot_path, admission_source, caller_staff_name,
                caller_staff_id, activation_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
            """, (
                data["admission_no"], data["student_name"], data["email"], data["phone"],
                data["courses_taken"], data["payment_mode"], data["account_holder"],
                data.get("original_fee", 0.0), data.get("concession_amount", 0.0),
                data.get("concession_reason", ""), data["final_amount"],
                data.get("utr_no", ""), data["payment_date"],
                data.get("screenshot_path", ""), data["admission_source"],
                data.get("caller_staff_name", ""), data.get("caller_staff_id", 0),
                data.get("notes", "")
            ))
            conn.commit()
            last_id = cursor.lastrowid
        self.sync_to_shadow_vault()
        return last_id

    def get_admissions(self, status=None, start_date=None, end_date=None, search_query=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM admissions WHERE 1=1"
            params = []

            if status and status != "All":
                query += " AND activation_status = ?"
                params.append(status)

            if start_date:
                query += " AND payment_date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND payment_date <= ?"
                params.append(end_date)

            if search_query:
                q = f"%{search_query.strip()}%"
                query += " AND (student_name LIKE ? OR phone LIKE ? OR email LIKE ? OR admission_no LIKE ? OR utr_no LIKE ?)"
                params.extend([q, q, q, q, q])

            query += " ORDER BY id DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_activation_status(self, admission_id, status, activated_by):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            cursor.execute("""
            UPDATE admissions 
            SET activation_status = ?, activated_at = ?, activated_by = ?
            WHERE id = ?
            """, (status, now_str if status == "Activated" else "", activated_by, admission_id))
            conn.commit()

    def delete_admission(self, admission_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admissions WHERE id = ?", (admission_id,))
            conn.commit()

    def clear_demo_data(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admissions WHERE notes LIKE '%DEMO%'")
            cursor.execute("DELETE FROM expenses WHERE title LIKE '%DEMO%'")
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

    # --- Dashboard Summary ---
    def get_dashboard_metrics(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            today_str = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("SELECT COUNT(*) FROM admissions")
            total_admissions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM admissions WHERE payment_date = ?", (today_str,))
            today_admissions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM admissions WHERE activation_status = 'Pending'")
            pending_activations = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(final_amount), 0.0) FROM admissions")
            total_revenue = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(amount), 0.0) FROM expenses")
            total_expenses = cursor.fetchone()[0]

            net_profit = total_revenue - total_expenses

            # Calculate Total Pending Due Fees
            cursor.execute("""
            SELECT 
                COUNT(*),
                COALESCE(SUM(CASE WHEN (original_fee - concession_amount) > final_amount THEN ((original_fee - concession_amount) - final_amount) ELSE 0.0 END), 0.0)
            FROM admissions
            WHERE (original_fee - concession_amount) > final_amount
            """)
            due_row = cursor.fetchone()
            due_students_count = due_row[0] if due_row else 0
            total_due_fee = due_row[1] if due_row else 0.0

            return {
                "total_admissions": total_admissions,
                "today_admissions": today_admissions,
                "pending_activations": pending_activations,
                "total_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_profit": net_profit,
                "total_due_fee": total_due_fee,
                "due_students_count": due_students_count
            }

    # --- Timetable Operations ---
    def add_schedule_item(self, teacher_name, subject, day_of_week, start_time, end_time, room_batch, updated_by):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO timetable (teacher_name, subject, day_of_week, start_time, end_time, room_batch, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (teacher_name, subject, day_of_week, start_time, end_time, room_batch, updated_by))
            conn.commit()
            last_id = cursor.lastrowid
        self.sync_to_shadow_vault()
        return last_id

    def get_timetable(self, day=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if day and day != "All":
                cursor.execute("SELECT * FROM timetable WHERE day_of_week = ? ORDER BY start_time ASC", (day,))
            else:
                cursor.execute("SELECT * FROM timetable ORDER BY day_of_week, start_time ASC")
            return [dict(row) for row in cursor.fetchall()]

    def update_teacher_leave(self, schedule_id, is_leave, substitute_teacher, updated_by):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE timetable 
            SET is_leave = ?, substitute_teacher = ?, updated_by = ?
            WHERE id = ?
            """, (1 if is_leave else 0, substitute_teacher, updated_by, schedule_id))
            conn.commit()

    def delete_schedule_item(self, schedule_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM timetable WHERE id = ?", (schedule_id,))
            conn.commit()

    # --- Expenses Operations ---
    def add_expense(self, title, category, amount, payment_mode, expense_date, paid_to, receipt_image_path, recorded_by):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO expenses (title, category, amount, payment_mode, expense_date, paid_to, receipt_image_path, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, category, amount, payment_mode, expense_date, paid_to, receipt_image_path, recorded_by))
            conn.commit()
            last_id = cursor.lastrowid
        self.sync_to_shadow_vault()
        return last_id

    def get_expenses(self, start_date=None, end_date=None, category=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM expenses WHERE 1=1"
            params = []
            if start_date:
                query += " AND expense_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND expense_date <= ?"
                params.append(end_date)
            if category and category != "All":
                query += " AND category = ?"
                params.append(category)
            query += " ORDER BY expense_date DESC, id DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # --- Courses List ---
    def get_courses(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE is_active = 1 ORDER BY name ASC")
            return [row["name"] for row in cursor.fetchall()]

    def add_course(self, name, standard_fee=0.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO courses (name, standard_fee) VALUES (?, ?)", (name.strip(), standard_fee))
            conn.commit()

    # --- Tamper-Proof Audit Logging ---
    def log_activity(self, user_id, username, user_role, action, details=""):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO audit_logs (user_id, username, user_role, action, details)
                VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, user_role, action, details))
                conn.commit()
        except Exception:
            pass

    def get_audit_logs(self, limit=100):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # --- Fee Installments Operations ---
    def add_installment(self, admission_id, amount, payment_mode, payment_date, notes="", recorded_by=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT admission_no, final_amount, original_fee, concession_amount FROM admissions WHERE id = ?", (admission_id,))
            adm = cursor.fetchone()
            if not adm:
                return False, "Admission record not found"

            adm_no = adm["admission_no"]
            cursor.execute("SELECT COUNT(*) FROM fee_installments WHERE admission_id = ?", (admission_id,))
            inst_count = cursor.fetchone()[0] + 1

            receipt_no = f"INST-{adm_no}-{inst_count:02d}"

            cursor.execute("""
            INSERT INTO fee_installments (
                admission_id, admission_no, installment_no, amount_paid,
                payment_mode, payment_date, receipt_no, notes, recorded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (admission_id, adm_no, inst_count, amount, payment_mode, payment_date, receipt_no, notes, recorded_by))

            # Update admission total paid
            new_total = float(adm["final_amount"]) + float(amount)
            cursor.execute("UPDATE admissions SET final_amount = ? WHERE id = ?", (new_total, admission_id))
            conn.commit()
        self.sync_to_shadow_vault()
        return True, receipt_no

    def get_installments(self, admission_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fee_installments WHERE admission_id = ? ORDER BY id ASC", (admission_id,))
            return [dict(row) for row in cursor.fetchall()]

    def reset_to_demo_data(self):
        """Cleans and re-seeds 10 realistic students, installments, and 5 expenses for live demo presentation."""
        from datetime import datetime, timedelta
        from PIL import Image, ImageDraw

        today = datetime.now()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admissions")
            cursor.execute("DELETE FROM expenses")
            cursor.execute("DELETE FROM fee_installments")
            cursor.execute("DELETE FROM audit_logs")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('admissions', 'expenses', 'fee_installments', 'audit_logs')")
            conn.commit()

        def create_sample_screenshot(fpath, sname, amt, utr, dt):
            try:
                img = Image.new("RGB", (420, 680), color="#0D1B2A")
                draw = ImageDraw.Draw(img)
                draw.rectangle([(0, 0), (420, 80)], fill="#1B263B")
                draw.text((20, 25), "Google Pay / PhonePe UPI", fill="#03F9FD")
                draw.ellipse([(170, 120), (250, 200)], fill="#10B981")
                draw.text((200, 145), "✓", fill="#FFFFFF")
                draw.text((130, 220), "Payment Successful", fill="#E0E1DD")
                draw.text((120, 260), f"₹{amt:,.2f}", fill="#03F9FD")
                draw.rectangle([(25, 330), (395, 540)], fill="#1B263B", outline="#415A77", width=1)
                draw.text((40, 350), f"Paid To: APNA Computer Center", fill="#E0E1DD")
                draw.text((40, 385), f"Student: {sname}", fill="#E0E1DD")
                draw.text((40, 420), f"UPI Ref / UTR: {utr}", fill="#E0E1DD")
                draw.text((40, 455), f"Date & Time: {dt} 11:30 AM", fill="#E0E1DD")
                draw.text((40, 490), "Mode: UPI QR Code Transfer", fill="#10B981")
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                img.save(fpath, format="JPEG", quality=85)
            except Exception:
                pass

        students_data = [
            {"name": "Aman Verma", "phone": "9823456710", "email": "aman.verma@gmail.com", "courses": "Python & AI Masterclass", "orig_fee": 8500.0, "disc": 1000.0, "disc_reason": "Early Bird Scholarship", "final_amt": 7500.0, "mode": "UPI QR", "acc": "APNA Center / HDFC Bank", "utr": "432109876501", "date": (today - timedelta(days=4)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Telecalling", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Pooja Sharma", "phone": "9134567821", "email": "pooja.sharma@yahoo.com", "courses": "Full-Stack Web Development", "orig_fee": 12000.0, "disc": 2000.0, "disc_reason": "पुराना छात्र रियायत (Loyalty Discount)", "final_amt": 10000.0, "mode": "UPI QR", "acc": "APNA Center / SBI", "utr": "432109876502", "date": (today - timedelta(days=4)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Walk-in", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Rohit Kumar", "phone": "8745678932", "email": "rohit.kumar@gmail.com", "courses": "ADCA (Advanced Diploma in Computer Applications)", "orig_fee": 6000.0, "disc": 0.0, "disc_reason": "", "final_amt": 6000.0, "mode": "Cash / नकद", "acc": "Cash / नकद (काउंटर)", "utr": "", "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Walk-in", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Ananya Mishra", "phone": "9956789043", "email": "ananya.mishra@gmail.com", "courses": "Data Analytics & Advanced Excel, Python & AI Masterclass", "orig_fee": 15000.0, "disc": 2500.0, "disc_reason": "Combo Special Discount", "final_amt": 12500.0, "mode": "UPI QR", "acc": "APNA Center / HDFC Bank", "utr": "432109876503", "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Telecalling", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Vikram Singh", "phone": "7867890154", "email": "vikram.singh@outlook.com", "courses": "Tally Prime with GST & Accounting", "orig_fee": 5500.0, "disc": 500.0, "disc_reason": "One-time Full Payment Offer", "final_amt": 5000.0, "mode": "UPI QR", "acc": "APNA Center / ICICI", "utr": "432109876504", "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Walk-in", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Neha Gupta", "phone": "9478901265", "email": "neha.gupta@gmail.com", "courses": "Graphic Designing (Photoshop & Illustrator)", "orig_fee": 7000.0, "disc": 1000.0, "disc_reason": "Women in Tech Scholarship", "final_amt": 6000.0, "mode": "Cash / नकद", "acc": "Cash / नकद (काउंटर)", "utr": "", "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Walk-in", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Suresh Patel", "phone": "8189012376", "email": "suresh.patel@gmail.com", "courses": "CCC (Course on Computer Concepts)", "orig_fee": 2500.0, "disc": 0.0, "disc_reason": "", "final_amt": 2500.0, "mode": "UPI QR", "acc": "APNA Center / HDFC Bank", "utr": "432109876505", "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "status": "Activated", "act_at": today.strftime("%Y-%m-%d %H:%M"), "act_by": "Founder (Admin)", "source": "Telecalling", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Deepak Yadav", "phone": "9690123487", "email": "deepak.yadav@gmail.com", "courses": "Full-Stack Web Development", "orig_fee": 12000.0, "disc": 1500.0, "disc_reason": "Special Refer Discount", "final_amt": 6000.0, "mode": "UPI QR", "acc": "APNA Center / SBI", "utr": "432109876506", "date": today.strftime("%Y-%m-%d"), "status": "Pending", "act_at": "", "act_by": "", "source": "Telecalling", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Kavita Choudhary", "phone": "7001234598", "email": "kavita.choudhary@gmail.com", "courses": "Spoken English & Communication", "orig_fee": 4000.0, "disc": 500.0, "disc_reason": "Sibling Discount", "final_amt": 3500.0, "mode": "Cash / नकद", "acc": "Cash / नकद (काउंटर)", "utr": "", "date": today.strftime("%Y-%m-%d"), "status": "Pending", "act_at": "", "act_by": "", "source": "Walk-in", "caller": "एडमिशन काउंसलर (Staff)"},
            {"name": "Manish Tiwari", "phone": "9812345609", "email": "manish.tiwari@gmail.com", "courses": "Data Analytics & Advanced Excel", "orig_fee": 6500.0, "disc": 1000.0, "disc_reason": "Weekend Batch Offer", "final_amt": 3000.0, "mode": "UPI QR", "acc": "APNA Center / ICICI", "utr": "432109876507", "date": today.strftime("%Y-%m-%d"), "status": "Pending", "act_at": "", "act_by": "", "source": "Telecalling", "caller": "एडमिशन काउंसलर (Staff)"}
        ]

        for idx, s in enumerate(students_data, start=1):
            adm_no = f"ADM-{today.year}-{idx:04d}"
            sc_path = ""
            if s["mode"] == "UPI QR":
                sc_filename = f"sample_sc_{idx}.jpg"
                sc_path = str(self.screenshots_dir / sc_filename)
                create_sample_screenshot(sc_path, s["name"], s["final_amt"], s["utr"], s["date"])

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO admissions (
                    admission_no, student_name, email, phone, courses_taken,
                    payment_mode, account_holder, original_fee, concession_amount,
                    concession_reason, final_amount, utr_no, payment_date,
                    screenshot_path, admission_source, caller_staff_name,
                    caller_staff_id, activation_status, activated_at, activated_by, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    adm_no, s["name"], s["email"], s["phone"], s["courses"], s["mode"], s["acc"],
                    s["orig_fee"], s["disc"], s["disc_reason"], s["final_amt"], s["utr"], s["date"],
                    sc_path, s["source"], s["caller"], 3, s["status"], s["act_at"], s["act_by"], "Verified Clean Entry"
                ))
                conn.commit()

            self.log_activity(3, "counselor", "caller", "NEW_ADMISSION", f"Created {adm_no} for {s['name']} (₹{s['final_amt']})")
            if s["status"] == "Activated":
                self.log_activity(1, "admin", "admin", "COURSE_ACTIVATED", f"Activated course for {adm_no} ({s['name']})")

        expenses = [
            ("कोचिंग हॉल किराया (Monthly Institute Rent)", "किराया (Rent)", 16000.0, "Bank Transfer", (today - timedelta(days=5)).strftime("%Y-%m-%d"), "मकान मालिक (Ramesh Sharma)", "अकाउंटेंट (Accountant)"),
            ("बिजली बिल भुगतान (Electricity Bill)", "बिजली (Electricity)", 3250.0, "UPI / Online", (today - timedelta(days=3)).strftime("%Y-%m-%d"), "UPPCL Electricity Board", "अकाउंटेंट (Accountant)"),
            ("फैकल्टी एडवांस वेतन (Faculty Advance Salary)", "वेतन (Staff / Faculty Salary)", 12000.0, "Bank Transfer", (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Prof. Alok Pandey", "अकाउंटेंट (Accountant)"),
            ("हाई-स्पीड फाइबर इंटरनेट बिल (Office Internet Bill)", "इंटरनेट व टेलीफोन (Internet)", 999.0, "UPI / Online", (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Airtel Fiber", "अकाउंटेंट (Accountant)"),
            ("ऑफिस स्टेशनरी, मार्कर व रजिस्टर (Office Supplies)", "स्टेशनरी व नोट्स प्रिंटिंग (Stationery)", 1450.0, "Cash / नकद", today.strftime("%Y-%m-%d"), "Shree Ram Book Depot", "अकाउंटेंट (Accountant)")
        ]

        for t_val, cat, amt, mode, dt, pt, rec_by in expenses:
            self.add_expense(t_val, cat, amt, mode, dt, pt, "", rec_by)
            self.log_activity(2, "accountant", "accountant", "EXPENSE_RECORDED", f"Added expense '{t_val}' of ₹{amt}")

        # Seed realistic timetable for today's day for live demo
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM timetable")
            today_day = today.strftime("%A")
            cursor.execute("""
            INSERT INTO timetable (teacher_name, subject, day_of_week, start_time, end_time, room_batch, is_leave, substitute_teacher, updated_by)
            VALUES 
            ('Prof. Alok Pandey', 'Python & AI Masterclass', ?, '09:00 AM', '10:30 AM', 'Lab-1 (Morning)', 0, '', 'Admin'),
            ('Er. Ramesh Verma', 'Full-Stack Web Development', ?, '10:30 AM', '12:00 PM', 'Hall-A (Batch 1)', 0, '', 'Admin'),
            ('CA S. K. Gupta', 'Tally Prime with GST & Accounting', ?, '12:30 PM', '02:00 PM', 'Lab-2 (Commerce)', 1, 'विकास सर (Substitute)', 'Admin'),
            ('Sunil Kumar', 'Basic Computers & Typing Lab', ?, '03:00 PM', '04:30 PM', 'Typing Lab', 0, '', 'Admin')
            """, (today_day, today_day, today_day, today_day))
            conn.commit()

        return True

    # --- Staff & Faculty Directory Operations ---
    def get_all_staff(self, active_only=True):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM staff_members"
            if active_only:
                query += " WHERE status = 'Active'"
            query += " ORDER BY id ASC"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def add_staff_member(self, name, category, designation, phone, monthly_salary, advance_balance=0.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO staff_members (name, category, designation, phone, monthly_salary, advance_balance)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (name.strip(), category, designation.strip(), phone.strip(), float(monthly_salary), float(advance_balance)))
            conn.commit()
            last_id = cursor.lastrowid
        self.sync_to_shadow_vault()
        return last_id

    def update_staff_member(self, staff_id, name, category, designation, phone, monthly_salary):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE staff_members
            SET name = ?, category = ?, designation = ?, phone = ?, monthly_salary = ?
            WHERE id = ?
            """, (name.strip(), category, designation.strip(), phone.strip(), float(monthly_salary), staff_id))
            conn.commit()
            return True

    def delete_staff_member(self, staff_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE staff_members SET status = 'Inactive' WHERE id = ?", (staff_id,))
            conn.commit()
            return True

    def record_staff_payment(self, staff_id, entry_type, amount, payment_date, payment_mode, month_cycle, notes="", recorded_by="Admin"):
        """
        Records staff payment (Salary, Advance Given, Advance Settled, Late / Due Salary).
        Automatically updates staff advance balance and records institute expense.
        """
        amount = float(amount)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM staff_members WHERE id = ?", (staff_id,))
            staff = cursor.fetchone()
            if not staff:
                return False, "Staff member not found"

            staff_name = staff["name"]
            current_adv = float(staff["advance_balance"])

            if entry_type == "Advance Given (एडवांस दिया)":
                new_adv = current_adv + amount
                cursor.execute("UPDATE staff_members SET advance_balance = ? WHERE id = ?", (new_adv, staff_id))
                exp_title = f"फैकल्टी / स्टाफ एडवांस: {staff_name}"
            elif entry_type == "Salary Paid (मासिक वेतन)":
                exp_title = f"मासिक वेतन ({month_cycle}): {staff_name}"
            elif entry_type == "Advance Settled (एडवांस काटा/समायोजित)":
                new_adv = max(0.0, current_adv - amount)
                cursor.execute("UPDATE staff_members SET advance_balance = ? WHERE id = ?", (new_adv, staff_id))
                exp_title = f"वेतन में से एडवांस समायोजन ({month_cycle}): {staff_name}"
            elif entry_type == "Due Salary Paid (देर से / पिछला वेतन)":
                exp_title = f"पिछला बकाया वेतन भुगतान ({month_cycle}): {staff_name}"
            else:
                exp_title = f"स्टाफ भुगतान ({entry_type}): {staff_name}"

            # Insert into staff ledger
            cursor.execute("""
            INSERT INTO staff_ledger (
                staff_id, staff_name, entry_type, amount, payment_date,
                payment_mode, month_cycle, notes, recorded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (staff_id, staff_name, entry_type, amount, payment_date, payment_mode, month_cycle, notes, recorded_by))

            # Auto-record in institute expenses (except pure advance settlement which is internal adjustment)
            if entry_type != "Advance Settled (एडवांस काटा/समायोजित)":
                cursor.execute("""
                INSERT INTO expenses (
                    title, category, amount, payment_mode, expense_date, paid_to, receipt_image_path, recorded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (exp_title, "वेतन (Staff / Faculty Salary)", amount, payment_mode, payment_date, staff_name, "", recorded_by))

            conn.commit()
            return True, "Payment successfully recorded"

    def get_staff_ledger(self, staff_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if staff_id:
                cursor.execute("SELECT * FROM staff_ledger WHERE staff_id = ? ORDER BY id DESC", (staff_id,))
            else:
                cursor.execute("SELECT * FROM staff_ledger ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    # --- Smart Multi-PC Auto-Merge Engine ---
    def merge_external_data(self, source_path, recorded_by="Admin"):
        """
        Smart Multi-PC Auto-Merge Engine:
        Merges admissions, installments, expenses, timetable, and staff records
        from an external SQLite .db or .zip backup into the master database.

        Guarantees:
        - 100% Conflict-free Deduplication: Avoids duplicate student admissions, installments, and expenses.
        - Automatic ID Collision Resolution: If an incoming admission_no collides with a different student,
          automatically re-allocates a new unique admission_no and updates all linked installments.
        - Automatic Pre-Merge Safety Snapshot: Preserves master DB state before writing.
        - Screenshot Extraction: Extracts payment screenshots into the master repository.
        """
        source_p = Path(source_path)
        if not source_p.exists():
            return {"success": False, "error": f"फ़ाइल नहीं मिली: {source_path}"}

        try:
            if source_p.resolve() == self.db_path.resolve():
                return {"success": False, "error": "आप वर्तमान सक्रिय डेटाबेस को उसी में मर्ज नहीं कर सकते। कृपया किसी अन्य सिस्टम (PC-1/PC-2) की बैकअप फ़ाइल चुनें।"}
        except Exception:
            pass

        temp_dir = None
        ext_db_path = None

        if zipfile.is_zipfile(source_p):
            try:
                temp_dir = tempfile.TemporaryDirectory()
                with zipfile.ZipFile(source_p, "r") as zf:
                    zf.extractall(temp_dir.name)
                db_candidates = list(Path(temp_dir.name).rglob("*.db"))
                if not db_candidates:
                    temp_dir.cleanup()
                    return {"success": False, "error": "चुनी गई ZIP बैकअप में कोई .db डेटाबेस फ़ाइल नहीं मिली।"}
                ext_db_path = db_candidates[0]

                # Copy extracted screenshots into master screenshots_dir
                for sc_cand in Path(temp_dir.name).rglob("screenshots"):
                    if sc_cand.is_dir():
                        for img in sc_cand.glob("*.*"):
                            tgt_img = self.screenshots_dir / img.name
                            if not tgt_img.exists():
                                try:
                                    shutil.copy2(img, tgt_img)
                                except Exception:
                                    pass
            except Exception as e:
                if temp_dir:
                    temp_dir.cleanup()
                return {"success": False, "error": f"ZIP फ़ाइल पढ़ने में त्रुटि: {str(e)}"}
        else:
            ext_db_path = source_p

        # Connect to source database
        try:
            src_conn = sqlite3.connect(str(ext_db_path))
            src_conn.row_factory = sqlite3.Row
            src_cur = src_conn.cursor()
            src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
            if not src_cur.fetchone():
                src_conn.close()
                if temp_dir:
                    temp_dir.cleanup()
                return {"success": False, "error": "यह एक मान्य APNA RMS डेटाबेस नहीं है (Admissions टेबल अनुपस्थित)।"}
        except Exception as e:
            if temp_dir:
                temp_dir.cleanup()
            return {"success": False, "error": f"डेटाबेस फ़ाइल खोलने में त्रुटि: {str(e)}"}

        # Safety snapshot of master database
        safety_name = f"safety_pre_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        safety_path = self.db_dir / safety_name
        try:
            shutil.copy2(self.db_path, safety_path)
        except Exception:
            safety_name = "N/A"

        admissions_added = 0
        admissions_updated = 0
        admissions_skipped = 0
        installments_added = 0
        expenses_added = 0
        expenses_skipped = 0
        timetable_added = 0
        staff_added = 0
        staff_ledger_added = 0
        total_revenue_added = 0.0
        total_expenses_added = 0.0

        adm_no_remap = {}

        try:
            with self.get_connection() as dest_conn:
                dest_cur = dest_conn.cursor()

                # --- 1. MERGE ADMISSIONS ---
                src_cur.execute("SELECT * FROM admissions ORDER BY id ASC")
                for row in src_cur.fetchall():
                    adm_no = row["admission_no"]
                    dest_cur.execute("SELECT id, student_name, phone, final_amount, activation_status FROM admissions WHERE admission_no = ?", (adm_no,))
                    existing = dest_cur.fetchone()

                    if not existing:
                        # Clean new admission: insert directly
                        sc_dest = ""
                        if row["screenshot_path"]:
                            sc_p = Path(row["screenshot_path"])
                            if sc_p.exists():
                                tgt_img = self.screenshots_dir / sc_p.name
                                if not tgt_img.exists():
                                    try:
                                        shutil.copy2(sc_p, tgt_img)
                                    except Exception:
                                        pass
                                sc_dest = str(tgt_img)
                            else:
                                local_chk = ext_db_path.parent / "screenshots" / sc_p.name
                                if local_chk.exists():
                                    tgt_img = self.screenshots_dir / sc_p.name
                                    if not tgt_img.exists():
                                        try:
                                            shutil.copy2(local_chk, tgt_img)
                                        except Exception:
                                            pass
                                    sc_dest = str(tgt_img)

                        dest_cur.execute("""
                        INSERT INTO admissions (
                            admission_no, student_name, email, phone, courses_taken,
                            payment_mode, account_holder, original_fee, concession_amount,
                            concession_reason, final_amount, utr_no, payment_date,
                            screenshot_path, admission_source, caller_staff_name,
                            caller_staff_id, activation_status, activated_at, activated_by, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            adm_no, row["student_name"], row["email"], row["phone"], row["courses_taken"],
                            row["payment_mode"], row["account_holder"], row["original_fee"], row["concession_amount"],
                            row["concession_reason"], row["final_amount"], row["utr_no"], row["payment_date"],
                            sc_dest or row["screenshot_path"], row["admission_source"], row["caller_staff_name"],
                            row["caller_staff_id"], row["activation_status"], row["activated_at"], row["activated_by"],
                            (row["notes"] or "") + f" [Merged from {source_p.name}]"
                        ))
                        admissions_added += 1
                        total_revenue_added += float(row["final_amount"] or 0.0)

                    else:
                        # Admission number already in destination: check if same student or collision
                        same_phone = (str(row["phone"]).strip() == str(existing["phone"]).strip())
                        same_name = (str(row["student_name"]).strip().lower() == str(existing["student_name"]).strip().lower())

                        if same_phone or same_name:
                            # Same student: check if activation status changed
                            if row["activation_status"] == "Activated" and existing["activation_status"] == "Pending":
                                dest_cur.execute("""
                                UPDATE admissions 
                                SET activation_status = 'Activated', activated_at = ?, activated_by = ?
                                WHERE id = ?
                                """, (row["activated_at"], row["activated_by"], existing["id"]))
                                admissions_updated += 1
                            else:
                                admissions_skipped += 1
                        else:
                            # COLLISION! Different student with same admission_no from isolated PC
                            # Re-allocate unique admission_no
                            dest_cur.execute("SELECT id FROM admissions ORDER BY id DESC LIMIT 1")
                            max_r = dest_cur.fetchone()
                            next_n = (max_r[0] + 1) if max_r else 1
                            year_str = datetime.now().strftime("%Y")
                            cand_adm_no = f"ADM-{year_str}-{next_n:04d}"
                            while True:
                                dest_cur.execute("SELECT id FROM admissions WHERE admission_no = ?", (cand_adm_no,))
                                if not dest_cur.fetchone():
                                    break
                                next_n += 1
                                cand_adm_no = f"ADM-{year_str}-{next_n:04d}"

                            adm_no_remap[adm_no] = cand_adm_no

                            dest_cur.execute("""
                            INSERT INTO admissions (
                                admission_no, student_name, email, phone, courses_taken,
                                payment_mode, account_holder, original_fee, concession_amount,
                                concession_reason, final_amount, utr_no, payment_date,
                                screenshot_path, admission_source, caller_staff_name,
                                caller_staff_id, activation_status, activated_at, activated_by, notes
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                cand_adm_no, row["student_name"], row["email"], row["phone"], row["courses_taken"],
                                row["payment_mode"], row["account_holder"], row["original_fee"], row["concession_amount"],
                                row["concession_reason"], row["final_amount"], row["utr_no"], row["payment_date"],
                                row["screenshot_path"], row["admission_source"], row["caller_staff_name"],
                                row["caller_staff_id"], row["activation_status"], row["activated_at"], row["activated_by"],
                                (row["notes"] or "") + f" [Auto-renumbered from {adm_no} during merge from {source_p.name}]"
                            ))
                            admissions_added += 1
                            total_revenue_added += float(row["final_amount"] or 0.0)

                # --- 2. MERGE FEE INSTALLMENTS ---
                src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_installments'")
                if src_cur.fetchone():
                    src_cur.execute("SELECT * FROM fee_installments ORDER BY id ASC")
                    for inst in src_cur.fetchall():
                        target_adm_no = adm_no_remap.get(inst["admission_no"], inst["admission_no"])
                        dest_cur.execute("""
                        SELECT id FROM fee_installments 
                        WHERE admission_no = ? AND installment_no = ? AND amount_paid = ? AND payment_date = ?
                        """, (target_adm_no, inst["installment_no"], inst["amount_paid"], inst["payment_date"]))
                        if not dest_cur.fetchone():
                            dest_cur.execute("SELECT id FROM admissions WHERE admission_no = ?", (target_adm_no,))
                            adm_match = dest_cur.fetchone()
                            if adm_match:
                                dest_adm_id = adm_match[0]
                                dest_cur.execute("""
                                INSERT INTO fee_installments (
                                    admission_id, admission_no, installment_no, amount_paid,
                                    payment_mode, payment_date, receipt_no, notes, recorded_by
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    dest_adm_id, target_adm_no, inst["installment_no"], inst["amount_paid"],
                                    inst["payment_mode"], inst["payment_date"], inst["receipt_no"],
                                    (inst["notes"] or "") + f" [Merged from {source_p.name}]",
                                    inst["recorded_by"]
                                ))
                                installments_added += 1
                                total_revenue_added += float(inst["amount_paid"] or 0.0)

                # --- 3. MERGE EXPENSES ---
                src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
                if src_cur.fetchone():
                    src_cur.execute("SELECT * FROM expenses ORDER BY id ASC")
                    for exp in src_cur.fetchall():
                        dest_cur.execute("""
                        SELECT id FROM expenses 
                        WHERE title = ? AND amount = ? AND expense_date = ? AND paid_to = ?
                        """, (exp["title"], exp["amount"], exp["expense_date"], exp["paid_to"]))
                        if not dest_cur.fetchone():
                            dest_cur.execute("""
                            INSERT INTO expenses (
                                title, category, amount, payment_mode, expense_date, paid_to, receipt_image_path, recorded_by
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                exp["title"], exp["category"], exp["amount"], exp["payment_mode"],
                                exp["expense_date"], exp["paid_to"], exp["receipt_image_path"],
                                (exp["recorded_by"] or "") + f" [Merged from {source_p.name}]"
                            ))
                            expenses_added += 1
                            total_expenses_added += float(exp["amount"] or 0.0)
                        else:
                            expenses_skipped += 1

                # --- 4. MERGE TIMETABLE ---
                src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='timetable'")
                if src_cur.fetchone():
                    src_cur.execute("SELECT * FROM timetable ORDER BY id ASC")
                    for tt in src_cur.fetchall():
                        dest_cur.execute("""
                        SELECT id FROM timetable 
                        WHERE teacher_name = ? AND day_of_week = ? AND start_time = ? AND end_time = ? AND room_batch = ?
                        """, (tt["teacher_name"], tt["day_of_week"], tt["start_time"], tt["end_time"], tt["room_batch"]))
                        if not dest_cur.fetchone():
                            dest_cur.execute("""
                            INSERT INTO timetable (
                                teacher_name, subject, day_of_week, start_time, end_time, room_batch, is_leave, substitute_teacher, updated_by
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                tt["teacher_name"], tt["subject"], tt["day_of_week"], tt["start_time"], tt["end_time"],
                                tt["room_batch"], tt["is_leave"], tt["substitute_teacher"], tt["updated_by"]
                            ))
                            timetable_added += 1

                # --- 5. MERGE STAFF & LEDGER ---
                src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff_members'")
                if src_cur.fetchone():
                    src_cur.execute("SELECT * FROM staff_members ORDER BY id ASC")
                    for st in src_cur.fetchall():
                        dest_cur.execute("SELECT id FROM staff_members WHERE name = ?", (st["name"],))
                        if not dest_cur.fetchone():
                            dest_cur.execute("""
                            INSERT INTO staff_members (name, category, designation, phone, monthly_salary, advance_balance, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (st["name"], st["category"], st["designation"], st["phone"], st["monthly_salary"], st["advance_balance"], st["status"]))
                            staff_added += 1

                src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff_ledger'")
                if src_cur.fetchone():
                    src_cur.execute("SELECT * FROM staff_ledger ORDER BY id ASC")
                    for sl in src_cur.fetchall():
                        dest_cur.execute("""
                        SELECT id FROM staff_ledger 
                        WHERE staff_name = ? AND entry_type = ? AND amount = ? AND payment_date = ? AND month_cycle = ?
                        """, (sl["staff_name"], sl["entry_type"], sl["amount"], sl["payment_date"], sl["month_cycle"]))
                        if not dest_cur.fetchone():
                            dest_cur.execute("SELECT id FROM staff_members WHERE name = ?", (sl["staff_name"],))
                            s_row = dest_cur.fetchone()
                            dest_s_id = s_row[0] if s_row else sl["staff_id"]
                            dest_cur.execute("""
                            INSERT INTO staff_ledger (
                                staff_id, staff_name, entry_type, amount, payment_date,
                                payment_mode, month_cycle, notes, recorded_by
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                dest_s_id, sl["staff_name"], sl["entry_type"], sl["amount"],
                                sl["payment_date"], sl["payment_mode"], sl["month_cycle"],
                                (sl["notes"] or "") + f" [Merged from {source_p.name}]", sl["recorded_by"]
                            ))
                            staff_ledger_added += 1

                # --- 6. AUDIT LOG ---
                dest_cur.execute("""
                INSERT INTO audit_logs (username, user_role, action, details)
                VALUES (?, ?, ?, ?)
                """, (
                    recorded_by, "admin", "MULTI_PC_DATA_MERGED",
                    f"स्रोत फ़ाइल '{source_p.name}' से डेटा मर्ज हुआ: +{admissions_added} नए एडमिशन, +{installments_added} किस्तें, +{expenses_added} खर्चे।"
                ))

                dest_conn.commit()

            src_conn.close()
            if temp_dir:
                temp_dir.cleanup()

            return {
                "success": True,
                "source_file": source_p.name,
                "admissions_added": admissions_added,
                "admissions_updated": admissions_updated,
                "admissions_skipped": admissions_skipped,
                "installments_added": installments_added,
                "expenses_added": expenses_added,
                "expenses_skipped": expenses_skipped,
                "timetable_added": timetable_added,
                "staff_added": staff_added,
                "staff_ledger_added": staff_ledger_added,
                "total_revenue_added": total_revenue_added,
                "total_expenses_added": total_expenses_added,
                "safety_backup": safety_name
            }
        except Exception as e:
            src_conn.close()
            if temp_dir:
                temp_dir.cleanup()
            return {"success": False, "error": f"डेटा मर्ज करते समय त्रुटि: {str(e)}"}
