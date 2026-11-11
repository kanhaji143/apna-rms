import subprocess
import os

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {
    font-family: 'Nirmala UI', 'Aparajita', 'Segoe UI', sans-serif;
    font-size: 16px;
    padding: 40px;
}
h1 { color: #00183A; font-size: 26px; }
.desc { font-size: 14px; line-height: 1.6; color: #333; }
</style>
</head>
<body>
<h1>सम्पूर्ण ऑपरेटिंग व स्टाफ ट्रेनिंग गाइड</h1>
<p class="desc">
यह गाइड कोचिंग संस्थानों, कंप्यूटर प्रशिक्षण केंद्रों एवं स्कूलों के लिए तैयार किए गए APNA Computer RMS सॉफ्टवेयर के सफल संचालन, स्टाफ प्रशिक्षण, फीस कलेक्शन, बकाया किस्त नियंत्रण, आई-कार्ड प्रिंटिंग एवं सुरक्षा नियमों का सम्पूर्ण आधिकारिक मार्गदर्शक है।
</p>
</body>
</html>"""

with open("test_hindi.html", "w", encoding="utf-8") as f:
    f.write(html_content)

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=test_hindi.pdf", os.path.abspath("test_hindi.html")]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
print("PDF exists:", os.path.exists("test_hindi.pdf"), "Size:", os.path.getsize("test_hindi.pdf") if os.path.exists("test_hindi.pdf") else 0)
