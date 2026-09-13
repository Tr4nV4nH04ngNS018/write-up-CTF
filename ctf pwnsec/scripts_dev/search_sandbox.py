import urllib.request, urllib.parse, re

q = 'allow-scripts allow-same-origin escape sandbox'
url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req) as r:
        html = r.read().decode('utf-8', errors='ignore')
        for m in re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html)[:5]:
            print('-', re.sub(r'<[^<]+?>', '', m))
except Exception as e:
    print('Err:', e)
