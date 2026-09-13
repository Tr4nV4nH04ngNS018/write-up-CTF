import urllib.request, re

req = urllib.request.Request('https://w3c.github.io/webappsec-fetch-metadata/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode('utf-8', errors='ignore')
        print("Spec length:", len(text))
        # Search for algorithms that set Sec-Fetch-Mode
        for m in re.finditer(r'Sec-Fetch-Mode', text):
            start = max(0, m.start() - 200)
            end = min(len(text), m.end() + 200)
            print("--- Snippet ---")
            print(text[start:end])
except Exception as e:
    print("Error:", e)
