import os
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from core.config import load_config
from core.database import DatabaseManager

class IDCardGenerator:
    @staticmethod
    def generate_id_card(student_data: dict, output_pdf_path: str):
        config = load_config()
        
        # Standard ID Card Size: 250pt x 380pt (Approx 3.5in x 5.2in pocket card)
        card_size = (250, 380)
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=card_size,
            rightMargin=10,
            leftMargin=10,
            topMargin=10,
            bottomMargin=10
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        brand_navy = colors.HexColor("#00183A")
        brand_cyan = colors.HexColor("#00B4D8")
        dark_text = colors.HexColor("#0F172A")
        card_border = colors.HexColor("#CBD5E1")
        
        inst_name = config.get("institute_name", "APNA COMPUTER").upper()
        inst_tagline = config.get("institute_tagline", "Computer & Skill Training Institute")
        inst_phone = config.get("institute_phone", "+91 98765 43210")
        
        title_style = ParagraphStyle(
            'IDTitle',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=colors.white,
            alignment=1, # Center
            leading=13
        )
        tag_style = ParagraphStyle(
            'IDTag',
            fontName='Helvetica',
            fontSize=6,
            textColor=colors.HexColor("#94A3B8"),
            alignment=1,
            leading=8
        )
        badge_style = ParagraphStyle(
            'IDBadge',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=brand_navy,
            alignment=1,
            leading=10
        )
        name_style = ParagraphStyle(
            'IDName',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=brand_navy,
            alignment=1,
            leading=13
        )
        label_style = ParagraphStyle(
            'IDLabel',
            fontName='Helvetica-Bold',
            fontSize=7,
            textColor=colors.HexColor("#64748B"),
            leading=9
        )
        val_style = ParagraphStyle(
            'IDVal',
            fontName='Helvetica-Bold',
            fontSize=7.5,
            textColor=dark_text,
            leading=9
        )
        footer_style = ParagraphStyle(
            'IDFooter',
            fontName='Helvetica-Bold',
            fontSize=6,
            textColor=colors.white,
            alignment=1,
            leading=8
        )
        
        # 1. Header Box
        header_text = [
            Paragraph(inst_name, title_style),
            Paragraph(inst_tagline, tag_style)
        ]
        header_tbl = Table([[header_text]], colWidths=[230])
        header_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), brand_navy),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_tbl)
        
        # 2. Sub-Header: STUDENT IDENTITY CARD
        sub_tbl = Table([[Paragraph("STUDENT IDENTITY CARD", badge_style)]], colWidths=[230])
        sub_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), brand_cyan),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(sub_tbl)
        elements.append(Spacer(1, 10))
        
        # 3. Photo Box Placeholder (Clean Avatar)
        avatar_text = Paragraph("<b>[ STUDENT PHOTO ]</b>", ParagraphStyle('Av', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#94A3B8"), alignment=1))
        avatar_tbl = Table([[avatar_text]], colWidths=[70], rowHeights=[75])
        avatar_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 1, brand_cyan),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(avatar_tbl)
        elements.append(Spacer(1, 8))
        
        # 4. Student Name
        elements.append(Paragraph(student_data.get("student_name", "Student Name").title(), name_style))
        elements.append(Spacer(1, 6))
        
        # 5. Details Table
        adm_date = student_data.get("payment_date", datetime.now().strftime("%Y-%m-%d"))
        try:
            valid_year = str(int(adm_date[:4]) + 1)
        except Exception:
            valid_year = "2027"
            
        details = [
            [Paragraph("Roll / Adm No:", label_style), Paragraph(student_data.get("admission_no", "-"), val_style)],
            [Paragraph("Course Enrolled:", label_style), Paragraph(student_data.get("courses_taken", "-")[:28], val_style)],
            [Paragraph("Contact Phone:", label_style), Paragraph(student_data.get("phone", "-"), val_style)],
            [Paragraph("Admission Date:", label_style), Paragraph(adm_date, val_style)],
            [Paragraph("Valid Upto:", label_style), Paragraph(f"31-Dec-{valid_year}", val_style)],
        ]
        details_tbl = Table(details, colWidths=[80, 140])
        details_tbl.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(details_tbl)
        elements.append(Spacer(1, 14))
        
        # 6. Signature Row
        sig_tbl = Table([
            [Paragraph("Student Sign", label_style), Paragraph("Authorized Director Sign", ParagraphStyle('AS', parent=label_style, alignment=2))]
        ], colWidths=[110, 110])
        elements.append(sig_tbl)
        elements.append(Spacer(1, 8))
        
        # 7. Footer Stripe
        footer_tbl = Table([[Paragraph(f"Helpline: {inst_phone} | apna.computer.rms", footer_style)]], colWidths=[230])
        footer_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), brand_navy),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(footer_tbl)
        
        doc.build(elements)
        return output_pdf_path
