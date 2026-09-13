import subprocess, os, tempfile

html_content = """<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
window.name = 'data:text/javascript,window.pwned=1';
async function run() {
    let r = {};
    try {
        await import('data:text/javascript,import(name)#/.js');
        await new Promise(res => setTimeout(res, 200));
        r['hash_trick'] = window.pwned ? 'SUCCESS' : 'FAILED_NO_EXEC';
    } catch (e) {
        r['hash_trick'] = 'ERROR: ' + e.message;
    }
    document.getElementById('res').textContent = JSON.stringify(r);
}
run();
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_hash.html')
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
