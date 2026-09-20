#!/usr/bin/env python3
"""
Solver script for CRYPTO CHALLENGE 2 (NeuroPay)
"""
import random
import string
import sys
import requests
import urllib3

urllib3.disable_warnings()

def solve(base_url):
    base_url = base_url.rstrip('/')
    stats_url = f"{base_url}/api/stats"
    admin_url = f"{base_url}/api/admin/flag"

    print(f"[*] Querying stats from {stats_url}...")
    r = requests.get(stats_url, verify=False, timeout=10)
    stats = r.json()
    started_at = stats.get('started_at')
    print(f"[+] Container started_at timestamp: {started_at}")

    # NeuroPay uses Python's standard random seeded with started_at
    # Alphabet: string.ascii_letters + string.digits (62 chars)
    # Token length: 16 characters via random.choices
    alphabet = string.ascii_letters + string.digits

    print("[*] Reconstructing admin token from PRNG seed...")
    for offset in range(-5, 6):
        ts = started_at + offset
        random.seed(ts)
        token = ''.join(random.choices(alphabet, k=16))

        r = requests.post(admin_url, json={"token": token}, verify=False, timeout=10)
        if r.status_code == 200:
            res = r.json()
            flag = res.get('flag')
            print(f"[+] Admin token found: {token} (seed={ts})")
            print(f"[+] FLAG: {flag}")
            return flag

    print("[-] Failed to retrieve flag.")
    return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = "https://b61025bc-38d9-4ab3-9dd4-16fa4bf3afbe.172.31.102.101.nip.io"
    solve(target_url)
