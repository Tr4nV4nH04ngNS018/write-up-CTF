import urllib.request, re

req = urllib.request.Request('https://w3c.github.io/webappsec-fetch-metadata/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode('utf-8', errors='ignore')
        idx = text.find('data-algorithm="set `Sec-Fetch-Mode`"')
        if idx != -1:
            print(text[idx:idx+1500].encode('ascii', errors='replace').decode())
except Exception as e:
    print("Error:", e)
