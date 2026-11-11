import sys
import os
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import DatabaseManager

def test_multi_pc_merge():
    print("=== Testing Smart Multi-PC Auto-Merge Engine ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_p = Path(temp_dir)
        
        # 1. Create Master DB
        master_db_path = temp_p / "master" / "apna_records.db"
        master_db_path.parent.mkdir(parents=True, exist_ok=True)
        master_db = DatabaseManager(master_db_path)
        
        # Add 1 initial student to master
        adm1 = master_db.add_admission({
            "admission_no": "ADM-2026-0001",
            "student_name": "Master Student 1",
            "email": "student1@gmail.com",
            "phone": "9800000001",
            "courses_taken": "Python & AI",
            "payment_mode": "UPI QR",
            "account_holder": "APNA Center",
            "original_fee": 5000.0,
            "concession_amount": 0.0,
            "concession_reason": "",
            "final_amount": 5000.0,
            "utr_no": "111122223333",
            "payment_date": "2026-11-01",
            "screenshot_path": "",
            "admission_source": "Walk-in",
            "caller_staff_name": "Counselor",
            "caller_staff_id": 1,
            "activation_status": "Activated",
            "notes": "Original"
        })
        print(f"Master DB created with 1 admission (id: {adm1})")

        # 2. Create PC-1 DB (e.g. Reception Desk)
        pc1_db_path = temp_p / "pc1" / "apna_records.db"
        pc1_db_path.parent.mkdir(parents=True, exist_ok=True)
        pc1_db = DatabaseManager(pc1_db_path)
        
        # PC-1 has a duplicate of student1 (same phone/name)
        pc1_db.add_admission({
            "admission_no": "ADM-2026-0001",
            "student_name": "Master Student 1",
            "email": "student1@gmail.com",
            "phone": "9800000001",
            "courses_taken": "Python & AI",
            "payment_mode": "UPI QR",
            "account_holder": "APNA Center",
            "original_fee": 5000.0,
            "concession_amount": 0.0,
            "concession_reason": "",
            "final_amount": 5000.0,
            "utr_no": "111122223333",
            "payment_date": "2026-11-01",
            "screenshot_path": "",
            "admission_source": "Walk-in",
            "caller_staff_name": "Counselor",
            "caller_staff_id": 1,
            "activation_status": "Activated",
            "notes": "PC1 Record"
        })

        # PC-1 has a NEW student (ADM-2026-0002)
        pc1_db.add_admission({
            "admission_no": "ADM-2026-0002",
            "student_name": "PC1 New Student",
            "email": "pc1@gmail.com",
            "phone": "9800000002",
            "courses_taken": "Full-Stack Web Dev",
            "payment_mode": "Cash / नकद",
            "account_holder": "Cash Counter",
            "original_fee": 10000.0,
            "concession_amount": 1000.0,
            "concession_reason": "Special Offer",
            "final_amount": 9000.0,
            "utr_no": "",
            "payment_date": "2026-11-10",
            "screenshot_path": "",
            "admission_source": "Walk-in",
            "caller_staff_name": "Counselor",
            "caller_staff_id": 1,
            "activation_status": "Pending",
            "notes": "PC1 New"
        })

        # PC-1 recorded an expense
        pc1_db.add_expense("Water Dispenser Refill", "कार्यालय खर्च", 250.0, "Cash", "2026-11-10", "Water Supplier", "", "Counselor")

        # 3. Create PC-2 DB (e.g. Isolated PC with ID collision)
        pc2_db_path = temp_p / "pc2" / "apna_records.db"
        pc2_db_path.parent.mkdir(parents=True, exist_ok=True)
        pc2_db = DatabaseManager(pc2_db_path)

        # PC-2 also generated ADM-2026-0002 independently, but for a DIFFERENT student!
        pc2_db.add_admission({
            "admission_no": "ADM-2026-0002",
            "student_name": "PC2 Conflicting Student",
            "email": "pc2@gmail.com",
            "phone": "9800000099", # DIFFERENT phone
            "courses_taken": "Data Analytics",
            "payment_mode": "UPI QR",
            "account_holder": "APNA Center",
            "original_fee": 6000.0,
            "concession_amount": 0.0,
            "concession_reason": "",
            "final_amount": 6000.0,
            "utr_no": "999988887777",
            "payment_date": "2026-11-10",
            "screenshot_path": "",
            "admission_source": "Telecalling",
            "caller_staff_name": "Caller 2",
            "caller_staff_id": 2,
            "activation_status": "Pending",
            "notes": "PC2 Independent Entry"
        })

        # Package PC-2 as a ZIP backup archive
        zip_p2 = temp_p / "PC2_EOD_Backup.zip"
        with zipfile.ZipFile(zip_p2, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(pc2_db_path, arcname="apna_records.db")

        # 4. Now perform Merge into Master DB!
        print("\n--- Merging PC-1 (.db) into Master ---")
        res1 = master_db.merge_external_data(pc1_db_path, recorded_by="Owner")
        print("Result 1:", res1)
        assert res1["success"] is True
        assert res1["admissions_added"] == 1  # ADM-2026-0002 added
        assert res1["admissions_skipped"] == 1 # ADM-2026-0001 recognized as duplicate & skipped
        assert res1["expenses_added"] == 1
        assert res1["total_revenue_added"] == 9000.0

        print("\n--- Merging PC-2 (.zip with Collision) into Master ---")
        res2 = master_db.merge_external_data(zip_p2, recorded_by="Owner")
        print("Result 2:", res2)
        assert res2["success"] is True
        assert res2["admissions_added"] == 1 # Conflicting student added with auto-renumbered ID!
        assert res2["total_revenue_added"] == 6000.0

        # Check total admissions in master
        all_master_admissions = master_db.get_admissions()
        print(f"\nTotal admissions in Master now: {len(all_master_admissions)}")
        for a in all_master_admissions:
            print(f" - [{a['admission_no']}] {a['student_name']} ({a['phone']}) - ₹{a['final_amount']}")

        assert len(all_master_admissions) == 3
        # Verify collision was resolved to a unique ID (e.g. ADM-2026-0003 or next)
        adm_nos = [a["admission_no"] for a in all_master_admissions]
        assert len(set(adm_nos)) == 3, "All admission numbers in master must be unique!"

        # 5. Idempotency test: Re-merging same PC-1 again should add 0 new admissions
        print("\n--- Re-merging PC-1 again (Duplicate Test) ---")
        res3 = master_db.merge_external_data(pc1_db_path, recorded_by="Owner")
        print("Result 3:", res3)
        assert res3["admissions_added"] == 0
        assert res3["expenses_added"] == 0
        assert res3["admissions_skipped"] >= 1
        print("Idempotency test PASSED: 0 duplicate records created!")

        print("\n✅ ALL MULTI-PC AUTO-MERGE TESTS PASSED 100%!")
        import gc
        del master_db, pc1_db, pc2_db
        gc.collect()

if __name__ == "__main__":
    test_multi_pc_merge()
