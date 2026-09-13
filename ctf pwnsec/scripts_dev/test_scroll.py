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
            # Attacker page
            html = '''<!DOCTYPE html><html><body>
            <h1>Attacker</h1>
            </body></html>'''
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(html.encode())

server = http.server.HTTPServer(('127.0.0.1', 8890), Handler)
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
    page.goto('http://127.0.0.1:8890/target#:~:text=SECRET_TOKEN_XYZ')
    page.wait_for_timeout(1000)
    scroll_y = page.evaluate("window.scrollY")
    print('Direct navigation scrollY:', scroll_y)

    # Now test if opened via window.open without user gesture
    attacker_page = b.new_page()
    attacker_page.goto('http://127.0.0.1:8890/')
    popup = attacker_page.evaluate("""() => {
        const w = window.open('http://127.0.0.1:8890/target#:~:text=SECRET_TOKEN_XYZ');
        return true;
    }""")
    attacker_page.wait_for_timeout(1000)
    
    # Check all pages in context
    for p_item in b.contexts[0].pages:
        if 'target' in p_item.url:
            print('Popup navigation scrollY:', p_item.evaluate("window.scrollY"))
    b.close()
