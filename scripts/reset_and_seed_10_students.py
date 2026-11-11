import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import DatabaseManager

def create_sample_upi_screenshot(filepath, student_name, amount, utr_no, date_str):
    img = Image.new("RGB", (420, 680), color="#0D1B2A")
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (420, 80)], fill="#1B263B")
    draw.text((20, 25), "Google Pay / PhonePe UPI", fill="#03F9FD")
    
    # Success Circle
    draw.ellipse([(170, 120), (250, 200)], fill="#10B981")
    draw.text((200, 145), "✓", fill="#FFFFFF")
    
    draw.text((130, 220), "Payment Successful", fill="#E0E1DD")
    draw.text((120, 260), f"₹{amount:,.2f}", fill="#03F9FD")
    
    # Details Box
    draw.rectangle([(25, 330), (395, 540)], fill="#1B263B", outline="#415A77", width=1)
    draw.text((40, 350), f"Paid To: APNA Computer Center", fill="#E0E1DD")
    draw.text((40, 385), f"Student: {student_name}", fill="#E0E1DD")
    draw.text((40, 420), f"UPI Ref / UTR: {utr_no}", fill="#E0E1DD")
    draw.text((40, 455), f"Date & Time: {date_str} 11:30 AM", fill="#E0E1DD")
    draw.text((40, 490), f"Mode: UPI QR Code Transfer", fill="#10B981")
    
    draw.text((100, 620), "100% Verified by Bank Gateway", fill="#778DA9")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, format="JPEG", quality=85)

def reset_and_seed():
    db = DatabaseManager.get_instance()
    
    print("Clearing existing admissions, expenses, and audit logs...")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admissions")
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('admissions', 'expenses', 'audit_logs')")
        conn.commit()
        
    today = datetime.now()
    
    students_data = [
        {
            "name": "Aman Verma",
            "phone": "9823456710",
            "email": "aman.verma@gmail.com",
            "courses": "Python & AI Masterclass",
            "orig_fee": 8500.0,
            "disc": 1000.0,
            "disc_reason": "Early Bird Scholarship",
            "final_amt": 7500.0,
            "mode": "UPI QR",
            "acc": "APNA Center / HDFC Bank",
            "utr": "432109876501",
            "date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Telecalling",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Pooja Sharma",
            "phone": "9134567821",
            "email": "pooja.sharma@yahoo.com",
            "courses": "Full-Stack Web Development",
            "orig_fee": 12000.0,
            "disc": 2000.0,
            "disc_reason": "पुराना छात्र रियायत (Loyalty Discount)",
            "final_amt": 10000.0,
            "mode": "UPI QR",
            "acc": "APNA Center / SBI",
            "utr": "432109876502",
            "date": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Walk-in",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Rohit Kumar",
            "phone": "8745678932",
            "email": "rohit.kumar@gmail.com",
            "courses": "ADCA (Advanced Diploma in Computer Applications)",
            "orig_fee": 6000.0,
            "disc": 0.0,
            "disc_reason": "",
            "final_amt": 6000.0,
            "mode": "Cash / नकद",
            "acc": "Cash / नकद (काउंटर)",
            "utr": "",
            "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Walk-in",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Ananya Mishra",
            "phone": "9956789043",
            "email": "ananya.mishra@gmail.com",
            "courses": "Data Analytics & Advanced Excel, Python & AI Masterclass",
            "orig_fee": 15000.0,
            "disc": 2500.0,
            "disc_reason": "Combo Special Discount",
            "final_amt": 12500.0,
            "mode": "UPI QR",
            "acc": "APNA Center / HDFC Bank",
            "utr": "432109876503",
            "date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Telecalling",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Vikram Singh",
            "phone": "7867890154",
            "email": "vikram.singh@outlook.com",
            "courses": "Tally Prime with GST & Accounting",
            "orig_fee": 5500.0,
            "disc": 500.0,
            "disc_reason": "One-time Full Payment Offer",
            "final_amt": 5000.0,
            "mode": "UPI QR",
            "acc": "APNA Center / ICICI",
            "utr": "432109876504",
            "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Walk-in",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Neha Gupta",
            "phone": "9478901265",
            "email": "neha.gupta@gmail.com",
            "courses": "Graphic Designing (Photoshop & Illustrator)",
            "orig_fee": 7000.0,
            "disc": 1000.0,
            "disc_reason": "Women in Tech Scholarship",
            "final_amt": 6000.0,
            "mode": "Cash / नकद",
            "acc": "Cash / नकद (काउंटर)",
            "utr": "",
            "date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Walk-in",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Suresh Patel",
            "phone": "8189012376",
            "email": "suresh.patel@gmail.com",
            "courses": "CCC (Course on Computer Concepts)",
            "orig_fee": 2500.0,
            "disc": 0.0,
            "disc_reason": "",
            "final_amt": 2500.0,
            "mode": "UPI QR",
            "acc": "APNA Center / HDFC Bank",
            "utr": "432109876505",
            "date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "status": "Activated",
            "act_at": today.strftime("%Y-%m-%d %H:%M"),
            "act_by": "Founder (Admin)",
            "source": "Telecalling",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Deepak Yadav",
            "phone": "9690123487",
            "email": "deepak.yadav@gmail.com",
            "courses": "Full-Stack Web Development",
            "orig_fee": 12000.0,
            "disc": 1500.0,
            "disc_reason": "Special Refer Discount",
            "final_amt": 10500.0,
            "mode": "UPI QR",
            "acc": "APNA Center / SBI",
            "utr": "432109876506",
            "date": today.strftime("%Y-%m-%d"),
            "status": "Pending",
            "act_at": "",
            "act_by": "",
            "source": "Telecalling",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Kavita Choudhary",
            "phone": "7001234598",
            "email": "kavita.choudhary@gmail.com",
            "courses": "Spoken English & Communication",
            "orig_fee": 4000.0,
            "disc": 500.0,
            "disc_reason": "Sibling Discount",
            "final_amt": 3500.0,
            "mode": "Cash / नकद",
            "acc": "Cash / नकद (काउंटर)",
            "utr": "",
            "date": today.strftime("%Y-%m-%d"),
            "status": "Pending",
            "act_at": "",
            "act_by": "",
            "source": "Walk-in",
            "caller": "एडमिशन काउंसलर (Staff)"
        },
        {
            "name": "Manish Tiwari",
            "phone": "9812345609",
            "email": "manish.tiwari@gmail.com",
            "courses": "Data Analytics & Advanced Excel",
            "orig_fee": 6500.0,
            "disc": 1000.0,
            "disc_reason": "Weekend Batch Offer",
            "final_amt": 5500.0,
            "mode": "UPI QR",
            "acc": "APNA Center / ICICI",
            "utr": "432109876507",
            "date": today.strftime("%Y-%m-%d"),
            "status": "Pending",
            "act_at": "",
            "act_by": "",
            "source": "Telecalling",
            "caller": "एडमिशन काउंसलर (Staff)"
        }
    ]
    
    print("Inserting 10 clean student admissions...")
    for idx, s in enumerate(students_data, start=1):
        adm_no = f"ADM-{today.year}-{idx:04d}"
        
        # Screenshot generation for UPI
        sc_path = ""
        if s["mode"] == "UPI QR":
            sc_filename = f"sample_sc_{idx}.jpg"
            sc_path = str(db.screenshots_dir / sc_filename)
            create_sample_upi_screenshot(sc_path, s["name"], s["final_amt"], s["utr"], s["date"])
            
        record = {
            "admission_no": adm_no,
            "student_name": s["name"],
            "email": s["email"],
            "phone": s["phone"],
            "courses_taken": s["courses"],
            "payment_mode": s["mode"],
            "account_holder": s["acc"],
            "original_fee": s["orig_fee"],
            "concession_amount": s["disc"],
            "concession_reason": s["disc_reason"],
            "final_amount": s["final_amt"],
            "utr_no": s["utr"],
            "payment_date": s["date"],
            "screenshot_path": sc_path,
            "admission_source": s["source"],
            "caller_staff_name": s["caller"],
            "caller_staff_id": 3,
            "activation_status": s["status"],
            "activated_at": s["act_at"],
            "activated_by": s["act_by"],
            "notes": "Verified Clean Entry"
        }
        
        with db.get_connection() as conn:
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
                record["admission_no"], record["student_name"], record["email"], record["phone"],
                record["courses_taken"], record["payment_mode"], record["account_holder"],
                record["original_fee"], record["concession_amount"], record["concession_reason"],
                record["final_amount"], record["utr_no"], record["payment_date"],
                record["screenshot_path"], record["admission_source"], record["caller_staff_name"],
                record["caller_staff_id"], record["activation_status"], record["activated_at"],
                record["activated_by"], record["notes"]
            ))
            conn.commit()
            
        db.log_activity(3, "counselor", "caller", "NEW_ADMISSION", f"Created {adm_no} for {s['name']} (₹{s['final_amt']})")
        if s["status"] == "Activated":
            db.log_activity(1, "admin", "admin", "COURSE_ACTIVATED", f"Activated course for {adm_no} ({s['name']})")
            
    print("Inserting 5 realistic coaching expenses...")
    expenses = [
        ("कोचिंग हॉल किराया (Monthly Institute Rent)", "किराया (Rent)", 16000.0, "Bank Transfer", (today - timedelta(days=5)).strftime("%Y-%m-%d"), "मकान मालिक (Ramesh Sharma)", "अकाउंटेंट (Accountant)"),
        ("बिजली बिल भुगतान (Electricity Bill)", "बिजली (Electricity)", 3250.0, "UPI / Online", (today - timedelta(days=3)).strftime("%Y-%m-%d"), "UPPCL Electricity Board", "अकाउंटेंट (Accountant)"),
        ("फैकल्टी एडवांस वेतन (Faculty Advance Salary)", "वेतन (Staff / Faculty Salary)", 12000.0, "Bank Transfer", (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Prof. Alok Pandey", "अकाउंटेंट (Accountant)"),
        ("हाई-स्पीड फाइबर इंटरनेट बिल (Office Internet Bill)", "इंटरनेट व टेलीफोन (Internet)", 999.0, "UPI / Online", (today - timedelta(days=1)).strftime("%Y-%m-%d"), "Airtel Fiber", "अकाउंटेंट (Accountant)"),
        ("ऑफिस स्टेशनरी, मार्कर व रजिस्टर (Office Supplies)", "स्टेशनरी व नोट्स प्रिंटिंग (Stationery)", 1450.0, "Cash / नकद", today.strftime("%Y-%m-%d"), "Shree Ram Book Depot", "अकाउंटेंट (Accountant)")
    ]
    
    for t_val, cat, amt, mode, dt, pt, rec_by in expenses:
        db.add_expense(t_val, cat, amt, mode, dt, pt, "", rec_by)
        db.log_activity(2, "accountant", "accountant", "EXPENSE_RECORDED", f"Added expense '{t_val}' of ₹{amt}")
        
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    reset_and_seed()
