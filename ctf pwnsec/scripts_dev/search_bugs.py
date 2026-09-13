import urllib.request
import urllib.parse
import re

url = "https://bugs.php.net/search.php?cmd=display&status=All&search_in_all=1&search_for=" + urllib.parse.quote("mysqli fetch_row segfault")
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        bugs = re.findall(r'<a href="bug\.php\?id=(\d+)">.*?</a>.*?<td>(.*?)</td>', html, re.DOTALL)
        print("Found bugs:", len(bugs))
        for b in bugs[:10]:
            print(b[0], re.sub('<[^<]+?>', '', b[1]).strip())
except Exception as e:
    print("Error:", e)
