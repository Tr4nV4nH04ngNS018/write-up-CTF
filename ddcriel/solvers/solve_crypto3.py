#!/usr/bin/env python3
"""
Padding Oracle Attack Solver for CRYPTO CHALLENGE 3 (VinAI Sessions)

Vulnerability:
- Cookie format: IV (16 bytes) || AES-CBC-128-PKCS7(session_json)
- Service endpoint: POST /api/login with {"cookie": "<hex>"}
- Padding Oracle behavior:
    - HTTP 400: Invalid PKCS7 padding
    - HTTP 401: Valid PKCS7 padding, invalid session/credentials
    - HTTP 200: Valid session
- Admin cookie ciphertext is leaked at GET /api/admin/cookie
- Note says: "encrypted with the session key; you have the oracle."
- The flag is stored directly inside the plaintext of the admin cookie:
  {"user":"audit-service","role":"flag{...}","exp":...}

Optimization:
- Plaintext Character Priority (ASCII/JSON character order) reduces queries per byte from ~128 to ~25.
- Retry logic with backoff handles nginx 503/429 rate limiting.
"""

import sys
import time
import requests
import urllib3

urllib3.disable_warnings()

BASE = "https://8e7837a9-3a79-412b-88e5-7590ee61466e.172.31.102.101.nip.io"
if len(sys.argv) > 1:
    BASE = sys.argv[1].rstrip("/")

session = requests.Session()
session.verify = False

request_count = 0

def oracle(cookie_hex):
    """
    Returns True if padding is valid (HTTP 401 or 200), False if invalid (HTTP 400).
    Retries on rate limits (503 / 429).
    """
    global request_count
    time.sleep(0.015)
    for attempt in range(8):
        try:
            request_count += 1
            r = session.post(f"{BASE}/api/login", json={"cookie": cookie_hex}, timeout=5)
            if r.status_code in (503, 429):
                time.sleep(0.1 * (attempt + 1))
                continue
            return r.status_code in (200, 401)
        except Exception:
            time.sleep(0.15)
    return False

# Priority order for plaintext characters (JSON format optimization)
LIKELY_CHARS = list(b'abcdefghijklmnopqrstuvwxyz0123456789-_":, {}.!@#$%^&*()+=/ABCDEFGHIJKLMNOPQRSTUVWXYZ' + bytes(range(1, 17)))
OTHER_CHARS = [b for b in range(256) if b not in LIKELY_CHARS]
CHAR_PRIORITY = LIKELY_CHARS + OTHER_CHARS

def decrypt_block(prev_block, target_block, block_num=1, total_blocks=5):
    intermediate = bytearray(16)
    plaintext = bytearray(16)
    
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        crafted = bytearray(16)
        for j in range(pos + 1, 16):
            crafted[j] = intermediate[j] ^ pad_val
            
        found = False
        for expected_char in CHAR_PRIORITY:
            guess = expected_char ^ prev_block[pos] ^ pad_val
            crafted[pos] = guess
            test_cookie = (crafted + target_block).hex()
            
            if oracle(test_cookie):
                # Verify edge case for pad=1 (pos == 15) to avoid false positive
                if pos == 15:
                    verify = bytearray(crafted)
                    verify[14] ^= 1
                    if not oracle((verify + target_block).hex()):
                        continue
                intermediate[pos] = guess ^ pad_val
                plaintext[pos] = intermediate[pos] ^ prev_block[pos]
                found = True
                char_display = repr(chr(plaintext[pos])) if 32 <= plaintext[pos] <= 126 else hex(plaintext[pos])
                print(f"  [+] B{block_num} pos {pos:2d}: {char_display} [reqs={request_count}]", flush=True)
                break
                
        if not found:
            raise RuntimeError(f"Failed at pos {pos} in block {block_num}")
            
    return bytes(plaintext)

def main():
    print(f"[*] Target: {BASE}")
    
    r = session.get(f"{BASE}/api/admin/cookie", timeout=5).json()
    admin_cookie = bytes.fromhex(r["cookie"])
    num_blocks = len(admin_cookie) // 16
    print(f"[+] Admin cookie: {admin_cookie.hex()} ({len(admin_cookie)} bytes = {num_blocks} blocks)")
    
    blocks = [admin_cookie[i*16:(i+1)*16] for i in range(num_blocks)]
    
    full_plaintext = b""
    start_time = time.time()
    
    for i in range(1, num_blocks):
        print(f"\n[*] Decrypting block {i}/{num_blocks-1}...", flush=True)
        pt = decrypt_block(blocks[i-1], blocks[i], block_num=i, total_blocks=num_blocks-1)
        full_plaintext += pt
        print(f"[+] Block {i} complete: {pt} (so far: {full_plaintext})", flush=True)
        
    elapsed = time.time() - start_time
    print(f"\n" + "="*56)
    print(f"[+] Decryption complete in {elapsed:.1f}s ({request_count} requests)!")
    print(f"[+] Full plaintext raw: {full_plaintext}")
    
    # Strip PKCS7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16 and full_plaintext[-pad_len:] == bytes([pad_len]) * pad_len:
        unpadded = full_plaintext[:-pad_len]
        print(f"[+] Unpadded plaintext: {unpadded.decode('utf-8', errors='replace')}")
    else:
        print(f"[+] Decoded: {full_plaintext.decode('utf-8', errors='replace')}")
    print("="*56)

if __name__ == "__main__":
    main()
