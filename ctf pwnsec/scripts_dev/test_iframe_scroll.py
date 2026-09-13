from playwright.sync_api import sync_playwright
import http.server, threading

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/target'):
            html = '''<!DOCTYPE html><html><body style="height: 3000px;">
            <div style="height: 1500px;">Spacing</div>
            <div id="target">SECRET_TOKEN_XYZ</div>
            <div style="height: 1500px;">Spacing</div>
            </body></html>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            html = '''<!DOCTYPE html><html><body>
            <iframe id="ifr" src="/target#:~:text=SECRET_TOKEN_XYZ" style="width:300px; height:300px;"></iframe>
            </body></html>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(html.encode())

server = http.server.HTTPServer(('127.0.0.1', 8891), Handler)
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
    page.goto('http://127.0.0.1:8891/')
    page.wait_for_timeout(1000)
    frame = page.frames[1]
    scroll_y = frame.evaluate("window.scrollY")
    print('Iframe scrollY:', scroll_y)
    b.close()
