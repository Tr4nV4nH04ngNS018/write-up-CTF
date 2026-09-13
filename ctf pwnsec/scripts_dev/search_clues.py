import urllib.request, urllib.parse, re

queries = [
    '7193363887985659142',
    'ketnipz "mouse in the house"',
    'ketnipz mouse',
    'pwnsec "mouse-in-the-house"',
    'pwnsec "Macabely"'
]

for q in queries:
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as r:
            html = r.read().decode('utf-8', errors='ignore')
            snippets = re.findall(r'<a class="result__snippet[^"]*"[^>]*>(.*?)</a>', html)
            print(f"=== Query: {q} ===")
            for s in snippets[:3]:
                print('-', re.sub(r'<[^<]+?>', '', s))
    except Exception as e:
        print(f"Error {q}: {e}")
