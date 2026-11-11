import sys
import os
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import DatabaseManager
from core.auth import AuthManager
from core.config import load_config, save_config

def test_instant_demo_flow():
    print("=== Testing Instant Demo Flow From Setup Wizard ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_p = Path(temp_dir)
        db_path = temp_p / "APNA_RMS_DATA" / "apna_records.db"
        
        # 1. Initialize DB and seed demo
        db = DatabaseManager.get_instance(str(db_path))
        AuthManager.ensure_default_staff_roles()
        db.reset_to_demo_data()
        
        # 2. Verify demo user exists
        demo_user = AuthManager.get_demo_user()
        assert demo_user is not None, "Demo user must exist!"
        assert demo_user["role"] == "admin"
        print(f"Demo user verified: {demo_user['full_name']} ({demo_user['username']})")
        
        # 3. Verify metrics
        metrics = db.get_dashboard_metrics()
        print(f"Metrics: {metrics}")
        assert metrics["total_admissions"] == 10
        assert metrics["total_revenue"] == 62000.0
        assert metrics["total_due_fee"] == 7000.0
        assert metrics["due_students_count"] == 2
        
        # 4. Verify timetable seeded
        tt = db.get_timetable()
        print(f"Timetable items: {len(tt)}")
        assert len(tt) >= 4
        
        print("✅ INSTANT DEMO FLOW TEST PASSED 100%!")
        import gc
        del db
        gc.collect()

if __name__ == "__main__":
    test_instant_demo_flow()
