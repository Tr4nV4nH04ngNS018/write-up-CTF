from playwright.sync_api import sync_playwright
import http.server, threading

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        html = '''<!DOCTYPE html><html><head>
        <style>#test { color: red; }</style>
        </head><body><div id='test'>Hello</div></body></html>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=UTF-8')
        self.send_header('Content-Security-Policy', "script-src 'none'; default-src 'self'; base-uri 'none'; frame-src 'none'; object-src 'none'")
        self.end_headers()
        self.wfile.write(html.encode())

server = http.server.HTTPServer(('127.0.0.1', 8889), Handler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.on('console', lambda msg: print('Console:', msg.text))
    page.goto('http://127.0.0.1:8889/')
    color = page.evaluate("getComputedStyle(document.getElementById('test')).color")
    print('Color with CSP:', color)
    b.close()
