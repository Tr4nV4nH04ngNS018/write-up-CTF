#!/usr/bin/env python3
"""
Robust Solver for MISC CHALLENGE 5 (Whisperbox Watermark Preview)
"""
import requests
import urllib3
import time
import sys

urllib3.disable_warnings()

BASE_URL = 'https://6d1fa0d6-6836-4201-882b-0e6dfd061aad.172.31.102.101.nip.io'
HI = -0.30
LO = -3.20
MID = (HI + LO) / 2.0  # -1.75
TOP_K = 8
N_PROBES = 32
SAMPLES_PER_PROBE = 10  # 10 samples gives std error ~ 0.17, highly accurate and safe

def solve(base_url=BASE_URL):
    base_url = base_url.rstrip('/')
    s = requests.Session()

    info = s.get(f"{base_url}/api/model/info", verify=False, timeout=5).json()
    print(f"[*] Connected to {base_url}")
    print(f"[*] Model Info: {info}")

    n_probes = info.get("n_probes", N_PROBES)
    recovered = []

    print("[*] Extracting watermark bytes across 32 probes...")
    start_time = time.time()

    for idx in range(n_probes):
        acc = [0.0] * TOP_K
        success_count = 0

        for attempt in range(SAMPLES_PER_PROBE):
            try:
                r = s.post(
                    f"{base_url}/api/completions",
                    json={"prompt": f"probe:{idx}", "top_k": TOP_K, "logprobs": True},
                    verify=False,
                    timeout=5
                )
                if r.status_code == 200:
                    tokens = r.json().get("tokens", [])
                    if len(tokens) == TOP_K:
                        for i, t in enumerate(tokens):
                            acc[i] += t["logprob"]
                        success_count += 1
                else:
                    time.sleep(0.05)
            except Exception as e:
                time.sleep(0.05)

        if success_count == 0:
            print(f"[-] Probe {idx} failed completely!")
            recovered.append(ord('?'))
            continue

        avg = [v / success_count for v in acc]
        bits = [1 if v > MID else 0 for v in avg]
        
        byte_val = 0
        for b in bits:
            byte_val = (byte_val << 1) | b
        recovered.append(byte_val)

        char = chr(byte_val) if 32 <= byte_val <= 126 else f'\\x{byte_val:02x}'
        print(f"  Probe {idx:2d} ({success_count} samples): bits={''.join(map(str, bits))} -> '{char}'")

    flag = bytes(recovered).decode('utf-8', errors='replace')
    elapsed = time.time() - start_time
    print(f"\n[+] Extracted in {elapsed:.2f}s")
    print(f"[+] Raw bytes: {bytes(recovered)}")
    print(f"[+] FLAG: {flag}\n")
    return flag

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    solve(url)
