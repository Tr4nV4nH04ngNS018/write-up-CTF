#!/usr/bin/env python3
"""
Solver for REVERSE CHALLENGE 8 (Chronon eval-harness)
Extracts the flag directly from the XOR-encrypted blob in the .pyc bytecode.
"""
import marshal
import sys
from pathlib import Path

def solve(pyc_path):
    with open(pyc_path, 'rb') as f:
        header = f.read(16)  # skip pyc header
        shuffled_body = f.read()

    # Unshuffle: swap every consecutive pair of bytes
    b = bytearray(shuffled_body)
    for i in range(0, len(b), 2):
        b[i], b[i + 1] = b[i + 1], b[i]
    body = bytes(b)

    # Load code object
    code = marshal.loads(body)

    # Find compute_flag function
    for c in code.co_consts:
        if hasattr(c, 'co_name') and c.co_name == 'compute_flag':
            # co_consts[4] = XOR key (55)
            # co_consts[5] = encrypted blob
            xor_key = c.co_consts[4]
            blob = c.co_consts[5]
            
            # Decrypt: XOR each byte, stop at null
            decrypted = bytes(byte ^ xor_key for byte in blob)
            flag = decrypted.split(b'\x00')[0].decode()
            
            print(f"[+] XOR key: {xor_key}")
            print(f"[+] FLAG: {flag}")
            return flag

    print("[-] compute_flag not found!")
    return None

if __name__ == '__main__':
    pyc = sys.argv[1] if len(sys.argv) > 1 else 'aimodel_eval_extracted/aimodel_eval.pyc'
    solve(pyc)
