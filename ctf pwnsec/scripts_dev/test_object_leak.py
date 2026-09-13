import http.server, socketserver, threading, subprocess, time, os

# Create a mock server that returns 200 for /test?s=1 and 404 for /test?s=0
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/test?s=1':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Found</h1>')
        elif self.path == '/test?s=0':
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Not Found</h1>')
        elif self.path == '/harness':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""<!doctype html>
<html>
<body>
<div id="res">waiting</div>
<script>
let results = {};
function testObject(url, name) {
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
    await testObject('/test?s=1', 'status_200');
    await testObject('/test?s=0', 'status_404');
    document.getElementById('res').textContent = JSON.stringify(results);
}
run();
</script>
</body>
</html>
""")
        else:
            self.send_error(404)

server = socketserver.TCPServer(('127.0.0.1', 9999), Handler)
t = threading.Thread(target=server.serve_forever)
t.daemon = True
t.start()

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
cmd = [
    chrome_path,
    '--headless=new',
    '--dump-dom',
    '--virtual-time-budget=3000',
    'http://127.0.0.1:9999/harness'
]

p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
for line in p.stdout.splitlines():
    if 'res' in line:
        print(line)

server.shutdown()
