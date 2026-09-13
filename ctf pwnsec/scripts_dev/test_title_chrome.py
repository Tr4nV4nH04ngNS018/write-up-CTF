import subprocess, os, tempfile

html_content = """<!doctype html>
<html>
<head>
<title>data:text/javascript,console.log(1337)</title>
</head>
<body>
<div id="res">waiting</div>
<script>
let r = {};
r['typeof_title'] = typeof title;
r['title_value'] = typeof title !== 'undefined' ? String(title) : 'undefined';
document.getElementById('res').textContent = JSON.stringify(r);
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_title.html')
with open(temp_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
cmd = [
    chrome_path,
    '--headless=new',
    '--dump-dom',
    '--virtual-time-budget=2000',
    temp_html
]

p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
for line in p.stdout.splitlines():
    if 'res' in line:
        print(line)
