import urllib.request
import json

queries = [
    "repo:php/php-src mysqli segfault",
    "repo:php/php-src mysqli crash",
    "repo:php/php-src fetch_row",
    "repo:php/php-src mysqli_result",
    "phault ctf",
]

for q in queries:
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== {q} ({data.get('total_count')}) ===")
            for item in data.get("items", [])[:5]:
                print(f"  #{item['number']}: {item['title']}")
    except Exception as e:
        print(f"Error for {q}:", e)
