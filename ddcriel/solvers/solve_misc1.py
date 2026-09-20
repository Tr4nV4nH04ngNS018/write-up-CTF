#!/usr/bin/env python3
"""
MISC Challenge 1 - LSB Steganography in Red Channel
"The Han River Bridge Never Looked Better Than After Someone Hid Bits in Its Red Channel"
"""
import urllib.request
import ssl
import io
import struct
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = "https://ca72e277-719c-4a64-8e73-63de3d380d12.172.31.102.101.nip.io"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Download the image
print("[*] Downloading /gallery.png ...")
req = urllib.request.Request(BASE + "/gallery.png")
resp = urllib.request.urlopen(req, context=ctx)
img_data = resp.read()
print(f"[*] Downloaded {len(img_data)} bytes")

# Save locally
with open("gallery.png", "wb") as f:
    f.write(img_data)
print("[*] Saved to gallery.png")

# Try to use PIL/Pillow
try:
    from PIL import Image
    img = Image.open(io.BytesIO(img_data))
    print(f"[*] Image size: {img.size}, mode: {img.mode}")
    
    width, height = img.size
    pixels = img.load()
    
    # Extract LSB from Red channel
    bits = []
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            r = pixel[0]
            bits.append(r & 1)
    
    print(f"[*] Extracted {len(bits)} bits from Red channel LSB")
    
    # Convert bits to bytes
    extracted_bytes = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        extracted_bytes.append(byte)
    
    # Look for flag pattern
    extracted_str = extracted_bytes.decode(errors='replace')
    
    # Print first 200 chars
    print(f"\n[*] First 200 chars of extracted data (MSB first):")
    print(repr(extracted_str[:200]))
    
    # Try LSB first bit order too
    extracted_bytes2 = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = byte | (bits[i + j] << j)
        extracted_bytes2.append(byte)
    
    extracted_str2 = extracted_bytes2.decode(errors='replace')
    print(f"\n[*] First 200 chars of extracted data (LSB first):")
    print(repr(extracted_str2[:200]))
    
    # Search for common flag formats
    for label, data in [("MSB", extracted_str), ("LSB", extracted_str2)]:
        for pattern in ['ddcriel{', 'flag{', 'CTF{', 'FLAG{', 'DDCRIEL{']:
            idx = data.find(pattern)
            if idx >= 0:
                end = data.find('}', idx)
                if end >= 0:
                    flag = data[idx:end+1]
                    print(f"\n[!!!] FLAG FOUND ({label} order): {flag}")
                else:
                    print(f"\n[!!!] Flag start found ({label} order) at {idx}: {data[idx:idx+100]}")
    
    # Also try extracting only first few rows
    print("\n[*] Trying extraction by rows (first 10 rows):")
    for num_rows in [1, 5, 10]:
        bits_row = []
        for y in range(num_rows):
            for x in range(width):
                pixel = pixels[x, y]
                r = pixel[0]
                bits_row.append(r & 1)
        
        # MSB first
        result = bytearray()
        for i in range(0, len(bits_row) - 7, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits_row[i + j]
            result.append(byte)
        print(f"  Rows 0-{num_rows-1} MSB: {result[:80]}")
        
        # LSB first
        result2 = bytearray()
        for i in range(0, len(bits_row) - 7, 8):
            byte = 0
            for j in range(8):
                byte = byte | (bits_row[i + j] << j)
            result2.append(byte)
        print(f"  Rows 0-{num_rows-1} LSB: {result2[:80]}")

    # Also check /prints/han-river-bridge page
    print("\n\n[*] Checking /prints/han-river-bridge ...")
    req2 = urllib.request.Request(BASE + "/prints/han-river-bridge")
    resp2 = urllib.request.urlopen(req2, context=ctx)
    html2 = resp2.read().decode()
    # Find download links or other images
    import re
    imgs2 = re.findall(r'(?:src|href)=["\']([^"\']*\.png[^"\']*)["\']', html2)
    print(f"  Images/PNGs found: {imgs2}")
    # Print relevant body content
    body = html2[html2.find('<body'):] if '<body' in html2 else html2
    print(f"  Body (first 3000):\n{body[:3000]}")

except ImportError:
    print("[!] PIL/Pillow not installed. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "Pillow"], check=True)
    print("[*] Please re-run this script")
