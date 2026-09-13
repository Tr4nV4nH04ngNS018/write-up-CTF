import urllib.request, urllib.parse, re

# W3C Fetch Metadata spec:
# Let's search W3C webappsec-fetch-metadata spec directly
urls = [
    'https://w3c.github.io/webappsec-fetch-metadata/',
    'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-Fetch-Mode',
    'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-Fetch-Dest'
]

for u in urls:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            # Look for cases where Sec-Fetch-Mode is omitted or undefined
            for m in re.finditer(r'(?:omit|not sent|undefined|absent|missing)[^.\n]*sec-fetch-mode', text, re.IGNORECASE):
                print(f"[{u}]", m.group(0))
            for m in re.finditer(r'sec-fetch-mode[^.\n]*(?:omit|not sent|undefined|absent|missing)', text, re.IGNORECASE):
                print(f"[{u}]", m.group(0))
    except Exception as e:
        print(f"Error {u}: {e}")
