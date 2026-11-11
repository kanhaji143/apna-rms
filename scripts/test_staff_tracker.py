import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import DatabaseManager

def test_staff():
    print("Testing Staff & Faculty Directory...")
    db = DatabaseManager.get_instance()
    staff = db.get_all_staff()
    print(f"Total staff members: {len(staff)}")
    for s in staff:
        print(f"ID={s['id']} | {s['name']} ({s['category']}) - {s['designation']} | Sal: ₹{s['monthly_salary']} | Adv: ₹{s['advance_balance']}")

    # Test giving advance
    target = staff[0]
    print(f"\nTesting giving advance of ₹2,000 to {target['name']}...")
    success, msg = db.record_staff_payment(
        target['id'], "Advance Given (एडवांस दिया)", 2000.0,
        "2026-11-10", "Bank Transfer", "Advance", "Test Festival Advance", "Admin"
    )
    print("Record payment result:", success, msg)
    assert success

    updated_staff = db.get_all_staff()
    u_target = [s for s in updated_staff if s['id'] == target['id']][0]
    print(f"Updated advance balance for {u_target['name']}: ₹{u_target['advance_balance']}")
    assert u_target['advance_balance'] == target['advance_balance'] + 2000.0

    # Test Ledger
    ledger = db.get_staff_ledger(target['id'])
    print(f"Ledger entries for {target['name']}: {len(ledger)}")
    assert len(ledger) > 0

    print("✅ STAFF & ADVANCE TRACKER VERIFIED 100%!")

if __name__ == "__main__":
    test_staff()
