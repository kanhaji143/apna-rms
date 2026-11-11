import os
import smtplib
import zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from core.config import load_config
from core.database import DatabaseManager
from core.excel_service import ExcelService

class MailService:
    @staticmethod
    def send_daily_eod_report(caller_name="All Staff"):
        config = load_config()
        smtp_server = config.get("smtp_server", "smtp.gmail.com")
        smtp_port = int(config.get("smtp_port", 587))
        smtp_email = config.get("smtp_email", "")
        smtp_password = config.get("smtp_password", "")
        admin_email = config.get("admin_backup_email", "")

        if not admin_email or not smtp_email or not smtp_password:
            return False, "SMTP or Admin Backup Email is not configured in Settings! / सेटिंग्स में SMTP या एडमिन ईमेल सेट नहीं है।"

        db = DatabaseManager.get_instance()
        today_str = datetime.now().strftime("%Y-%m-%d")
        display_date = datetime.now().strftime("%d-%b-%Y")

        # Fetch today's admissions
        today_admissions = db.get_admissions(start_date=today_str, end_date=today_str)
        total_count = len(today_admissions)
        total_rev = sum(a["final_amount"] for a in today_admissions)
        pending_count = sum(1 for a in today_admissions if a["activation_status"] == "Pending")

        temp_dir = db.db_dir / "temp_mail"
        temp_dir.mkdir(parents=True, exist_ok=True)

        excel_filename = f"Daily_Report_{today_str}_{caller_name.replace(' ', '_')}.xlsx"
        excel_path = temp_dir / excel_filename
        ExcelService.export_admissions_to_excel(str(excel_path), start_date=today_str, end_date=today_str)

        # Create zip of today's screenshots
        zip_filename = f"Screenshots_{today_str}_{caller_name.replace(' ', '_')}.zip"
        zip_path = temp_dir / zip_filename
        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zipf:
            for a in today_admissions:
                s_path = a.get("screenshot_path", "")
                if s_path and os.path.exists(s_path):
                    zipf.write(s_path, arcname=Path(s_path).name)

        # Build Email
        msg = MIMEMultipart()
        msg["From"] = f"{config.get('institute_name', 'APNA RMS')} <{smtp_email}>"
        msg["To"] = admin_email
        msg["Subject"] = f"📊 [Daily Admission EOD Report - {display_date}] - Staff: {caller_name} | {total_count} Adm (₹{total_rev:,.0f})"

        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6;">
            <div style="background-color: #00183A; color: #03F9FD; padding: 18px; border-radius: 8px;">
                <h2 style="margin: 0;">{config.get('institute_name', 'APNA COMPUTER')} - Daily EOD Report</h2>
                <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 13px;">Date: {display_date} | Staff: {caller_name}</p>
            </div>
            
            <div style="margin-top: 20px; padding: 16px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
                <h3 style="margin-top: 0; color: #00183A;">Executive Summary / आज का सारांश:</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <tr style="border-bottom: 1px solid #cbd5e1;">
                        <td style="padding: 8px 0;"><b>Total Admissions Recorded Today:</b></td>
                        <td style="padding: 8px 0; text-align: right; font-weight: bold;">{total_count}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #cbd5e1;">
                        <td style="padding: 8px 0;"><b>Total Fee Revenue Collected:</b></td>
                        <td style="padding: 8px 0; text-align: right; font-weight: bold; color: #10B981;">₹{total_rev:,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0;"><b>Pending Course Activations:</b></td>
                        <td style="padding: 8px 0; text-align: right; font-weight: bold; color: {'#EF4444' if pending_count > 0 else '#10B981'};">{pending_count}</td>
                    </tr>
                </table>
            </div>

            <p style="font-size: 13px; color: #475569; margin-top: 20px;">
                Attached with this email are:
                <br/>1. <b>{excel_filename}</b> (Complete audit record with student and payment details)
                <br/>2. <b>{zip_filename}</b> (All payment confirmation slips and UPI screenshots compressed)
            </p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin-top: 24px;"/>
            <p style="font-size: 11px; color: #94a3b8;">
                Generated automatically by <b>APNA Computer RMS (Record Management Software)</b>. 100% Offline Secure Local Backup.
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body_html, "html"))

        # Attach Excel file
        if excel_path.exists():
            with open(excel_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={excel_filename}")
            msg.attach(part)

        # Attach Zip file
        if zip_path.exists() and os.path.getsize(str(zip_path)) > 100:
            with open(zip_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={zip_filename}")
            msg.attach(part)

        # Send via SMTP
        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.send_message(msg)
            return True, f"Daily report successfully emailed to {admin_email}! / आज की रिपोर्ट ईमेल पर भेज दी गई!"
        except Exception as e:
            return False, f"Failed to send email: {str(e)} / ईमेल भेजने में विफल: {str(e)}"
        finally:
            # Clean up temp files
            try:
                if excel_path.exists():
                    os.remove(excel_path)
                if zip_path.exists():
                    os.remove(zip_path)
            except Exception:
                pass
