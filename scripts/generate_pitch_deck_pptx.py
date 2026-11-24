"""
APNA COMPUTER RMS — Client Presentation Pitch Deck Generator (.pptx)
Generates high-impact 16:9 widescreen presentation slides for coaching & computer institute clients.
Includes visual architecture diagrams, 2-minute elevator pitch, security vault flow, and trial lifecycle.
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# Color Palette
NAVY_DARK = RGBColor(10, 25, 47)       # #0A192F
NAVY_MID = RGBColor(15, 34, 64)        # #0F2240
CYAN_BRIGHT = RGBColor(0, 240, 255)    # #00F0FF
BLUE_PRIMARY = RGBColor(2, 132, 199)   # #0284C7
BLUE_LIGHT = RGBColor(224, 242, 254)   # #E0F2FE
GREEN_ACCENT = RGBColor(16, 185, 129)  # #10B981
GREEN_LIGHT = RGBColor(220, 252, 231)  # #DCFCE7
GOLD_ACCENT = RGBColor(245, 158, 11)   # #F59E0B
GOLD_LIGHT = RGBColor(254, 243, 199)   # #FEF3C7
RED_ACCENT = RGBColor(239, 68, 68)     # #EF4444
RED_LIGHT = RGBColor(254, 226, 226)    # #FEE2E2
WHITE = RGBColor(255, 255, 255)
BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC
CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
TEXT_DARK = RGBColor(15, 23, 42)       # #0F172A
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # completely blank

    def add_header(slide, title_text, category_text="APNA COMPUTER RMS • EXECUTIVE PRESENTATION"):
        # Header strip
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = NAVY_DARK
        top_bar.line.color.rgb = CYAN_BRIGHT
        top_bar.line.width = Pt(1.5)

        tf = top_bar.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = CYAN_BRIGHT

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = WHITE

        # Footer strip
        foot = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.05), Inches(13.333), Inches(0.45))
        foot.fill.solid()
        foot.fill.fore_color.rgb = NAVY_DARK
        foot.line.fill.background()
        tf_f = foot.text_frame
        tf_f.vertical_anchor = MSO_ANCHOR.MIDDLE
        pf = tf_f.paragraphs[0]
        pf.text = "APNA Computer (कृष्णा जी)  |  Helpline: 8504985149  |  100% Offline • Zero-Cloud • Enterprise-Grade"
        pf.font.size = Pt(9.5)
        pf.font.color.rgb = WHITE
        pf.alignment = PP_ALIGN.CENTER

    def add_card(slide, left, top, width, height, title, subtitle="", bg_color=WHITE, border_color=CARD_BORDER, border_width=1):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
        tf = shape.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        
        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.size = Pt(10)
            p2.font.color.rgb = TEXT_MUTED
        return shape

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (HERO)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY_DARK
    bg1.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.333), Inches(3.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "APNA COMPUTER RMS"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = CYAN_BRIGHT

    p2 = tf1.add_paragraph()
    p2.text = "Coaching & Computer Institute Operating System"
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = WHITE

    p3 = tf1.add_paragraph()
    p3.text = "100% Offline • Zero-Cloud Subscriptions • 0.05s Instant Speed • Self-Healing Shadow Vault"
    p3.font.size = Pt(14)
    p3.font.color.rgb = GOLD_ACCENT

    # Badges row
    badges = [
        ("🛡️ Self-Healing Vault", "1s Auto-Restore on Delete"),
        ("⚡ 100% True Offline", "No Internet, No Server Lag"),
        ("📄 Crystal-Clear Receipts", "Google Noto Sans Devanagari"),
        ("⭐ 30-Day VIP Trial", "Hardware ID & Remote Extension")
    ]
    for i, (b_title, b_sub) in enumerate(badges):
        bx = 1.0 + (i * 2.85)
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(bx), Inches(4.5), Inches(2.7), Inches(1.2))
        card.fill.solid()
        card.fill.fore_color.rgb = NAVY_MID
        card.line.color.rgb = CYAN_BRIGHT
        card.line.width = Pt(1)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
        cp1 = ctf.paragraphs[0]
        cp1.text = b_title
        cp1.font.size = Pt(12)
        cp1.font.bold = True
        cp1.font.color.rgb = WHITE
        cp2 = ctf.add_paragraph()
        cp2.text = b_sub
        cp2.font.size = Pt(9.5)
        cp2.font.color.rgb = CYAN_BRIGHT

    # Footer note on Slide 1
    ft1 = s1.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.333), Inches(0.6))
    ftp = ft1.text_frame.paragraphs[0]
    ftp.text = "सॉफ्टवेयर निर्माता: APNA Computer (कृष्णा जी)  |  Helpline: 8504985149  |  Confidential Client Presentation"
    ftp.font.size = Pt(11)
    ftp.font.color.rgb = WHITE
    ftp.font.bold = True

    # =========================================================================
    # SLIDE 2: 2-MINUTE MAGIC ELEVATOR PITCH (8 HIGHLIGHTS)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "⚡ 2-मिनट का अचूक मैजिक पिच (The 2-Minute Magic Pitch)", "EXECUTIVE ELEVATOR PITCH")

    points = [
        ("1. 🛡️ सेल्फ-हीलिंग शैडो वॉल्ट", "मुख्य D:\\ फोल्डर Shift+Delete होने पर भी हिडन वॉल्ट से 1 सेकंड में 100% डेटा व रसीदें ऑटो-रीस्टोर हो जाती हैं।", GREEN_LIGHT, GREEN_ACCENT),
        ("2. ⚡ 100% ट्रू ऑफलाइन-फर्स्ट", "शून्य इंटरनेट, शून्य मासिक सर्वर बिल। बेसमेंट या ग्रामीण इलाके में भी 0.05 सेकंड की सुपरफास्ट स्पीड।", BLUE_LIGHT, BLUE_PRIMARY),
        ("3. 📄 क्रिस्टल-क्लियर हिंदी रसीदें", "Google Noto Sans Devanagari व Chromium शेपिंग—कोई काले डिब्बे (■■■) नहीं, शुद्ध A4/हाफ रसीद प्रिंट।", WHITE, BLUE_PRIMARY),
        ("4. 🔑 30-दिन VIP ट्रायल व WhatsApp एक्सटेंशन", "हार्डवेयर-लॉक्ड ACR-XXXX ID। 30 दिन बाद वेंडर द्वारा WhatsApp पर 10-15 दिन का एक्सटेंशन कोड जारी।", GOLD_LIGHT, GOLD_ACCENT),
        ("5. ⏰ एंटी-क्लॉक टैम्परिंग इंजन", "यदि कोई ऑपरेटर कंप्यूटर की घड़ी पीछे करके ट्रायल बाईपास करने की कोशिश करे, तो सिस्टम तुरंत लॉक लगा देता है।", RED_LIGHT, RED_ACCENT),
        ("6. 💾 1-क्लिक EOD पेनड्राइव बैकअप", "दिन समाप्त होने पर 1 क्लिक में पेनड्राइव बैकअप—कंप्यूटर खराब हो या चोरी, कोचिंग का काम कभी नहीं रुकता।", WHITE, GREEN_ACCENT),
        ("7. 🔀 मल्टी-पीसी सेफ डेटा मर्जिंग", "रिसेप्शन और डायरेक्टर केबिन के अलग-अलग पीसी का डेटा बिना किसी डुप्लीकेसी के 1 सेकंड में सुरक्षित मर्ज।", WHITE, BLUE_PRIMARY),
        ("8. 🔒 ज़ीरो-बैट व Authenticode साइंड", "कोई सस्पेक्टेड बैट फ़ाइल नहीं। Microsoft Authenticode SHA-256 साइंड सिंगल .exe जो बिना रुकावट चलती है।", WHITE, NAVY_DARK)
    ]

    for idx, (p_title, p_desc, bg_c, brd_c) in enumerate(points):
        row = idx // 2
        col = idx % 2
        left = 0.8 + (col * 5.95)
        top = 1.35 + (row * 1.35)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(5.8), Inches(1.25))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_c
        card.line.color.rgb = brd_c
        card.line.width = Pt(1.5)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.vertical_anchor = MSO_ANCHOR.TOP
        
        p1 = ctf.paragraphs[0]
        p1.text = p_title
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        
        p2 = ctf.add_paragraph()
        p2.text = p_desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 3: VISUAL ARCHITECTURE & DISASTER RECOVERY DIAGRAM
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "📊 विजुअल सिस्टम आर्किटेक्चर डायग्राम (Visual Architecture & Recovery Flow)", "SYSTEM SECURITY ARCHITECTURE")

    # Diagram Row 1: Dual Sync Architecture
    row1_title = s3.shapes.add_textbox(Inches(0.8), Inches(1.25), Inches(11.733), Inches(0.4))
    r1_p = row1_title.text_frame.paragraphs[0]
    r1_p.text = "1. डुअल-राइट सेल्फ-हीलिंग आर्किटेक्चर (Dual-Write Vault Architecture):"
    r1_p.font.size = Pt(13)
    r1_p.font.bold = True
    r1_p.font.color.rgb = BLUE_PRIMARY

    # Node A: Reception
    node_a = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.75), Inches(3.2), Inches(1.8))
    node_a.fill.solid()
    node_a.fill.fore_color.rgb = BLUE_LIGHT
    node_a.line.color.rgb = BLUE_PRIMARY
    node_a.line.width = Pt(1.5)
    tf_a = node_a.text_frame
    tf_a.word_wrap = True
    tf_a.vertical_anchor = MSO_ANCHOR.MIDDLE
    pa1 = tf_a.paragraphs[0]
    pa1.text = "🖥️ रिसेप्शन / कैश काउंटर"
    pa1.font.size = Pt(13)
    pa1.font.bold = True
    pa1.font.color.rgb = BLUE_PRIMARY
    pa2 = tf_a.add_paragraph()
    pa2.text = "• 100% ऑफलाइन लोकल ऐप\n• 0.05 सेकंड इंस्टेंट रिस्पॉन्स\n• कैश/UPI रसीद जनरेशन"
    pa2.font.size = Pt(9.5)
    pa2.font.color.rgb = TEXT_DARK

    # Arrow 1
    arr1 = s3.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.15), Inches(2.45), Inches(0.6), Inches(0.4))
    arr1.fill.solid()
    arr1.fill.fore_color.rgb = BLUE_PRIMARY
    arr1.line.fill.background()

    # Node B: Main Database
    node_b = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.9), Inches(1.75), Inches(3.5), Inches(1.8))
    node_b.fill.solid()
    node_b.fill.fore_color.rgb = GOLD_LIGHT
    node_b.line.color.rgb = GOLD_ACCENT
    node_b.line.width = Pt(1.5)
    tf_b = node_b.text_frame
    tf_b.word_wrap = True
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    pb1 = tf_b.paragraphs[0]
    pb1.text = "📁 मुख्य डेटाबेस (D:\\APNA_RMS_DATA)"
    pb1.font.size = Pt(13)
    pb1.font.bold = True
    pb1.font.color.rgb = GOLD_ACCENT
    pb2 = tf_b.add_paragraph()
    pb2.text = "• SQLite WAL Mode मास्टर डेटाबेस\n• रसीद PDF व फोटो डायरेक्टरी\n• यूजर विजिबल वर्किंग डायरेक्टरी"
    pb2.font.size = Pt(9.5)
    pb2.font.color.rgb = TEXT_DARK

    # Arrow 2
    arr2 = s3.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.55), Inches(2.45), Inches(0.6), Inches(0.4))
    arr2.fill.solid()
    arr2.fill.fore_color.rgb = GREEN_ACCENT
    arr2.line.fill.background()

    # Node C: Secret Shadow Vault
    node_c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.3), Inches(1.75), Inches(3.2), Inches(1.8))
    node_c.fill.solid()
    node_c.fill.fore_color.rgb = GREEN_LIGHT
    node_c.line.color.rgb = GREEN_ACCENT
    node_c.line.width = Pt(2.0)
    tf_c = node_c.text_frame
    tf_c.word_wrap = True
    tf_c.vertical_anchor = MSO_ANCHOR.MIDDLE
    pc1 = tf_c.paragraphs[0]
    pc1.text = "🛡️ सेल्फ-हीलिंग शैडो वॉल्ट"
    pc1.font.size = Pt(13)
    pc1.font.bold = True
    pc1.font.color.rgb = GREEN_ACCENT
    pc2 = tf_c.add_paragraph()
    pc2.text = "• Hidden %LOCALAPPDATA% Vault\n• रीयल-टाइम डुअल सिंक मिरर\n• 1 सेकंड में स्वतः रीस्टोर"
    pc2.font.size = Pt(9.5)
    pc2.font.color.rgb = TEXT_DARK

    # Diagram Row 2: Disaster Recovery Sequence
    row2_title = s3.shapes.add_textbox(Inches(0.8), Inches(3.85), Inches(11.733), Inches(0.4))
    r2_p = row2_title.text_frame.paragraphs[0]
    r2_p.text = "2. आपदा रिकवरी चक्र (Disaster Recovery & Self-Healing Lifecycle):"
    r2_p.font.size = Pt(13)
    r2_p.font.bold = True
    r2_p.font.color.rgb = GREEN_ACCENT

    rec_steps = [
        ("1. खतरा / डिलीट", "मुख्य D:\\ फोल्डर Shift+Delete या करप्ट हुआ", RED_LIGHT, RED_ACCENT),
        ("2. ऑटो-डिटेक्शन", "सॉफ्टवेयर स्टार्ट होते ही शैडो वॉल्ट चेक करता है", GOLD_LIGHT, GOLD_ACCENT),
        ("3. ऑटो-रीस्टोर", "1 सेकंड में संपूर्ण DB व रसीदें जीवित हो जाती हैं", GREEN_LIGHT, GREEN_ACCENT),
        ("4. ब्लैक-बॉक्स लॉग", "SECURITY_RECOVERY_LOG.txt में समय दर्ज", BLUE_LIGHT, BLUE_PRIMARY)
    ]
    for idx, (st_t, st_d, s_bg, s_brd) in enumerate(rec_steps):
        s_left = 0.8 + (idx * 2.95)
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(s_left), Inches(4.35), Inches(2.8), Inches(1.5))
        box.fill.solid()
        box.fill.fore_color.rgb = s_bg
        box.line.color.rgb = s_brd
        box.line.width = Pt(1.5)
        btf = box.text_frame
        btf.word_wrap = True
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp1 = btf.paragraphs[0]
        bp1.text = st_t
        bp1.font.size = Pt(11)
        bp1.font.bold = True
        bp1.font.color.rgb = TEXT_DARK
        bp2 = btf.add_paragraph()
        bp2.text = st_d
        bp2.font.size = Pt(9)
        bp2.font.color.rgb = TEXT_DARK

    # Bottom Callout
    b_note = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.8))
    b_note.fill.solid()
    b_note.fill.fore_color.rgb = NAVY_MID
    b_note.line.color.rgb = CYAN_BRIGHT
    b_note.line.width = Pt(1)
    tf_bn = b_note.text_frame
    tf_bn.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_bn = tf_bn.paragraphs[0]
    p_bn.text = "🎯 ओनर गारंटी: कंप्यूटर जल जाए, फॉर्मेट हो जाए या स्टाफ पूरा फोल्डर डिलीट कर दे—APNA Computer RMS में डेटा का एक कण भी नहीं खोता!"
    p_bn.font.size = Pt(11)
    p_bn.font.bold = True
    p_bn.font.color.rgb = WHITE
    p_bn.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 4: 30-DAY TRIAL & LICENSING LIFECYCLE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "🔑 30-दिन VIP मुफ़्त ट्रायल व हार्डवेयर-लॉक सिक्योरिटी (Trial & Licensing Engine)", "CLIENT ONBOARDING & EXTENSION")

    lic_steps = [
        ("चरण 1: 30-दिन VIP मुफ़्त ट्रायल", "• पहली बार इंस्टॉल होते ही 30 दिन का फुल VIP ट्रायल चालू।\n• हार्डवेयर-लॉक्ड ACR-XXXX इंस्टॉलेशन आईडी।\n• 100% फीचर्स अनलॉक—कोई भी प्रतिबंध नहीं।", GOLD_LIGHT, GOLD_ACCENT),
        ("चरण 2: ग्रेसफुल लॉक (डेटा सुरक्षित)", "• 30 दिन पूरे होने पर केवल नए एडमिशन/फीस एंट्री रुकती है।\n• डेटाबेस, बैकअप व पुरानी रसीदें डाउनलोड करने की पूरी छूट।\n• ओनर का पिछला कोई डेटा ब्लॉक या डिलीट नहीं होता।", RED_LIGHT, RED_ACCENT),
        ("चरण 3: 10-15 दिन WhatsApp एक्सटेंशन", "• ग्राहक के कॉल करने पर वेंडर द्वारा 10-15 दिन का नया कोड।\n• सुपर एडमिन 'Vendor Master Keygen' से कोड जारी।\n• बिना इंटरनेट के सिर्फ कोड डालने से सिस्टम तुरंत अनलॉक।", GREEN_LIGHT, GREEN_ACCENT),
        ("चरण 4: एंटी-क्लॉक टैम्परिंग इंजन", "• यदि कोई ऑपरेटर कंप्यूटर की घड़ी पीछे करने की कोशिश करे।\n• सिस्टम तुरंत 'Clock Tampering' पहचान कर लॉक कर देता है।\n• सिर्फ अधिकृत मास्टर की से ही रिसेट संभव।", BLUE_LIGHT, BLUE_PRIMARY)
    ]

    for idx, (l_title, l_desc, l_bg, l_brd) in enumerate(lic_steps):
        left = 0.8 + (idx * 2.95)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(1.5), Inches(2.8), Inches(3.6))
        card.fill.solid()
        card.fill.fore_color.rgb = l_bg
        card.line.color.rgb = l_brd
        card.line.width = Pt(1.5)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.vertical_anchor = MSO_ANCHOR.TOP
        
        p1 = ctf.paragraphs[0]
        p1.text = l_title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        
        p2 = ctf.add_paragraph()
        p2.text = l_desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_DARK

    # Bottom summary box on Trial
    ts_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.5))
    ts_box.fill.solid()
    ts_box.fill.fore_color.rgb = WHITE
    ts_box.line.color.rgb = BLUE_PRIMARY
    ts_box.line.width = Pt(1.5)
    ts_tf = ts_box.text_frame
    ts_tf.word_wrap = True
    ts_p1 = ts_tf.paragraphs[0]
    ts_p1.text = "💡 वेंडर सेल्स स्ट्रैटेजी (High Conversion Sales Strategy):"
    ts_p1.font.size = Pt(12)
    ts_p1.font.bold = True
    ts_p1.font.color.rgb = BLUE_PRIMARY

    ts_p2 = ts_tf.add_paragraph()
    ts_p2.text = "ग्राहक जब 1 महीना उपयोग कर लेता है और नए बैच के समय 10-15 दिन का और ट्रायल मांगता है—तो उसे WhatsApp पर तुरंत एक्सटेंशन कोड भेजें। 90%+ कोचिंग संचालक इस भरोसे और सपोर्ट को देखकर लाइफटाइम लाइसेंस तुरंत खरीद लेते हैं!"
    ts_p2.font.size = Pt(10.5)
    ts_p2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 5: COACHING & COMPUTER INSTITUTE POWERHOUSE FEATURES
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "🎓 कोचिंग व कंप्यूटर सेंटर स्पेशल फीचर्स (Coaching-First Features)", "CORE INSTITUTIONAL WORKFLOWS")

    c_feats = [
        ("1. कोर्स व बैच मैनेजमेंट", "DCA, ADCA, Tally, PGDCA, Python, CCC आदि कोर्स और मॉर्निंग/इवनिंग बैच की सटीक टाइमिंग व सीट क्षमता नियंत्रण।"),
        ("2. स्टूडेंट 360° लेजर व प्रोफाइल", "छात्र का पूरा इतिहास: एडमिशन तारीख, फोटो, पिता का नाम, आवंटित लैब/कंप्यूटर नंबर, कुल फीस, दी गई किस्तें व बकाया शेष।"),
        ("3. 2-सेकंड फ़ीस कलेक्शन", "छात्र का नाम या मोबाइल नंबर टाइप करते ही बकाया फीस स्क्रीन पर। कैश या UPI मोड चुनते ही 1-क्लिक में रसीद प्रिंट।"),
        ("4. ऑटोमैटिक आई-कार्ड व सर्टिफिकेट", "संस्थान का लोगो, बारकोड व स्टूडेंट फोटो के साथ A4 शीट पर 4/8 लेआउट में 1-क्लिक आई-कार्ड और कोर्स सर्टिफिकेट प्रिंटिंग।"),
        ("5. दैनिक खर्च व वाउचर रजिस्टर", "बिजली बिल, इंटरनेट, ऑफिस स्टेशनरी, चाय-पानी आदि दैनिक खर्चों की तुरंत रसीद व वाउचर एंट्री।"),
        ("6. स्टाफ अटेंडेंस व एडवांस सैलरी", "टीचर्स व ऑपरेटर की उपस्थिति, लीव रिकॉर्ड, अग्रिम भुगतान (Advance Salary) और मासिक वेतन गणना।")
    ]

    for idx, (cf_title, cf_desc) in enumerate(c_feats):
        row = idx // 2
        col = idx % 2
        left = 0.8 + (col * 5.95)
        top = 1.45 + (row * 1.7)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(5.8), Inches(1.55))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BLUE_PRIMARY
        card.line.width = Pt(1)
        ctf = card.text_frame
        ctf.word_wrap = True
        
        p1 = ctf.paragraphs[0]
        p1.text = cf_title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = BLUE_PRIMARY
        
        p2 = ctf.add_paragraph()
        p2.text = cf_desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 6: CRYSTAL-CLEAR HINDI PRINT ENGINE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "📄 1-क्लिक हाई-स्पीड रसीद व सर्टिफिकेट इंजन (Crystal-Clear Printing)", "PRINTING & DEVANAGARI TYPOGRAPHY")

    p_boxes = [
        ("Google Noto Sans Devanagari", "शुद्ध हिंदी अक्षरों की सटीक रेंडरिंग। कोई काले डिब्बे (■■■) या टूटे हुए शब्द नहीं दिखेंगे।", BLUE_LIGHT, BLUE_PRIMARY),
        ("Chromium Headless शेपिंग", "हाई-स्पीड 0.2 सेकंड में पीडीएफ जनरेशन। थर्मल प्रिंटर (80mm) व A4/A5 लेजर प्रिंटर दोनों पर परफेक्ट।", GOLD_LIGHT, GOLD_ACCENT),
        ("ऑफलाइन QR कोड ऑथेंटिकेशन", "हर रसीद पर यूनिक वेरिफिकेशन QR कोड, जिसे स्मार्टफोन कैमरे से स्कैन करके रसीद का असली होना जांचा जा सकता है।", GREEN_LIGHT, GREEN_ACCENT)
    ]
    for idx, (pt_t, pt_d, p_bg, p_brd) in enumerate(p_boxes):
        left = 0.8 + (idx * 3.95)
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(1.5), Inches(3.8), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = p_bg
        card.line.color.rgb = p_brd
        card.line.width = Pt(1.5)
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p1 = ctf.paragraphs[0]
        p1.text = pt_t
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        p2 = ctf.add_paragraph()
        p2.text = pt_d
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK

    # Comparison Table (APNA Computer RMS vs Others)
    cmp_box = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.0), Inches(11.733), Inches(2.8))
    cmp_box.fill.solid()
    cmp_box.fill.fore_color.rgb = WHITE
    cmp_box.line.color.rgb = CARD_BORDER
    cmp_tf = cmp_box.text_frame
    cmp_tf.word_wrap = True
    cp = cmp_tf.paragraphs[0]
    cp.text = "📊 रसीद प्रिंटिंग तुलना (Print Quality Comparison):"
    cp.font.size = Pt(12)
    cp.font.bold = True
    cp.font.color.rgb = NAVY_DARK

    comps = [
        "• अन्य पुराने सॉफ्टवेयर: काले डिब्बे (■■■), टूटे हुए संयुक्ताक्षर, धीमी प्रिंटिंग, सिर्फ एक प्रिंटर सपोर्ट।",
        "• क्लाउड सॉफ्टवेयर: इंटरनेट डाउन होने पर रसीद प्रिंट नहीं होती, काउंटर पर अभिभावकों की लंबी लाइन लग जाती है।",
        "• APNA Computer RMS: 100% ऑफ़लाइन, 0.2 सेकंड में प्रिंट, 80mm थर्मल स्लिप व A4 फुल/हाफ रसीद, शुद्ध हिंदी फॉन्ट!"
    ]
    for c in comps:
        cp_i = cmp_tf.add_paragraph()
        cp_i.text = c
        cp_i.font.size = Pt(10.5)
        cp_i.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 7: FINANCIAL TRANSPARENCY & EOD CASH RECONCILIATION
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "💰 वित्तीय नियंत्रण, EOD कैश मिलान व लाभ-हानि (Financial Transparency)", "END OF DAY CASH RECONCILIATION")

    fin_cards = [
        ("1. कैश व UPI विभाजन", "काउंसलर ने दिन भर में कितना नकद (Cash) लिया और कितना QR/UPI में आया, इसका अलग-अलग सटीक रजिस्टर।"),
        ("2. दिन का EOD कैश मिलान", "दुकान/कोचिंग बंद करते समय 1-क्लिक में EOD (End of Day) रिपोर्ट निकालें और गल्ले के नकद से पाई-पाई मिलाएं।"),
        ("3. मासिक आय-व्यय व लाभ", "कुल फीस वसूली माइनस कुल स्टाफ सैलरी व खर्च = वास्तविक मासिक मुनाफा एक सेकंड में स्क्रीन पर।"),
        ("4. 1-क्लिक Excel / PDF एक्सपोर्ट", "सीए (CA) या आयकर रिटर्न के लिए पूरा ऑडिट रिकॉर्ड 1 क्लिक में एक्सेल या पीडीएफ में एक्सपोर्ट करें।")
    ]
    for idx, (fc_t, fc_d) in enumerate(fin_cards):
        left = 0.8 + (idx * 2.95)
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(1.6), Inches(2.8), Inches(3.2))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = GREEN_ACCENT
        card.line.width = Pt(1.5)
        ctf = card.text_frame
        ctf.word_wrap = True
        p1 = ctf.paragraphs[0]
        p1.text = fc_t
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = GREEN_ACCENT
        p2 = ctf.add_paragraph()
        p2.text = fc_d
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK

    fin_banner = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.6))
    fin_banner.fill.solid()
    fin_banner.fill.fore_color.rgb = NAVY_MID
    fin_banner.line.color.rgb = GOLD_ACCENT
    fb_tf = fin_banner.text_frame
    fb_tf.word_wrap = True
    fbp = fb_tf.paragraphs[0]
    fbp.text = "🎯 संस्थान संचालक का वित्तीय शांति कवच (Zero Financial Leakage):"
    fbp.font.size = Pt(12)
    fbp.font.bold = True
    fbp.font.color.rgb = GOLD_ACCENT
    fbp2 = fb_tf.add_paragraph()
    fbp2.text = "कोचिंग में सबसे बड़ी समस्या होती है कि रिसेप्शन पर कितनी फीस आई और कितनी जमा हुई, इसका हिसाब नहीं मिल पाता। APNA Computer RMS हर रसीद पर ऑटोमैटिक नंबरिंग और ऑडिट लॉग रखता है जिससे 1 रुपये की भी हेराफेरी संभव नहीं है।"
    fbp2.font.size = Pt(10.5)
    fbp2.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 8: MULTI-PC SYNC & CONFLICT-FREE DATA MERGING
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "🔀 मल्टी-पीसी सिंक व सुरक्षित डेटा मर्जिंग (Multi-PC Sync & Safe Merge)", "MULTI-COUNTER WORKFLOW")

    mpc_cards = [
        ("विधि 1: वाई-फाई / LAN शेयरिंग (Recommended)", "• मुख्य PC के D:\\APNA_RMS_DATA फोल्डर को नेटवर्क पर शेयर करें।\n• बाकी रिसेप्शन/काउंसलर कंप्यूटरों को उस पाथ से कनेक्ट कर दें।\n• 100% ऑफ़लाइन रीयल-टाइम सिंक—इंटरनेट की कोई जरूरत नहीं।", BLUE_LIGHT, BLUE_PRIMARY),
        ("विधि 2: Google Drive डेस्कटॉप ऑटो-सिंक", "• डेटाबेस पाथ को गूगल ड्राइव डेस्कटॉप फोल्डर में सेट कर दें।\n• संचालक घर बैठे या दूसरी ब्रांच से भी लाइव कलेक्शन देख सकते हैं।\n• क्लाउड पर ऑटो-बैकअप सुरक्षित रहता है।", GOLD_LIGHT, GOLD_ACCENT),
        ("विधि 3: 1-क्लिक स्मार्ट मल्टी-पीसी ऑटो-मर्ज", "• बिना LAN/इंटरनेट वाले पूरी तरह अलग कंप्यूटरों के लिए।\n• शाम को पेनड्राइव से .db फ़ाइल ओनर के पीसी में 1-क्लिक मर्ज करें।\n• शून्य डुप्लीकेसी—नए एडमिशन व फीस बिना टकराव के जुड़ जाते हैं।", GREEN_LIGHT, GREEN_ACCENT)
    ]
    for idx, (mc_t, mc_d, mc_bg, mc_brd) in enumerate(mpc_cards):
        left = 0.8 + (idx * 3.95)
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(1.6), Inches(3.8), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = mc_bg
        card.line.color.rgb = mc_brd
        card.line.width = Pt(1.5)
        ctf = card.text_frame
        ctf.word_wrap = True
        p1 = ctf.paragraphs[0]
        p1.text = mc_t
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        p2 = ctf.add_paragraph()
        p2.text = mc_d
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 9: ZERO-FRICTION INSTALLATION & VENDOR SUPPORT
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "🚀 तकनीकी श्रेष्ठता, इंस्टॉलेशन व वेंडर सपोर्ट (Vendor Trust & Deployment)", "TECHNICAL SPECIFICATIONS")

    tech_specs = [
        ("ज़ीरो-डिपेंडेंसी इंस्टॉलर", "क्लाइंट पीसी पर कोई Python, Node.js या डेटाबेस सर्वर इंस्टॉल करने की जरूरत नहीं। इन-बिल्ट रनटाइम के साथ 1 मिनट में सेटअप।"),
        ("Microsoft Authenticode साइंड", "एंटीवायरस फ्रेंडली SHA-256 डिजिटल सिग्नेचर। विंडोज़ डिफेंडर या स्मार्टस्क्रीन द्वारा कोई अवांछित रुकावट नहीं।"),
        ("शून्य सस्पेक्टेड बैट फाइल्स", "विंडोज़ 11 SAC (Smart App Control) व Error 4551 से 100% सुरक्षित। कोई अन-साइंड हेल्पर स्क्रिप्ट नहीं।"),
        ("24x7 वेंडर हेल्पलाइन व ट्रेनिंग", "सॉफ्टवेयर निर्माता द्वारा पूर्ण रिमोट ट्रेनिंग, डेटा माइग्रेशन और निरंतर तकनीकी सहायता की गारंटी।")
    ]
    for idx, (ts_t, ts_d) in enumerate(tech_specs):
        row = idx // 2
        col = idx % 2
        left = 0.8 + (col * 5.95)
        top = 1.5 + (row * 1.8)
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(5.8), Inches(1.6))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BLUE_PRIMARY
        card.line.width = Pt(1)
        ctf = card.text_frame
        ctf.word_wrap = True
        p1 = ctf.paragraphs[0]
        p1.text = ts_t
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = BLUE_PRIMARY
        p2 = ctf.add_paragraph()
        p2.text = ts_d
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK

    ts_foot = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.4), Inches(11.733), Inches(1.3))
    ts_foot.fill.solid()
    ts_foot.fill.fore_color.rgb = NAVY_DARK
    ts_foot.line.color.rgb = CYAN_BRIGHT
    ts_tf = ts_foot.text_frame
    ts_tf.word_wrap = True
    ts_p = ts_tf.paragraphs[0]
    ts_p.text = "📞 डायरेक्ट वेंडर संपर्क: APNA Computer (कृष्णा जी)  |  हेल्पलाइन: 8504985149"
    ts_p.font.size = Pt(14)
    ts_p.font.bold = True
    ts_p.font.color.rgb = CYAN_BRIGHT
    ts_p.alignment = PP_ALIGN.CENTER
    ts_p2 = ts_tf.add_paragraph()
    ts_p2.text = "आज ही 30-दिन VIP मुफ़्त डेमो शुरू करें और अपने संस्थान को पेपरलेस व डिजिटल बनाएं!"
    ts_p2.font.size = Pt(11)
    ts_p2.font.color.rgb = WHITE
    ts_p2.alignment = PP_ALIGN.CENTER

    # Save Deck
    root_dir = Path(__file__).resolve().parent.parent
    dist_doc_dir = root_dir / "dist" / "Documentation"
    dist_doc_dir.mkdir(parents=True, exist_ok=True)
    
    out_pptx = dist_doc_dir / "APNA_Computer_RMS_Client_Pitch_Deck.pptx"
    prs.save(str(out_pptx))
    print(f"✅ Generated PPTX: {out_pptx} ({os.path.getsize(out_pptx)} bytes)")
    
    # Also save to dist
    out_pptx_dist = root_dir / "dist" / "APNA_Computer_RMS_Client_Pitch_Deck.pptx"
    import shutil
    shutil.copy(out_pptx, out_pptx_dist)
    print(f"✅ Copied to: {out_pptx_dist}")

if __name__ == "__main__":
    create_deck()
