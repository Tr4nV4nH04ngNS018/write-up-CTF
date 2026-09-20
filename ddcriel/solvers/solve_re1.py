#!/usr/bin/env python3
"""
Solver script for REVERSE CHALLENGE 1 (NovaGo)
"""
import sys

def solve(binary_path='novago'):
    with open(binary_path, 'rb') as f:
        data = f.read()

    start = b'NVGO_ENC_FLAG_START_MARKER_ZONE_'
    end = b'NVGO_ENC_FLAG_END_MARKER_ZONE___'

    p1 = data.find(start)
    p2 = data.find(end)
    if p1 == -1 or p2 == -1:
        print("[-] Markers not found!")
        return None

    encrypted = data[p1 + len(start):p2]
    decrypted = bytes([b ^ 0x5A for b in encrypted])
    flag = decrypted.split(b'\x00')[0].decode('utf-8')
    print("[+] Flag:", flag)
    return flag

if __name__ == '__main__':
    binary = sys.argv[1] if len(sys.argv) > 1 else 'novago'
    solve(binary)
