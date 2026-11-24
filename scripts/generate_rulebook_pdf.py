import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def generate_rulebook_html():
    today_str = datetime.now().strftime("%d %B %Y")
    
    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<title>APNA Computer RMS — सिस्टम रूल-बुक एवं ट्रबलशूटिंग गाइड</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

    @page {{
        size: A4 portrait;
        margin: 10mm 12mm 10mm 12mm;
        @bottom-right {{
            content: counter(page);
        }}
    }}

    * {{
        box-sizing: border-box;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    body {{
        font-family: 'Noto Sans Devanagari', 'Inter', 'Segoe UI', sans-serif;
        color: #1E293B;
        margin: 0;
        padding: 0;
        font-size: 11px;
        line-height: 1.42;
        background: #FFFFFF;
    }}

    .page {{
        page-break-after: always;
        position: relative;
    }}

    .page:last-child {{
        page-break-after: avoid;
    }}

    .header-banner {{
        background: linear-gradient(135deg, #0A2540 0%, #0F3864 100%);
        color: #FFFFFF;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-left: 5px solid #00D2D6;
    }}

    .header-banner h1 {{
        margin: 0 0 3px 0;
        font-size: 19px;
        font-weight: 800;
        letter-spacing: -0.3px;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .header-banner .subtitle {{
        margin: 0 0 5px 0;
        font-size: 11px;
        color: #00D2D6;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .header-banner .meta-bar {{
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        font-size: 10px;
        color: #94A3B8;
        border-top: 1px solid rgba(255, 255, 255, 0.15);
        padding-top: 6px;
        margin-top: 5px;
    }}

    .header-banner .meta-item strong {{
        color: #E2E8F0;
    }}

    .section-title {{
        font-size: 13.5px;
        font-weight: 700;
        color: #0A2540;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 4px;
        margin: 14px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .golden-rule-card {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #F59E0B;
        border-radius: 6px;
        padding: 7px 11px;
        margin-bottom: 7px;
    }}

    .golden-rule-card .rule-num {{
        font-weight: 700;
        color: #D97706;
        font-size: 11.5px;
        margin-bottom: 2px;
    }}

    .golden-rule-card .rule-desc {{
        color: #334155;
        font-size: 10.5px;
        margin: 0;
    }}

    .bug-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 7px;
        margin-bottom: 7px;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        page-break-inside: avoid;
    }}

    .bug-header {{
        background: #0A2540;
        color: #FFFFFF;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 700;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .bug-header .badge {{
        background: #00D2D6;
        color: #0A2540;
        font-size: 9px;
        font-weight: 800;
        padding: 1px 6px;
        border-radius: 10px;
        text-transform: uppercase;
    }}

    .bug-body {{
        padding: 6px 10px;
    }}

    .bug-row {{
        margin-bottom: 3px;
        font-size: 10.5px;
    }}

    .bug-row:last-child {{
        margin-bottom: 0;
    }}

    .bug-label {{
        font-weight: 700;
        color: #475569;
        display: inline-block;
        min-width: 80px;
    }}

    .symptom-tag {{
        color: #DC2626;
        font-weight: 600;
    }}

    .cause-tag {{
        color: #D97706;
    }}

    .fix-box {{
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 3px solid #16A34A;
        border-radius: 5px;
        padding: 5px 9px;
        margin-top: 3px;
        color: #14532D;
        font-size: 10.5px;
    }}

    .fix-box ul {{
        margin: 2px 0 0 0;
        padding-left: 14px;
    }}

    .fix-box li {{
        margin-bottom: 1px;
    }}

    .checklist-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
        font-size: 10.5px;
    }}

    .checklist-table th {{
        background: #0A2540;
        color: #FFFFFF;
        text-align: left;
        padding: 6px 8px;
        font-weight: 600;
    }}

    .checklist-table td {{
        padding: 5px 8px;
        border-bottom: 1px solid #E2E8F0;
    }}

    .checklist-table tr:nth-child(even) {{
        background: #F8FAFC;
    }}

    .code-span {{
        font-family: 'Consolas', monospace;
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 10px;
        color: #0F172A;
    }}

    .footer-bar {{
        margin-top: 18px;
        padding-top: 8px;
        border-top: 1.5px solid #CBD5E1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 10px;
        color: #64748B;
    }}

    .footer-bar .dev-credit strong {{
        color: #0A2540;
    }}
</style>
</head>
<body>

<!-- PAGE 1: TITLE & GOLDEN RULES -->
<div class="page">
    <div class="header-banner">
        <div class="subtitle">Official Standard Operating Procedure (SOP)</div>
        <h1>📜 APNA Computer RMS — सिस्टम रूल-बुक एवं ट्रबलशूटिंग गाइड</h1>
        <div style="font-size: 12px; color: #E2E8F0; margin-top: 4px;">
            Permanent Architecture Rules, Bug History & Technical Resolution Guide • भविष्य के सभी अपडेट्स व प्रोजेक्ट्स हेतु आधिकारिक मार्गदर्शिका
        </div>
        <div class="meta-bar">
            <div class="meta-item">सॉफ्टवेयर निर्माता: <strong>APNA Computer (कृष्णा जी)</strong></div>
            <div class="meta-item">हेल्पलाइन: <strong>8504985149</strong></div>
            <div class="meta-item">ईमेल: <strong>krishnaskb143@gmail.com</strong></div>
            <div class="meta-item">अपडेट तिथि: <strong>{today_str}</strong></div>
            <div class="meta-item">संस्करण: <strong>v2.0 Enterprise</strong></div>
        </div>
    </div>

    <div class="section-title">🏛️ 1. सिस्टम की 7 अपरिवर्तनीय नीतियाँ (Golden Rules)</div>
    <div style="font-size: 11.5px; color: #64748B; margin-bottom: 12px;">
        इन 7 नियमों को भविष्य के किसी भी नए प्रोजेक्ट, फ़ीचर या कंपाइलेशन में कभी भी नहीं तोड़ना है:
    </div>

    <div class="golden-rule-card">
        <div class="rule-num">1. 100% ऑफ़लाइन फर्स्ट (Offline-First Architecture)</div>
        <div class="rule-desc">सॉफ़्टवेयर को चलने के लिए इंटरनेट की आवश्यकता कभी नहीं होनी चाहिए। कोई भी बाहरी API कॉल या सर्वर डिपेंडेंसी कोर फ़ीचर्स में नहीं जोड़ी जाएगी।</div>
    </div>

    <div class="golden-rule-card">
        <div class="rule-num">2. डेटा सुरक्षा एवं ड्राइव पोर्टेबिलिटी (Drive Choice)</div>
        <div class="rule-desc">डेटाबेस, रसीदें और स्क्रीनशॉट्स कभी भी डिफ़ॉल्ट रूप से C:\ ड्राइव में जबरन नहीं डाले जाएंगे। हमेशा यूजर द्वारा चुनी गई ड्राइव (जैसे D:\APNA_RMS_DATA) में रहेंगे ताकि विंडोज़ री-इंस्टॉल होने पर भी डेटा 100% सुरक्षित रहे।</div>
    </div>

    <div class="golden-rule-card">
        <div class="rule-num">3. सुपर एडमिन व वेंडर कंट्रोल (Vendor Master Control)</div>
        <div class="rule-desc">सुपर एडमिन (<span class="code-span">hanuganeshan</span>) का खाता और सेटिंग्स का वेंडर पैनल हमेशा क्लाइंट एडमिन से ऊपर और लॉक रहेगा। लोगो व कोर ब्रांडिंग बदलने का अधिकार केवल सुपर एडमिन के पास रहेगा तथा रसीद के फुटर में डेवलपर क्रेडिट लाइन सुरक्षित रहेगी।</div>
    </div>

    <div class="golden-rule-card">
        <div class="rule-num">4. एग्जीक्यूटेबल नामकरण नियम (EXE Naming)</div>
        <div class="rule-desc">आउटपुट फाइल का नाम हमेशा शुद्ध रूप से <span class="code-span">APNA_Computer_RMS.exe</span> व इंस्टॉलर का नाम <span class="code-span">APNA_Computer_RMS_Setup.exe</span> रहेगा। कभी भी "Release" या कोई अन्य प्रत्यय (suffix) नहीं जोड़ना है।</div>
    </div>

    <div class="golden-rule-card">
        <div class="rule-num">5. CustomTkinter फॉन्ट साइज़ नियम (Integer Font Sizes)</div>
        <div class="rule-desc">Python 3.15 में CustomTkinter के सभी फॉन्ट साइज़ अनिवार्य रूप से पूर्णांक (Integer - जैसे 11, 12, 14, 16) होने चाहिए। कभी भी फ्लोट (<span class="code-span">11.5</span>, <span class="code-span">9.5</span>) नहीं देना है।</div>
    </div>

    <div class="golden-rule-card">
        <div class="rule-num">6. CustomTkinter बॉर्डर कलर नियम (Border Width Rule)</div>
        <div class="rule-desc"><span class="code-span">border_color="transparent"</span> कभी नहीं लिखना है (यह विंडोज़ पर क्रैश करता है)। जब बॉर्डर न चाहिए हो तो <span class="code-span">border_width=0</span> रखें।</div>
    </div>

    <div class="golden-rule-card" style="border-left-color: #00D2D6;">
        <div class="rule-num" style="color: #0284C7;">7. EXE मेटाडेटा एवं प्रॉपर्टीज़ नियम (Windows Properties -> Details Tab Rule)</div>
        <div class="rule-desc">भविष्य के किसी भी प्रोजेक्ट या नए कंपाइलेशन में Windows Properties -> Details टैब को कभी खाली (<span class="code-span">0.0.0.0</span> या Blank Copyright) नहीं छोड़ना है। PyInstaller के लिए <span class="code-span">file_version_info.txt</span> और Inno Setup के लिए <span class="code-span">VersionInfoCompany</span>, <span class="code-span">VersionInfoDescription</span>, <span class="code-span">VersionInfoVersion=1.0.0.0</span>, <span class="code-span">VersionInfoCopyright</span>, <span class="code-span">AppComments</span> हमेशा अनिवार्य रूप से जोड़े जाएंगे ताकि क्लाइंट राइट-क्लिक करके डेवलपर, हेल्पलाइन नंबर और अधिकृत कॉपीराइट देख सके।</div>
    </div>
</div>

<!-- PAGE 2: BUGS 1 TO 6 -->
<div class="page">
    <div class="section-title">🔍 2. ऐतिहासिक समस्याओं की सूची और उनका स्थायी समाधान (Bugs 1 - 6)</div>

    <!-- Bug 1 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 1: PDF रसीद में हिंदी का ख़राब दिखना (Broken Glyphs / Blue Underlines)</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">ReportLab से बनी रसीद में हिंदी शब्द काले डिब्बों (■■■) में आते थे या Chrome में नीली डॉटेड अंडरलाइन दिखती थी।</span></div>
            <div class="bug-row"><span class="bug-label">मूल कारण (Cause):</span> <span class="cause-tag">ReportLab में OpenType HarfBuzz टेक्स्ट शेपिंग इंजन नहीं था तथा Windows सिस्टम फॉन्ट्स मिसमैच थे।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> रसीद जनरेशन को ReportLab से हटाकर <strong>HTML5 + CSS3 + Playwright Chromium Engine</strong> पर माइग्रेट किया गया। प्रोजेक्ट में Google के आधिकारिक <strong>NotoSansDevanagari</strong> फॉन्ट्स को Base64 Data URI के रूप में इंजेक्ट किया गया ताकि विंडोज़ सिस्टम फॉन्ट पर कोई निर्भरता न रहे।
            </div>
        </div>
    </div>

    <!-- Bug 2 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 2: रसीद डाउनलोड/प्रिंट में लैग तथा ऐप स्टार्टअप स्पीड</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">प्रिंट बटन दबाने पर 10-15 सेकंड का लैग आता था और ऐप स्टार्टअप भारी हो जाता था।</span></div>
            <div class="bug-row"><span class="bug-label">मूल कारण (Cause):</span> <span class="cause-tag">हर प्रिंट पर नया Chromium प्रोसेस शून्य से स्टार्ट हो रहा था और ऐप ओपन होते ही बैकग्राउंड में लोड होता था।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> 1. Persistent Worker Pool बनाया गया। 2. Strict Lazy Loading लागू की गई जिससे स्टार्टअप पर 0 Chromium प्रोसेस लोड होते हैं। 3. Smart Cache Check द्वारा पहले से मौजूद रसीद 0.05 सेकंड में तुरंत खुल जाती है।
            </div>
        </div>
    </div>

    <!-- Bug 3 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 3: लॉगिन स्क्रीन पर "admin" यूज़रनेम ऑटो-फिल होना (OS Autofill)</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">लॉगिन बॉक्स खाली होने के बजाय अपने आप "admin" लिखा हुआ आ जाता था।</span></div>
            <div class="bug-row"><span class="bug-label">मूल कारण (Cause):</span> <span class="cause-tag">विंडोज़ ऑपरेटिंग सिस्टम का क्रेडेंशियल ऑटो-फिल इनपुट बॉक्स में टेक्स्ट इंजेक्ट कर रहा था।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> ऑटो-फिल टाइमर को शुद्ध UI फोकस स्टेट मशीन द्वारा रिप्लेस किया गया और फील्ड्स को क्लीन लोड किया गया।
            </div>
        </div>
    </div>

    <!-- Bug 4 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 4: Master Recovery Key का "Invalid" बताना</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">डेमो मोड या फ्रेश इंस्टॉल में मास्टर की दर्ज करने पर Invalid Key का एरर आता था।</span></div>
            <div class="bug-row"><span class="bug-label">मूल कारण (Cause):</span> <span class="cause-tag">डेमो डेटाबेस रीसेट होते समय रिकवरी की टेबल में सेव नहीं हो रही थी।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> <span class="code-span">launch_instant_demo()</span> में रिकवरी की सेव की गई तथा यूनिवर्सल वेंडर मास्टर की <strong>APNA-ADMIN-RECOVERY</strong> को स्थायी रूप से कोड में सुरक्षित किया गया।
            </div>
        </div>
    </div>

    <!-- Bug 5 & 6 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 5 व 6: एग्जिट डायलॉग टेक्स्ट कंट्रास्ट एवं वेंडर लीगल आईपी ब्रांडिंग</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">लाइट थीम में डायलॉग का टेक्स्ट छिप जाता था, और रसीद पर डेवलपर की अधिकृत लाइन नहीं थी।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> डायनामिक थीम ट्यूपल <span class="code-span">text_color=("#334155", "#CBD5E1")</span> लागू किया गया। रसीद के फुटर में अधिकृत लीगल लाइन जोड़ी गई: <em>"Software Developed & Licensed by APNA Computer (कृष्णा जी) | Helpline: 8504985149"</em>।
            </div>
        </div>
    </div>
</div>

<!-- PAGE 3: BUGS 7 TO 12 -->
<div class="page">
    <div class="section-title">🔍 2. ऐतिहासिक समस्याओं की सूची और उनका स्थायी समाधान (Bugs 7 - 12)</div>

    <!-- Bug 7 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 7: ऑफलाइन फोल्डर डिलीट या छेड़छाड़ का खतरा (Self-Healing Shadow Vault)</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">यदि कोई D:\APNA_RMS_DATA फोल्डर डिलीट कर दे तो सारा डेटा नष्ट होने का जोखिम था।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> 1. हिडन शैडो वॉल्ट (<span class="code-span">%LOCALAPPDATA%\\APNA_Computer_RMS\\vault</span>) बनाया गया। 2. SQLite Live Backup API द्वारा ज़ीरो-लॉक बैकअप होता है। 3. फोल्डर डिलीट होने पर ऐप शुरू होते ही 1 सेकंड में 100% डेटा व रसीदें ऑटो-रीस्टोर हो जाती हैं।
            </div>
        </div>
    </div>

    <!-- Bug 8 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 8: रूट विंडो डिस्ट्रॉय से स्क्रीन फ्रीज (TclError: cannot invoke "wm" command)</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">क्विक लाइव डेमो बटन दबाने या लॉगिन करने के बाद विंडो फ्रीज या क्रैश हो जाती थी।</span></div>
            <div class="bug-row"><span class="bug-label">मूल कारण (Cause):</span> <span class="cause-tag">LoginWindow और MainWindow दोनों अलग-अलग CTk रूट विंडो थीं। पहली को destroy करने पर Tcl क्रैश हो जाता था।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> <strong>सिंगल-रूट आर्किटेक्चर (<span class="code-span">ApnaRMSApp(ctk.CTk)</span>)</strong> लागू किया गया। ऐप में केवल एक स्थायी रूट विंडो रहती है और व्यू केवल फ्रेम्स के रूप में बिना रूट डिस्ट्रॉय किए तुरंत स्वैप होते हैं।
            </div>
        </div>
    </div>

    <!-- Bug 9 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 9: Settings & Backup का ब्लैंक दिखना और लॉगिन स्टक होना</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">सेटिंग्स पर क्लिक करने पर स्क्रीन ब्लैंक हो जाना और लॉगिन बटन पर एरर न दिखना।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> 1. <span class="code-span">settings_view.py</span> में मिसिंग इंपोर्ट्स व नल-सेफ फॉलबैक्स जोड़े गए। 2. <span class="code-span">MainWindow.navigate_to()</span> को बुलेटप्रूफ try-except में रैप किया गया ताकि स्क्रीन कभी ब्लैंक न रहे। 3. <span class="code-span">hanuganeshan</span> और <span class="code-span">admin</span> हेतु ऑटो-हीलिंग क्रेडेंशियल ऑथेंटिकेशन लागू किया गया।
            </div>
        </div>
    </div>

    <!-- Bug 10 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 10: क्लाइंट PC पर इंस्टॉलेशन के बाद डेस्कटॉप आइकन न बनना</span>
            <span class="badge">Fixed</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">सॉफ्टवेयर इंस्टॉल करने पर डेस्कटॉप पर कोई आइकन नहीं बनता था।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> <span class="code-span">installer_setup.iss</span> से <span class="code-span">Flags: unchecked</span> हटा दिया गया। अब हर कंप्यूटर पर "Create Desktop Icon" स्वतः टिक रहता है और 1-क्लिक में डेस्कटॉप पर आइकन बन जाता है।
            </div>
        </div>
    </div>

    <!-- Bug 11 -->
    <div class="bug-card">
        <div class="bug-header">
            <span>समस्या 11: उत्पादकता बढ़ाने हेतु ग्लोबल कीबोर्ड शॉर्टकट्स</span>
            <span class="badge">Feature</span>
        </div>
        <div class="bug-body">
            <div class="fix-box" style="background: #F8FAFC; border-color: #CBD5E1; border-left-color: #0284C7; color: #0F172A;">
                <strong>शॉर्टकट सूची:</strong> 
                <span class="code-span">Ctrl+1</span> डैशबोर्ड | 
                <span class="code-span">Ctrl+2 / F2</span> नया एडमिशन | 
                <span class="code-span">Ctrl+3</span> छात्र रिकॉर्ड | 
                <span class="code-span">Ctrl+4</span> एक्टिवेशन | 
                <span class="code-span">Ctrl+5</span> टाइम-टेबल | 
                <span class="code-span">Ctrl+6</span> स्टाफ | 
                <span class="code-span">Ctrl+7</span> खर्चे | 
                <span class="code-span">Ctrl+8</span> रिपोर्ट्स | 
                <span class="code-span">Ctrl+9</span> सेटिंग्स व बैकअप | 
                <span class="code-span">F5</span> डेटा रिफ्रेश
            </div>
        </div>
    </div>

    <!-- Bug 12 -->
    <div class="bug-card" style="border-left: 3px solid #00D2D6;">
        <div class="bug-header" style="background: #0F3864;">
            <span>समस्या 12: Windows Properties -> Details टैब में 0.0.0.0 वर्शन व ब्लैंक कॉपीराइट दिखना</span>
            <span class="badge" style="background: #F59E0B; color: #000;">New Solution</span>
        </div>
        <div class="bug-body">
            <div class="bug-row"><span class="bug-label">लक्षण (Symptom):</span> <span class="symptom-tag">Setup.exe पर राइट-क्लिक करके Properties -> Details में File version 0.0.0.0 आता था और कॉपीराइट पूरी तरह खाली था।</span></div>
            <div class="bug-row"><span class="bug-label">मूल कारण (Cause):</span> <span class="cause-tag">Inno Setup स्क्रिप्ट में VersionInfoVersion और VersionInfoCompany डायरेक्टिव्स शामिल नहीं थे।</span></div>
            <div class="fix-box">
                <strong>स्थायी समाधान:</strong> 
                1. <span class="code-span">installer_setup.iss</span> में <span class="code-span">VersionInfoVersion=1.0.0.0</span>, <span class="code-span">VersionInfoCompany=APNA Computer (Helpline: 8504985149)</span>, <span class="code-span">VersionInfoCopyright</span> व <span class="code-span">AppComments</span> जोड़े गए।<br>
                2. <span class="code-span">file_version_info.txt</span> में मुख्य EXE हेतु StringTable में कंपनी, हेल्पलाइन व कॉपीराइट एम्बेड किए गए।<br>
                3. <span class="code-span">scripts/sign_executable.ps1</span> द्वारा डिजिटल हस्ताक्षर लगाना अनिवार्य किया गया।
            </div>
        </div>
    </div>
</div>

<!-- PAGE 4: SOP CHECKLIST & CONTACT -->
<div class="page">
    <div class="section-title">🛠️ 3. भविष्य के लिए डेवलपमेंट व डिप्लॉयमेंट चेकलिस्ट (SOP)</div>
    <div style="font-size: 11.5px; color: #64748B; margin-bottom: 10px;">
        जब भी भविष्य में कोई नया बदलाव किया जाए, डेवलपर को निम्नलिखित चरणों का अनिवार्य रूप से पालन करना होगा:
    </div>

    <table class="checklist-table">
        <thead>
            <tr>
                <th style="width: 25%;">स्टेज</th>
                <th style="width: 50%;">कार्य एवं अनिवार्य चेकपॉइंट</th>
                <th style="width: 25%;">कमांड / लोकेशन</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>चरण 1: कोड बदलाव</strong></td>
                <td>
                    • किसी भी CTkFont में फ्लोट साइज़ न दें (केवल integer दें)<br>
                    • <span class="code-span">border_color="transparent"</span> कभी न लिखें<br>
                    • Noto Sans Devanagari फॉन्ट को कभी न हटाएं
                </td>
                <td><span class="code-span">ui/</span>, <span class="code-span">core/</span></td>
            </tr>
            <tr>
                <td><strong>चरण 2: वर्शन व मेटाडेटा</strong></td>
                <td>
                    • <span class="code-span">file_version_info.txt</span> में वर्शन 1.0.0.0 व हेल्पलाइन चेक करें<br>
                    • <span class="code-span">installer_setup.iss</span> में VersionInfo directivies चेक करें
                </td>
                <td>Root Directory</td>
            </tr>
            <tr>
                <td><strong>चरण 3: नया EXE बिल्ड</strong></td>
                <td>
                    • <span class="code-span">fonts/</span> में चारों TTF फाइलें मौजूद हों<br>
                    • PyInstaller और Inno Setup द्वारा नया सेटअप कंपाइल करें
                </td>
                <td><span class="code-span">python scripts/build_portable_and_installer.py</span></td>
            </tr>
            <tr>
                <td><strong>चरण 4: डिजिटल हस्ताक्षर</strong></td>
                <td>
                    • Authenticode डिजिटल सर्टिफिकेट से Setup.exe को साइन करें<br>
                    • Properties -> Digital Signatures टैब में APNA Computer Institute सत्यापित करें
                </td>
                <td><span class="code-span">powershell -File scripts/sign_executable.ps1</span></td>
            </tr>
            <tr>
                <td><strong>चरण 5: क्वालिटी ऑडिट</strong></td>
                <td>
                    • 12-स्टेज सिस्टम ऑडिट चलाकर 100% पास सुनिश्चित करें<br>
                    • Properties -> Details टैब में वर्शन 1.0.0.0 व कॉपीराइट चेक करें
                </td>
                <td><span class="code-span">python tests/ultimate_system_audit.py</span></td>
            </tr>
            <tr>
                <td><strong>चरण 6: गिट कमिट व सिंक</strong></td>
                <td>
                    • कोई टेस्ट/स्क्रैच फाइल गिट पर ट्रैक न हो<br>
                    • <span class="code-span">dist/APNA_Computer_RMS_Setup.exe</span> को main ब्रांच पर पुश करें
                </td>
                <td><span class="code-span">git push origin main</span></td>
            </tr>
        </tbody>
    </table>

    <div style="background: linear-gradient(135deg, #0A2540 0%, #133E68 100%); color: #FFFFFF; border-radius: 10px; padding: 18px 22px; margin-top: 30px;">
        <div style="font-size: 15px; font-weight: 700; color: #00D2D6; margin-bottom: 8px;">
            📞 आधिकारिक संपर्क व तकनीकी सहायता (Authorized Contact & Support)
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
            <div>• <strong>सॉफ्टवेयर निर्माता:</strong> APNA Computer (कृष्णा जी)</div>
            <div>• <strong>आधिकारिक हेल्पलाइन:</strong> 8504985149</div>
            <div>• <strong>सपोर्ट ईमेल:</strong> krishnaskb143@gmail.com</div>
            <div>• <strong>लाइसेंस प्रकार:</strong> अधिकृत कमर्शियल डेस्कटॉप सॉल्यूशन</div>
            <div>• <strong>सुरक्षा मोड:</strong> 100% ऑफलाइन लोकल एन्क्रिप्टेड</div>
            <div>• <strong>Hardware ID:</strong> APNA-RMS-HQ-2026</div>
        </div>
    </div>

    <div class="footer-bar">
        <div class="dev-credit">APNA Computer RMS v2.0 • <strong>System Rulebook & Troubleshooting Guide</strong></div>
        <div>Page 4 of 4 • Confidential & Official Developer SOP</div>
    </div>
</div>

</body>
</html>
"""
    return html

def compile_pdf(html_content, output_pdf_path):
    temp_html = Path(os.environ.get('TEMP', '.')) / "rulebook_temp.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

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
        raise RuntimeError("No Chromium browser found for PDF compilation!")

    temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'edge_pdf_profile')
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={temp_dir}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path}",
        str(temp_html)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"PDF Compile failed: {res.stderr}")
    print(f"Generated: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")

if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    dist_doc_dir = root_dir / "dist" / "Documentation"
    dist_doc_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Generating APNA Computer RMS System Rulebook PDF...")
    rulebook_html = generate_rulebook_html()
    
    # 1. Output to dist/Documentation/
    pdf_path1 = dist_doc_dir / "SYSTEM_RULEBOOK_AND_TROUBLESHOOTING.pdf"
    compile_pdf(rulebook_html, pdf_path1)
    
    # 2. Also output named APNA_Computer_RMS_System_Rulebook.pdf for easy sharing
    pdf_path2 = dist_doc_dir / "APNA_Computer_RMS_System_Rulebook.pdf"
    import shutil
    shutil.copy2(pdf_path1, pdf_path2)
    print(f"Copied alias: {pdf_path2}")
    
    print("\n✅ System Rulebook PDF generated successfully!")
