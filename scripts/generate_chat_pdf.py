import os
import sys
import json
import re
import html
from pathlib import Path
from datetime import datetime

TRANSCRIPT_PATH = Path(r"C:\Users\A\.gemini\antigravity\brain\85610b85-8b24-460b-b9db-ef4e681de9c6\.system_generated\logs\transcript.jsonl")
PROJECT_ROOT = Path(r"E:\AI\Boot Camp 3.0\Operating Software")
FONTS_DIR = PROJECT_ROOT / "fonts"
OUTPUT_PDF = PROJECT_ROOT / "dist" / "APNA_Computer_RMS_Development_Chat_History.pdf"
OUTPUT_PDF_ROOT = PROJECT_ROOT / "APNA_Computer_RMS_Development_Chat_History.pdf"
HTML_PATH = PROJECT_ROOT / "dist" / "chat_transcript.html"

def format_text_to_html(raw_text: str) -> str:
    """Converts markdown text to clean HTML."""
    if not raw_text:
        return ""
    
    # Escape HTML special characters
    text = html.escape(raw_text)
    
    # Code blocks
    def replace_code_block(match):
        code_content = match.group(1)
        return f'<pre class="code-block"><code>{code_content}</code></pre>'
    text = re.sub(r'```(?:\w+)?\n?(.*?)```', replace_code_block, text, flags=re.DOTALL)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
    
    # Headings
    text = re.sub(r'^### (.*?)$', r'<h4 class="md-h3">\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h3 class="md-h2">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h2 class="md-h1">\1</h2>', text, flags=re.MULTILINE)
    
    # Bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Italic *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Blockquotes
    text = re.sub(r'^&gt; (.*?)$', r'<blockquote class="md-quote">\1</blockquote>', text, flags=re.MULTILINE)
    
    # Unordered list items
    text = re.sub(r'^[•\-\*] (.*?)$', r'<li class="md-li">\1</li>', text, flags=re.MULTILINE)
    
    # Numbered list items
    text = re.sub(r'^\d+\. (.*?)$', r'<li class="md-oli">\1</li>', text, flags=re.MULTILINE)
    
    # Line breaks
    text = text.replace('\n\n', '</p><p class="md-p">')
    text = text.replace('\n', '<br/>')
    
    return f'<p class="md-p">{text}</p>'

def extract_conversations():
    """Extracts clean user and assistant messages from transcript.jsonl."""
    messages = []
    
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            
            t = obj.get("type")
            s = obj.get("source")
            content = obj.get("content", "")
            if not content:
                continue
            
            created_at = obj.get("created_at", "")
            formatted_time = ""
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    formatted_time = dt.strftime("%d %b %Y, %I:%M %p")
                except Exception:
                    formatted_time = created_at[:19]
            
            if t == "USER_INPUT" and s == "USER_EXPLICIT":
                clean = content
                matches = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
                if matches:
                    clean = "\n\n".join([m.strip() for m in matches if m.strip()])
                else:
                    clean = re.sub(r'<[^>]+>', '', content).strip()
                
                if clean.startswith("<CONTEXT_SUMMARY>") or "This summary was generated" in clean:
                    sub = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', clean, re.DOTALL)
                    if sub:
                        clean = "\n\n".join([x.strip() for x in sub])
                    else:
                        continue
                
                if clean:
                    messages.append({
                        "role": "user",
                        "sender": "कृष्णा जी (User)",
                        "time": formatted_time,
                        "text": clean
                    })
                    
            elif t == "PLANNER_RESPONSE" and s == "MODEL":
                stripped = content.strip()
                if not stripped or stripped.startswith("call:") or stripped.startswith("{") or stripped.startswith("["):
                    continue
                if stripped.startswith("Created At:") or stripped.startswith("Task:"):
                    continue
                
                messages.append({
                    "role": "assistant",
                    "sender": "Antigravity AI Assistant",
                    "time": formatted_time,
                    "text": stripped
                })
                
    return messages

def build_pdf_html(messages):
    dev_reg = (FONTS_DIR / "NotoSansDevanagari-Regular.ttf").resolve().as_uri()
    dev_bold = (FONTS_DIR / "NotoSansDevanagari-Bold.ttf").resolve().as_uri()
    eng_reg = (FONTS_DIR / "NotoSans-Regular.ttf").resolve().as_uri()
    eng_bold = (FONTS_DIR / "NotoSans-Bold.ttf").resolve().as_uri()

    chat_items_html = []
    for idx, msg in enumerate(messages, 1):
        is_user = msg["role"] == "user"
        formatted_body = format_text_to_html(msg["text"])
        
        card_class = "user-bubble" if is_user else "ai-bubble"
        badge_class = "user-badge" if is_user else "ai-badge"
        avatar_text = "👤" if is_user else "🤖"
        
        chat_items_html.append(f"""
        <div class="message-card {card_class}">
            <div class="msg-header">
                <div class="sender-info">
                    <span class="avatar">{avatar_text}</span>
                    <span class="sender-badge {badge_class}">{html.escape(msg['sender'])}</span>
                    <span class="msg-counter">Message #{idx}</span>
                </div>
                <div class="msg-time">{html.escape(msg['time'])}</div>
            </div>
            <div class="msg-content">
                {formatted_body}
            </div>
        </div>
        """)

    full_chat_html = "\n".join(chat_items_html)

    html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>APNA Computer RMS - Development Chat History</title>
    <style>
        @font-face {{
            font-family: 'Noto Sans Devanagari';
            src: url('{dev_reg}') format('truetype');
            font-weight: 400;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Noto Sans Devanagari';
            src: url('{dev_bold}') format('truetype');
            font-weight: 700;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Noto Sans';
            src: url('{eng_reg}') format('truetype');
            font-weight: 400;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Noto Sans';
            src: url('{eng_bold}') format('truetype');
            font-weight: 700;
            font-style: normal;
        }}

        @page {{
            size: A4 portrait;
            margin: 18mm 15mm 20mm 15mm;
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-family: 'Noto Sans', 'Noto Sans Devanagari', sans-serif;
                font-size: 8pt;
                color: #64748B;
            }}
            @bottom-left {{
                content: "APNA Computer RMS • Complete Development Transcript • Krishna Ji";
                font-family: 'Noto Sans', 'Noto Sans Devanagari', sans-serif;
                font-size: 8pt;
                color: #64748B;
            }}
        }}

        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        body {{
            font-family: 'Noto Sans Devanagari', 'Noto Sans', sans-serif;
            font-size: 9.5pt;
            line-height: 1.5;
            color: #1E293B;
            background: #FFFFFF;
            margin: 0;
            padding: 0;
        }}

        .cover-header {{
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: #FFFFFF;
            padding: 22px 26px;
            border-radius: 12px;
            margin-bottom: 22px;
            border-left: 6px solid #2563EB;
        }}

        .cover-title {{
            font-size: 17pt;
            font-weight: 700;
            margin: 0 0 6px 0;
            letter-spacing: -0.3px;
        }}

        .cover-subtitle {{
            font-size: 10.5pt;
            color: #94A3B8;
            margin: 0 0 16px 0;
        }}

        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            background: rgba(255, 255, 255, 0.08);
            padding: 12px 14px;
            border-radius: 8px;
            font-size: 8.5pt;
        }}

        .meta-item strong {{
            color: #60A5FA;
            display: block;
            margin-bottom: 2px;
            text-transform: uppercase;
            font-size: 7.5pt;
            letter-spacing: 0.5px;
        }}

        .message-card {{
            margin-bottom: 14px;
            border-radius: 8px;
            padding: 12px 16px;
            page-break-inside: avoid;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}

        .user-bubble {{
            background: #F0F7FF;
            border: 1px solid #BFDBFE;
            border-left: 5px solid #2563EB;
        }}

        .ai-bubble {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #0D9488;
        }}

        .msg-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0,0,0,0.06);
            padding-bottom: 6px;
            margin-bottom: 8px;
        }}

        .sender-info {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .avatar {{
            font-size: 11pt;
        }}

        .sender-badge {{
            font-size: 8.5pt;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
        }}

        .user-badge {{
            background: #DBEAFE;
            color: #1E40AF;
        }}

        .ai-badge {{
            background: #CCFBF1;
            color: #115E59;
        }}

        .msg-counter {{
            font-size: 8pt;
            color: #94A3B8;
            font-weight: 600;
        }}

        .msg-time {{
            font-size: 8pt;
            color: #64748B;
        }}

        .msg-content {{
            font-size: 9.5pt;
            color: #1E293B;
            word-wrap: break-word;
        }}

        .md-p {{
            margin: 0 0 8px 0;
        }}

        .md-h1, .md-h2, .md-h3 {{
            color: #0F172A;
            margin: 10px 0 5px 0;
            font-weight: 700;
        }}

        .md-h1 {{ font-size: 12pt; }}
        .md-h2 {{ font-size: 11pt; }}
        .md-h3 {{ font-size: 10pt; }}

        .code-block {{
            background: #0F172A;
            color: #F8FAFC;
            padding: 8px 12px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 8pt;
            overflow-x: auto;
            margin: 6px 0;
            white-space: pre-wrap;
        }}

        .inline-code {{
            background: #E2E8F0;
            color: #0F172A;
            padding: 1px 4px;
            border-radius: 3px;
            font-family: 'Consolas', monospace;
            font-size: 8.5pt;
        }}

        .md-quote {{
            border-left: 3px solid #94A3B8;
            padding-left: 10px;
            margin: 6px 0;
            color: #475569;
            font-style: italic;
        }}

        .md-li, .md-oli {{
            margin-bottom: 3px;
            padding-left: 4px;
        }}

        strong {{
            font-weight: 700;
            color: #0F172A;
        }}
    </style>
</head>
<body>

    <div class="cover-header">
        <div class="cover-title">APNA Computer RMS — Complete Development Transcript</div>
        <div class="cover-subtitle">सॉफ्टवेयर निर्माण की शुरू से अंत तक की पूरी बातचीत व विकास यात्रा (Full Project Audit & Chat Log)</div>
        <div class="meta-grid">
            <div class="meta-item">
                <strong>Project Name</strong>
                APNA Computer RMS (Offline ERP)
            </div>
            <div class="meta-item">
                <strong>Software Developer & Owner</strong>
                कृष्णा जी (APNA Computer)
            </div>
            <div class="meta-item">
                <strong>Document Generation Date</strong>
                {datetime.now().strftime('%d %B %Y, %I:%M %p')}
            </div>
            <div class="meta-item">
                <strong>Helpline / Contact</strong>
                8504985149 | krishnaskb143@gmail.com
            </div>
            <div class="meta-item">
                <strong>Core Technologies Used</strong>
                Python, CustomTkinter, SQLite, Playwright
            </div>
            <div class="meta-item">
                <strong>Total Conversation Exchanges</strong>
                {len(messages)} Key Messages
            </div>
        </div>
    </div>

    {full_chat_html}

</body>
</html>"""
    return html_content

def main():
    print("1. Extracting chat history from transcript.jsonl...", flush=True)
    messages = extract_conversations()
    print(f"   Extracted {len(messages)} conversational messages.", flush=True)

    if not messages:
        print("ERROR: No messages found!", flush=True)
        return

    print("2. Generating styled HTML with file-referenced fonts...", flush=True)
    html_content = build_pdf_html(messages)
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"   Saved HTML: {HTML_PATH} ({HTML_PATH.stat().st_size / (1024):.1f} KB)", flush=True)

    print("3. Launching Playwright to render multi-page PDF...", flush=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-gpu', '--no-sandbox'])
        page = browser.new_page()
        # Direct file URL is lightning fast!
        page.goto(HTML_PATH.resolve().as_uri(), wait_until="load", timeout=60000)
        
        OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        print("4. Generating PDF file (this takes a few seconds)...", flush=True)
        page.pdf(
            path=str(OUTPUT_PDF),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "18mm", "left": "15mm", "right": "15mm"},
            display_header_footer=True,
            header_template='<div></div>',
            footer_template='''
                <div style="font-family: sans-serif; font-size: 8px; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; padding: 0 15mm;">
                    <span>APNA Computer RMS • Development Transcript • Software Developed by APNA Computer (कृष्णा जी)</span>
                    <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
                </div>
            '''
        )
        browser.close()

    import shutil
    shutil.copy2(OUTPUT_PDF, OUTPUT_PDF_ROOT)

    print(f"\nSUCCESS! Generated Complete Chat PDF:")
    print(f"  1. {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  2. {OUTPUT_PDF_ROOT} ({OUTPUT_PDF_ROOT.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
