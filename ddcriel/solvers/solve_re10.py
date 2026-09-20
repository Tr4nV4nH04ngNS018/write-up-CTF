#!/usr/bin/env python3
"""
Solver for REVERSE CHALLENGE 10 (SentryMark Activation Gate v2.0)
Category: Reverse Engineering
Points: 456

Vulnerability / Mechanism:
SentryMark implements a 2-round Substitution-Permutation Network (SPN) inside an obfuscated
switch-statement state machine (MBA - Mixed Boolean-Arithmetic).
Each round consists of:
1. XOR with KEY (implemented as (A + B) - 2*(A & B))
2. ADD with TRL modulo 256 (implemented as (A ^ B) + 2*(A & B))
3. MUL with MUL modulo 256 (odd multipliers, invertible via modinv(MUL, 256))
4. Byte permutation (PERM)

Since all operations are bijections on (Z/256Z)^16, the transformation is completely invertible.
We invert the operations from TGT backwards to find the unique 16-byte activation code:
  b'pocL38BO(R3shuLT'
Submitting its hex string `706f634c3338424f2852337368754c54` to POST /activate yields the flag.
"""
import requests
import urllib3
import struct
import sys
import os
import re

urllib3.disable_warnings()

BASE_URL = 'https://f8e0441a-e392-4c0d-a640-ed6c8f7d8002.172.31.102.101.nip.io'

def solve(base_url=BASE_URL):
    base_url = base_url.rstrip('/')
    print(f"[*] Target URL: {base_url}")

    # 1. Download sentrymark binary if not present
    binary_path = 'sentrymark'
    if not os.path.exists(binary_path) or os.path.getsize(binary_path) == 0:
        print("[*] Downloading sentrymark binary from server...")
        r = requests.get(f"{base_url}/sentrymark", verify=False, timeout=10)
        with open(binary_path, 'wb') as f:
            f.write(r.content)
        print(f"[+] Downloaded {len(r.content)} bytes.")

    # 2. Extract constant data blobs from binary
    with open(binary_path, 'rb') as f:
        elf_data = f.read()

    e_phoff = struct.unpack_from('<Q', elf_data, 32)[0]
    e_phnum = struct.unpack_from('<H', elf_data, 56)[0]
    e_phentsize = struct.unpack_from('<H', elf_data, 54)[0]

    segments = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('<IIQQQQQQ', elf_data, off)
        segments.append((p_vaddr, p_memsz, p_offset, p_filesz))

    def vaddr_to_offset(vaddr):
        for seg_vaddr, seg_memsz, seg_offset, seg_filesz in segments:
            if seg_vaddr <= vaddr < seg_vaddr + seg_memsz:
                return seg_offset + (vaddr - seg_vaddr)
        return None

    def get_blob(addr):
        off = vaddr_to_offset(addr + 16)
        return list(elf_data[off:off+16])

    TGT   = get_blob(0x404050)
    PERM1 = get_blob(0x404070)
    MUL1  = get_blob(0x404090)
    TRL1  = get_blob(0x4040b0)
    KEY1  = get_blob(0x4040d0)
    PERM0 = get_blob(0x4040f0)
    MUL0  = get_blob(0x404110)
    TRL0  = get_blob(0x404130)
    KEY0  = get_blob(0x404150)

    print("[*] Constant blobs extracted successfully.")

    # 3. Invert the 2-round cipher backwards from TGT
    # Invert Round 1
    s = TGT[:]
    # Invert PERM1: temp[PERM1[i]] = prev[i] => prev[i] = temp[PERM1[i]]
    prev = [0] * 16
    for i in range(16):
        prev[i] = s[PERM1[i]]
    s = prev[:]

    # Invert MUL1: s[i] = prev[i] * MUL1[i] mod 256
    MUL1_INV = [pow(m, -1, 256) for m in MUL1]
    s = [(s[i] * MUL1_INV[i]) & 0xff for i in range(16)]

    # Invert TRL1: s[i] = prev[i] + TRL1[i] mod 256
    s = [(s[i] - TRL1[i]) & 0xff for i in range(16)]

    # Invert KEY1: s[i] = prev[i] ^ KEY1[i]
    s = [s[i] ^ KEY1[i] for i in range(16)]

    # Invert Round 0
    # Invert PERM0
    prev = [0] * 16
    for i in range(16):
        prev[i] = s[PERM0[i]]
    s = prev[:]

    # Invert MUL0
    MUL0_INV = [pow(m, -1, 256) for m in MUL0]
    s = [(s[i] * MUL0_INV[i]) & 0xff for i in range(16)]

    # Invert TRL0
    s = [(s[i] - TRL0[i]) & 0xff for i in range(16)]

    # Invert KEY0
    s = [s[i] ^ KEY0[i] for i in range(16)]

    activation_bytes = bytes(s)
    hex_code = activation_bytes.hex()
    ascii_code = activation_bytes.decode('utf-8', errors='replace')

    print(f"[+] Recovered Activation Code (raw):   {activation_bytes}")
    print(f"[+] Recovered Activation Code (ASCII): {ascii_code}")
    print(f"[+] Recovered Activation Code (hex):   {hex_code}")

    # 4. Submit hex activation code to /activate
    print("[*] Submitting code to /activate...")
    resp = requests.post(f"{base_url}/activate", json={"code": hex_code}, verify=False, timeout=10)
    data = resp.json()
    print(f"[*] Response ({resp.status_code}): {data}")

    flag = data.get("flag")
    if flag:
        print(f"\n[+] SUCCESS! FLAG: {flag}\n")
        return flag
    else:
        print("[-] Activation failed!")
        return None

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    solve(url)
