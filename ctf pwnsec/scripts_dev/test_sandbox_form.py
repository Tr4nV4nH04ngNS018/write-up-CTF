import subprocess, os, tempfile

html_content = """<!doctype html>
<html>
<head>
<meta http-equiv="Content-Security-Policy" content="sandbox allow-scripts allow-same-origin; script-src 'self' 'unsafe-inline'; form-action 'self'">
</head>
<body>
<div id="res">waiting</div>
<form id="f" action="http://127.0.0.1:3000/notes" method="GET">
<input name="search" value="123">
</form>
<script>
let r = {};
try {
    document.getElementById('f').submit();
    r['form_submit'] = 'SUBMITTED';
} catch (e) {
    r['form_submit'] = 'ERROR: ' + e.message;
}
document.getElementById('res').textContent = JSON.stringify(r);
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_sandbox_form.html')
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
