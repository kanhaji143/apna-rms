"""
APNA COMPUTER RMS — Widescreen 16:9 Presentation Deck PDF Generator
Renders an executive, high-resolution slide deck in PDF format matching the PPTX.
Ensures clients can view the presentation on mobile, WhatsApp, or any PC without PowerPoint.
"""

import os
import subprocess
from pathlib import Path

def generate_presentation_deck_html():
    return """<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<title>APNA COMPUTER RMS — Client Presentation Pitch Deck</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700;800&display=swap');
    
    @page {
        size: 297mm 167mm; /* 16:9 widescreen landscape */
        margin: 0;
    }
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    body {
        font-family: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #0A192F;
        color: #0F172A;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .slide {
        width: 297mm;
        height: 167mm;
        page-break-after: always;
        position: relative;
        background: #F8FAFC;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    /* SLIDE HEADER & FOOTER */
    .slide-header {
        background: #0A192F;
        color: #FFFFFF;
        padding: 10px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #00F0FF;
    }
    .slide-header .cat {
        font-size: 10px;
        font-weight: 700;
        color: #00F0FF;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .slide-header h2 {
        font-size: 16px;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 2px;
    }
    .slide-body {
        flex: 1;
        padding: 14px 24px;
        display: flex;
        flex-direction: column;
    }
    .slide-footer {
        background: #0A192F;
        color: #94A3B8;
        padding: 6px 24px;
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        border-top: 1px solid #1E293B;
    }
    .slide-footer span.bold {
        color: #FFFFFF;
        font-weight: 600;
    }

    /* HERO SLIDE */
    .hero-slide {
        background: radial-gradient(circle at top right, #1E3A8A 0%, #0A192F 70%);
        color: #FFFFFF;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 30px;
    }
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        color: #00F0FF;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .hero-sub {
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 12px;
    }
    .hero-tag {
        display: inline-block;
        background: rgba(0, 240, 255, 0.15);
        color: #FBBF24;
        border: 1px solid #F59E0B;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 24px;
    }
    .hero-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        width: 100%;
        max-width: 1000px;
        margin-top: 10px;
    }
    .hero-card {
        background: rgba(15, 34, 64, 0.85);
        border: 1px solid #00F0FF;
        border-radius: 8px;
        padding: 12px;
        text-align: left;
    }
    .hero-card h4 {
        color: #FFFFFF;
        font-size: 12.5px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .hero-card p {
        color: #00F0FF;
        font-size: 10.5px;
        line-height: 1.3;
    }

    /* GRID LAYOUTS */
    .grid-2x4 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        flex: 1;
    }
    .pitch-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 8px 12px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .pitch-card h4 {
        font-size: 11.5px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 3px;
    }
    .pitch-card p {
        font-size: 10px;
        color: #334155;
        line-height: 1.35;
    }

    /* DIAGRAM BOXES */
    .diag-container {
        background: #FFFFFF;
        border: 1.5px solid #0284C7;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .diag-flow {
        display: grid;
        grid-template-columns: 1fr auto 1fr auto 1fr;
        align-items: center;
        gap: 10px;
        text-align: center;
        margin-top: 8px;
    }
    .diag-node {
        border-radius: 6px;
        padding: 10px;
    }
    .diag-arrow {
        font-size: 20px;
        font-weight: bold;
    }

    /* 4-COLUMN CARDS */
    .grid-4col {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        flex: 1;
    }
    .col-card {
        border-radius: 8px;
        padding: 12px;
        display: flex;
        flex-direction: column;
    }
    .col-card h3 {
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .col-card p, .col-card li {
        font-size: 9.5px;
        line-height: 1.4;
        color: #1E293B;
    }

    /* 2-COLUMN FEATURE CARDS */
    .grid-2col {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        flex: 1;
    }
    .feat-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 10px 12px;
    }
    .feat-card h4 {
        font-size: 12px;
        font-weight: 700;
        color: #0284C7;
        margin-bottom: 4px;
    }
    .feat-card p {
        font-size: 10px;
        color: #334155;
        line-height: 1.4;
    }
</style>
</head>
<body>

<!-- SLIDE 1: HERO TITLE SLIDE -->
<div class="slide hero-slide">
    <div class="hero-title">APNA COMPUTER RMS</div>
    <div class="hero-sub">Coaching & Computer Institute Operating System</div>
    <div class="hero-tag">⚡ 100% Offline • Zero-Cloud Subscriptions • 0.05s Instant Speed • Self-Healing Vault</div>

    <div class="hero-grid">
        <div class="hero-card">
            <h4>🛡️ Self-Healing Vault</h4>
            <p>Shift+Delete होने पर भी 1 सेकंड में 100% डेटा व रसीदें जीवित</p>
        </div>
        <div class="hero-card">
            <h4>⚡ 100% True Offline</h4>
            <p>शून्य इंटरनेट, शून्य सर्वर बिल, बेसमेंट में भी 0.05s स्पीड</p>
        </div>
        <div class="hero-card">
            <h4>📄 शुद्ध हिंदी रसीदें</h4>
            <p>Google Noto Sans Devanagari—कोई काले डिब्बे (■■■) नहीं</p>
        </div>
        <div class="hero-card">
            <h4>⭐ 30-दिन VIP ट्रायल</h4>
            <p>हार्डवेयर-लॉक्ड ACR-XXXX व रिमोट WhatsApp एक्सटेंशन</p>
        </div>
    </div>

    <div style="margin-top: 24px; font-size: 12px; color: #E2E8F0;">
        <strong>सॉफ्टवेयर निर्माता:</strong> APNA Computer (कृष्णा जी)  |  <strong>हेल्पलाइन:</strong> 8504985149  |  Confidential Presentation Deck
    </div>
</div>

<!-- SLIDE 2: 2-MINUTE MAGIC ELEVATOR PITCH -->
<div class="slide">
    <div class="slide-header">
        <div>
            <div class="cat">EXECUTIVE ELEVATOR PITCH</div>
            <h2>⚡ 2-मिनट का अचूक मैजिक पिच (The 2-Minute Magic Pitch)</h2>
        </div>
        <div style="color:#00F0FF; font-size: 11px; font-weight: bold;">8 Unbeatable Highlights</div>
    </div>
    <div class="slide-body">
        <div class="grid-2x4">
            <div class="pitch-card" style="border-left: 3px solid #10B981; background: #F0FDF4;">
                <h4>1. 🛡️ सेल्फ-हीलिंग शैडो वॉल्ट:</h4>
                <p>मुख्य D:\\ फोल्डर Shift+Delete होने पर भी हिडन वॉल्ट से 1 सेकंड में 100% डेटा व रसीदें ऑटो-रीस्टोर हो जाती हैं।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #0284C7; background: #F0F9FF;">
                <h4>2. ⚡ 100% ट्रू ऑफलाइन-फर्स्ट:</h4>
                <p>शून्य इंटरनेट, शून्य मासिक सर्वर बिल। बेसमेंट या ग्रामीण इलाके में भी 0.05 सेकंड की सुपरफास्ट स्पीड।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #8B5CF6;">
                <h4>3. 📄 क्रिस्टल-क्लियर हिंदी रसीदें:</h4>
                <p>Google Noto Sans Devanagari व Chromium शेपिंग इंजन—कोई काले डिब्बे (■■■) नहीं, शुद्ध A4/हाफ रसीद प्रिंट।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #F59E0B; background: #FEFCE8;">
                <h4>4. 🔑 30-दिन VIP ट्रायल व WhatsApp एक्सटेंशन:</h4>
                <p>हार्डवेयर-लॉक्ड ACR-XXXX ID। 30 दिन बाद वेंडर द्वारा WhatsApp पर 10-15 दिन का एक्सटेंशन कोड तुरंत जारी।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #EF4444; background: #FEF2F2;">
                <h4>5. ⏰ एंटी-क्लॉक टैम्परिंग इंजन:</h4>
                <p>यदि कोई ऑपरेटर कंप्यूटर की घड़ी पीछे करके ट्रायल बाईपास करने की कोशिश करे, तो सिस्टम तुरंत लॉक लगा देता है।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #059669;">
                <h4>6. 💾 1-क्लिक EOD पेनड्राइव बैकअप:</h4>
                <p>दिन समाप्त होने पर 1 क्लिक में पेनड्राइव बैकअप—कंप्यूटर जल जाए या चोरी हो जाए, कोचिंग का काम कभी नहीं रुकता।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #6366F1;">
                <h4>7. 🔀 मल्टी-पीसी सेफ डेटा मर्जिंग:</h4>
                <p>रिसेप्शन और डायरेक्टर केबिन के अलग-अलग पीसी का डेटा बिना किसी डुप्लीकेसी के 1 सेकंड में सुरक्षित मर्ज।</p>
            </div>
            <div class="pitch-card" style="border-left: 3px solid #0D9488;">
                <h4>8. 🔒 ज़ीरो-बैट व Authenticode साइंड:</h4>
                <p>कोई सस्पेक्टेड बैट फ़ाइल नहीं। Microsoft Authenticode SHA-256 साइंड सिंगल .exe जो बिना रुकावट चलती है।</p>
            </div>
        </div>
    </div>
    <div class="slide-footer">
        <span>APNA Computer RMS • Confidential Pitch Deck</span>
        <span class="bold">पेज 2 / 5</span>
        <span>हेल्पलाइन: 8504985149</span>
    </div>
</div>

<!-- SLIDE 3: VISUAL ARCHITECTURE & DISASTER RECOVERY DIAGRAM -->
<div class="slide">
    <div class="slide-header">
        <div>
            <div class="cat">SYSTEM RESILIENCE & ARCHITECTURE</div>
            <h2>📊 विजुअल सिस्टम आर्किटेक्चर डायग्राम (Visual Architecture & Recovery Flow)</h2>
        </div>
        <div style="color:#00F0FF; font-size: 11px; font-weight: bold;">Zero Data Loss Blueprint</div>
    </div>
    <div class="slide-body">
        <!-- ARCHITECTURE DIAGRAM -->
        <div class="diag-container">
            <div style="font-weight: 700; color: #0284C7; font-size: 12px; margin-bottom: 4px;">
                1. डुअल-राइट सेल्फ-हीलिंग आर्किटेक्चर (Dual-Write Vault Architecture):
            </div>
            <div class="diag-flow">
                <div class="diag-node" style="background: #E0F2FE; border: 1.5px solid #0284C7;">
                    <div style="font-weight: 800; color: #0369A1; font-size: 12px;">🖥️ रिसेप्शन / कैश काउंटर</div>
                    <div style="font-size: 10px; color: #334155; margin-top: 3px;">100% ऑफलाइन लोकल ऐप<br>0.05 सेकंड इंस्टेंट स्पीड</div>
                </div>
                <div class="diag-arrow" style="color: #0284C7;">⇄</div>
                <div class="diag-node" style="background: #FEF3C7; border: 1.5px solid #F59E0B;">
                    <div style="font-weight: 800; color: #B45309; font-size: 12px;">📁 मुख्य डेटाबेस (D:\ Drive)</div>
                    <div style="font-size: 10px; color: #334155; margin-top: 3px;">SQLite WAL Mode मास्टर DB<br>रसीदें व डेटा फ़ाइलें</div>
                </div>
                <div class="diag-arrow" style="color: #10B981;">⇄</div>
                <div class="diag-node" style="background: #DCFCE7; border: 2px solid #10B981;">
                    <div style="font-weight: 800; color: #15803D; font-size: 12px;">🛡️ सेल्फ-हीलिंग शैडो वॉल्ट</div>
                    <div style="font-size: 10px; color: #334155; margin-top: 3px;">Hidden %LOCALAPPDATA%<br>1 सेकंड में स्वतः रीस्टोर</div>
                </div>
            </div>
        </div>

        <!-- RECOVERY STEPS -->
        <div style="font-weight: 700; color: #15803D; font-size: 12px; margin-bottom: 6px;">
            2. आपदा रिकवरी चक्र (Disaster Recovery & Self-Healing Lifecycle):
        </div>
        <div class="grid-4col" style="flex: unset; height: 75px;">
            <div class="col-card" style="background: #FEE2E2; border: 1px solid #F87171;">
                <h3 style="color: #991B1B;">1. खतरा / डिलीट</h3>
                <p>मुख्य D:\ फोल्डर Shift+Delete या करप्ट हुआ।</p>
            </div>
            <div class="col-card" style="background: #FEF3C7; border: 1px solid #FCD34D;">
                <h3 style="color: #92400E;">2. ऑटो-डिटेक्शन</h3>
                <p>सॉफ्टवेयर स्टार्ट होते ही शैडो वॉल्ट चेक करता है।</p>
            </div>
            <div class="col-card" style="background: #DCFCE7; border: 1.5px solid #4ADE80;">
                <h3 style="color: #166534;">3. ऑटो-रीस्टोर</h3>
                <p>1 सेकंड में संपूर्ण DB व रसीदें जीवित हो जाती हैं।</p>
            </div>
            <div class="col-card" style="background: #E0F2FE; border: 1px solid #7DD3FC;">
                <h3 style="color: #075985;">4. ब्लैक-बॉक्स लॉग</h3>
                <p>SECURITY_RECOVERY_LOG.txt में समय दर्ज।</p>
            </div>
        </div>

        <!-- FOOTER CALLOUT -->
        <div style="background: #0F2240; border-left: 4px solid #00F0FF; color: #FFFFFF; border-radius: 6px; padding: 8px 14px; margin-top: 10px; font-size: 10.5px;">
            🎯 <strong>ओनर गारंटी:</strong> कंप्यूटर जल जाए, विंडोज़ फॉर्मेट हो जाए या स्टाफ पूरा फोल्डर डिलीट कर दे—APNA Computer RMS में डेटा का एक कण भी नहीं खोता!
        </div>
    </div>
    <div class="slide-footer">
        <span>APNA Computer RMS • Confidential Pitch Deck</span>
        <span class="bold">पेज 3 / 5</span>
        <span>हेल्पलाइन: 8504985149</span>
    </div>
</div>

<!-- SLIDE 4: 30-DAY TRIAL & LICENSING LIFECYCLE -->
<div class="slide">
    <div class="slide-header">
        <div>
            <div class="cat">CLIENT ONBOARDING & EXTENSION</div>
            <h2>🔑 30-दिन VIP मुफ़्त ट्रायल व हार्डवेयर-लॉक सिक्योरिटी (Trial & Licensing Engine)</h2>
        </div>
        <div style="color:#00F0FF; font-size: 11px; font-weight: bold;">Zero Cloud Friction</div>
    </div>
    <div class="slide-body">
        <div class="grid-4col" style="margin-bottom: 10px;">
            <div class="col-card" style="background: #FEF3C7; border: 1.5px solid #F59E0B;">
                <h3 style="color: #B45309;">चरण 1: 30-दिन VIP ट्रायल</h3>
                <p>• पहली बार इंस्टॉल होते ही 30 दिन का फुल VIP ट्रायल चालू।<br>• हार्डवेयर-लॉक्ड ACR-XXXX इंस्टॉलेशन आईडी।<br>• 100% फीचर्स अनलॉक—कोई भी प्रतिबंध नहीं।</p>
            </div>
            <div class="col-card" style="background: #FEE2E2; border: 1.5px solid #EF4444;">
                <h3 style="color: #B91C1C;">चरण 2: ग्रेसफुल लॉक</h3>
                <p>• 30 दिन पूरे होने पर केवल नए एडमिशन/फीस एंट्री रुकती है।<br>• डेटाबेस, बैकअप व रसीदें डाउनलोड करने की पूरी छूट।<br>• ओनर का पिछला कोई डेटा ब्लॉक या डिलीट नहीं।</p>
            </div>
            <div class="col-card" style="background: #DCFCE7; border: 1.5px solid #10B981;">
                <h3 style="color: #15803D;">चरण 3: 10-15 दिन WhatsApp एक्सटेंशन</h3>
                <p>• ग्राहक के कॉल करने पर 10-15 दिन का नया एक्सटेंशन कोड।<br>• सुपर एडमिन 'Vendor Master Keygen' से कोड जारी।<br>• बिना इंटरनेट के सिर्फ कोड डालने से सिस्टम अनलॉक।</p>
            </div>
            <div class="col-card" style="background: #E0F2FE; border: 1.5px solid #0284C7;">
                <h3 style="color: #0369A1;">चरण 4: एंटी-क्लॉक टैम्परिंग</h3>
                <p>• यदि कोई ऑपरेटर कंप्यूटर की घड़ी पीछे करने की कोशिश करे।<br>• सिस्टम तुरंत 'Clock Tampering' पहचान कर लॉक कर देता है।<br>• सिर्फ अधिकृत मास्टर की से ही रिसेट संभव।</p>
            </div>
        </div>

        <div style="background: #FFFFFF; border: 1.5px solid #0284C7; border-radius: 6px; padding: 10px 14px; font-size: 10.5px;">
            <strong style="color: #0284C7; font-size: 11.5px;">💡 वेंडर सेल्स स्ट्रैटेजी (High Conversion Sales Strategy):</strong><br>
            ग्राहक जब 1 महीना उपयोग कर लेता है और नए बैच के समय 10-15 दिन का और ट्रायल मांगता है—तो उसे WhatsApp पर तुरंत एक्सटेंशन कोड भेजें। 90%+ कोचिंग संचालक इस भरोसे और सपोर्ट को देखकर लाइफटाइम लाइसेंस तुरंत खरीद लेते हैं!
        </div>
    </div>
    <div class="slide-footer">
        <span>APNA Computer RMS • Confidential Pitch Deck</span>
        <span class="bold">पेज 4 / 5</span>
        <span>हेल्पलाइन: 8504985149</span>
    </div>
</div>

<!-- SLIDE 5: MULTI-PC SYNC & VENDOR GUARANTEE -->
<div class="slide">
    <div class="slide-header">
        <div>
            <div class="cat">MULTI-COUNTER & VENDOR SUPPORT</div>
            <h2>🔀 मल्टी-पीसी सिंक, ज़ीरो-डिपेंडेंसी व वेंडर संपर्क (Multi-PC & Support)</h2>
        </div>
        <div style="color:#00F0FF; font-size: 11px; font-weight: bold;">Lifetime Peace of Mind</div>
    </div>
    <div class="slide-body">
        <div class="grid-2col" style="margin-bottom: 10px;">
            <div class="feat-card">
                <h4>🔀 मल्टी-पीसी सेफ डेटा शेयरिंग व मर्जिंग</h4>
                <p><strong>तरीका A: वाई-फाई / LAN शेयरिंग (Recommended)</strong><br>मालिक के PC के <code>D:\APNA_RMS_DATA</code> फोल्डर को शेयर करें। इंटरनेट के बिना भी रीयल-टाइम डेटा दिखेगा।<br><strong>तरीका B: 1-क्लिक इन-बिल्ट डेटा मर्जिंग</strong><br>अलग-अलग पीसी का डेटा शाम को पेनड्राइव से 1 क्लिक में ओनर के सिस्टम में बिना किसी डुप्लीकेसी के मर्ज।</p>
            </div>
            <div class="feat-card">
                <h4>🚀 ज़ीरो-डिपेंडेंसी व Authenticode साइंड</h4>
                <p><strong>• कोई पाइथन/नोड जरूरी नहीं:</strong> इन-बिल्ट रनटाइम के साथ 1 मिनट में इंस्टॉलेशन।<br><strong>• Microsoft Authenticode SHA-256 साइंड:</strong> एंटीवायरस व डिफेंडर फ्रेंडली।<br><strong>• विंडोज़ 11 Error 4551 से पूर्ण मुक्त:</strong> कोई अन-साइंड या टेम्प बैट स्क्रिप्ट नहीं।</p>
            </div>
        </div>

        <div style="background: #0A192F; border: 1.5px solid #00F0FF; border-radius: 8px; padding: 12px 18px; color: #FFFFFF; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 15px; font-weight: 800; color: #00F0FF;">📞 डायरेक्ट वेंडर संपर्क: APNA Computer (कृष्णा जी)</div>
                <div style="font-size: 11px; color: #E2E8F0; margin-top: 2px;">24x7 हेल्पलाइन: <strong>8504985149</strong>  •  ईमेल: support@apnacomputer.com</div>
            </div>
            <div style="text-align: right;">
                <span style="background: #10B981; color: #FFFFFF; padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: 700;">30-दिन मुफ़्त VIP डेमो चालू करें</span>
            </div>
        </div>
    </div>
    <div class="slide-footer">
        <span>APNA Computer RMS • Confidential Pitch Deck</span>
        <span class="bold">पेज 5 / 5</span>
        <span>हेल्पलाइन: 8504985149</span>
    </div>
</div>

</body>
</html>
"""

def compile_presentation_pdf():
    root_dir = Path(__file__).resolve().parent.parent
    dist_doc_dir = root_dir / "dist" / "Documentation"
    dist_doc_dir.mkdir(parents=True, exist_ok=True)
    
    html_content = generate_presentation_deck_html()
    temp_html = dist_doc_dir / "APNA_Computer_RMS_Presentation_Deck.html"
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
        raise RuntimeError("No browser found!")

    out_pdf = dist_doc_dir / "APNA_Computer_RMS_Presentation_Deck.pdf"
    temp_dir = os.path.join(os.environ.get('TEMP', '.'), 'edge_pdf_profile_deck')
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={temp_dir}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={out_pdf}",
        str(temp_html)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"PDF Compile failed: {res.stderr}")
    print(f"✅ Generated Presentation Deck PDF: {out_pdf} ({os.path.getsize(out_pdf)} bytes)")
    
    # Copy to dist
    out_pdf_dist = root_dir / "dist" / "APNA_Computer_RMS_Presentation_Deck.pdf"
    import shutil
    shutil.copy(out_pdf, out_pdf_dist)
    print(f"✅ Copied to: {out_pdf_dist}")

if __name__ == "__main__":
    compile_presentation_pdf()
