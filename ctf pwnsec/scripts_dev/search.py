import urllib.request
import urllib.parse
import re

def search(q):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        matches = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html)
        print(f"=== Results for {q} ===")
        for m in matches[:5]:
            print("-", re.sub('<[^<]+?>', '', m))
    except Exception as e:
        print("Error:", e)

search('mysqli fetch_row segfault')
search('php 8.2 segfault mysqli')
search('"phault" ctf')
