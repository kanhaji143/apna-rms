import os
import sys
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Nirmala UI Hindi Fonts from Windows
FONT_REGULAR = "NirmalaUI"
FONT_BOLD = "NirmalaUI-Bold"

try:
    pdfmetrics.registerFont(TTFont("NirmalaUI", r"C:\Windows\Fonts\Nirmala.ttf"))
    pdfmetrics.registerFont(TTFont("NirmalaUI-Bold", r"C:\Windows\Fonts\NirmalaB.ttf"))
except Exception as e:
    print(f"Warning: Could not register Nirmala font, trying Aparajita: {e}")
    try:
        pdfmetrics.registerFont(TTFont("NirmalaUI", r"C:\Windows\Fonts\aparaj.ttf"))
        pdfmetrics.registerFont(TTFont("NirmalaUI-Bold", r"C:\Windows\Fonts\aparajb.ttf"))
    except Exception as e2:
        print(f"Fallback font error: {e2}")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # No header/footer on cover page

        self.saveState()
        self.setFont(FONT_BOLD, 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (Pure Hindi & English in Nirmala UI font)
        self.drawString(36, 805, "APNA COMPUTER RMS — सम्पूर्ण ऑपरेटिंग व ट्रेनिंग मैनुअल (Complete User Guide)")
        self.drawRightString(559, 805, "Helpline: 8504985149")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 798, 559, 798)

        # Footer
        self.line(36, 45, 559, 45)
        self.drawString(36, 32, "Created BY: Apna Computer  |  Contact: 8504985149")
        self.drawRightString(559, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_manual_pdf(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=48,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    elements = []

    # Colors
    navy = colors.HexColor("#00183A")
    cyan = colors.HexColor("#00B4D8")
    accent_green = colors.HexColor("#10B981")
    dark_gray = colors.HexColor("#1E293B")
    light_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    # Typography Styles using Nirmala UI Font
    cover_title = ParagraphStyle(
        'CoverTitle',
        fontName=FONT_BOLD,
        fontSize=22,
        textColor=navy,
        leading=28,
        alignment=1
    )
    cover_sub = ParagraphStyle(
        'CoverSub',
        fontName=FONT_BOLD,
        fontSize=12,
        textColor=cyan,
        leading=16,
        alignment=1
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        fontName=FONT_BOLD,
        fontSize=13,
        textColor=navy,
        leading=17,
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        fontName=FONT_BOLD,
        fontSize=10.5,
        textColor=cyan,
        leading=14,
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName=FONT_REGULAR,
        fontSize=9.5,
        textColor=dark_gray,
        leading=14
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        fontName=FONT_REGULAR,
        fontSize=9,
        textColor=dark_gray,
        leading=13.5,
        leftIndent=14
    )
    table_cell = ParagraphStyle(
        'TableCell',
        fontName=FONT_REGULAR,
        fontSize=8.5,
        textColor=dark_gray,
        leading=12
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName=FONT_BOLD,
        fontSize=8.5,
        textColor=navy,
        leading=12
    )
    table_header = ParagraphStyle(
        'TableHead',
        fontName=FONT_BOLD,
        fontSize=9,
        textColor=colors.white,
        leading=12
    )
    note_box_style = ParagraphStyle(
        'NoteText',
        fontName=FONT_REGULAR,
        fontSize=9,
        textColor=colors.HexColor("#065F46"),
        leading=13.5
    )

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    elements.append(Spacer(1, 40))

    banner_data = [[
        Paragraph("<font color='#03F9FD'><b>APNA COMPUTER RMS v2.0</b></font><br/><font color='#FFFFFF' size='11'>ऑफ़लाइन रिकॉर्ड व संस्थान प्रबंधन सॉफ्टवेयर</font>", ParagraphStyle('Bnr', fontName=FONT_BOLD, fontSize=18, alignment=1, leading=22))
    ]]
    banner_tbl = Table(banner_data, colWidths=[520], rowHeights=[70])
    banner_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(banner_tbl)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph("सम्पूर्ण ऑपरेटिंग व स्टाफ ट्रेनिंग गाइड", cover_title))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Complete Professional Staff Training & User Manual", cover_sub))
    elements.append(Spacer(1, 15))

    elements.append(HRFlowable(width="60%", thickness=2, color=cyan, spaceBefore=8, spaceAfter=18))

    cover_desc = (
        "यह गाइड कोचिंग संस्थानों, कंप्यूटर प्रशिक्षण केंद्रों एवं स्कूलों के लिए तैयार किए गए "
        "<b>APNA Computer RMS</b> सॉफ्टवेयर के सफल संचालन, स्टाफ प्रशिक्षण, फीस कलेक्शन, "
        "बकाया किस्त नियंत्रण, आई-कार्ड प्रिंटिंग एवं सुरक्षा नियमों का सम्पूर्ण आधिकारिक मार्गदर्शक है।"
    )
    elements.append(Paragraph(cover_desc, ParagraphStyle('CD', fontName=FONT_REGULAR, fontSize=10, textColor=dark_gray, leading=15, alignment=1)))
    elements.append(Spacer(1, 35))

    # Feature Highlights Table
    badges = [
        [
            Paragraph("<b>100% ऑफ़लाइन</b><br/>बिना इंटरनेट के कंप्यूटर पर सुपरफास्ट", ParagraphStyle('Bg', fontName=FONT_REGULAR, fontSize=8.5, leading=11.5, alignment=1)),
            Paragraph("<b>0% API Key</b><br/>कोई मासिक खर्च नहीं, कोई API नहीं", ParagraphStyle('Bg', fontName=FONT_REGULAR, fontSize=8.5, leading=11.5, alignment=1)),
            Paragraph("<b>बैंक-लेवल सुरक्षा</b><br/>डुप्लीकेट UTR व फ्रॉड ब्लॉकर", ParagraphStyle('Bg', fontName=FONT_REGULAR, fontSize=8.5, leading=11.5, alignment=1)),
            Paragraph("<b>1-क्लिक आई-कार्ड</b><br/>पॉकेट आई-कार्ड व रसीद PDF", ParagraphStyle('Bg', fontName=FONT_REGULAR, fontSize=8.5, leading=11.5, alignment=1))
        ]
    ]
    badge_tbl = Table(badges, colWidths=[125, 125, 125, 125])
    badge_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(badge_tbl)
    elements.append(Spacer(1, 45))

    # Author & Contact Box
    author_info = [
        [Paragraph("<b>सॉफ्टवेयर निर्माता (Created By):</b>", table_cell_bold), Paragraph("<b>Apna Computer</b>", table_cell_bold)],
        [Paragraph("<b>हेल्पलाइन व सपोर्ट (Contact No.):</b>", table_cell_bold), Paragraph("<b>8504985149</b>", table_cell_bold)],
        [Paragraph("<b>आधिकारिक ईमेल:</b>", table_cell_bold), Paragraph("krishnaskb143@gmail.com", table_cell)],
        [Paragraph("<b>सॉफ्टवेयर संस्करण:</b>", table_cell_bold), Paragraph("v2.0 Enterprise Standalone Edition", table_cell)],
        [Paragraph("<b>प्रकाशन तिथि:</b>", table_cell_bold), Paragraph(datetime.now().strftime("%d-%B-%Y"), table_cell)],
    ]
    author_tbl = Table(author_info, colWidths=[180, 240])
    author_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DBEAFE")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(author_tbl)

    elements.append(PageBreak())

    # =========================================================================
    # MODULE 1 & 2: QUICK STARTUP & 3 ROLES
    # =========================================================================
    elements.append(Paragraph("1. सॉफ्टवेयर परिचय व त्वरित शुरुआत (Quick Startup)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "<b>APNA Computer RMS</b> एक पोर्टेबल स्टैंडअलोन सॉफ्टवेयर है। इसे किसी भी विंडोज कंप्यूटर (Windows 10/11) "
        "पर चलाने के लिए किसी भी जटिल इंस्टॉलेशन की आवश्यकता नहीं होती।", body_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("• <b>पेनड्राइव से सीधे चालू करें:</b> पेनड्राइव लगाएं और <b>APNA_Computer_RMS.exe</b> पर डबल-क्लिक करें।", bullet_style))
    elements.append(Paragraph("• <b>100% ऑफ़लाइन कार्यप्रणाली:</b> सारा डेटा आपके कंप्यूटर या पेनड्राइव के सुरक्षित डेटाबेस में रहता है।", bullet_style))
    elements.append(Paragraph("• <b>संस्थान की ब्रांडिंग:</b> सेटिंग्स मेन्यू से 1-क्लिक में अपनी कोचिंग का नाम, पता, फोन व लोगो बदल सकते हैं।", bullet_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. त्रि-स्तरीय यूज़र रोल्स एवं डेटा सुरक्षा (3-Tier RBAC)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "कोचिंग में डेटा चोरी (Data Leak) और अनधिकृत छेड़छाड़ रोकने के लिए सिस्टम में 3 अलग-अलग यूज़र रोल्स दिए गए हैं:", body_style
    ))
    elements.append(Spacer(1, 6))

    roles_data = [
        [Paragraph("यूज़र रोल", table_header), Paragraph("डिफ़ॉल्ट खाता", table_header), Paragraph("अधिकार एवं कार्यक्षेत्र (Permissions)", table_header)],
        [
            Paragraph("<b>Admin (मालिक)</b>", table_cell_bold),
            Paragraph("User: admin<br/>Pass: (Setup Password)", table_cell),
            Paragraph("<b>सम्पूर्ण नियंत्रण:</b> कुल कलेक्शन, शुद्ध मुनाफा (P&L), सेटिंग्स, स्टाफ खाता प्रबंधन, एवं <b>पासवर्ड-प्रोटेक्टेड रिकॉर्ड डिलीशन</b>।", table_cell)
        ],
        [
            Paragraph("<b>Accountant (अकाउंटेंट)</b>", table_cell_bold),
            Paragraph("User: accountant<br/>Pass: accountant@123", table_cell),
            Paragraph("<b>खर्च व फीस प्रबंधन:</b> नया खर्च दर्ज करना, फीस रसीद देखना, खर्च रिपोर्ट एक्सेल में निकालना। (रिकॉर्ड डिलीट करना व सेटिंग्स पूरी तरह बंद)।", table_cell)
        ],
        [
            Paragraph("<b>Counselor (स्टाफ)</b>", table_cell_bold),
            Paragraph("User: counselor<br/>Pass: staff@123", table_cell),
            Paragraph("<b>एडमिशन डेस्क:</b> नया एडमिशन लेना, फीस रसीद व आई-कार्ड प्रिंट करना, टाइम-टेबल देखना। <b>(कुल कलेक्शन, खर्चे और बल्क एक्सेल एक्सपोर्ट कॉलर से पूरी तरह छिपे रहते हैं ताकि डेटा चोरी न हो)</b>।", table_cell)
        ]
    ]
    roles_tbl = Table(roles_data, colWidths=[110, 120, 290])
    roles_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg])
    ]))
    elements.append(roles_tbl)
    elements.append(Spacer(1, 14))

    # =========================================================================
    # MODULE 3: ADMISSION STANDARD OPERATING PROCEDURE
    # =========================================================================
    elements.append(Paragraph("3. नया एडमिशन दर्ज करने की मानक प्रक्रिया (Admission SOP)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "काउंसलर या स्टाफ जब नया एडमिशन फॉर्म भरता है, तो सिस्टम गलत इनपुट रोकने के लिए कड़े नियम लागू करता है:", body_style
    ))
    elements.append(Spacer(1, 6))

    sop_data = [
        [Paragraph("फील्ड (Field)", table_header), Paragraph("नियम (Validation Rule)", table_header), Paragraph("सिस्टम सुरक्षा व्यवहार", table_header)],
        [
            Paragraph("<b>Student Full Name</b>", table_cell_bold),
            Paragraph("कम से कम 2 अक्षर, केवल नाम", table_cell),
            Paragraph("स्वतः शुद्ध होकर <b>Title Case</b> (उदा: Rahul Kumar Sharma) में सुरक्षित होता है।", table_cell)
        ],
        [
            Paragraph("<b>Phone (10 Digits)</b>", table_cell_bold),
            Paragraph("ठीक 10 अंक, 6, 7, 8, 9 से शुरुआत", table_cell),
            Paragraph("<b>की-स्ट्रोक फिल्टरिंग:</b> एबीसीडी या स्पेशल कैरेक्टर टाइप ही नहीं होगा। 10 अंक से ज्यादा नहीं जाएगा।", table_cell)
        ],
        [
            Paragraph("<b>Payment Date</b>", table_cell_bold),
            Paragraph("कैलेंडर YYYY-MM-DD", table_cell),
            Paragraph("गलत तारीख या टेक्स्ट डालने पर फॉर्म सबमिट नहीं होगा। डिफ़ॉल्ट रूप से आज की तारीख रहती है।", table_cell)
        ],
        [
            Paragraph("<b>Payment Mode</b>", table_cell_bold),
            Paragraph("UPI / Cash / Card", table_cell),
            Paragraph("<b>कैश मोड:</b> अकाउंट स्वतः <i>Cash (काउंटर)</i> सेट हो जाता है और स्क्रीनशॉट वैकल्पिक रहता है।<br/><b>UPI मोड:</b> 12-अंक का UTR और स्क्रीनशॉट अनिवार्य होता है।", table_cell)
        ],
        [
            Paragraph("<b>Duplicate UTR Block</b>", table_cell_bold),
            Paragraph("100% यूनिक UTR नंबर", table_cell),
            Paragraph("यदि कोई स्टाफ पुराना UTR दोबारा डालेगा, तो सिस्टम तुरंत रोक देगा और पिछले छात्र का नाम दिखाएगा।", table_cell)
        ]
    ]
    sop_tbl = Table(sop_data, colWidths=[120, 140, 260])
    sop_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg])
    ]))
    elements.append(sop_tbl)
    elements.append(Spacer(1, 10))

    note_box = [
        [Paragraph("<b>एडमिशन के तुरंत बाद 1-क्लिक एक्शन:</b><br/>"
                   "1. <b>Print Fee Receipt:</b> तुरंत A4 साइज की वैध रसीद खुलती है जिसे प्रिंट किया जा सकता है।<br/>"
                   "2. <b>Send WhatsApp:</b> 1-क्लिक में छात्र के मोबाइल पर स्वागत व रसीद का पूरा संदेश चला जाता है (बिना किसी API के)।", note_box_style)]
    ]
    note_tbl = Table(note_box, colWidths=[520])
    note_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#D1FAE5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10B981")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(note_tbl)

    elements.append(PageBreak())

    # =========================================================================
    # MODULE 4 & 5: INSTALLMENT TRACKER & ID CARDS
    # =========================================================================
    elements.append(Paragraph("4. बकाया फीस व किस्त प्रबंधन (Installment & Due Fee Tracker)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "कोचिंग में अधिकांश छात्र फीस किस्तों में जमा करते हैं। सॉफ्टवेयर इस पूरी प्रक्रिया को स्वचालित रखता है:", body_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("• <b>ऑटो-कैलकुलेशन:</b> बकाया राशि (Balance Due) = (कुल फीस - छूट) - जमा राशि", bullet_style))
    elements.append(Paragraph("• <b>लाइव अलर्ट:</b> 'सभी Records' में जिस छात्र की फीस बाकी होगी, उसके आगे नारंगी रंग में <b>बाकी ₹2,000</b> साफ दिखाई देगा।", bullet_style))
    elements.append(Paragraph("• <b>किस्त जमा बटन [Card Icon]:</b> छात्र जब 1 महीने बाद दूसरी किस्त लेकर आए, तो बस किस्त बटन दबाएं।", bullet_style))
    elements.append(Paragraph("• <b>अपडेटेड रसीद:</b> किस्त दर्ज होते ही रसीद स्वतः अपडेट हो जाती है और नीचे किस्त का पूरा इतिहास (1st Installment, 2nd Installment) दर्ज हो जाता है।", bullet_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("5. 1-क्लिक छात्र आई-कार्ड जनरेटर (Student ID Card PDF)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "छात्रों को क्लास में प्रवेश हेतु आई-कार्ड जारी करने के लिए 'सभी Records' में प्रत्येक छात्र के आगे <b>[ID Card Icon]</b> दिया गया है:", body_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("• <b>पॉकेट साइज फॉर्मेट:</b> स्टैंडर्ड 3.5\" x 5.2\" कार्ड साइज जो लैमिनेशन और डोरी (Lanyard) के लिए उपयुक्त है।", bullet_style))
    elements.append(Paragraph("• <b>संस्थान की ब्रांडिंग:</b> आपके संस्थान का नाम, स्लोगन और हेल्पलाइन ऊपर नेवी ब्लू व इलेक्ट्रिक सायन में अंकित रहती है।", bullet_style))
    elements.append(Paragraph("• <b>छात्र का विवरण:</b> छात्र का पूरा नाम, रोल/एडमिशन नंबर, नामांकित कोर्स, मोबाइल नंबर और 1 वर्ष की वैधता।", bullet_style))
    elements.append(Paragraph("• <b>हस्ताक्षर व मुहर:</b> छात्र के हस्ताक्षर और अधिकृत डायरेक्टर/संस्थान मुहर का स्थान दिया गया है।", bullet_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("6. कोर्स एक्टिवेशन कतार (Activation Queue)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "जब कॉलर फोन पर ऑनलाइन एडमिशन दर्ज करता है, तो छात्र <b>Pending (लाल झंडा)</b> कतार में चला जाता है। "
        "जब संस्थान बैंक खाते में पैसा चेक कर लेता है, तो Admin या Coordinator 1-क्लिक में <b>'Activate Now'</b> दबाकर छात्र का बैच व पोर्टल एक्सेस चालू कर देता है।", body_style
    ))
    elements.append(Spacer(1, 14))

    # =========================================================================
    # MODULE 7, 8 & 9: EXPENSES, EOD EMAIL & BACKUP
    # =========================================================================
    elements.append(Paragraph("7. खर्च प्रबंधन व शुद्ध मुनाफा (Expense & P&L Management)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "सॉफ्टवेयर में कोचिंग का P&L (Profit & Loss) लाइव कैलकुलेट होता है: "
        "<b>शुद्ध बचत (Net Profit) = कुल प्राप्त फीस - कुल संस्थान खर्चे</b>", body_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("• <b>खर्च की श्रेणियां:</b> किराया (Rent), बिजली, फैकल्टी वेतन, इंटरनेट, स्टेशनरी आदि (अपनी श्रेणी भी टाइप कर सकते हैं)।", bullet_style))
    elements.append(Paragraph("• <b>अकाउंटेंट एक्सेस:</b> अकाउंटेंट यूजर खर्चे दर्ज कर सकता है और सीए/टैक्स ऑडिट हेतु एक्सेल शीट एक्सपोर्ट कर सकता है।", bullet_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("8. दैनिक EOD रिपोर्ट व 1-क्लिक जीमेल बैकअप (Daily Reporting)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(
        "दिनभर का काम खत्म होने पर शाम को स्टाफ <b>Reports & Daily Mail</b> में जाकर लाल बटन दबाएगा: "
        "<b>'1-क्लिक जीमेल में भेजें (Open in Gmail)'</b>।", body_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("• आज की एडमिशन एक्सेल शीट और सभी स्क्रीनशॉट्स का ज़िप अपने आप स्क्रीन पर फोल्डर में खुल जाएगा।", bullet_style))
    elements.append(Paragraph("• ब्राउज़र में जीमेल कंपोज़ विंडो खुलेगी जिसमें <b>To: krishnaskb143@gmail.com</b> पहले से भरा होगा।", bullet_style))
    elements.append(Paragraph("• स्टाफ दोनों फाइलें ड्रैग करके Send दबा देगा। <b>जीरो पासवर्ड, 100% सफल!</b>", bullet_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("9. सिस्टम बैकअप व डेटा सुरक्षा (Disaster Recovery)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph("• <b>1-क्लिक पेनड्राइव बैकअप:</b> Settings में जाकर 'पूर्ण सिस्टम बैकअप' दबाकर 1 फाइल में सारा डेटा व स्क्रीनशॉट्स पेनड्राइव में सुरक्षित कर सकते हैं।", bullet_style))
    elements.append(Paragraph("• <b>Google Drive ऑटो-सिंक:</b> कंप्यूटर में Google Drive Desktop इंस्टॉल करके उसका फोल्डर सेटिंग्स में चुन लें, डेटा स्वतः क्लाउड पर सुरक्षित होता रहेगा।", bullet_style))

    elements.append(PageBreak())

    # =========================================================================
    # SHORTCUTS, FAQS & SUPPORT
    # =========================================================================
    elements.append(Paragraph("10. आइकॉन गाइड एवं क्विक एक्शन चीट-शीट (Quick Icon Guide)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    icons_data = [
        [Paragraph("बटन / एक्शन", table_header), Paragraph("फीचर का नाम", table_header), Paragraph("कार्य एवं उपयोग (Action)", table_header)],
        [Paragraph("<b>[ View ]</b>", table_cell_bold), Paragraph("View Screenshot", table_cell), Paragraph("छात्र द्वारा भेजे गए UPI पेमेंट स्क्रीनशॉट को बड़ा करके देखें।", table_cell)],
        [Paragraph("<b>[ Receipt ]</b>", table_cell_bold), Paragraph("Print Receipt", table_cell), Paragraph("छात्र की आधिकारिक A4 साइज फीस रसीद (PDF) खोलें व प्रिंट करें।", table_cell)],
        [Paragraph("<b>[ ID Card ]</b>", table_cell_bold), Paragraph("Print ID Card", table_cell), Paragraph("संस्थान के लोगो व छात्र विवरण के साथ पॉकेट आई-कार्ड PDF बनाएं।", table_cell)],
        [Paragraph("<b>[ Pay ]</b>", table_cell_bold), Paragraph("Pay Installment", table_cell), Paragraph("छात्र की बाकी फीस की अगली किस्त जमा करें और रसीद अपडेट करें।", table_cell)],
        [Paragraph("<b>[ WhatsApp ]</b>", table_cell_bold), Paragraph("Send WhatsApp", table_cell), Paragraph("1-क्लिक में छात्र के फोन पर एडमिशन रसीद या फीस रिमाइंडर भेजें।", table_cell)],
        [Paragraph("<b>[ Activate ]</b>", table_cell_bold), Paragraph("Quick Activate", table_cell), Paragraph("पेंडिंग छात्र का कोर्स व क्लास एक्सेस तुरंत सक्रिय (Activate) करें।", table_cell)],
        [Paragraph("<b>[ Delete ]</b>", table_cell_bold), Paragraph("Delete Record", table_cell), Paragraph("<b>केवल एडमिन:</b> एडमिन का लॉगिन पासवर्ड डालने पर ही रिकॉर्ड हटेगा।", table_cell)]
    ]
    icons_tbl = Table(icons_data, colWidths=[90, 120, 310])
    icons_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg])
    ]))
    elements.append(icons_tbl)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("11. अक्सर पूछे जाने वाले सवाल (FAQs & Support)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=navy, spaceBefore=2, spaceAfter=8))

    faqs = [
        ("प्र.1: क्या यह सॉफ्टवेयर बिना इंटरनेट वाले किसी भी कंप्यूटर पर चल सकता है?",
         "उत्तर: हाँ! यह सॉफ्टवेयर 100% ऑफ़लाइन है। आप पेनड्राइव से किसी भी Windows 10 या 11 कंप्यूटर पर इसे सीधे चला सकते हैं।"),
        ("प्र.2: क्या कोई स्टाफ छात्र का मोबाइल नंबर या फीस में हेराफेरी कर सकता है?",
         "उत्तर: बिल्कुल नहीं! मोबाइल नंबर में केवल 10 अंक ही स्वीकार होंगे। किसी भी रिकॉर्ड को डिलीट करने का बटन सिर्फ एडमिन के पास है और उसके लिए भी एडमिन का पासवर्ड अनिवार्य है। हर गतिविधि का ऑडिट लॉग बनता है।"),
        ("प्र.3: कंप्यूटर खराब या फॉर्मेट होने पर डेटा कैसे बचेगा?",
         "उत्तर: सॉफ्टवेयर का डेटा C: ड्राइव में नहीं, आपकी चुनी हुई सुरक्षित ड्राइव (D: ड्राइव) में रहता है। इसके अलावा 1-क्लिक पेनड्राइव बैकअप और Google Drive सिंक से डेटा 100% सुरक्षित रहता है।")
    ]
    for q, a in faqs:
        elements.append(Paragraph(f"<b>{q}</b>", h2_style))
        elements.append(Paragraph(a, body_style))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 20))

    # Final Help Desk Box
    final_box = [
        [
            Paragraph(
                "<font size='11'><b>तकनीकी सहायता एवं प्रशिक्षण हेल्पलाइन (Helpline)</b></font><br/><br/>"
                "सॉफ्टवेयर से संबंधित किसी भी सहायता, ट्रेनिंग या कस्टमाइजेशन के लिए संपर्क करें:<br/>"
                "• <b>निर्माता (Created By):</b> <b>Apna Computer</b><br/>"
                "• <b>मोबाइल व व्हाट्सएप नंबर (Contact No.):</b> <font color='#03F9FD'><b>8504985149</b></font><br/>"
                "• <b>ईमेल:</b> krishnaskb143@gmail.com<br/>"
                "<i>\"अपना कंप्यूटर — आपके संस्थान को डिजिटल, सुरक्षित और पारदर्शी बनाने का विश्वसनीय साथी।\"</i>",
                ParagraphStyle('FnHp', fontName=FONT_REGULAR, fontSize=9.5, textColor=colors.white, leading=14)
            )
        ]
    ]
    final_tbl = Table(final_box, colWidths=[520])
    final_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), navy),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1.5, cyan),
    ]))
    elements.append(final_tbl)

    # Build Document
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Manual PDF with Nirmala UI Font generated successfully at: {output_pdf_path}")

if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent.parent / "APNA_Computer_RMS_Training_Manual.pdf"
    generate_manual_pdf(str(out_file))
