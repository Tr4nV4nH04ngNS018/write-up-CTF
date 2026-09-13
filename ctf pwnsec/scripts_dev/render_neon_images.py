import os
from PIL import Image, ImageDraw, ImageFont

img_dir = "c:/Users/ACER/Downloads/ctf/ctf pwnsec/images"
os.makedirs(img_dir, exist_ok=True)

# 1. RENDER TERMINAL
def render_terminal(title, lines, out_path):
    font_size = 17
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", font_size)
    bold_font = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", font_size)
    header_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)

    line_height = 25
    padding_x = 24
    padding_y = 20
    header_height = 42

    width = 1020
    height = header_height + padding_y * 2 + len(lines) * line_height

    img = Image.new("RGBA", (width, height), (15, 17, 26, 255))
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (width, header_height)], fill=(24, 27, 40, 255))
    # Window controls (macOS style dots)
    draw.ellipse([(16, 15), (28, 27)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 15), (48, 27)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 15), (68, 27)], fill=(39, 201, 63, 255))

    # Title
    draw.text((width // 2 - len(title) * 4, 13), title, fill=(160, 170, 190, 255), font=header_font)

    # Content
    y = header_height + padding_y
    for text, color, is_bold in lines:
        f = bold_font if is_bold else font
        draw.text((padding_x, y), text, fill=color, font=f)
        y += line_height

    img.save(out_path)
    print(f"Saved: {out_path}")

neon_lines = [
    ("$ python solve_neon.py 0c6523a28168f7fd.chal.ctf.ae", (255, 255, 255, 255), True),
    ("[*] Step 1: Deploying Stage 1 (evil.html) & Stage 2 (s.js) via Pickle RCE...", (100, 200, 255, 255), False),
    ("    [-] Overriding Flask configuration: webapp.app.static_folder = '/tmp'", (180, 190, 205, 255), False),
    ("    [-] Writing payloads to /tmp/evil.html and /tmp/s.js across all workers", (180, 190, 205, 255), False),
    ("    [+] Verified evil.html: https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html", (80, 240, 120, 255), False),
    ("    [+] Verified s.js:      https://0c6523a28168f7fd.chal.ctf.ae/static/s.js", (80, 240, 120, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[*] Step 2: Submitting evil URL to Neon Skies Bot (/report)...", (100, 200, 255, 255), False),
    ("    [-] POST /report -> url=https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html", (180, 190, 205, 255), False),
    ("    [+] Response: Filed. The archivist looked at ... and moved on.", (80, 240, 120, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[*] Step 3: Bot Execution & Cookie Tossing Chain in Playwright...", (100, 200, 255, 255), False),
    ("    [-] Bot visits evil.html -> sets document.cookie='FLAG=x</output><script>...; domain=chal.ctf.ae'", (255, 220, 100, 255), False),
    ("    [-] Bot navigates top-level to https://65b68ef3c79fb356.chal.ctf.ae/admin", (180, 190, 205, 255), False),
    ("    [-] Crystal Cookie Parser (Last-Wins) echoes unescaped XSS payload into DOM", (255, 220, 100, 255), False),
    ("    [-] s.js deletes injected domain cookie -> fetch('/admin') sends ONLY real Strict FLAG", (180, 190, 205, 255), False),
    ("    [-] s.js scrapes <output id='flag'> and exfiltrates to webhook.site", (180, 190, 205, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[*] Step 4: Waiting for beacon on Webhook listener...", (100, 200, 255, 255), False),
    ("    [+] Beacon: s.js_loaded@https://65b68ef3c79fb356.chal.ctf.ae/admin", (80, 240, 120, 255), False),
    ("    =======================================================", (39, 201, 63, 255), True),
    ("    [🎉] FLAG EXTRACTED: pwnsec{9abdf66a5f2afecb}", (39, 201, 63, 255), True),
    ("    =======================================================", (39, 201, 63, 255), True),
]

render_terminal("bash - CTF Terminal - Neon Skies Exploit Chain", neon_lines, f"{img_dir}/neon_skies_terminal.png")

# 2. RENDER ARCHITECTURE DIAGRAM
def render_architecture_diagram(out_path):
    width = 1100
    height = 680
    img = Image.new("RGBA", (width, height), (13, 15, 24, 255))
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    f_box_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
    f_box_text = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
    f_arrow = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)

    # Title
    draw.text((36, 25), "Neon Skies — Chuỗi Khai Thác Cookie Tossing & Cross-Challenge RCE", fill=(255, 255, 255, 255), font=f_title)
    draw.text((36, 58), "Mô hình tương tác giữa Attacker, Pickle Instance, Playwright Bot, Crystal Backend & Webhook Exfil", fill=(150, 160, 185, 255), font=f_sub)

    # Box 1: Attacker
    draw.rounded_rectangle([(40, 110), (280, 280)], radius=10, fill=(22, 26, 38, 255), outline=(76, 86, 120, 255), width=2)
    draw.text((56, 125), "1. Attacker (solve_neon.py)", fill=(100, 200, 255, 255), font=f_box_title)
    draw.text((56, 160), "- RCE payload sang pickle\n- Gửi evil.html sang /report\n- Chờ webhook nhận cờ", fill=(200, 210, 230, 255), font=f_box_text)

    # Box 2: Pickle Challenge (Host for evil.html & s.js)
    draw.rounded_rectangle([(410, 110), (700, 280)], radius=10, fill=(22, 26, 38, 255), outline=(245, 158, 11, 255), width=2)
    draw.text((426, 125), "2. Pickle Subdomain (*.chal.ctf.ae)", fill=(255, 200, 80, 255), font=f_box_title)
    draw.text((426, 160), "0c6523a28168f7fd.chal.ctf.ae\n- static_folder = '/tmp'\n- Host evil.html (toss cookie)\n- Host s.js (stage-2 XSS)", fill=(200, 210, 230, 255), font=f_box_text)

    # Box 3: Playwright Bot
    draw.rounded_rectangle([(820, 110), (1060, 280)], radius=10, fill=(22, 26, 38, 255), outline=(236, 72, 153, 255), width=2)
    draw.text((836, 125), "3. Archivist Bot (Playwright)", fill=(244, 114, 182, 255), font=f_box_title)
    draw.text((836, 160), "- Giữ FLAG (SameSite=Strict)\n- Đăng nhập session 'sid'\n- Mở link nộp từ /report", fill=(200, 210, 230, 255), font=f_box_text)

    # Box 4: Neon Skies App (/admin unescaped sink)
    draw.rounded_rectangle([(410, 420), (700, 610)], radius=10, fill=(22, 26, 38, 255), outline=(168, 85, 247, 255), width=2)
    draw.text((426, 435), "4. Neon Skies App (/admin)", fill=(192, 132, 252, 255), font=f_box_title)
    draw.text((426, 470), "65b68ef3c79fb356.chal.ctf.ae\n- Nhận Cookie (Last-Wins)\n- Echo <output id=flag><%= @flag %>\n- XSS kích hoạt s.js trên Origin!", fill=(200, 210, 230, 255), font=f_box_text)

    # Box 5: Webhook Exfil
    draw.rounded_rectangle([(40, 420), (280, 610)], radius=10, fill=(22, 26, 38, 255), outline=(34, 197, 94, 255), width=2)
    draw.text((56, 435), "5. Webhook Listener (Exfil)", fill=(74, 222, 128, 255), font=f_box_title)
    draw.text((56, 470), "webhook.site/.../requests\n- Nhận Beacon s.js_loaded\n- Nhận Flag thật từ s.js\n- FLAG: pwnsec{9abdf6...}", fill=(200, 210, 230, 255), font=f_box_text)

    # Draw connection lines and labels
    # 1 -> 2
    draw.line([(280, 195), (410, 195)], fill=(100, 200, 255, 255), width=2)
    draw.text((305, 175), "RCE Write", fill=(100, 200, 255, 255), font=f_arrow)

    # 3 -> 2
    draw.line([(820, 195), (700, 195)], fill=(236, 72, 153, 255), width=2)
    draw.text((725, 175), "Bot visits", fill=(244, 114, 182, 255), font=f_arrow)

    # 2 -> 4 (Cookie toss & Redirect)
    draw.line([(650, 280), (650, 420)], fill=(245, 158, 11, 255), width=2)
    draw.text((658, 335), "Toss Cookie FLAG\n& Redirect /admin", fill=(255, 200, 80, 255), font=f_arrow)

    # 4 -> 5 (Exfiltration)
    draw.line([(410, 515), (280, 515)], fill=(34, 197, 94, 255), width=2)
    draw.text((300, 495), "Exfil Flag", fill=(74, 222, 128, 255), font=f_arrow)

    img.save(out_path)
    print(f"Saved: {out_path}")

render_architecture_diagram(f"{img_dir}/neon_skies_architecture.png")

# 3. RENDER BROWSER UI MOCKUP (Admin Seed Vault Unsealed)
def render_neon_browser(out_path):
    width = 1100
    height = 680
    img = Image.new("RGBA", (width, height), (5, 3, 12, 255))
    draw = ImageDraw.Draw(img)

    f_ui = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    f_url = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
    f_h1 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
    f_p = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    f_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)
    f_flag = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)

    # Browser Top Bar
    draw.rectangle([(0, 0), (width, 75)], fill=(22, 16, 42, 255))
    # Tab
    draw.rounded_rectangle([(80, 10), (320, 42)], radius=6, fill=(35, 25, 65, 255))
    draw.text((100, 16), "The Seed Vault · Neon Skies", fill=(220, 210, 240, 255), font=f_ui)
    # Dots
    draw.ellipse([(16, 16), (28, 28)], fill=(237, 106, 94, 255))
    draw.ellipse([(36, 16), (48, 28)], fill=(245, 190, 78, 255))
    draw.ellipse([(56, 16), (68, 28)], fill=(98, 197, 84, 255))
    # URL Bar
    draw.rounded_rectangle([(16, 42), (width - 16, 70)], radius=14, fill=(12, 8, 25, 255))
    draw.text((36, 47), "https://65b68ef3c79fb356.chal.ctf.ae/admin", fill=(190, 180, 220, 255), font=f_url)

    # Page Content Area
    y = 120
    draw.text((width // 2 - 120, y), "CLEARANCE GRANTED · DRAWER 09", fill=(168, 85, 247, 255), font=f_mono)
    y += 35
    draw.text((width // 2 - 160, y), "The Long Lost Human Seed", fill=(255, 255, 255, 255), font=f_h1)
    y += 45
    sub_text = "Sealed the night the last broadcast stopped. Catalogued, never opened, never decayed."
    draw.text((width // 2 - len(sub_text) * 3 - 30, y), sub_text, fill=(160, 150, 190, 255), font=f_p)

    # Panel
    y += 50
    panel_rect = [(width // 2 - 380, y), (width // 2 + 380, y + 330)]
    draw.rounded_rectangle(panel_rect, radius=14, fill=(18, 12, 38, 230), outline=(168, 85, 247, 120), width=1)

    py = y + 30
    draw.text((width // 2 - 340, py), "CUSTODIAN: archivist    |    DRAWER: 09 / terra    |    STATE: unsealed", fill=(192, 132, 252, 255), font=f_mono)

    # Flag Box
    py += 55
    flag_box = [(width // 2 - 340, py), (width // 2 + 340, py + 120)]
    draw.rounded_rectangle(flag_box, radius=10, fill=(8, 4, 18, 255), outline=(124, 58, 237, 200), width=2)

    draw.text((width // 2 - 315, py + 18), "SPECIMEN DESIGNATION (FLAG)", fill=(168, 85, 247, 255), font=f_mono)
    draw.text((width // 2 - 315, py + 55), "pwnsec{9abdf66a5f2afecb}", fill=(74, 222, 128, 255), font=f_flag)

    py += 150
    draw.text((width // 2 - 340, py), "Session: 7b3e9a4f210d... · This drawer closes when the session does.", fill=(120, 110, 150, 255), font=f_mono)
    draw.text((width // 2 - 340, py + 30), "Exploit Stage-2 (s.js) successfully scraped Designation and exfiltrated to Webhook.", fill=(236, 72, 153, 255), font=f_mono)

    img.save(out_path)
    print(f"Saved: {out_path}")

render_neon_browser(f"{img_dir}/neon_skies_browser.png")

# 4. RENDER WEBHOOK EXFIL LOGS
def render_webhook_log(out_path):
    width = 1020
    height = 520
    img = Image.new("RGBA", (width, height), (15, 17, 26, 255))
    draw = ImageDraw.Draw(img)

    f_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    f_monob = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
    f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)

    # Header
    draw.rectangle([(0, 0), (width, 45)], fill=(25, 30, 45, 255))
    draw.text((20, 12), "Webhook.site — Incoming Beacon Exfiltration Requests (Live Capture)", fill=(240, 245, 255, 255), font=f_title)

    lines = [
        ("[#1] GET /08470564-f80c-4271-b2f2-8acc4f44a5a9?stage=s.js_loaded@https://65b68ef3c79fb356.chal.ctf.ae/admin", (100, 200, 255, 255), False),
        ("     IP: 44.221.247.145 (AWS EC2 / HeadlessChrome 152.0.0.0)", (150, 160, 180, 255), False),
        ("     Origin: https://65b68ef3c79fb356.chal.ctf.ae | Stage: Stage-2 Payload Executed on App Origin", (180, 190, 210, 255), False),
        ("", (255, 255, 255, 255), False),
        ("[#2] GET /08470564-f80c-4271-b2f2-8acc4f44a5a9?flag=pwnsec%7B9abdf66a5f2afecb%7D", (255, 220, 100, 255), True),
        ("     IP: 44.221.247.145 (AWS EC2 / HeadlessChrome 152.0.0.0)", (150, 160, 180, 255), False),
        ("     Sec-Fetch-Site: cross-site | Method: new Image().src beacon", (180, 190, 210, 255), False),
        ("     >>> PARSED QUERY PARAMETER: flag = pwnsec{9abdf66a5f2afecb}", (39, 201, 63, 255), True),
        ("", (255, 255, 255, 255), False),
        ("[#3] POST /08470564-f80c-4271-b2f2-8acc4f44a5a9?flag=pwnsec%7B9abdf66a5f2afecb%7D", (255, 220, 100, 255), True),
        ("     Sec-Fetch-Site: cross-site | Method: navigator.sendBeacon()", (180, 190, 210, 255), False),
        ("     >>> CONFIRMED IDENTICAL FLAG FROM SECOND EXFIL CHANNEL", (80, 240, 120, 255), True),
    ]

    y = 65
    for text, color, is_bold in lines:
        f = f_monob if is_bold else f_mono
        draw.text((24, y), text, fill=color, font=f)
        y += 28

    img.save(out_path)
    print(f"Saved: {out_path}")

render_webhook_log(f"{img_dir}/neon_skies_webhook.png")
print("ALL IMAGES RENDERED SUCCESSFULLY!")
