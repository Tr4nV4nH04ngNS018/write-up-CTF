import os
from PIL import Image, ImageDraw, ImageFont

def render_browser_page(url_bar, code_snippet, error_text, out_path):
    width = 1100
    font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    font_bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
    font_ui = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    font_url = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)

    # Calculate height
    lines = code_snippet.strip().splitlines()
    err_lines = error_text.strip().splitlines()
    line_h = 22

    content_h = (len(lines) + len(err_lines) + 4) * line_h + 40
    header_h = 75
    height = header_h + content_h

    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Browser Top Bar
    draw.rectangle([(0, 0), (width, header_h)], fill=(241, 243, 244, 255))
    # Tabs
    draw.rounded_rectangle([(80, 10), (280, 42)], radius=6, fill=(255, 255, 255, 255))
    draw.text((100, 16), "PHAULT - PHP SQLi", fill=(60, 64, 67, 255), font=font_ui)

    # Window controls (dots)
    draw.ellipse([(16, 16), (28, 28)], fill=(237, 106, 94, 255))
    draw.ellipse([(36, 16), (48, 28)], fill=(245, 190, 78, 255))
    draw.ellipse([(56, 16), (68, 28)], fill=(98, 197, 84, 255))

    # URL Bar
    draw.rounded_rectangle([(16, 42), (width - 16, 70)], radius=14, fill=(232, 234, 237, 255))
    draw.text((36, 47), url_bar, fill=(32, 33, 36, 255), font=font_url)

    # Page Content Area (PHP highlight_file style)
    y = header_h + 20
    draw.rectangle([(16, y), (width - 16, y + len(lines) * line_h + 10)], fill=(250, 250, 250, 255), outline=(220, 220, 220, 255))
    y += 10
    for l in lines:
        draw.text((30, y), l, fill=(0, 0, 187, 255) if "$" in l else (0, 119, 0, 255), font=font_code)
        y += line_h

    y += 25
    # Fatal Error Banner (PHP error style)
    draw.rectangle([(16, y - 5), (width - 16, y + len(err_lines) * line_h + 15)], fill=(255, 235, 235, 255), outline=(255, 180, 180, 255))
    for i, el in enumerate(err_lines):
        f = font_bold if i == 0 else font_code
        color = (180, 20, 20, 255) if i == 0 else (60, 60, 60, 255)
        draw.text((30, y + 5), el, fill=color, font=f)
        y += line_h

    img.save(out_path)
    print("Saved:", out_path)

code = """<?php
$START = microtime(true);
ob_start();
register_shutdown_function(function () use ($START) {
    $remaining = 2.0 - (microtime(true) - $START);
    if ($remaining > 0) {
        usleep((int)($remaining * 1000000));
    }
}); // no timing attack!!
mysqli_report(MYSQLI_REPORT_OFF);
$db = new mysqli("127.0.0.1", "user", "user", "chall");
echo highlight_file(__FILE__, true);
if (isset($_GET["id"])) {
    $sql = "SELECT username FROM users WHERE id = " . $_GET["id"];
    $res = $db->query($sql);
    if (!$res) {
        die("ill try to tell him, dw");
    }
    $row = $res->fetch_row();
    echo 'ill try to tell him, dw';
}
?>"""

err = """Fatal error: Uncaught Error: Call to a member function fetch_row() on bool in /var/www/html/index.php:19
Stack trace:
#0 {main}
  thrown in /var/www/html/index.php on line 19"""

render_browser_page(
    "https://[INSTANCE].chal.ctf.ae/?id=1 UNION SELECT 2 WHERE (1=2) INTO @a",
    code,
    err,
    "c:/Users/ACER/Downloads/ctf/ctf pwnsec/images/phault_browser_error.png"
)
render_browser_page(
    "https://[INSTANCE].chal.ctf.ae/?id=1 UNION SELECT 2 WHERE (1=2) INTO @a",
    code,
    err,
    "C:/Users/ACER/.gemini/antigravity-ide/brain/cf6eca68-4479-4674-b4a1-03b3a2748534/phault_browser_error.png"
)
