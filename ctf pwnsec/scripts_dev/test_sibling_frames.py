import subprocess, os, tempfile

# Test if sibling iframes can access each other via parent[0] or window.open('', name)
html_content = """<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<iframe name="target" src="data:text/html,<div id=secret>FLAG1337</div>"></iframe>
<iframe name="attacker" src="data:text/html,<script>
let r = {};
try {
    const s = window.parent.frames['target'];
    r['via_parent_name'] = s.document.getElementById('secret').textContent;
} catch (e) {
    r['via_parent_name'] = e.message;
}
try {
    const s2 = window.open('', 'target');
    r['via_open'] = s2.document.getElementById('secret').textContent;
} catch (e) {
    r['via_open'] = e.message;
}
window.parent.postMessage(JSON.stringify(r), '*');
</script>"></iframe>
<script>
window.onmessage = e => {
    document.getElementById('res').textContent = e.data;
};
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_sibling_frames.html')
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
