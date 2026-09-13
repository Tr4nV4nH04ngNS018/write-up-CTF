import urllib.request

url = "https://esm.sh/gh/PrismJS/prism@36ad7f8/es2022/src/global.mjs"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    code = resp.read().decode()

with open("scripts_dev/prism_source.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Saved prism_source.js, length:", len(code))

pos = 0
while True:
    pos = code.find("pluginRegistry", pos)
    if pos == -1:
        break
    print("--- MATCH AT", pos, "---")
    print(code[max(0, pos - 150):min(len(code), pos + 300)])
    pos += 1
