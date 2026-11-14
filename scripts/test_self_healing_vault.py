import os
import sys
import sqlite3
import shutil
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import DatabaseManager

def test_self_healing():
    print("=" * 60)
    print("TEST: Self-Healing Shadow Vault & Anti-Tamper Engine")
    print("=" * 60)

    # 1. Initialize DB
    print("\n[Step 1] Initializing DatabaseManager...")
    db = DatabaseManager.get_instance()
    print(f"  Primary DB Path: {db.db_path}")
    print(f"  Shadow Vault Dir: {db.vault_dir}")
    print(f"  Shadow Vault DB: {db.vault_db_path}")
    
    assert db.vault_dir.exists(), "Vault dir should exist!"
    assert db.vault_db_path.exists(), "Vault DB should exist after init!"
    print("  PASS: Shadow Vault initialized and synced.")

    # 2. Add a test admission
    import time
    test_adm_no = f"ADM-VAULT-{int(time.time())}"
    print(f"\n[Step 2] Inserting test admission '{test_adm_no}'...")
    test_data = {
        "admission_no": test_adm_no,
        "student_name": "सुरक्षा परीक्षण छात्र (Vault Test)",
        "email": "vault.test@apna.com",
        "phone": "9998887776",
        "courses_taken": "CCC, Python Master",
        "payment_mode": "Cash",
        "account_holder": "APNA Cash",
        "original_fee": 5000.0,
        "concession_amount": 500.0,
        "concession_reason": "Security Test",
        "final_amount": 4500.0,
        "payment_date": "2026-11-14",
        "admission_source": "Direct"
    }
    db.add_admission(test_data)
    
    # 3. Verify sync to vault
    print("\n[Step 3] Verifying sync to Shadow Vault...")
    v_conn = sqlite3.connect(str(db.vault_db_path))
    v_cur = v_conn.cursor()
    v_cur.execute("SELECT student_name, final_amount FROM admissions WHERE admission_no = ?", (test_adm_no,))
    v_row = v_cur.fetchone()
    v_conn.close()
    
    assert v_row is not None, "Test admission must be present in Shadow Vault!"
    print(f"  PASS: Record verified in Shadow Vault -> {v_row[0]} | Rs. {v_row[1]}")

    # 4. Create a test receipt in primary receipts_dir and sync
    test_receipt = db.receipts_dir / f"Receipt_{test_adm_no}.pdf"
    with open(test_receipt, "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 Mock Receipt for Security Test")
    db.sync_to_shadow_vault()
    
    vault_receipt = db.vault_receipts_dir / f"Receipt_{test_adm_no}.pdf"
    assert vault_receipt.exists(), "Receipt must be mirrored to vault!"
    print(f"  PASS: Receipt mirrored to Shadow Vault -> {vault_receipt.name}")

    # 5. SIMULATE MALICIOUS DELETION!
    print("\n[Step 4] SIMULATING ACCIDENTAL / MALICIOUS DELETION!")
    db_path_to_delete = db.db_path
    print(f"  DELETING primary database: {db_path_to_delete}...")
    # Close connections first
    DatabaseManager._instance = None
    del db
    import gc, time
    gc.collect()
    time.sleep(0.5)
    if db_path_to_delete.exists():
        os.remove(db_path_to_delete)
    if test_receipt.exists():
        os.remove(test_receipt)

    assert not db_path_to_delete.exists(), "Primary DB must be deleted for test!"
    assert not test_receipt.exists(), "Primary receipt must be deleted for test!"
    print("  CONFIRMED: Primary database and receipt have been completely DELETED.")

    # 6. TRIGGER SELF-HEALING (App restart)
    print("\n[Step 5] Triggering Self-Healing Recovery on App Restart...")
    new_db = DatabaseManager.get_instance()
    
    # 7. VERIFY RESTORATION
    assert new_db.db_path.exists(), "Self-healing must restore primary DB!"
    assert new_db.db_path.stat().st_size > 1000, "Restored DB must not be empty!"
    assert test_receipt.exists(), "Self-healing must restore missing receipts!"

    # Check restored data in primary DB
    r_conn = new_db.get_connection()
    r_cur = r_conn.cursor()
    r_cur.execute("SELECT student_name, final_amount FROM admissions WHERE admission_no = ?", (test_adm_no,))
    r_row = r_cur.fetchone()
    
    assert r_row is not None, "Student data must be 100% recovered!"
    print(f"  PASS: Student data recovered successfully -> {r_row['student_name']} | Rs. {r_row['final_amount']}")

    # Check security recovery log
    log_file = new_db.db_dir / "SECURITY_RECOVERY_LOG.txt"
    assert log_file.exists(), "Recovery log must be written!"
    with open(log_file, "r", encoding="utf-8") as lf:
        log_content = lf.read()
    print(f"  PASS: Security Audit Log recorded:\n    {log_content.strip()}")

    # 8. Clean up test record
    print("\n[Step 6] Cleaning up test records...")
    r_cur.execute("DELETE FROM admissions WHERE admission_no = ?", (test_adm_no,))
    r_conn.commit()
    r_conn.close()
    if test_receipt.exists():
        os.remove(test_receipt)
    if vault_receipt.exists():
        os.remove(vault_receipt)
    new_db.sync_to_shadow_vault()

    print("\n" + "=" * 60)
    print("SUCCESS: 100% Self-Healing & Anti-Tamper Engine VERIFIED!")
    print("=" * 60)

if __name__ == "__main__":
    test_self_healing()
