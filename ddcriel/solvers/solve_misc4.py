#!/usr/bin/env python3
"""
MISC Challenge 4 - Recover deleted file from FAT32 image
"The Sensitive File Was Deleted, and Its Bytes Were Assured This Made Them Truly Private."
"""
import struct
import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IMG = "workstation.img"

with open(IMG, "rb") as f:
    data = f.read()

print(f"[*] Image size: {len(data)} bytes ({len(data)//1024//1024} MiB)")

# Parse FAT32 BPB (BIOS Parameter Block)
bytes_per_sector = struct.unpack_from('<H', data, 11)[0]
sectors_per_cluster = data[13]
reserved_sectors = struct.unpack_from('<H', data, 14)[0]
num_fats = data[16]
root_entry_count = struct.unpack_from('<H', data, 17)[0]  # 0 for FAT32
total_sectors_16 = struct.unpack_from('<H', data, 19)[0]
fat_size_16 = struct.unpack_from('<H', data, 22)[0]
total_sectors_32 = struct.unpack_from('<I', data, 32)[0]
fat_size_32 = struct.unpack_from('<I', data, 36)[0]
root_cluster = struct.unpack_from('<I', data, 44)[0]

fat_size = fat_size_32 if fat_size_32 else fat_size_16
total_sectors = total_sectors_32 if total_sectors_32 else total_sectors_16

print(f"\n[*] FAT32 BPB:")
print(f"  Bytes per sector: {bytes_per_sector}")
print(f"  Sectors per cluster: {sectors_per_cluster}")
print(f"  Reserved sectors: {reserved_sectors}")
print(f"  Number of FATs: {num_fats}")
print(f"  FAT size (sectors): {fat_size}")
print(f"  Root cluster: {root_cluster}")
print(f"  Total sectors: {total_sectors}")

cluster_size = bytes_per_sector * sectors_per_cluster
fat_start = reserved_sectors * bytes_per_sector
data_start = (reserved_sectors + num_fats * fat_size) * bytes_per_sector

print(f"  Cluster size: {cluster_size}")
print(f"  FAT start: {fat_start}")
print(f"  Data start: {data_start}")

def cluster_to_offset(cluster):
    return data_start + (cluster - 2) * cluster_size

def get_fat_entry(cluster):
    offset = fat_start + cluster * 4
    return struct.unpack_from('<I', data, offset)[0] & 0x0FFFFFFF

def read_cluster_chain(start_cluster):
    result = b''
    cluster = start_cluster
    visited = set()
    while cluster >= 2 and cluster < 0x0FFFFFF8 and cluster not in visited:
        visited.add(cluster)
        off = cluster_to_offset(cluster)
        result += data[off:off + cluster_size]
        cluster = get_fat_entry(cluster)
    return result

# Read root directory
print(f"\n[*] Reading root directory (cluster {root_cluster})...")
root_data = read_cluster_chain(root_cluster)

def parse_directory(dir_data, label=""):
    entries = []
    lfn_parts = {}
    i = 0
    while i < len(dir_data):
        entry = dir_data[i:i+32]
        if len(entry) < 32:
            break
        
        first_byte = entry[0]
        if first_byte == 0x00:  # End of directory
            break
        
        attr = entry[11]
        
        # Check for LFN entry
        if attr == 0x0F:
            seq = entry[0] & 0x3F
            name_part = b''
            name_part += entry[1:11]    # chars 1-5
            name_part += entry[14:26]   # chars 6-11
            name_part += entry[28:32]   # chars 12-13
            try:
                lfn_str = name_part.decode('utf-16-le').rstrip('\x00').rstrip('\uffff')
            except:
                lfn_str = ''
            lfn_parts[seq] = lfn_str
            i += 32
            continue
        
        # Regular entry
        is_deleted = (first_byte == 0xE5)
        
        # Short name
        name = entry[0:8].decode('ascii', errors='replace').rstrip()
        ext = entry[8:11].decode('ascii', errors='replace').rstrip()
        if is_deleted:
            name = '?' + name[1:]  # First char was overwritten with 0xE5
        
        short_name = f"{name}.{ext}" if ext else name
        
        # Build LFN
        lfn = ''
        if lfn_parts:
            for seq in sorted(lfn_parts.keys()):
                lfn += lfn_parts[seq]
            lfn_parts = {}
        
        # File attributes
        attrs = []
        if attr & 0x01: attrs.append('R')
        if attr & 0x02: attrs.append('H')
        if attr & 0x04: attrs.append('S')
        if attr & 0x08: attrs.append('V')  # Volume label
        if attr & 0x10: attrs.append('D')  # Directory
        if attr & 0x20: attrs.append('A')  # Archive
        
        # Cluster
        cluster_hi = struct.unpack_from('<H', entry, 20)[0]
        cluster_lo = struct.unpack_from('<H', entry, 26)[0]
        cluster = (cluster_hi << 16) | cluster_lo
        
        # File size
        file_size = struct.unpack_from('<I', entry, 28)[0]
        
        status = "DELETED" if is_deleted else "ACTIVE"
        display_name = lfn if lfn else short_name
        
        print(f"  [{status}] {display_name:40s} short={short_name:15s} attrs={''.join(attrs):5s} cluster={cluster:6d} size={file_size:10d}")
        
        entries.append({
            'name': display_name,
            'short_name': short_name,
            'deleted': is_deleted,
            'attr': attr,
            'cluster': cluster,
            'size': file_size,
            'is_dir': bool(attr & 0x10),
        })
        
        lfn_parts = {}
        i += 32
    
    return entries

print("\n=== ROOT DIRECTORY ===")
root_entries = parse_directory(root_data)

# Scan subdirectories
for entry in root_entries:
    if entry['is_dir'] and entry['cluster'] >= 2 and entry['name'] not in ['.', '..']:
        print(f"\n=== DIRECTORY: {entry['name']} ===")
        sub_data = read_cluster_chain(entry['cluster'])
        sub_entries = parse_directory(sub_data)
        
        # For deleted files in subdirs, try to recover
        for sub in sub_entries:
            if sub['deleted'] and sub['size'] > 0:
                print(f"\n  [*] Attempting to recover deleted file: {sub['name']} (cluster {sub['cluster']}, size {sub['size']})")
                if sub['cluster'] >= 2:
                    recovered = data[cluster_to_offset(sub['cluster']):cluster_to_offset(sub['cluster']) + sub['size']]
                    # Check content
                    print(f"      First 200 bytes: {recovered[:200]}")
                    rec_str = recovered.decode(errors='replace')
                    if 'flag' in rec_str.lower() or 'ddcriel' in rec_str.lower() or '{' in rec_str:
                        print(f"\n  [!!!] POSSIBLE FLAG in recovered file!")
                        print(f"      Content: {rec_str[:500]}")

# Also recover deleted files from root
print("\n\n=== RECOVERING DELETED FILES FROM ROOT ===")
for entry in root_entries:
    if entry['deleted'] and entry['size'] > 0 and entry['cluster'] >= 2:
        print(f"\n[*] Recovering: {entry['name']} (cluster {entry['cluster']}, size {entry['size']})")
        recovered = data[cluster_to_offset(entry['cluster']):cluster_to_offset(entry['cluster']) + entry['size']]
        print(f"    First 200 bytes: {recovered[:200]}")
        rec_str = recovered.decode(errors='replace')
        if 'flag' in rec_str.lower() or 'ddcriel' in rec_str.lower() or '{' in rec_str:
            print(f"\n[!!!] POSSIBLE FLAG!")
            print(f"    Content: {rec_str[:500]}")

# Also search the entire image for flag pattern
print("\n\n=== SEARCHING ENTIRE IMAGE FOR FLAG ===")
for pattern in [b'flag{', b'FLAG{', b'ddcriel{', b'DDCRIEL{']:
    idx = 0
    while True:
        idx = data.find(pattern, idx)
        if idx < 0:
            break
        end = data.find(b'}', idx)
        if end > 0 and end - idx < 200:
            flag = data[idx:end+1].decode(errors='replace')
            print(f"  Found at offset {idx} (0x{idx:x}): {flag}")
        idx += 1
