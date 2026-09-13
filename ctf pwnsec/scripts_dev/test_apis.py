import http.server, socketserver, threading, subprocess, os

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        mode = self.headers.get('Sec-Fetch-Mode', '<MISSING>')
        dest = self.headers.get('Sec-Fetch-Dest', '<MISSING>')
        print(f"[API TEST] Path: {self.path} | Sec-Fetch-Mode: {mode} | Sec-Fetch-Dest: {dest}")
        self.send_response(200)
        self.send_header('Content-Type', 'text/javascript')
        self.end_headers()
        self.wfile.write(b'// ok')

server = socketserver.TCPServer(('127.0.0.1', 9995), Handler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

html_content = """<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
async function test() {
    try { new Worker('http://127.0.0.1:9995/worker'); } catch(e){}
    try { new SharedWorker('http://127.0.0.1:9995/shared_worker'); } catch(e){}
    try { new EventSource('http://127.0.0.1:9995/eventsource'); } catch(e){}
    try { navigator.sendBeacon('http://127.0.0.1:9995/beacon'); } catch(e){}
    try { fetch('http://127.0.0.1:9995/fetch'); } catch(e){}
    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', 'http://127.0.0.1:9995/xhr');
        xhr.send();
    } catch(e){}
}
test();
</script>
</body>
</html>
"""

temp_html = os.path.join(os.environ.get('TEMP', ''), 'test_apis.html')
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

subprocess.run(cmd, capture_output=True, text=True, timeout=10)
server.shutdown()
