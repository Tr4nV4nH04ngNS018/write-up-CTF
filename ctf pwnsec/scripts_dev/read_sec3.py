import urllib.request, re

req = urllib.request.Request('https://w3c.github.io/webappsec-fetch-metadata/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode('utf-8', errors='ignore')
        # find section 3 "Processing model"
        idx = text.find('id="processing-model"')
        if idx != -1:
            print(text[idx:idx+3000].encode('ascii', errors='replace').decode())
except Exception as e:
    print("Error:", e)
