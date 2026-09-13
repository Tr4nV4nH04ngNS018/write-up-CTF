import urllib.request
import json

for q in ["phault", "pwnsec"]:
    url = f"https://api.github.com/search/repositories?q={q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"=== Repos for {q} ({data.get('total_count')}) ===")
            for item in data.get("items", [])[:5]:
                print(" ", item["full_name"], ":", item["description"])
    except Exception as e:
        print(f"Error for {q}:", e)
