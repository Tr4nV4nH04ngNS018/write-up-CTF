import subprocess, os, json, tempfile

html_content = """<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
async function run() {
    let results = [];
    try {
        await import('data:,window.test1 = 1');
        results.push('data: without mime SUCCEEDED');
    } catch (e) {
        results.push('data: without mime FAILED: ' + e.message);
    }
    try {
        await import('data:text/javascript,window.test2 = 2');
        results.push('data:text/javascript SUCCEEDED');
    } catch (e) {
        results.push('data:text/javascript FAILED: ' + e.message);
    }
    document.getElementById('res').textContent = JSON.stringify(results);
}
run();
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_data_import.html')
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
    if 'data:' in line or 'SUCCEEDED' in line or 'FAILED' in line or 'res' in line:
        print(line)
