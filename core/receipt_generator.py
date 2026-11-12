import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core.config import load_config
from core.database import DatabaseManager

def get_unicode_fonts():
    reg_font = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    oblique_font = 'Helvetica-Oblique'
    
    win_nirmala = 'C:/Windows/Fonts/Nirmala.ttf'
    win_nirmala_b = 'C:/Windows/Fonts/NirmalaB.ttf'
    if os.path.exists(win_nirmala) and os.path.exists(win_nirmala_b):
        try:
            if 'Nirmala' not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont('Nirmala', win_nirmala))
            if 'Nirmala-Bold' not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont('Nirmala-Bold', win_nirmala_b))
            reg_font = 'Nirmala'
            bold_font = 'Nirmala-Bold'
            oblique_font = 'Nirmala'
        except Exception:
            pass
    return reg_font, bold_font, oblique_font

class ReceiptGenerator:
    @staticmethod
    def generate_fee_receipt(admission_data: dict, output_pdf_path: str):
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

        # Color palette
        brand_navy = colors.HexColor("#00183A")
        brand_cyan = colors.HexColor("#00B4D8")
        dark_text = colors.HexColor("#1E293B")
        light_bg = colors.HexColor("#F8FAFC")

        # Custom Paragraph Styles with Unicode support
        title_style = ParagraphStyle(
            'InstTitle',
            parent=styles['Heading1'],
            fontName=bold_font,
            fontSize=18,
            textColor=brand_navy,
            leading=22,
            alignment=0
        )
        tagline_style = ParagraphStyle(
            'InstTagline',
            parent=styles['Normal'],
            fontName=oblique_font,
            fontSize=9.5,
            textColor=colors.HexColor("#475569"),
            leading=13
        )
        receipt_badge_style = ParagraphStyle(
            'ReceiptBadge',
            parent=styles['Normal'],
            fontName=bold_font,
            fontSize=11,
            textColor=brand_navy,
            leading=15,
            alignment=2
        )
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName=bold_font,
            fontSize=9,
            textColor=colors.HexColor("#334155"),
            leading=12
        )
        meta_val_style = ParagraphStyle(
            'MetaVal',
            parent=styles['Normal'],
            fontName=reg_font,
            fontSize=9,
            textColor=dark_text,
            leading=12
        )
        cell_right_style = ParagraphStyle(
            'CellRight',
            parent=styles['Normal'],
            fontName=reg_font,
            fontSize=9,
            textColor=dark_text,
            alignment=2,
            leading=12
        )
        cell_right_bold = ParagraphStyle(
            'CellRightBold',
            parent=styles['Normal'],
            fontName=bold_font,
            fontSize=9.5,
            textColor=brand_navy,
            alignment=2,
            leading=13
        )

        # Header Table: Logo on Left, Institute Details in Middle/Right
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
            Paragraph(config.get('institute_tagline', 'कंप्यूटर एवं कौशल प्रशिक्षण संस्थान'), tagline_style),
            Paragraph(f"Phone: {config.get('institute_phone', '8504985149')} | Email: {config.get('institute_email', 'krishnaskb143@gmail.com')}", meta_val_style),
            Paragraph(config.get('institute_address', ''), meta_val_style)
        ]

        header_table = Table([[logo_elem, inst_info]], colWidths=[1.3*inch, 5.8*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6)
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=2, color=brand_navy, spaceBefore=6, spaceAfter=12))

        # Receipt Number & Date Banner
        banner_data = [
            [
                Paragraph("<b>OFFICIAL FEE PAYMENT RECEIPT / फीस रसीद</b>", ParagraphStyle('BTitle', fontName=bold_font, fontSize=11, textColor=brand_navy, leading=14)),
                Paragraph(f"<b>Receipt No:</b> {admission_data.get('admission_no', 'N/A')}<br/><b>Date:</b> {admission_data.get('payment_date', datetime.now().strftime('%Y-%m-%d'))}", receipt_badge_style)
            ]
        ]
        banner_table = Table(banner_data, colWidths=[4.2*inch, 2.9*inch])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(banner_table)
        elements.append(Spacer(1, 14))

        # Student Information Grid
        student_grid = [
            [
                Paragraph("<b>Student Name:</b>", meta_label_style),
                Paragraph(str(admission_data.get("student_name", "")), meta_val_style),
                Paragraph("<b>Mobile No:</b>", meta_label_style),
                Paragraph(str(admission_data.get("phone", "")), meta_val_style)
            ],
            [
                Paragraph("<b>Registered Email:</b>", meta_label_style),
                Paragraph(str(admission_data.get("email", "")), meta_val_style),
                Paragraph("<b>Admission Type:</b>", meta_label_style),
                Paragraph(str(admission_data.get("admission_source", "Telecalling")), meta_val_style)
            ],
            [
                Paragraph("<b>Account Beneficiary:</b>", meta_label_style),
                Paragraph(str(admission_data.get("account_holder", "")), meta_val_style),
                Paragraph("<b>Payment Mode:</b>", meta_label_style),
                Paragraph(str(admission_data.get("payment_mode", "UPI")), meta_val_style)
            ]
        ]
        if admission_data.get("utr_no"):
            student_grid.append([
                Paragraph("<b>UPI / UTR Ref No:</b>", meta_label_style),
                Paragraph(str(admission_data.get("utr_no", "")), meta_val_style),
                Paragraph("<b>Issued By Staff:</b>", meta_label_style),
                Paragraph(str(admission_data.get("caller_staff_name", "Office Staff")), meta_val_style)
            ])

        student_table = Table(student_grid, colWidths=[1.5*inch, 2.3*inch, 1.4*inch, 1.9*inch])
        student_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elements.append(student_table)
        elements.append(Spacer(1, 16))

        # Fee Details Table
        fee_headers = [
            Paragraph("<b>#</b>", ParagraphStyle('FH', fontName=bold_font, textColor=colors.white)),
            Paragraph("<b>Description / Course Enrolled</b>", ParagraphStyle('FH', fontName=bold_font, textColor=colors.white)),
            Paragraph("<b>Standard Fee (Rs.)</b>", ParagraphStyle('FH_R', fontName=bold_font, textColor=colors.white, alignment=2)),
            Paragraph("<b>Discount (Rs.)</b>", ParagraphStyle('FH_R', fontName=bold_font, textColor=colors.white, alignment=2)),
            Paragraph("<b>Net Amount Paid (Rs.)</b>", ParagraphStyle('FH_R', fontName=bold_font, textColor=colors.white, alignment=2))
        ]

        orig_fee = float(admission_data.get("original_fee") or admission_data.get("final_amount") or 0.0)
        disc_fee = float(admission_data.get("concession_amount") or 0.0)
        paid_fee = float(admission_data.get("final_amount") or 0.0)
        net_fee = max(0.0, orig_fee - disc_fee)
        balance_due = max(0.0, net_fee - paid_fee)

        fee_row = [
            Paragraph("1", meta_val_style),
            Paragraph(f"<b>{admission_data.get('courses_taken', 'Course')}</b>", meta_val_style),
            Paragraph(f"Rs. {orig_fee:,.2f}", cell_right_style),
            Paragraph(f"Rs. {disc_fee:,.2f}" if disc_fee > 0 else "-", cell_right_style),
            Paragraph(f"<b>Rs. {paid_fee:,.2f}</b>", cell_right_bold)
        ]

        total_row = [
            "",
            Paragraph("<b>TOTAL RECEIVED AMOUNT / कुल प्राप्त राशि:</b>", meta_label_style),
            Paragraph(f"Rs. {orig_fee:,.2f}", cell_right_style),
            Paragraph(f"Rs. {disc_fee:,.2f}", cell_right_style),
            Paragraph(f"<b>Rs. {paid_fee:,.2f}</b>", cell_right_bold)
        ]

        due_text = "<b>PAID IN FULL / पूर्ण चुकता (Rs. 0.00)</b>" if balance_due == 0 else f"<font color='#DC2626'><b>BALANCE DUE / शेष बकाया: Rs. {balance_due:,.2f}</b></font>"
        due_row = [
            "",
            Paragraph(due_text, meta_label_style),
            "",
            "",
            Paragraph(f"<b>Rs. {balance_due:,.2f}</b>" if balance_due > 0 else "Rs. 0.00", cell_right_bold)
        ]

        fee_table_data = [fee_headers, fee_row, total_row, due_row]
        fee_table = Table(fee_table_data, colWidths=[0.4*inch, 3.2*inch, 1.2*inch, 1.0*inch, 1.3*inch])
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

        # Check for installment history
        adm_id = admission_data.get("id")
        if adm_id:
            try:
                db = DatabaseManager.get_instance()
                inst_list = db.get_installments(adm_id)
                if inst_list:
                    elements.append(Spacer(1, 8))
                    elements.append(Paragraph("<b>Payment Installment History / किस्त भुगतान इतिहास:</b>", meta_label_style))
                    inst_headers = [
                        Paragraph("<b>Receipt No</b>", meta_label_style),
                        Paragraph("<b>Date</b>", meta_label_style),
                        Paragraph("<b>Mode</b>", meta_label_style),
                        Paragraph("<b>Amount (Rs.)</b>", ParagraphStyle('InstR', fontName=bold_font, fontSize=9, alignment=2))
                    ]
                    inst_rows = [inst_headers]
                    for inst in inst_list:
                        inst_rows.append([
                            Paragraph(str(inst["receipt_no"]), meta_val_style),
                            Paragraph(str(inst["payment_date"]), meta_val_style),
                            Paragraph(str(inst["payment_mode"]), meta_val_style),
                            Paragraph(f"Rs. {inst['amount_paid']:,.2f}", cell_right_style)
                        ])
                    inst_tbl = Table(inst_rows, colWidths=[2.2*inch, 1.6*inch, 1.6*inch, 1.7*inch])
                    inst_tbl.setStyle(TableStyle([
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                        ('PADDING', (0,0), (-1,-1), 4),
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
                    ]))
                    elements.append(inst_tbl)
            except Exception:
                pass

        if admission_data.get("concession_reason"):
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"<i>* Discount Remark: {admission_data.get('concession_reason')}</i>", tagline_style))

        elements.append(Spacer(1, 28))

        # Signatures & Verification Row
        sig_data = [
            [
                Paragraph("<b>Terms & Conditions:</b><br/>1. Fees once paid is non-refundable.<br/>2. Course access credentials are sent to registered email.<br/>3. System generated authorized receipt.", ParagraphStyle('TC', fontName=reg_font, fontSize=8, textColor=colors.HexColor("#64748B"), leading=11)),
                Paragraph("<b>For " + config.get("institute_name", "APNA COMPUTER") + "</b><br/><br/><br/>____________________________<br/><b>Authorized Signatory / Seal</b>", ParagraphStyle('AS', fontName=reg_font, fontSize=9, textColor=brand_navy, alignment=2, leading=13))
            ]
        ]
        sig_table = Table(sig_data, colWidths=[4.2*inch, 2.9*inch])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(sig_table)
        elements.append(Spacer(1, 18))

        # Social Media & YouTube Footer Banner
        social_parts = []
        if config.get("youtube_link"):
            social_parts.append(f"YouTube: {config.get('youtube_link')}")
        if config.get("instagram_link"):
            social_parts.append(f"Instagram: {config.get('instagram_link')}")
        if config.get("telegram_link"):
            social_parts.append(f"Telegram: {config.get('telegram_link')}")

        if social_parts:
            social_text = " | ".join(social_parts)
            footer_data = [[Paragraph(f"<b>Follow us for Free Classes & Updates:</b> {social_text}", ParagraphStyle('Soc', fontName=reg_font, fontSize=8, textColor=colors.HexColor("#0284C7"), alignment=1, leading=10))]]
            footer_table = Table(footer_data, colWidths=[7.1*inch])
            footer_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
                ('PADDING', (0,0), (-1,-1), 6)
            ]))
            elements.append(footer_table)

        doc.build(elements)
        return output_pdf_path
