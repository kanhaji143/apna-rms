import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def generate_html_manual():
    today_str = datetime.now().strftime("%d %B %Y")
    
    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<title>APNA Computer RMS — सम्पूर्ण ऑपरेटिंग व ट्रेनिंग मैनुअल</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    @page {{
        size: A4 portrait;
        margin: 12mm 14mm 14mm 14mm;
    }}

    * {{
        box-sizing: border-box;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    body {{
        font-family: 'Nirmala UI', 'Aparajita', 'Segoe UI', 'Mangal', -apple-system, sans-serif;
        color: #1E293B;
        margin: 0;
        padding: 0;
        font-size: 13px;
        line-height: 1.5;
        background: #FFFFFF;
    }}

    .page {{
        page-break-after: always;
        position: relative;
        min-height: 100%;
        display: flex;
        flex-direction: column;
    }}

    .page:last-child {{
        page-break-after: avoid;
    }}

    /* Header & Footer styling for pages */
    .page-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1.5px solid #CBD5E1;
        padding-bottom: 5px;
        margin-bottom: 12px;
        font-size: 11px;
        font-weight: 600;
        color: #64748B;
    }}

    .page-header .brand {{
        color: #00183A;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}

    .page-footer {{
        margin-top: auto;
        border-top: 1px solid #E2E8F0;
        padding-top: 5px;
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        color: #64748B;
    }}

    /* Typography */
    h1, h2, h3, h4 {{
        color: #00183A;
        margin: 0 0 6px 0;
        font-weight: 700;
    }}

    .section-title {{
        font-size: 15px;
        color: #00183A;
        border-left: 4px solid #00B4D8;
        padding-left: 9px;
        margin-top: 11px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
    }}

    p {{
        margin: 0 0 6px 0;
    }}

    /* Cover Page */
    .cover-container {{
        text-align: center;
        padding: 24px 20px 14px 20px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    .cover-banner {{
        background: linear-gradient(135deg, #00183A 0%, #0A2540 100%);
        color: #FFFFFF;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,24,58,0.15);
        border: 2px solid #00B4D8;
    }}

    .cover-banner h1 {{
        color: #00F0FF;
        font-size: 28px;
        margin-bottom: 4px;
        letter-spacing: 1px;
    }}

    .cover-banner .subtitle {{
        color: #E2E8F0;
        font-size: 14.5px;
        font-weight: 500;
    }}

    .cover-hero-title {{
        font-size: 24px;
        color: #00183A;
        margin-top: 22px;
        margin-bottom: 5px;
        font-weight: 800;
    }}

    .cover-hero-sub {{
        font-size: 14px;
        color: #0284C7;
        font-weight: 600;
        margin-bottom: 14px;
    }}

    .cover-divider {{
        width: 100px;
        height: 3px;
        background: #00B4D8;
        margin: 0 auto 16px auto;
        border-radius: 2px;
    }}

    .cover-summary {{
        font-size: 13.5px;
        color: #334155;
        max-width: 620px;
        margin: 0 auto 20px auto;
        line-height: 1.55;
        text-align: justify;
        text-align-last: center;
    }}

    /* Badges Grid */
    .badge-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin: 16px 0;
    }}

    .badge-card {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 6px;
        text-align: center;
    }}

    .badge-card .title {{
        font-weight: 700;
        color: #00183A;
        font-size: 12px;
        margin-bottom: 3px;
    }}

    .badge-card .desc {{
        font-size: 10.5px;
        color: #64748B;
        line-height: 1.3;
    }}

    /* Info Table */
    .author-box {{
        background: #EFF6FF;
        border: 1.5px solid #BFDBFE;
        border-radius: 10px;
        padding: 14px 18px;
        max-width: 500px;
        margin: 20px auto 0 auto;
        text-align: left;
    }}

    .author-box table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12.5px;
    }}

    .author-box td {{
        padding: 4px 6px;
    }}

    .author-box td.label {{
        font-weight: 700;
        color: #1E3A8A;
        width: 45%;
    }}

    .author-box td.val {{
        font-weight: 600;
        color: #0F172A;
    }}

    /* Tables */
    table.data-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 6px 0 10px 0;
        font-size: 11.5px;
        border-radius: 6px;
        overflow: hidden;
    }}

    table.data-table th {{
        background: #00183A;
        color: #FFFFFF;
        padding: 7px 9px;
        text-align: left;
        font-weight: 600;
        font-size: 11.5px;
    }}

    table.data-table td {{
        padding: 6px 9px;
        border-bottom: 1px solid #E2E8F0;
        border-right: 1px solid #F1F5F9;
        vertical-align: top;
    }}

    table.data-table tr:nth-child(even) {{
        background: #F8FAFC;
    }}

    table.data-table td.strong {{
        font-weight: 700;
        color: #00183A;
    }}

    /* Callout Note Boxes */
    .callout-box {{
        background: #ECFDF5;
        border-left: 4px solid #10B981;
        border-top: 1px solid #D1FAE5;
        border-right: 1px solid #D1FAE5;
        border-bottom: 1px solid #D1FAE5;
        border-radius: 6px;
        padding: 9px 12px;
        margin: 8px 0;
        font-size: 11.5px;
        color: #065F46;
        line-height: 1.45;
    }}

    .callout-box.cyan {{
        background: #F0F9FF;
        border-left-color: #0284C7;
        border-color: #BAE6FD;
        color: #0369A1;
    }}

    .callout-box.navy {{
        background: #00183A;
        border-left-color: #00B4D8;
        border: 1px solid #00B4D8;
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 16px;
    }}

    .callout-box.navy .highlight {{
        color: #00F0FF;
        font-weight: bold;
    }}

    /* Bullet List */
    ul.guide-list {{
        margin: 3px 0 8px 0;
        padding-left: 16px;
    }}

    ul.guide-list li {{
        margin-bottom: 3px;
        font-size: 12px;
    }}

    .action-tag {{
        display: inline-block;
        background: #E2E8F0;
        color: #0F172A;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 10.5px;
        border: 1px solid #CBD5E1;
    }}

    .tag-blue {{
        background: #DBEAFE;
        color: #1E40AF;
        border-color: #93C5FD;
    }}

    .tag-green {{
        background: #DCFCE7;
        color: #166534;
        border-color: #86EFAC;
    }}

    .tag-orange {{
        background: #FFEDD5;
        color: #9A3412;
        border-color: #FDBA74;
    }}

    .tag-red {{
        background: #FEE2E2;
        color: #991B1B;
        border-color: #FCA5A5;
    }}
</style>
</head>
<body>

<!-- ===================================================================== -->
<!-- PAGE 1: COVER PAGE -->
<!-- ===================================================================== -->
<div class="page">
    <div class="cover-container">
        <div>
            <div class="cover-banner">
                <h1>APNA COMPUTER RMS v2.0</h1>
                <div class="subtitle">ऑफ़लाइन रिकॉर्ड व कोचिंग संस्थान प्रबंधन सॉफ्टवेयर</div>
            </div>

            <div class="cover-hero-title">सम्पूर्ण ऑपरेटिंग, स्टाफ ट्रेनिंग व बैकअप गाइड</div>
            <div class="cover-hero-sub">Complete Professional Staff Training, Operations & Multi-PC Backup Manual</div>
            <div class="cover-divider"></div>

            <div class="cover-summary">
                यह गाइड कोचिंग संस्थानों, कंप्यूटर प्रशिक्षण केंद्रों एवं स्कूलों के लिए तैयार किए गए 
                <b>APNA Computer RMS</b> सॉफ्टवेयर के सफल संचालन, स्टाफ ट्रेनिंग, 1-क्लिक लाइव डेमो, 
                फीस कलेक्शन, बकाया किस्त नियंत्रण, 1-क्लिक आई-कार्ड प्रिंटिंग, बिना पासवर्ड के दैनिक जीमेल रिपोर्टिंग 
                एवं मल्टी-पीसी डेटा मर्ज व बैकअप का आधिकारिक व सम्पूर्ण मार्गदर्शक है।
            </div>

            <div class="badge-grid">
                <div class="badge-card">
                    <div class="title">100% ऑफ़लाइन</div>
                    <div class="desc">बिना इंटरनेट के कंप्यूटर पर सुपरफास्ट स्पीड</div>
                </div>
                <div class="badge-card">
                    <div class="title">1-Click Live Demo</div>
                    <div class="desc">बिना पासवर्ड के तुरंत प्रेजेंटेशन व रीसेट टूल</div>
                </div>
                <div class="badge-card">
                    <div class="title">Hover Tooltips</div>
                    <div class="desc">माउस ले जाते ही हर बटन का नाम व काम दिखेगा</div>
                </div>
                <div class="badge-card">
                    <div class="title">Zero-Password Mail</div>
                    <div class="desc">1-क्लिक जीमेल में रिपोर्ट व स्क्रीनशॉट्स बैकअप</div>
                </div>
            </div>
        </div>

        <div class="author-box">
            <table>
                <tr>
                    <td class="label">सॉफ्टवेयर निर्माता (Created By):</td>
                    <td class="val">Apna Computer</td>
                </tr>
                <tr>
                    <td class="label">हेल्पलाइन व संपर्क (Contact No.):</td>
                    <td class="val">8504985149</td>
                </tr>
                <tr>
                    <td class="label">आधिकारिक सहायता ईमेल:</td>
                    <td class="val">krishnaskb143@gmail.com</td>
                </tr>
                <tr>
                    <td class="label">सॉफ्टवेयर संस्करण:</td>
                    <td class="val">v2.0 Standalone Enterprise Edition</td>
                </tr>
                <tr>
                    <td class="label">मैनुअल अपडेट तिथि:</td>
                    <td class="val">{today_str}</td>
                </tr>
            </table>
        </div>
    </div>
</div>

<!-- ===================================================================== -->
<!-- PAGE 2: MODULE 1, 2 & 1-CLICK LIVE DEMO -->
<!-- ===================================================================== -->
<div class="page">
    <div class="page-header">
        <span class="brand">APNA COMPUTER RMS — ऑपरेटिंग व ट्रेनिंग मैनुअल</span>
        <span>सपोर्ट: 8504985149</span>
    </div>

    <div class="section-title">1. सॉफ्टवेयर परिचय एवं त्वरित शुरुआत (Quick Startup Guide)</div>
    <p>
        <b>APNA Computer RMS</b> एक स्टैंडअलोन और पोर्टेबल विंडोज सॉफ्टवेयर है। इसे किसी भी विंडोज कंप्यूटर (Windows 10 / 11) पर बिना किसी डेटाबेस सर्वर सेटअप के सीधे चलाया जा सकता है।
    </p>
    <ul class="guide-list">
        <li><b>पेनड्राइव से सीधे चलाएं:</b> सॉफ्टवेयर फाइल <code>APNA_Computer_RMS.exe</code> को किसी भी कंप्यूटर या पेनड्राइव में रखकर सीधे चालू किया जा सकता है।</li>
        <li><b>डेस्कटॉप शॉर्टकट बनाएं:</b> फाइल पर राइट-क्लिक करके <b>"Send to → Desktop (create shortcut)"</b> कर लें, जिससे रोज सुबह स्क्रीन से सीधे चालू किया जा सके।</li>
        <li><b>संस्थान की ब्रांडिंग:</b> Settings में जाकर 1-क्लिक में अपनी कोचिंग का नाम, पता, फोन व नया लोगो अपलोड कर सकते हैं।</li>
    </ul>

    <div class="section-title">2. त्रि-स्तरीय यूज़र रोल्स एवं डेटा सुरक्षा (3-Tier RBAC)</div>
    <p>
        कोचिंग में डेटा चोरी और अनधिकृत छेड़छाड़ रोकने के लिए 3 अलग-अलग यूज़र रोल्स दिए गए हैं:
    </p>
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 22%;">यूज़र रोल</th>
                <th style="width: 25%;">डिफ़ॉल्ट खाता</th>
                <th>कार्यक्षेत्र एवं अधिकार (Permissions)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="strong">Admin (मालिक / डायरेक्टर)</td>
                <td>admin<br/><small style="color:#64748B;">(सेटअप पासवर्ड)</small></td>
                <td><b>पूर्ण अधिकार:</b> कुल कलेक्शन व मुनाफा देखना, सेटिंग्स, स्टाफ पासवर्ड प्रबंधन, ऑडिट लॉग्स एवं <b>पासवर्ड-प्रोटेक्टेड रिकॉर्ड डिलीशन</b>।</td>
            </tr>
            <tr>
                <td class="strong">Accountant (अकाउंटेंट)</td>
                <td>accountant<br/><small style="color:#64748B;">(accountant@123)</small></td>
                <td><b>खर्च व फीस प्रबंधन:</b> नया खर्च दर्ज करना, फीस रसीद व रिपोर्ट एक्सेल में निकालना। (रिकॉर्ड डिलीट करना व सेटिंग्स पूरी तरह ब्लॉक रहती हैं)।</td>
            </tr>
            <tr>
                <td class="strong">Counselor (एडमिशन स्टाफ)</td>
                <td>counselor<br/><small style="color:#64748B;">(staff@123)</small></td>
                <td><b>एडमिशन डेस्क:</b> नया एडमिशन लेना, फीस रसीद व आई-कार्ड प्रिंट करना, टाइम-टेबल देखना। <b>(संस्थान का कुल मुनाफा, खर्चे और एक्सेल एक्सपोर्ट स्टाफ से पूरी तरह छिपे रहते हैं)</b>।</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">3. 1-क्लिक लाइव डेमो मोड (Sales Presentation & Demo Mode)</div>
    <p>
        जब आप किसी ग्राहक, कोचिंग डायरेक्टर या नए स्टाफ को सॉफ्टवेयर का डेमो दिखा रहे हों:
    </p>
    <ul class="guide-list">
        <li><b>बिना पासवर्ड का हरा बटन:</b> लॉगिन स्क्रीन पर हरा बटन दिया गया है: <b>[ 🎮 1-क्लिक लाइव डेमो (Explore Live Demo) ]</b>। इस पर क्लिक करते ही बिना पासवर्ड टाइप किए तुरंत फुल डायरेक्टर एक्सेस खुल जाता है।</li>
        <li><b>सैंपल डेटा लोड:</b> डेमो में 10 वास्तविक छात्रों का रिकॉर्ड, ₹69,000 रेवेन्यू, ₹33,699 खर्चे और ₹35,301 का शुद्ध मुनाफा पहले से तैयार दिखता है।</li>
        <li><b>1-क्लिक डेटा रीसेट:</b> हेडर में <b>[ 🔄 रीसेट डेमो डेटा ]</b> बटन है। अगर क्लाइंट ने टेस्ट करते हुए कुछ डिलीट या नया जोड़ दिया, तो 1 सेकंड में वापस फ्रेश डेटा रीसेट हो जाता है।</li>
    </ul>

    <div class="callout-box">
        <b>मैनुअल डेमो लॉगिन:</b> यूज़रनेम <code>demo</code> और पासवर्ड <code>demo123</code> डालकर भी डेमो में सीधे प्रवेश किया जा सकता है।
    </div>

    <div class="page-footer">
        <span>Created BY: Apna Computer  |  Helpline: 8504985149</span>
        <span>पेज 2</span>
    </div>
</div>

<!-- ===================================================================== -->
<!-- PAGE 3: ADMISSION, STRICT FILTERS & WHATSAPP -->
<!-- ===================================================================== -->
<div class="page">
    <div class="page-header">
        <span class="brand">APNA COMPUTER RMS — ऑपरेटिंग व ट्रेनिंग मैनुअल</span>
        <span>सपोर्ट: 8504985149</span>
    </div>

    <div class="section-title">4. नया एडमिशन दर्ज करने की मानक प्रक्रिया (Admission SOP)</div>
    <p>एडमिशन डेस्क पर गलत या फर्जी डेटा रोकने के लिए सिस्टम में सख्त नियम लागू हैं:</p>
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 25%;">फील्ड (Field)</th>
                <th style="width: 25%;">नियम (Validation)</th>
                <th>सिस्टम सुरक्षा एवं व्यवहार</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="strong">Student Full Name</td>
                <td>कम से कम 2 अक्षर</td>
                <td>सिस्टम स्वतः शुद्ध करके <b>Title Case</b> (उदा: Rahul Kumar Sharma) में सुरक्षित करता है।</td>
            </tr>
            <tr>
                <td class="strong">Phone (10 Digits)</td>
                <td>ठीक 10 अंक, 6,7,8,9 से शुरू</td>
                <td><b>की-स्ट्रोक फ़िल्टर:</b> एबीसीडी या स्पेशल कैरेक्टर टाइप ही नहीं होगा। 10 अंक से ज्यादा नहीं जाएगा।</td>
            </tr>
            <tr>
                <td class="strong">Payment Date</td>
                <td>कैलेंडर YYYY-MM-DD</td>
                <td>गलत तारीख या टेक्स्ट डालने पर फॉर्म सबमिट नहीं होगा। डिफ़ॉल्ट रूप से आज की तारीख चुनी रहती है।</td>
            </tr>
            <tr>
                <td class="strong">Payment Mode</td>
                <td>UPI / Cash / Card</td>
                <td><b>कैश मोड:</b> काउंटर अकाउंट स्वतः सेट हो जाता है।<br/><b>UPI मोड:</b> 12-अंक का UTR और पेमेंट स्क्रीनशॉट अनिवार्य होता है।</td>
            </tr>
            <tr>
                <td class="strong">Duplicate UTR Block</td>
                <td>100% यूनिक UTR</td>
                <td>यदि कोई स्टाफ पुराना UTR दोबारा डालेगा, तो सिस्टम तुरंत रोक देगा और पिछले छात्र का नाम दिखाएगा।</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">5. 1-क्लिक डायरेक्ट व्हाट्सएप (Zero API Messaging)</div>
    <p>छात्रों को फीस रसीद व फीस रिमाइंडर भेजने के लिए किसी थर्ड-पार्टी API या मासिक खर्च की ज़रूरत नहीं:</p>
    <ul class="guide-list">
        <li><b>एडमिशन के तुरंत बाद:</b> फॉर्म सबमिट होते ही व्हाट्सएप का पॉपअप खुलता है। 1-क्लिक करते ही छात्र के नंबर पर आधिकारिक स्वागत संदेश व रसीद विवरण चला जाता है।</li>
        <li><b>रिकॉर्ड्स टेबल में:</b> हर छात्र के आगे <b>[ 💬 WhatsApp ]</b> बटन है। अगर छात्र की फीस बाकी है, तो बकाया राशि व अंतिम तिथि का रिमाइंडर मैसेज स्वतः बन जाता है।</li>
    </ul>

    <div class="section-title">6. बकाया फीस व किस्त ट्रैकर एवं पॉकेट आई-कार्ड</div>
    <ul class="guide-list">
        <li><b>लाइव बकाया बैज:</b> जिस छात्र की फीस बाकी होगी, उसके नाम के आगे नारंगी रंग में <span class="action-tag tag-orange">बाकी ₹2,000</span> का बैज दिखेगा।</li>
        <li><b>किस्त जमा बटन [ 💳 Pay ]:</b> छात्र जब 1 महीने बाद दूसरी किस्त जमा करे, तो Pay बटन दबाएं। रसीद में पिछली किस्तों का इतिहास (1st Installment, 2nd Installment) अपने आप जुड़ जाता है।</li>
        <li><b>1-क्लिक पॉकेट आई-कार्ड [ 🪪 ID Card ]:</b> 3.5" x 5.2" पॉकेट साइज आई-कार्ड PDF तुरंत जनरेट होता है जिसमें संस्थान का लोगो, छात्र का नाम, एडमिशन नंबर और मुहर/हस्ताक्षर की जगह होती है।</li>
    </ul>

    <div class="page-footer">
        <span>Created BY: Apna Computer  |  Helpline: 8504985149</span>
        <span>पेज 3</span>
    </div>
</div>

<!-- ===================================================================== -->
<!-- PAGE 4: HOVER TOOLTIPS, ACTIONS & P&L -->
<!-- ===================================================================== -->
<div class="page">
    <div class="page-header">
        <span class="brand">APNA COMPUTER RMS — ऑपरेटिंग व ट्रेनिंग मैनुअल</span>
        <span>सपोर्ट: 8504985149</span>
    </div>

    <div class="section-title">7. स्मार्ट एक्शन बटन्स व टूलटिप गाइड (Hover Tooltips)</div>
    <p>टेबल के दाईं तरफ दिए गए रंग-बिरंगे बटन्स पर <b>माउस ले जाते ही (Hover)</b> उनका नाम व काम तुरंत स्क्रीन पर दिखता है:</p>
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 15%;">बटन (Icon)</th>
                <th style="width: 18%;">रंग</th>
                <th style="width: 32%;">माउस ले जाने पर दिखने वाला नाम</th>
                <th>कार्य एवं उपयोग (Action)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="action-tag tag-blue">👁️</span></td>
                <td>नीला</td>
                <td class="strong">👁️ पेमेंट स्क्रीनशॉट देखें</td>
                <td>छात्र द्वारा भेजे गए UPI पेमेंट स्क्रीनशॉट को बड़ा करके देखें।</td>
            </tr>
            <tr>
                <td><span class="action-tag" style="background:#E2E8F0;">🖨️</span></td>
                <td>स्लेट ग्रे</td>
                <td class="strong">🖨️ A4 फीस रसीद प्रिंट करें</td>
                <td>छात्र की आधिकारिक A4 साइज वैध फीस रसीद (PDF) खोलें व प्रिंट करें।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-blue">🪪</span></td>
                <td>जामुनी</td>
                <td class="strong">🪪 पॉकेट आई-कार्ड बनाएं</td>
                <td>संस्थान के लोगो व छात्र विवरण के साथ पॉकेट आई-कार्ड PDF बनाएं।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-orange">💳</span></td>
                <td>नारंगी</td>
                <td class="strong">💳 बकाया किस्त जमा करें</td>
                <td>छात्र की बाकी फीस की अगली किस्त जमा करें और रसीद अपडेट करें।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-green">💬</span></td>
                <td>हरा</td>
                <td class="strong">💬 व्हाट्सएप फीस रिमाइंडर भेजें</td>
                <td>1-क्लिक में छात्र के फोन पर एडमिशन रसीद या फीस रिमाइंडर भेजें।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-green">✅</span></td>
                <td>गहरा हरा</td>
                <td class="strong">✅ कोर्स एक्टिवेट करें</td>
                <td>पेंडिंग छात्र का कोर्स व क्लास एक्सेस तुरंत सक्रिय (Activate) करें।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-red">🗑️</span></td>
                <td>लाल</td>
                <td class="strong">🗑️ रिकॉर्ड डिलीट करें</td>
                <td><b>केवल एडमिन:</b> एडमिन का लॉगिन पासवर्ड डालने पर ही रिकॉर्ड हटेगा।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-blue">🔄</span></td>
                <td>नीला</td>
                <td class="strong">तालिका रिफ्रेश करें</td>
                <td>नए एडमिशन या किस्तों के बाद रिकॉर्ड्स टेबल को तुरंत रिफ्रेश करें।</td>
            </tr>
            <tr>
                <td><span class="action-tag tag-blue">📊</span></td>
                <td>इलेक्ट्रिक सायन</td>
                <td class="strong">एक्सेल शीट डाउनलोड करें</td>
                <td>सभी छात्रों का सम्पूर्ण डेटा एक्सेल (.xlsx) फॉर्मेट में एक्सपोर्ट करें।</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">8. खर्च प्रबंधन एवं शुद्ध मुनाफा (Expense & P&L Live Tracking)</div>
    <p>सॉफ्टवेयर में कोचिंग का P&L (Profit & Loss) लाइव कैलकुलेट होता है:</p>
    <div class="callout-box cyan">
        <b>शुद्ध बचत (Net Profit) = कुल प्राप्त फीस कलेक्शन - कुल संस्थान खर्चे</b>
    </div>
    <ul class="guide-list">
        <li><b>खर्च की श्रेणियां:</b> किराया (Rent), बिजली, फैकल्टी वेतन, इंटरनेट, स्टेशनरी आदि दर्ज करें।</li>
        <li><b>अकाउंटेंट एक्सेस:</b> अकाउंटेंट यूजर खर्चे दर्ज कर सकता है और सीए/टैक्स ऑडिट हेतु एक्सेल शीट एक्सपोर्ट कर सकता है।</li>
    </ul>

    <div class="page-footer">
        <span>Created BY: Apna Computer  |  Helpline: 8504985149</span>
        <span>पेज 4</span>
    </div>
</div>

<!-- ===================================================================== -->
<!-- PAGE 5: EOD REPORTING & 1-CLICK GMAIL BACKUP -->
<!-- ===================================================================== -->
<div class="page">
    <div class="page-header">
        <span class="brand">APNA COMPUTER RMS — ऑपरेटिंग व ट्रेनिंग मैनुअल</span>
        <span>सपोर्ट: 8504985149</span>
    </div>

    <div class="section-title">9. दैनिक शाम की EOD रिपोर्टिंग व 1-क्लिक जीमेल बैकअप (Zero-Password Mail)</div>
    <p>
        दिनभर का काम खत्म होने पर शाम को संस्थान के मुख्य ईमेल <b>krishnaskb143@gmail.com</b> पर दैनिक रिपोर्ट भेजने की विस्तृत प्रक्रिया:
    </p>

    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 18%;">कदम (Step)</th>
                <th style="width: 32%;">स्टाफ को क्या करना है</th>
                <th>सिस्टम का स्वचालित व्यवहार</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="strong">स्टेप 1: बटन दबाएं</td>
                <td>मेनू में <b>Reports & EOD Mail</b> पर जाएं और लाल बटन दबाएं: <b>"1-क्लिक जीमेल में भेजें (Open in Gmail)"</b></td>
                <td>सिस्टम आज के सभी नए एडमिशन की एक्सेल शीट और सभी पेमेंट स्क्रीनशॉट्स का ज़िप (.zip) फाइल बैकग्राउंड में तैयार कर लेता है।</td>
            </tr>
            <tr>
                <td class="strong">स्टेप 2: फोल्डर खुलना</td>
                <td>स्क्रीन पर सामने खुले फोल्डर में आज की 2 फाइलें दिखेंगी: <code>Admissions_Today.xlsx</code> और <code>Screenshots_Today.zip</code></td>
                <td>Windows Explorer अपने आप उस फोल्डर को खोलकर स्क्रीन पर सामने ला देता है ताकि स्टाफ को फाइलें ढूंढनी न पड़ें।</td>
            </tr>
            <tr>
                <td class="strong">स्टेप 3: जीमेल खुलना</td>
                <td>आपके ब्राउज़र में Gmail Compose विंडो अपने आप खुल जाएगी।</td>
                <td><b>To: krishnaskb143@gmail.com</b>, विषय (Subject: Daily EOD Report) और पूरा ईमेल ड्राफ्ट पहले से लिखा हुआ मिलेगा।</td>
            </tr>
            <tr>
                <td class="strong">स्टेप 4: ड्रैग एंड ड्रॉप</td>
                <td>स्टाफ दोनों फाइलों को माउस से खींचकर (Drag & Drop) जीमेल में छोड़ देगा और <b>Send</b> बटन दबा देगा!</td>
                <td><b>100% गारंटीड सफलता:</b> इसमें न कोई ऐप पासवर्ड चाहिए, न Google टू-स्टेप वेरिफिकेशन की रुकावट, और न ही कोई टेक्निकल एरर!</td>
            </tr>
        </tbody>
    </table>

    <div class="callout-box">
        <b>सॉफ्टवेयर बंद करते समय ऑटो-रिमाइंडर (Safety Prompt):</b><br/>
        अगर शाम को स्टाफ रिपोर्ट भेजे बिना सॉफ्टवेयर बंद करने की कोशिश करेगा, तो सिस्टम तुरंत अलर्ट देगा: <i>"क्या आपने आज की रिपोर्ट व बैकअप ईमेल पर भेज दिया है?"</i>। स्टाफ वहीं से सीधे <b>"भेजें और बंद करें"</b> चुन सकता है।
    </div>

    <div class="section-title">10. 1-क्लिक पेनड्राइव बैकअप (Full System Backup)</div>
    <ul class="guide-list">
        <li><b>स्थान:</b> Settings (सेटिंग्स) मेनू में जाएं → <b>"पूर्ण सिस्टम बैकअप (Full System Backup)"</b> पर क्लिक करें।</li>
        <li><b>पेनड्राइव चुनें:</b> अपनी पेनड्राइव या बाहरी हार्ड डिस्क का फोल्डर चुनें।</li>
        <li><b>1 सुरक्षित ज़िप फाइल:</b> सॉफ्टवेयर आपके पूरे डेटाबेस, सभी छात्रों के पेमेंट स्क्रीनशॉट्स और फीस रसीदों को 1 सुरक्षित ज़िप फाइल में पैक करके पेनड्राइव में सुरक्षित कर देता है।</li>
        <li><b>सिफारिश:</b> हर शनिवार शाम को 1 पेनड्राइव बैकअप अवश्य बनाकर ऑफिस की अलमारी में रखें।</li>
    </ul>

    <div class="page-footer">
        <span>Created BY: Apna Computer  |  Helpline: 8504985149</span>
        <span>पेज 5</span>
    </div>
</div>

<!-- ===================================================================== -->
<!-- PAGE 6: MULTI-PC SYNC, DISASTER RECOVERY & HELPLINE -->
<!-- ===================================================================== -->
<div class="page">
    <div class="page-header">
        <span class="brand">APNA COMPUTER RMS — ऑपरेटिंग व ट्रेनिंग मैनुअल</span>
        <span>सपोर्ट: 8504985149</span>
    </div>

    <div class="section-title">11. मल्टी-पीसी नेटवर्क सिंक व 4 कंप्यूटरों का डेटा जोड़ना (Multi-PC Setup)</div>
    <p>यदि संस्थान में 3 या 4 लोग अलग-अलग कंप्यूटर पर काम कर रहे हैं, तो उनका डेटा आपस में जोड़ने के 3 तरीके:</p>

    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 26%;">तरीका (Setup Method)</th>
                <th style="width: 32%;">लागू करने का तरीका</th>
                <th>मुख्य लाभ एवं उपयोग</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="strong">तरीका A: वाई-फाई / LAN शेयरिंग (Recommended)</td>
                <td>मालिक के PC के <code>D:\APNA_RMS_DATA</code> फोल्डर को शेयर कर दें। बाकी 3 कंप्यूटर के सेटिंग्स में शेयर्ड पाथ (जैसे: <code>\\DIRECTOR-PC\APNA_RMS_DATA</code>) चुन दें।</td>
                <td><b>100% ऑफ़लाइन व रीयल-टाइम:</b> इंटरनेट के बिना भी काउंसलर के एडमिशन करते ही डायरेक्टर की स्क्रीन पर 1 सेकंड में डेटा दिख जाएगा।</td>
            </tr>
            <tr>
                <td class="strong">तरीका B: Google Drive डेस्कटॉप ऑटो-सिंक</td>
                <td>कंप्यूटर में फ्री "Google Drive for Desktop" डाल दें और डेटाबेस पाथ को गूगल ड्राइव फोल्डर में सेट कर दें।</td>
                <td>अगर स्टाफ घर से काम कर रहा है या दूसरी शाखा में है, तो डेटा अपने आप क्लाउड पर सिंक होकर सब जगह पहुंच जाता है।</td>
            </tr>
            <tr>
                <td class="strong">तरीका C: दैनिक EOD रिपोर्ट असेंबलिंग</td>
                <td>शाम को सभी स्टाफ अपनी दैनिक एक्सेल शीट ईमेल/पेनड्राइव से डायरेक्टर को भेजेंगे।</td>
                <td>डायरेक्टर के पास दिन के अंत में सभी काउंटरों का सम्पूर्ण लेखा-जोखा एक्सेल में एक साथ सुरक्षित रहता है।</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">12. डिजास्टर रिकवरी व कंप्यूटर फॉर्मेट होने पर डेटा सुरक्षा</div>
    <ul class="guide-list">
        <li><b>D: ड्राइव सुरक्षा कवच:</b> सॉफ्टवेयर का डेटा कभी भी C: ड्राइव में नहीं रहता। यह <code>D:\APNA_RMS_DATA\</code> में रहता है। अगर Windows करप्ट हो जाए या कंप्यूटर फॉर्मेट हो जाए, तब भी D: ड्राइव का डेटा 100% सुरक्षित रहता है।</li>
        <li><b>नया कंप्यूटर लगाने पर:</b> नए कंप्यूटर पर बस पेनड्राइव से <code>APNA_Computer_RMS.exe</code> चलाएं और D: ड्राइव का पुराना डेटाबेस फोल्डर चुन लें — 10 सेकंड में सारा पुराना रिकॉर्ड वापस चालू!</li>
    </ul>

    <div class="callout-box navy" style="margin-top: 14px;">
        <div style="font-size: 13px; font-weight: 700; margin-bottom: 5px; color: #00F0FF;">
            तकनीकी सहायता एवं ट्रेनिंग हेल्पलाइन (Official Help Desk)
        </div>
        <div style="font-size: 11.5px; line-height: 1.55;">
            सॉफ्टवेयर संचालन, स्टाफ ट्रेनिंग, बैकअप सेटअप या कस्टमाइजेशन के लिए संपर्क करें:<br/>
            • <b>निर्माता (Created By):</b> <span class="highlight">Apna Computer</span><br/>
            • <b>मोबाइल व व्हाट्सएप (Contact No.):</b> <span class="highlight" style="font-size: 13.5px;">8504985149</span><br/>
            • <b>ईमेल:</b> krishnaskb143@gmail.com<br/>
            <i>"अपना कंप्यूटर — आपके संस्थान को डिजिटल, सुरक्षित और पारदर्शी बनाने का विश्वसनीय साथी।"</i>
        </div>
    </div>

    <div class="page-footer">
        <span>Created BY: Apna Computer  |  Helpline: 8504985149</span>
        <span>पेज 6</span>
    </div>
</div>

</body>
</html>
"""
    html_path = Path(__file__).resolve().parent.parent / "training_manual.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML manual generated at: {html_path}")
    return html_path

def compile_to_pdf(html_path, pdf_path):
    browser_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    browser = None
    for p in browser_paths:
        if os.path.exists(p):
            browser = p
            break
            
    if not browser:
        raise RuntimeError("No Edge or Chrome browser found to compile PDF!")
        
    print(f"Using browser: {browser}")
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        str(html_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Compile stderr:", res.stderr)
        raise RuntimeError(f"Browser PDF compilation failed with code {res.returncode}")
        
    print(f"Successfully generated PDF at: {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    html_file = generate_html_manual()
    pdf_file = Path(__file__).resolve().parent.parent / "APNA_Computer_RMS_Training_Manual.pdf"
    compile_to_pdf(html_file, pdf_file)

    # Also copy to dist folder
    dist_pdf = Path(__file__).resolve().parent.parent / "dist" / "APNA_Computer_RMS_Training_Manual.pdf"
    import shutil
    shutil.copy(pdf_file, dist_pdf)
    print(f"Also copied updated PDF to: {dist_pdf}")
