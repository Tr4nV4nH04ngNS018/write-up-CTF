import subprocess, os, json, tempfile

mimes = [
    'text/js',
    'application/js',
    'text/javascript',
    'application/javascript',
    'text/ecmascript',
    'application/ecmascript',
    'text/plain',
    'text/x-javascript',
    'application/x-javascript',
    'text/node',
    'text/mjs',
    'application/mjs',
    'text/json',
    'application/json',
    'text/',
    'application/',
    'custom/js',
]

test_cases_js = []
for m in mimes:
    test_cases_js.append(f"""
    try {{
        await import('data:{m},window["{m}"] = 1');
        results["{m}"] = "OK";
    }} catch (e) {{
        results["{m}"] = e.message;
    }}
    """)

html_content = f"""<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
async function run() {{
    let results = {{}};
    {chr(10).join(test_cases_js)}
    document.getElementById('res').textContent = JSON.stringify(results);
}}
run();
</script>
</body>
</html>
"""

temp_html = os.path.join(tempfile.gettempdir(), 'test_mimes.html')
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
