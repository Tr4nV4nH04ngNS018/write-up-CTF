import urllib.request
import urllib.parse
import re

def google_search(q):
    url = "https://www.google.com/search?q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Extract text from search results
            snippets = re.findall(r'<div[^>]*class="[^"]*VwiC3b[^"]*"[^>]*>(.*?)</div>', html)
            print(f"Results for: {q}")
            for s in snippets[:5]:
                print("-", re.sub('<[^<]+?>', '', s))
            if not snippets:
                titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
                for t in titles[:5]:
                    print("- title:", re.sub('<[^<]+?>', '', t))
    except Exception as e:
        print("Google search error:", e)

google_search('"slop slop go away" ctf')
google_search('"Fat Mesh" ctf')
google_search('phault ctf.ae')
google_search('"no timing attack" mysqli ctf')
