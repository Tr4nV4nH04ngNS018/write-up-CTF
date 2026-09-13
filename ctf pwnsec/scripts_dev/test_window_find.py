import subprocess, os, tempfile

html_content = """<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
async function run() {
    // 1. Open target window with name "flag_win"
    const target = window.open('data:text/html,<h1 id="secret">FLAG1234</h1>', 'flag_win');
    
    // 2. Simulate note finding that window by name
    await new Promise(r => setTimeout(r, 200));
    
    let r = {};
    try {
        const found = window.open('', 'flag_win');
        r['found'] = found ? true : false;
        r['content'] = found.document.getElementById('secret').textContent;
    } catch (e) {
        r['error'] = e.message;
    }
    
    document.getElementById('res').textContent = JSON.stringify(r);
}
run();
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_window_find.html')
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
