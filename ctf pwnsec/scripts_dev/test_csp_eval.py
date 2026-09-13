import subprocess, os, tempfile

html_content = """<!doctype html>
<html>
<head>
<meta http-equiv="Content-Security-Policy" content="script-src 'self' 'nonce-1234' data:">
</head>
<body>
<div id="res">waiting</div>
<script nonce="1234">
async function run() {
    let results = {};
    try {
        eval('1+1');
        results['inline_eval'] = 'ALLOWED';
    } catch (e) {
        results['inline_eval'] = e.message;
    }

    try {
        await import('data:text/javascript,try{eval("window.data_eval=1");}catch(e){window.data_eval_err=e.message;}//');
        results['data_eval'] = window.data_eval ? 'ALLOWED' : window.data_eval_err;
    } catch (e) {
        results['data_eval_import'] = e.message;
    }

    document.getElementById('res').textContent = JSON.stringify(results);
}
run();
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_data_eval.html')
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
