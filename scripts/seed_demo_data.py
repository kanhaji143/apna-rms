import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random
from datetime import datetime, timedelta
from core.database import DatabaseManager
from core.config import load_config

def seed():
    config = load_config()
    db = DatabaseManager.get_instance()

    print(f"Connecting to database at: {db.db_path}")

    # Realistic student names & details
    students = [
        ("Aarav Sharma", "9876543210", "aarav.sharma@gmail.com", "Python & AI Masterclass", 5000, "UPI QR", "APNA Center HDFC", "UTR883920192841", "Telecalling", "Rahul Caller", "Activated", 1000, "Old Student Concession"),
        ("Priya Verma", "9812345678", "priya.verma@yahoo.com", "ADCA (Advanced Diploma)", 6500, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Activated", 500, "Direct Walk-in Special"),
        ("Amit Kumar", "9723456789", "amit.k@gmail.com", "CCC (Course on Computer Concepts)", 2500, "UPI QR", "APNA Center SBI", "UTR992817263541", "Telecalling", "Pooja Caller", "Pending", 0, ""),
        ("Sneha Patel", "9634567890", "sneha.p@outlook.com", "Full-Stack Web Development", 8000, "UPI QR", "APNA Center HDFC", "UTR112233445566", "Telecalling", "Rahul Caller", "Activated", 1500, "Merit Loyalty Discount"),
        ("Vikas Gupta", "9545678901", "vikas.g@gmail.com", "Data Analytics & Advanced Excel", 4500, "Card Swipe", "APNA POS Machine", "TXN77665544", "Walk-in", "Counter Reception", "Activated", 0, ""),
        ("Pooja Singh", "9456789012", "pooja.singh@gmail.com", "Tally Prime with GST & Accounting", 4000, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Pending", 0, ""),
        ("Mohd. Imran", "9367890123", "imran.m@gmail.com", "Python & AI Masterclass", 5000, "UPI QR", "APNA Center HDFC", "UTR334455667788", "Telecalling", "Aman Caller", "Activated", 500, "Referral Discount"),
        ("Anjali Mishra", "9278901234", "anjali.m@gmail.com", "Spoken English & Communication", 2500, "UPI QR", "APNA Center SBI", "UTR556677889900", "Telecalling", "Pooja Caller", "Activated", 0, ""),
        ("Rohit Mehra", "9189012345", "rohit.m@gmail.com", "Graphic Designing (Photoshop)", 4500, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Pending", 500, "Old CCC Student"),
        ("Divya Rathore", "9090123456", "divya.r@gmail.com", "DCA (Diploma in Computer)", 3500, "UPI QR", "APNA Center HDFC", "UTR778899001122", "Telecalling", "Rahul Caller", "Activated", 0, ""),
        ("Kunal Sen", "8901234567", "kunal.s@gmail.com", "Python & AI Masterclass, CCC", 7000, "UPI QR", "APNA Center HDFC", "UTR990011223344", "Telecalling", "Aman Caller", "Pending", 1000, "Combo Pack Concession"),
        ("Rani Kumari", "8812345678", "rani.k@gmail.com", "Tally Prime with GST & Accounting", 4000, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Activated", 0, ""),
        ("Deepak Tiwari", "8723456789", "deepak.t@gmail.com", "ADCA (Advanced Diploma)", 6500, "UPI QR", "APNA Center SBI", "UTR123123123123", "Telecalling", "Rahul Caller", "Activated", 500, "Festive Offer"),
        ("Kavita Yadav", "8634567890", "kavita.y@gmail.com", "Data Analytics & Advanced Excel", 4500, "UPI QR", "APNA Center HDFC", "UTR456456456456", "Telecalling", "Pooja Caller", "Pending", 0, ""),
        ("Saurabh Joshi", "8545678901", "saurabh.j@gmail.com", "Full-Stack Web Development", 8000, "Net Banking", "APNA Center HDFC", "NET789789789", "Telecalling", "Aman Caller", "Activated", 1000, "Early Bird Discount"),
        ("Megha Jain", "8456789012", "megha.j@gmail.com", "Spoken English & Communication", 2500, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Activated", 0, ""),
        ("Harsh Vardhan", "8367890123", "harsh.v@gmail.com", "Python & AI Masterclass", 5000, "UPI QR", "APNA Center SBI", "UTR111222333444", "Telecalling", "Rahul Caller", "Activated", 500, "Old Student"),
        ("Neha Saxena", "8278901234", "neha.s@gmail.com", "CCC (Course on Computer Concepts)", 2500, "UPI QR", "APNA Center HDFC", "UTR555666777888", "Telecalling", "Pooja Caller", "Pending", 0, ""),
        ("Manish Dubey", "8189012345", "manish.d@gmail.com", "ADCA (Advanced Diploma)", 6500, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Activated", 0, ""),
        ("Shweta Pandey", "8090123456", "shweta.p@gmail.com", "Graphic Designing (Photoshop)", 4500, "UPI QR", "APNA Center HDFC", "UTR999888777666", "Telecalling", "Aman Caller", "Activated", 500, "Student Discount"),
        ("Alok Srivastava", "7901234567", "alok.s@gmail.com", "Data Analytics & Advanced Excel", 4500, "UPI QR", "APNA Center SBI", "UTR333222111000", "Telecalling", "Rahul Caller", "Pending", 0, ""),
        ("Pankaj Chauhan", "7812345678", "pankaj.c@gmail.com", "Tally Prime with GST & Accounting", 4000, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Activated", 0, ""),
        ("Nisha Rawat", "7723456789", "nisha.r@gmail.com", "Full-Stack Web Development", 8000, "UPI QR", "APNA Center HDFC", "UTR444555666777", "Telecalling", "Pooja Caller", "Activated", 1000, "Special Concession"),
        ("Gaurav Bajpai", "7634567890", "gaurav.b@gmail.com", "Python & AI Masterclass", 5000, "UPI QR", "APNA Center SBI", "UTR888777666555", "Telecalling", "Aman Caller", "Pending", 0, ""),
        ("Sunita Maurya", "7545678901", "sunita.m@gmail.com", "CCC (Course on Computer Concepts)", 2500, "Cash / नकद", "Cash in Hand", "", "Walk-in", "Counter Reception", "Activated", 0, "")
    ]

    now = datetime.now()

    for idx, s in enumerate(students, start=1):
        # Stagger dates: some today, some yesterday, some earlier
        days_ago = (idx % 5)
        p_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        adm_no = f"ADM-2026-{idx:04d}"

        data = {
            "admission_no": adm_no,
            "student_name": s[0],
            "phone": s[1],
            "email": s[2],
            "courses_taken": s[3],
            "final_amount": s[4],
            "payment_mode": s[5],
            "account_holder": s[6],
            "utr_no": s[7],
            "admission_source": s[8],
            "caller_staff_name": s[9],
            "caller_staff_id": 1,
            "original_fee": s[4] + s[11],
            "concession_amount": s[11],
            "concession_reason": s[12],
            "payment_date": p_date,
            "screenshot_path": "",
            "notes": "[DEMO RECORD] - परीक्षण हेतु रिकॉर्ड"
        }

        try:
            adm_id = db.add_admission(data)
            if s[10] == "Activated":
                act_time = (now - timedelta(days=days_ago, hours=2)).strftime("%Y-%m-%d %I:%M %p")
                with db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE admissions SET activation_status='Activated', activated_at=?, activated_by='Backend Team' WHERE id=?", (act_time, adm_id))
                    conn.commit()
            print(f"Added {adm_no}: {s[0]} ({s[3]}) - {s[10]}")
        except Exception as e:
            print(f"Error adding {adm_no}: {e}")

    # Seed 5 sample expenses
    expenses = [
        ("🏢 सेंटर किराया (Office Rent) - [DEMO]", "🏢 Rent / सेंटर किराया", 25000, "Bank Transfer", (now - timedelta(days=5)).strftime("%Y-%m-%d"), "मकान मालिक (Landlord)"),
        ("⚡ बिजली बिल (Electricity Bill) - [DEMO]", "⚡ Electricity, Water & Internet / बिजली बिल", 4500, "UPI / Online", (now - timedelta(days=3)).strftime("%Y-%m-%d"), "UPPCL"),
        ("👨‍🏫 विकास सर - गेस्ट लेक्चर मानदेय - [DEMO]", "👨‍🏫 Teacher Salary / मानदेय", 12000, "Bank Transfer", (now - timedelta(days=2)).strftime("%Y-%m-%d"), "विकास सर"),
        ("📢 फेसबुक/इंस्टाग्राम विज्ञापन - [DEMO]", "📢 Marketing & Online Ads / विज्ञापन", 5000, "Card / Online", (now - timedelta(days=1)).strftime("%Y-%m-%d"), "Meta Ads"),
        ("☕ ऑफिस चाय-नाश्ता व मेंटेनेंस - [DEMO]", "☕ Tea, Refreshment & Office Misc / मेंटेनेंस", 1200, "Cash / नकद", now.strftime("%Y-%m-%d"), "लोकल वेंडर")
    ]

    for exp in expenses:
        db.add_expense(exp[0], exp[1], exp[2], exp[3], exp[4], exp[5], "", "Accountant")
        print(f"Added Expense: {exp[0]} (₹{exp[2]})")

    print("\n✅ Successfully seeded 25 Admissions and 5 Expenses!")

if __name__ == "__main__":
    seed()
