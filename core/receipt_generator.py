import os
import sys
import base64
import threading
from pathlib import Path
from datetime import datetime

# ReportLab imports kept for backwards compatibility and fallback
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.config import load_config
from core.database import DatabaseManager

# ─────────────────────────────────────────────────────────────────────────────
# Backwards-compatibility for ID card generator and other modules
# ─────────────────────────────────────────────────────────────────────────────
_HINDI_FONTS_REGISTERED = False

def _register_font_safe(name, path):
    try:
        if name not in pdfmetrics.getRegisteredFontNames() and os.path.exists(path):
            pdfmetrics.registerFont(TTFont(name, path))
            return True
    except Exception:
        pass
    return False

def get_unicode_fonts():
    """Kept for core.id_card_generator and other ReportLab consumers."""
    WIN_FONTS = 'C:/Windows/Fonts/'
    nirmala_reg  = WIN_FONTS + 'Nirmala.ttf'
    nirmala_bold = WIN_FONTS + 'NirmalaB.ttf'
    nirmala_semi = WIN_FONTS + 'NirmalaS.ttf'

    if os.path.exists(nirmala_reg):
        ok_reg  = _register_font_safe('NirmalaUI', nirmala_reg)
        _register_font_safe('NirmalaUI-Bold', nirmala_bold if os.path.exists(nirmala_bold) else nirmala_reg)
        _register_font_safe('NirmalaUI-SemiLight', nirmala_semi if os.path.exists(nirmala_semi) else nirmala_reg)
        if ok_reg:
            return 'NirmalaUI', 'NirmalaUI-Bold', 'NirmalaUI'

    return 'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique'

# ─────────────────────────────────────────────────────────────────────────────
# Local Font Cache
# ─────────────────────────────────────────────────────────────────────────────
_BASE64_FONT_CACHE = {}

def _get_base64_font(font_filename: str) -> str:
    global _BASE64_FONT_CACHE
    if font_filename in _BASE64_FONT_CACHE:
        return _BASE64_FONT_CACHE[font_filename]

    candidate_dirs = []
    if getattr(sys, 'frozen', False):
        candidate_dirs.append(getattr(sys, '_MEIPASS', ''))
        candidate_dirs.append(os.path.join(getattr(sys, '_MEIPASS', ''), 'fonts'))

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate_dirs.append(os.path.join(root_dir, 'fonts'))
    candidate_dirs.append(os.path.join(os.getcwd(), 'fonts'))
    candidate_dirs.append('C:/Windows/Fonts')

    for d in candidate_dirs:
        if not d:
            continue
        p = os.path.join(d, font_filename)
        if os.path.exists(p):
            try:
                with open(p, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    _BASE64_FONT_CACHE[font_filename] = encoded
                    return encoded
            except Exception:
                pass
    return ""

def _get_base64_file(path: str) -> str:
    if path and os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            pass
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# HTML + CSS Receipt Template Builder with Developer Watermark
# ─────────────────────────────────────────────────────────────────────────────
def build_receipt_html(admission_data: dict, config: dict) -> str:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Embedded TrueType Fonts: Noto Sans Devanagari + Noto Sans
    noto_dev_reg = _get_base64_font("NotoSansDevanagari-Regular.ttf")
    noto_dev_bold = _get_base64_font("NotoSansDevanagari-Bold.ttf")
    noto_en_reg = _get_base64_font("NotoSans-Regular.ttf")
    noto_en_bold = _get_base64_font("NotoSans-Bold.ttf")

    # Logo base64
    logo_base64 = ""
    logo_path = config.get("logo_path", "")
    if logo_path and os.path.isabs(logo_path) and os.path.exists(logo_path):
        logo_base64 = _get_base64_file(logo_path)
    elif logo_path:
        rel_logo = os.path.join(root_dir, logo_path)
        if os.path.exists(rel_logo):
            logo_base64 = _get_base64_file(rel_logo)
    if not logo_base64:
        default_logo = os.path.join(root_dir, "Logo.png")
        if os.path.exists(default_logo):
            logo_base64 = _get_base64_file(default_logo)

    # Fee Calculations
    orig_fee = float(admission_data.get("original_fee") or admission_data.get("final_amount") or 0.0)
    disc_fee = float(admission_data.get("concession_amount") or 0.0)
    paid_fee = float(admission_data.get("final_amount") or 0.0)
    net_fee = max(0.0, orig_fee - disc_fee)
    balance_due = max(0.0, net_fee - paid_fee)

    # Installment History
    installments_html = ""
    adm_id = admission_data.get("id")
    if adm_id:
        try:
            db = DatabaseManager.get_instance()
            inst_list = db.get_installments(adm_id)
            if inst_list:
                rows_html = ""
                for inst in inst_list:
                    rows_html += f"""
                    <tr>
                        <td style="padding: 5px 8px; border: 1px solid #E2E8F0;">{inst.get('receipt_no', '')}</td>
                        <td style="padding: 5px 8px; border: 1px solid #E2E8F0;">{inst.get('payment_date', '')}</td>
                        <td style="padding: 5px 8px; border: 1px solid #E2E8F0;">{inst.get('payment_mode', '')}</td>
                        <td style="padding: 5px 8px; border: 1px solid #E2E8F0; text-align: right;">Rs. {float(inst.get('amount_paid', 0)):,.2f}</td>
                    </tr>
                    """
                installments_html = f"""
                <div style="margin-top: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: #334155; margin-bottom: 4px;">Payment Installment History / किस्त भुगतान इतिहास:</div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                        <thead>
                            <tr style="background-color: #F8FAFC; color: #334155;">
                                <th style="padding: 5px 8px; border: 1px solid #E2E8F0; text-align: left;">Receipt No</th>
                                <th style="padding: 5px 8px; border: 1px solid #E2E8F0; text-align: left;">Date</th>
                                <th style="padding: 5px 8px; border: 1px solid #E2E8F0; text-align: left;">Mode</th>
                                <th style="padding: 5px 8px; border: 1px solid #E2E8F0; text-align: right;">Amount (Rs.)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """
        except Exception:
            pass

    # Social footer
    social_parts = []
    if config.get("youtube_link"):
        social_parts.append(f"YouTube: {config.get('youtube_link')}")
    if config.get("instagram_link"):
        social_parts.append(f"Instagram: {config.get('instagram_link')}")
    if config.get("telegram_link"):
        social_parts.append(f"Telegram: {config.get('telegram_link')}")

    social_footer_html = ""
    if social_parts:
        social_text = " | ".join(social_parts)
        social_footer_html = f"""
        <div style="margin-top: 14px; background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 4px; padding: 6px 10px; font-size: 10px; color: #0284C7; text-align: center;">
            <strong>Follow us for Free Classes & Updates:</strong> {social_text}
        </div>
        """

    utr_row_html = ""
    if admission_data.get("utr_no") or admission_data.get("caller_staff_name"):
        utr_val = str(admission_data.get("utr_no") or "N/A")
        staff_val = str(admission_data.get("caller_staff_name") or "Office Staff")
        utr_row_html = f"""
        <tr>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">UPI / UTR Ref No:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{utr_val}</td>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Issued By Staff:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{staff_val}</td>
        </tr>
        """

    concession_reason = admission_data.get("concession_reason", "")
    concession_remark_html = ""
    if concession_reason:
        concession_remark_html = f"""
        <div style="margin-top: 6px; font-size: 10.5px; font-style: italic; color: #475569;">
            * Discount Remark: {concession_reason}
        </div>
        """

    if balance_due == 0:
        due_row_bg = "#ECFDF5"
        due_row_text = '<span style="color: #059669; font-weight: 700;">PAID IN FULL / पूर्ण चुकता (Rs. 0.00)</span>'
        due_row_val = '<span style="color: #059669; font-weight: 700;">Rs. 0.00</span>'
    else:
        due_row_bg = "#FEF2F2"
        due_row_text = f'<span style="color: #DC2626; font-weight: 700;">BALANCE DUE / शेष बकाया: Rs. {balance_due:,.2f}</span>'
        due_row_val = f'<span style="color: #DC2626; font-weight: 700;">Rs. {balance_due:,.2f}</span>'

    logo_img_html = f'<img src="data:image/png;base64,{logo_base64}" style="max-width: 84px; max-height: 84px; object-fit: contain;" />' if logo_base64 else '<div style="font-size: 26px; font-weight: 800; color: #00183A;">APNA</div>'

    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Fee Receipt - {admission_data.get('admission_no', '')}</title>
    <style>
        @font-face {{
            font-family: 'Noto Sans Devanagari';
            src: url('data:font/truetype;charset=utf-8;base64,{noto_dev_reg}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Noto Sans Devanagari';
            src: url('data:font/truetype;charset=utf-8;base64,{noto_dev_bold}') format('truetype');
            font-weight: bold;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Noto Sans';
            src: url('data:font/truetype;charset=utf-8;base64,{noto_en_reg}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Noto Sans';
            src: url('data:font/truetype;charset=utf-8;base64,{noto_en_bold}') format('truetype');
            font-weight: bold;
            font-style: normal;
        }}

        @page {{
            size: A4 portrait;
            margin: 12mm 14mm 10mm 14mm;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}

        body {{
            font-family: 'Noto Sans Devanagari', 'Noto Sans', 'Segoe UI', Arial, sans-serif;
            color: #1E293B;
            background-color: #FFFFFF;
            font-size: 11.5px;
            line-height: 1.4;
        }}

        .header-container {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding-bottom: 8px;
        }}

        .logo-box {{
            width: 86px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .institute-info {{
            flex-grow: 1;
        }}

        .institute-name {{
            font-size: 22px;
            font-weight: 800;
            color: #00183A;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            line-height: 1.2;
        }}

        .institute-tagline {{
            font-size: 12px;
            font-weight: 600;
            color: #334155;
            margin-top: 3px;
        }}

        .institute-contact {{
            font-size: 11px;
            color: #475569;
            margin-top: 3px;
        }}

        .divider {{
            height: 2.5px;
            background-color: #00183A;
            margin: 8px 0 14px 0;
            border-radius: 1px;
        }}

        .banner-box {{
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 5px;
            padding: 8px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }}

        .banner-title {{
            font-size: 13.5px;
            font-weight: 700;
            color: #00183A;
            letter-spacing: 0.3px;
        }}

        .banner-badge {{
            text-align: right;
            font-size: 12px;
            color: #00183A;
            line-height: 1.35;
        }}

        .student-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11.5px;
            margin-bottom: 15px;
        }}

        .student-table tr {{
            border-bottom: 1px solid #E2E8F0;
        }}

        .fee-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11.5px;
            margin-top: 4px;
            border: 1px solid #CBD5E1;
        }}

        .fee-table th {{
            background-color: #00183A;
            color: #FFFFFF;
            padding: 7px 8px;
            font-weight: 700;
            border: 1px solid #00183A;
            font-size: 11.5px;
        }}

        .fee-table td {{
            padding: 7px 8px;
            border: 1px solid #CBD5E1;
            vertical-align: middle;
        }}

        .footer-signatures {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-top: 24px;
            padding-top: 6px;
        }}

        .terms-box {{
            width: 58%;
            font-size: 9.5px;
            color: #64748B;
            line-height: 1.45;
        }}

        .sign-box {{
            width: 38%;
            text-align: right;
            font-size: 11px;
            color: #00183A;
        }}

        .developer-watermark {{
            margin-top: 20px;
            padding-top: 8px;
            border-top: 1px dashed #CBD5E1;
            text-align: center;
            font-size: 8.5px;
            color: #64748B;
            letter-spacing: 0.3px;
        }}
    </style>
</head>
<body>

    <!-- Header Section -->
    <div class="header-container">
        <div class="logo-box">
            {logo_img_html}
        </div>
        <div class="institute-info">
            <div class="institute-name">{config.get('institute_name', 'APNA COMPUTER')}</div>
            <div class="institute-tagline">{config.get('institute_tagline', 'कंप्यूटर और कौशल प्रशिक्षण संस्थान')}</div>
            <div class="institute-contact">Phone: {config.get('institute_phone', '8504985149')} | Email: {config.get('institute_email', 'krishnaskb143@gmail.com')}</div>
            {f'<div class="institute-contact">{config.get("institute_address", "")}</div>' if config.get("institute_address") else ''}
        </div>
    </div>

    <div class="divider"></div>

    <!-- Receipt No & Date Banner -->
    <div class="banner-box">
        <div class="banner-title">OFFICIAL FEE PAYMENT RECEIPT / फीस रसीद</div>
        <div class="banner-badge">
            <strong>Receipt No:</strong> {admission_data.get('admission_no', 'N/A')}<br/>
            <strong>Date:</strong> {admission_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))}
        </div>
    </div>

    <!-- Student Details Grid -->
    <table class="student-table">
        <tr>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Student Name:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{admission_data.get('student_name', '')}</td>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Mobile No:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{admission_data.get('phone', '')}</td>
        </tr>
        <tr>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Registered Email:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{admission_data.get('email', '')}</td>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Admission Type:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{admission_data.get('admission_source', 'Telecalling')}</td>
        </tr>
        <tr>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Account Beneficiary:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{admission_data.get('account_holder', '')}</td>
            <td style="padding: 5px 6px; font-weight: 700; color: #334155; width: 18%;">Payment Mode:</td>
            <td style="padding: 5px 6px; color: #1E293B; width: 32%;">{admission_data.get('payment_mode', 'UPI')}</td>
        </tr>
        {utr_row_html}
    </table>

    <!-- Fee Details Table -->
    <table class="fee-table">
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">#</th>
                <th style="width: 45%; text-align: left;">Description / Course Enrolled</th>
                <th style="width: 16%; text-align: right;">Standard Fee (Rs.)</th>
                <th style="width: 16%; text-align: right;">Discount (Rs.)</th>
                <th style="width: 18%; text-align: right;">Net Amount Paid (Rs.)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="text-align: center;">1</td>
                <td><strong>{admission_data.get('courses_taken', 'Course')}</strong></td>
                <td style="text-align: right;">Rs. {orig_fee:,.2f}</td>
                <td style="text-align: right;">{'Rs. ' + f'{disc_fee:,.2f}' if disc_fee > 0 else '-'}</td>
                <td style="text-align: right;"><strong>Rs. {paid_fee:,.2f}</strong></td>
            </tr>
            <tr style="background-color: #E2E8F0; font-weight: 700;">
                <td></td>
                <td style="color: #334155;">TOTAL RECEIVED AMOUNT / कुल प्राप्त राशि:</td>
                <td style="text-align: right;">Rs. {orig_fee:,.2f}</td>
                <td style="text-align: right;">{'Rs. ' + f'{disc_fee:,.2f}' if disc_fee > 0 else '-'}</td>
                <td style="text-align: right; color: #00183A;">Rs. {paid_fee:,.2f}</td>
            </tr>
            <tr style="background-color: {due_row_bg};">
                <td></td>
                <td>{due_row_text}</td>
                <td></td>
                <td></td>
                <td style="text-align: right;">{due_row_val}</td>
            </tr>
        </tbody>
    </table>

    {installments_html}
    {concession_remark_html}

    <!-- Signatures and Terms -->
    <div class="footer-signatures">
        <div class="terms-box">
            <strong style="color: #475569;">Terms & Conditions:</strong><br/>
            1. Fees once paid is non-refundable.<br/>
            2. Course access credentials are sent to registered email.<br/>
            3. System generated authorized receipt.
        </div>
        <div class="sign-box">
            <strong>For {config.get('institute_name', 'APNA COMPUTER')}</strong><br/><br/><br/>
            ____________________________<br/>
            <strong>Authorized Signatory / Seal</strong>
        </div>
    </div>

    {social_footer_html}

    <!-- Developer & Legal Watermark Footer -->
    <div class="developer-watermark">
        System Generated Authorized Receipt • Software Developed & Licensed by APNA Computer (कृष्णा जी) | Helpline: 8504985149 | Email: krishnaskb143@gmail.com
    </div>

</body>
</html>"""
    return html

# ─────────────────────────────────────────────────────────────────────────────
# High-Performance Persistent Chromium Worker Thread
# Eliminates 10-20s lag by keeping a warm, persistent Chromium browser
# All Playwright calls execute inside the dedicated worker thread safely.
# ─────────────────────────────────────────────────────────────────────────────
class _ChromiumWorker:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        import queue
        self._task_queue = queue.Queue()
        self._ready_event = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="ChromiumPDFWorker")
        self._thread.start()
        # Wait up to 15s for initial browser startup on first on-demand creation
        self._ready_event.wait(timeout=15)

    def _run_loop(self):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                launch_args = [
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate'
                ]
                browser = None
                for launch_opt in [
                    {'args': launch_args},
                    {'channel': 'msedge', 'args': launch_args},
                    {'channel': 'chrome', 'args': launch_args}
                ]:
                    try:
                        browser = p.chromium.launch(headless=True, **launch_opt)
                        if browser:
                            break
                    except Exception:
                        continue

                if not browser:
                    return

                context = browser.new_context()
                page = context.new_page()
                self._ready_event.set()

                while True:
                    task = self._task_queue.get()
                    if task is None:
                        break
                    html, out_path, result_queue = task
                    try:
                        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
                        page.set_content(html, wait_until="load")
                        page.pdf(
                            path=out_path,
                            format="A4",
                            print_background=True,
                            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
                        )
                        result_queue.put((True, None))
                    except Exception as e:
                        result_queue.put((False, e))
                    finally:
                        self._task_queue.task_done()

                browser.close()
        except Exception:
            pass

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def render_pdf(self, html_content: str, output_pdf_path: str, timeout: float = 20.0):
        if not self._ready_event.is_set():
            if not self._ready_event.wait(timeout=timeout):
                raise RuntimeError("Chromium worker not ready or failed to launch within timeout.")
        import queue
        rq = queue.Queue()
        self._task_queue.put((html_content, output_pdf_path, rq))
        success, err = rq.get(timeout=timeout)
        if not success:
            raise err

# Note: Chromium is strictly lazy-loaded on demand via _ChromiumWorker.get_instance()
# inside ReceiptGenerator.generate_fee_receipt(). App startup, Dashboard, and other
# views do NOT launch Chromium, saving memory and eliminating startup contention.

# ─────────────────────────────────────────────────────────────────────────────
# Fallback Renderer: ReportLab (Preserved for safe redundancy)
# ─────────────────────────────────────────────────────────────────────────────
def _render_receipt_with_reportlab_fallback(admission_data: dict, output_pdf_path: str):
    config = load_config()
    reg_font, bold_font, oblique_font = get_unicode_fonts()

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []
    brand_navy = colors.HexColor("#00183A")
    dark_text = colors.HexColor("#1E293B")
    light_bg = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle('InstTitle', parent=styles['Heading1'], fontName=bold_font, fontSize=18, textColor=brand_navy, leading=22, alignment=0)
    tagline_style = ParagraphStyle('InstTagline', parent=styles['Normal'], fontName=reg_font, fontSize=10, textColor=colors.HexColor("#334155"), leading=14, spaceAfter=0)
    receipt_badge_style = ParagraphStyle('ReceiptBadge', parent=styles['Normal'], fontName=bold_font, fontSize=11, textColor=brand_navy, leading=15, alignment=2)
    meta_label_style = ParagraphStyle('MetaLabel', parent=styles['Normal'], fontName=bold_font, fontSize=9, textColor=colors.HexColor("#334155"), leading=12)
    meta_val_style = ParagraphStyle('MetaVal', parent=styles['Normal'], fontName=reg_font, fontSize=9, textColor=dark_text, leading=12)
    cell_right_style = ParagraphStyle('CellRight', parent=styles['Normal'], fontName=reg_font, fontSize=9, textColor=dark_text, alignment=2, leading=12)
    cell_right_bold = ParagraphStyle('CellRightBold', parent=styles['Normal'], fontName=bold_font, fontSize=9.5, textColor=brand_navy, alignment=2, leading=13)

    logo_path = config.get("logo_path", "")
    logo_elem = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo_elem = RLImage(logo_path, width=1.1*inch, height=1.1*inch)
        except Exception:
            logo_elem = Paragraph("<b>APNA</b>", title_style)
    else:
        logo_elem = Paragraph("<b>APNA</b>", title_style)

    inst_info = [
        Paragraph(f"<b>{config.get('institute_name', 'APNA COMPUTER')}</b>", title_style),
        Paragraph(config.get('institute_tagline', 'कंप्यूटर और कौशल प्रशिक्षण संस्थान'), tagline_style),
        Paragraph(f"Phone: {config.get('institute_phone', '8504985149')} | Email: {config.get('institute_email', 'krishnaskb143@gmail.com')}", meta_val_style),
        Paragraph(config.get('institute_address', ''), meta_val_style)
    ]

    header_table = Table([[logo_elem, inst_info]], colWidths=[1.3*inch, 5.8*inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=2, color=brand_navy, spaceBefore=6, spaceAfter=12))

    banner_data = [[
        Paragraph("<b>OFFICIAL FEE PAYMENT RECEIPT / फीस रसीद</b>", ParagraphStyle('BTitle', fontName=bold_font, fontSize=11, textColor=brand_navy, leading=14)),
        Paragraph(f"<b>Receipt No:</b> {admission_data.get('admission_no', 'N/A')}<br/><b>Date:</b> {admission_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))}", receipt_badge_style)
    ]]
    banner_table = Table(banner_data, colWidths=[4.2*inch, 2.9*inch])
    banner_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), light_bg), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")), ('PADDING', (0,0), (-1,-1), 8), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(banner_table)
    elements.append(Spacer(1, 14))

    student_grid = [
        [Paragraph("<b>Student Name:</b>", meta_label_style), Paragraph(str(admission_data.get("student_name", "")), meta_val_style), Paragraph("<b>Mobile No:</b>", meta_label_style), Paragraph(str(admission_data.get("phone", "")), meta_val_style)],
        [Paragraph("<b>Registered Email:</b>", meta_label_style), Paragraph(str(admission_data.get("email", "")), meta_val_style), Paragraph("<b>Admission Type:</b>", meta_label_style), Paragraph(str(admission_data.get("admission_source", "Telecalling")), meta_val_style)],
        [Paragraph("<b>Account Beneficiary:</b>", meta_label_style), Paragraph(str(admission_data.get("account_holder", "")), meta_val_style), Paragraph("<b>Payment Mode:</b>", meta_label_style), Paragraph(str(admission_data.get("payment_mode", "UPI")), meta_val_style)]
    ]
    if admission_data.get("utr_no") or admission_data.get("caller_staff_name"):
        student_grid.append([
            Paragraph("<b>UPI / UTR Ref No:</b>", meta_label_style),
            Paragraph(str(admission_data.get("utr_no", "")), meta_val_style),
            Paragraph("<b>Issued By Staff:</b>", meta_label_style),
            Paragraph(str(admission_data.get("caller_staff_name", "Office Staff")), meta_val_style)
        ])

    student_table = Table(student_grid, colWidths=[1.5*inch, 2.3*inch, 1.4*inch, 1.9*inch])
    student_table.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")), ('PADDING', (0,0), (-1,-1), 5), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(student_table)
    elements.append(Spacer(1, 16))

    orig_fee = float(admission_data.get("original_fee") or admission_data.get("final_amount") or 0.0)
    disc_fee = float(admission_data.get("concession_amount") or 0.0)
    paid_fee = float(admission_data.get("final_amount") or 0.0)
    net_fee = max(0.0, orig_fee - disc_fee)
    balance_due = max(0.0, net_fee - paid_fee)

    fee_headers = [
        Paragraph("<b>#</b>", ParagraphStyle('FH', fontName=bold_font, textColor=colors.white)),
        Paragraph("<b>Description / Course Enrolled</b>", ParagraphStyle('FH', fontName=bold_font, textColor=colors.white)),
        Paragraph("<b>Standard Fee (Rs.)</b>", ParagraphStyle('FH_R', fontName=bold_font, textColor=colors.white, alignment=2)),
        Paragraph("<b>Discount (Rs.)</b>", ParagraphStyle('FH_R', fontName=bold_font, textColor=colors.white, alignment=2)),
        Paragraph("<b>Net Amount Paid (Rs.)</b>", ParagraphStyle('FH_R', fontName=bold_font, textColor=colors.white, alignment=2))
    ]
    fee_row = [
        Paragraph("1", meta_val_style),
        Paragraph(f"<b>{admission_data.get('courses_taken', 'Course')}</b>", meta_val_style),
        Paragraph(f"Rs. {orig_fee:,.2f}", cell_right_style),
        Paragraph(f"Rs. {disc_fee:,.2f}" if disc_fee > 0 else "-", cell_right_style),
        Paragraph(f"<b>Rs. {paid_fee:,.2f}</b>", cell_right_bold)
    ]
    total_row = [
        "", Paragraph("<b>TOTAL RECEIVED AMOUNT / कुल प्राप्त राशि:</b>", meta_label_style),
        Paragraph(f"Rs. {orig_fee:,.2f}", cell_right_style),
        Paragraph(f"Rs. {disc_fee:,.2f}", cell_right_style),
        Paragraph(f"<b>Rs. {paid_fee:,.2f}</b>", cell_right_bold)
    ]
    due_text = "<b>PAID IN FULL / पूर्ण चुकता (Rs. 0.00)</b>" if balance_due == 0 else f"<font color='#DC2626'><b>BALANCE DUE / शेष बकाया: Rs. {balance_due:,.2f}</b></font>"
    due_row = ["", Paragraph(due_text, meta_label_style), "", "", Paragraph(f"<b>Rs. {balance_due:,.2f}</b>" if balance_due > 0 else "Rs. 0.00", cell_right_bold)]

    fee_table = Table([fee_headers, fee_row, total_row, due_row], colWidths=[0.4*inch, 3.2*inch, 1.2*inch, 1.0*inch, 1.3*inch])
    fee_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), brand_navy),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#FEF2F2") if balance_due > 0 else colors.HexColor("#ECFDF5")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(fee_table)

    if admission_data.get("concession_reason"):
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<i>* Discount Remark: {admission_data.get('concession_reason')}</i>", tagline_style))

    elements.append(Spacer(1, 28))
    sig_data = [[
        Paragraph("<b>Terms & Conditions:</b><br/>1. Fees once paid is non-refundable.<br/>2. Course access credentials are sent to registered email.<br/>3. System generated authorized receipt.<br/><br/><font size='7' color='#94A3B8'>System Generated Authorized Receipt • Software Developed & Licensed by APNA Computer (कृष्णा जी) | Helpline: 8504985149</font>", ParagraphStyle('TC', fontName=reg_font, fontSize=8, textColor=colors.HexColor("#64748B"), leading=11)),
        Paragraph("<b>For " + config.get("institute_name", "APNA COMPUTER") + "</b><br/><br/><br/>____________________________<br/><b>Authorized Signatory / Seal</b>", ParagraphStyle('AS', fontName=reg_font, fontSize=9, textColor=brand_navy, alignment=2, leading=13))
    ]]
    sig_table = Table(sig_data, colWidths=[4.2*inch, 2.9*inch])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(sig_table)

    doc.build(elements)

# ─────────────────────────────────────────────────────────────────────────────
# Main ReceiptGenerator Interface
# ─────────────────────────────────────────────────────────────────────────────
class ReceiptGenerator:
    @staticmethod
    def generate_fee_receipt(admission_data: dict, output_pdf_path: str) -> str:
        config = load_config()

        # Step 1: High-Speed Persistent Chromium Worker rendering (< 0.5s)
        try:
            html = build_receipt_html(admission_data, config)
            worker = _ChromiumWorker.get_instance()
            worker.render_pdf(html, output_pdf_path)
            if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 1000:
                return output_pdf_path
        except Exception as e:
            print(f"[ReceiptGenerator] Chromium rendering error: {e}, falling back to ReportLab...")

        # Step 2: Fallback to ReportLab if Chromium pool fails
        try:
            _render_receipt_with_reportlab_fallback(admission_data, output_pdf_path)
        except Exception as e:
            print(f"[ReceiptGenerator] ReportLab fallback error: {e}")
            raise e

        return output_pdf_path
