import urllib.request
import json
import urllib.parse

q = "repo:php/php-src mysqli segfault"
url = f"https://api.github.com/search/commits?q={urllib.parse.quote(q)}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.cloak-preview"})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Total commits:", data.get("total_count"))
        for item in data.get("items", [])[:10]:
            print("-", item["commit"]["message"].splitlines()[0])
except Exception as e:
    print("Error:", e)
