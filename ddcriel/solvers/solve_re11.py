#!/usr/bin/env python3
"""
Solver for REVERSE CHALLENGE 11 (ChromaVault SPIR-V Compute Shader)
Category: Reverse Engineering
Points: 428

Vulnerability / Mechanism:
ChromaVault runs an image watermark validator on a Vulkan compute shader (`watermark.spv`).
The SPIR-V bytecode implements a 16-thread workgroup validator where thread `tid` (0 <= tid < 16):
1. Loads two 16-element constant arrays:
   ARR1 = [158, 160, 39, 36, 112, 162, 178, 232, 226, 42, 71, 86, 217, 250, 186, 29]
   ARR2 = [181, 30, 66, 154, 60, 46, 65, 83, 36, 154, 173, 107, 169, 151, 48, 132]
2. Computes an intermediate key K[tid] using helper function `f11(tid, ARR1[tid])`:
   v = ARR1[tid]
   v = ((v + tid) * 977317915) & 0xff
   v = ((v ^ (v >> 6)) * 2897629957) & 0xff
   v = ((v + tid * 243) ^ 182) & 0xff
3. Computes the target watermark value:
   TARGET[tid] = (ARR2[tid] ^ K[tid]) & 0xff
4. Compares the input watermark byte with TARGET[tid]:
   diff[tid] = (INPUT[tid] ^ TARGET[tid]) & 0xff
5. Accumulates all 16 diffs: if all diffs are 0, verification succeeds.

By computing TARGET for all 16 bytes, we recover the watermark:
  `KctFrBHKfG0E83DI`
Submitting this to POST /verify outputs the flag.
"""
import requests
import urllib3
import struct
import time
import sys
import re
import os

urllib3.disable_warnings()

BASE_URL = 'https://fc1392f3-a225-4e21-b280-7f56360c698c.172.31.102.101.nip.io'

def f11(tid, val):
    v = val
    v = ((v + tid) * 977317915) & 0xff
    v = ((v ^ (v >> 6)) * 2897629957) & 0xff
    v = ((v + tid * 243) ^ 182) & 0xff
    return v

def solve(base_url=BASE_URL):
    base_url = base_url.rstrip('/')
    print(f"[*] Target URL: {base_url}")

    # 1. Download watermark.spv if needed
    spv_path = 'watermark.spv'
    if not os.path.exists(spv_path) or os.path.getsize(spv_path) == 0:
        print("[*] Downloading watermark.spv...")
        r = requests.get(f"{base_url}/watermark.spv", verify=False, timeout=10)
        with open(spv_path, 'wb') as f:
            f.write(r.content)
        print(f"[+] Downloaded {len(r.content)} bytes.")

    # 2. Extract constants from SPIR-V bytecode or use parsed values
    ARR1 = [158, 160, 39, 36, 112, 162, 178, 232, 226, 42, 71, 86, 217, 250, 186, 29]
    ARR2 = [181, 30, 66, 154, 60, 46, 65, 83, 36, 154, 173, 107, 169, 151, 48, 132]

    # 3. Compute target watermark
    target_bytes = []
    for i in range(16):
        k = f11(i, ARR1[i])
        tgt = (ARR2[i] ^ k) & 0xff
        target_bytes.append(tgt)

    watermark = bytes(target_bytes).decode('utf-8')
    print(f"[+] Target Watermark: {watermark} (hex: {bytes(target_bytes).hex()})")

    # 4. Submit to /verify
    print("[*] Submitting watermark to /verify...")
    resp = requests.post(f"{base_url}/verify", data={"watermark": watermark}, verify=False, timeout=10)
    
    m = re.search(r'flag:\s*(flag\{[^}]+\})', resp.text)
    if m:
        flag = m.group(1)
        print(f"\n[+] SUCCESS! FLAG: {flag}\n")
        return flag
    else:
        print("[-] Flag not found in response!")
        print(resp.text[:500])
        return None

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    solve(url)
