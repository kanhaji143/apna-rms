import re
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from core.database import DatabaseManager

class ExcelService:
    @staticmethod
    def export_admissions_to_excel(file_path: str, start_date=None, end_date=None, status=None, search_query=None):
        db = DatabaseManager.get_instance()
        admissions = db.get_admissions(status=status, start_date=start_date, end_date=end_date, search_query=search_query)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Admissions_Summary"

        # Theme Colors
        navy_fill = PatternFill(start_color="00183A", end_color="00183A", fill_type="solid")
        cyan_font = Font(name="Calibri", size=11, bold=True, color="03F9FD")
        header_fill = PatternFill(start_color="06224D", end_color="06224D", fill_type="solid")
        white_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        regular_font = Font(name="Calibri", size=10, color="000000")
        
        green_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # Title Row (AI / LLM & Tax Audit Ready)
        ws.merge_cells("A1:P1")
        ws["A1"] = "APNA Computer RMS - Admissions & Financial Audit Report (AI / LLM & Tax Ready)"
        ws["A1"].fill = navy_fill
        ws["A1"].font = cyan_font
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 28

        # Date & Metrics Row
        total_rev = sum(a["final_amount"] for a in admissions)
        total_disc = sum(a.get("concession_amount", 0.0) for a in admissions)
        pending_count = sum(1 for a in admissions if a["activation_status"] == "Pending")
        
        ws.merge_cells("A2:P2")
        ws["A2"] = f"Generated On: {datetime.now().strftime('%d-%b-%Y %I:%M %p')} | Total Records: {len(admissions)} | Total Fees: ₹{total_rev:,.2f} | Concessions: ₹{total_disc:,.2f} | Pending Activations: {pending_count}"
        ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="00183A")
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 20

        # Column Headers
        headers = [
            "Adm No", "Date", "Student Name", "Phone", "Email",
            "Courses Enrolled", "Standard Fee (₹)", "Concession (₹)", "Concession Reason",
            "Paid Amount (₹)", "Payment Mode", "Account Holder", "UTR / Ref No",
            "Staff Caller", "Activation Status", "Activated Date & Time"
        ]

        ws.append([]) # empty row 3
        ws.append(headers) # row 4
        ws.row_dimensions[4].height = 24

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=4, column=col_idx)
            cell.fill = header_fill
            cell.font = white_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Data Rows
        row_num = 5
        for a in admissions:
            status_val = a["activation_status"]
            row_data = [
                a["admission_no"],
                a["payment_date"],
                a["student_name"],
                a["phone"],
                a["email"],
                a["courses_taken"],
                a.get("original_fee", 0.0),
                a.get("concession_amount", 0.0),
                a.get("concession_reason", ""),
                a["final_amount"],
                a["payment_mode"],
                a["account_holder"],
                a.get("utr_no", ""),
                a.get("caller_staff_name", ""),
                status_val,
                a.get("activated_at", "")
            ]
            ws.append(row_data)

            # Style status cell
            status_cell = ws.cell(row=row_num, column=15)
            if status_val == "Activated":
                status_cell.fill = green_fill
                status_cell.font = Font(name="Calibri", size=10, bold=True, color="065F46")
            else:
                status_cell.fill = red_fill
                status_cell.font = Font(name="Calibri", size=10, bold=True, color="991B1B")

            for col_idx in range(1, len(headers) + 1):
                c = ws.cell(row=row_num, column=col_idx)
                c.border = thin_border
                if col_idx in (7, 8, 10):
                    c.number_format = '#,##0.00'

            row_num += 1

        # Adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

        wb.save(file_path)
        return True

    @staticmethod
    def generate_import_template(file_path: str):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Student_Import_Template"

        headers = [
            "Student Name*", "Phone (10 digits)*", "Email*", "Courses Enrolled*",
            "Amount Paid (₹)*", "Payment Mode", "Account Holder*", "Payment Date (YYYY-MM-DD)*",
            "UTR Number", "Concession Amount", "Activation Status (Pending/Activated)"
        ]

        ws.append(headers)
        # Sample row
        sample_row = [
            "Rahul Sharma", "9876543210", "rahul@gmail.com", "Python & AI Masterclass",
            4500, "UPI", "APNA Center Account", datetime.now().strftime("%Y-%m-%d"),
            "UTR1234567890", 500, "Activated"
        ]
        ws.append(sample_row)

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="00183A", end_color="00183A", fill_type="solid")

        wb.save(file_path)
        return True

    @staticmethod
    def bulk_import_from_excel(file_path: str, default_caller="Bulk Import"):
        db = DatabaseManager.get_instance()
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active

        success_count = 0
        errors = []

        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            return 0, ["The excel file is empty or missing data rows."]

        for idx, row in enumerate(rows[1:], start=2):
            if not any(row):
                continue
            name = str(row[0] or "").strip()
            phone = str(row[1] or "").strip().replace(" ", "").replace("+91", "")
            email = str(row[2] or "").strip()
            course = str(row[3] or "").strip()
            amount_val = row[4]
            pay_mode = str(row[5] or "Cash").strip()
            account_holder = str(row[6] or "General").strip()
            pay_date = str(row[7] or datetime.now().strftime("%Y-%m-%d")).strip()
            utr = str(row[8] or "").strip()
            concession = float(row[9] or 0.0)
            status = str(row[10] or "Activated").strip()

            if not name or not phone:
                errors.append(f"Row {idx}: Name or Phone is missing.")
                continue

            try:
                final_amount = float(amount_val or 0.0)
            except ValueError:
                errors.append(f"Row {idx}: Invalid Amount.")
                continue

            adm_no = db.generate_next_admission_no()
            adm_data = {
                "admission_no": adm_no,
                "student_name": name,
                "email": email,
                "phone": phone,
                "courses_taken": course or "General Course",
                "payment_mode": pay_mode,
                "account_holder": account_holder,
                "original_fee": final_amount + concession,
                "concession_amount": concession,
                "concession_reason": "Historical / Import",
                "final_amount": final_amount,
                "utr_no": utr,
                "payment_date": pay_date,
                "screenshot_path": "", # Historical records don't force screenshot
                "admission_source": "Historical Import",
                "caller_staff_name": default_caller,
                "caller_staff_id": 1,
                "notes": "Imported via Excel"
            }

            try:
                new_id = db.add_admission(adm_data)
                if status.lower() == "activated":
                    db.update_activation_status(new_id, "Activated", default_caller)
                success_count += 1
            except Exception as e:
                errors.append(f"Row {idx}: Error saving - {str(e)}")

        return success_count, errors
