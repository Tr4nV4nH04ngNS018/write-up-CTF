import urllib.request
import json
import urllib.parse

queries = [
    "CANAS ctf",
    "Fat Mesh",
    "slop slop go away",
    "Be the person that you fear",
    "pwnsec phault",
]

for q in queries:
    url = f"https://api.github.com/search/code?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== {q} ({data.get('total_count')}) ===")
            for item in data.get("items", [])[:3]:
                print(" ", item["html_url"])
    except Exception as e:
        print(f"Error for {q}:", e)
