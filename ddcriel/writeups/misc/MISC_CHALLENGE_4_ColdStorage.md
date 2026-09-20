# Writeup: MISC CHALLENGE 4 (Cold Storage)

> **Sự kiện:** DDC CTF  
> **Danh mục:** Digital Forensics / FAT32 Recovery  
> **Độ khó:** Easy  
> **Điểm:** 48  
> **Mục tiêu (Target):** `https://397ed25d-a3a6-4ce1-8ea7-4377961cfec9.172.31.102.101.nip.io/`  
> **Mô tả đề bài:** *"Old Workstations Go to Cold Storage, but Not Everything on the FAT32 Drive Stays Buried."*  
> **Flag:** `flag{777ee36a-a2ce-46a9-a8be-2f19c90d6362}`

---

## 1. Tóm tắt (TL;DR)

1. Tải file disk image `workstation.img` (dung lượng 12 MiB, phân vùng định dạng FAT32) từ dịch vụ lưu trữ chứng cứ **Cold Storage**.
2. Dựa vào mô tả *"The Sensitive File Was Deleted"*, bài toán yêu cầu phục hồi dữ liệu từ file đã bị xóa trên hệ thống tệp FAT32.
3. Phân tích bảng thư mục gốc (Root Directory Table), tìm thấy mục tệp bị xóa với ký tự đầu `0xE5`: `?RAINI~1.TXT` (tên gốc `training-run.txt`).
4. File bị xóa trỏ tới bắt đầu tại **Cluster 7** với dung lượng 250 bytes.
5. Đọc trực tiếp 250 bytes dữ liệu tại vị trí Cluster 7 trên disk image, thu được flag xác thực:
   `flag{777ee36a-a2ce-46a9-a8be-2f19c90d6362}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát cấu trúc FAT32
Tải file `workstation.img` và phân tích BIOS Parameter Block (BPB):
- Số byte mỗi sector: 512 bytes.
- Số sector mỗi cluster: 1 sector (Cluster size = 512 bytes).
- Số reserved sectors: 32 sectors.
- Số bảng FAT: 2.
- Dung lượng mỗi bảng FAT: 189 sectors.

Vị trí bắt đầu của vùng dữ liệu (Data Region - tương ứng Cluster 2):
$$	ext{Data Start Offset} = (	ext{Reserved Sectors} + 	ext{Num FATs} 	imes 	ext{FAT Size}) 	imes 	ext{Bytes per Sector}$$
$$	ext{Data Start Offset} = (32 + 2 	imes 189) 	imes 512 = 410 	imes 512 = 209,920 	ext{ bytes}$$

### Bước 2: Quét danh mục thư mục (Directory Entries)
Trong hệ thống tập tin FAT32:
- Khi một file bị xóa, hệ điều hành chỉ thay thế byte đầu tiên của tên file trong Directory Entry bằng `0xE5`.
- Nội dung trỏ đến cluster bắt đầu và kích thước file trong Directory Entry vẫn được giữ nguyên vẹn cho đến khi bị ghi đè bởi file mới.

Quét toàn bộ thư mục gốc tìm các mục tệp:
| Trạng thái | Tên file | Cluster bắt đầu | Kích thước (bytes) |
| :--- | :--- | :--- | :--- |
| ACTIVE | `README.TXT` | 3 | 206 |
| ACTIVE | `meeting-notes.txt` | 4 | 251 |
| ACTIVE | `model_card.md` | 5 | 192 |
| ACTIVE | `changelog.md` | 6 | 172 |
| ACTIVE | `SCRATCH1.LOG` | 8 | 250 |
| ACTIVE | `SCRATCH2.LOG` | 9 | 150 |
| **DELETED (`0xE5`)** | **`?RAINI~1.TXT`** | **7** | **250** |

Mục tệp `?RAINI~1.TXT` (tương ứng `training-run.txt`) bắt đầu tại **Cluster 7** với kích thước 250 bytes.

### Bước 3: Khôi phục nội dung tệp
Vị trí offset của Cluster 7 trên disk image:
$$	ext{Offset} = 	ext{Data Start} + (	ext{Cluster} - 2) 	imes 	ext{Cluster Size}$$
$$	ext{Offset} = 209,920 + (7 - 2) 	imes 512 = 209,920 + 2,560 = 212,480$$

Đọc 250 bytes từ offset 212,480:
```text
VinAI training-run credentials
-------------------------------

model:     NovaLLM-3.5-eval
dataset:   internal-2026-Q2
checksum:  b3c9e26d0af5c1a2

redemption flag: flag{777ee36a-a2ce-46a9-a8be-2f19c90d6362}

(do not commit this to source control.)
```

---

## 3. Mã khai thác hoàn chỉnh (`solve_misc4.py`)

```python
#!/usr/bin/env python3
"""
DDC CTF - MISC CHALLENGE 4: Cold Storage
Exploit: FAT32 Deleted File Directory Parsing & Carving
"""

import struct
import sys

def solve(image_path="workstation.img"):
    print(f"[*] Đang phân tích disk image: {image_path}")
    with open(image_path, "rb") as f:
        data = f.read()

    # 1. Parse FAT32 BPB
    bytes_per_sector = struct.unpack_from('<H', data, 11)[0]
    sectors_per_cluster = data[13]
    reserved_sectors = struct.unpack_from('<H', data, 14)[0]
    num_fats = data[16]
    fat_size = struct.unpack_from('<I', data, 36)[0]

    cluster_size = bytes_per_sector * sectors_per_cluster
    data_start = (reserved_sectors + num_fats * fat_size) * bytes_per_sector
    print(f"[+] Sector size: {bytes_per_sector}, Cluster size: {cluster_size}, Data start: {data_start}")

    # 2. Đọc file bị xóa tại Cluster 7 (kích thước 250 bytes)
    cluster = 7
    offset = data_start + (cluster - 2) * cluster_size
    recovered = data[offset:offset + 250]
    recovered_text = recovered.decode('utf-8', errors='replace')
    
    print("\n[+] Nội dung file khôi phục thành công:")
    print("-" * 50)
    print(recovered_text.strip())
    print("-" * 50)

    if "flag{" in recovered_text:
        start = recovered_text.find("flag{")
        end = recovered_text.find("}", start) + 1
        flag = recovered_text[start:end]
        print(f"\n[+] FLAG: {flag}")
        return flag

if __name__ == '__main__':
    img = sys.argv[1] if len(sys.argv) > 1 else "workstation.img"
    solve(img)
```

---

## 4. Bài học rút ra (Key Takeaways)

- **Cơ chế xóa file trên hệ thống FAT32**: Khi xóa file thông thường, hệ điều hành chỉ thay byte đầu tiên của tên file thành `0xE5` và đánh dấu cluster trong bảng FAT là trống. Dữ liệu thực tế trên đĩa không bị xóa và có thể khôi phục 100% bằng kỹ thuật File Carving / Forensic Recovery.
- **Tầm quan trọng của Secure Erase (Wipe)**: Khi loại biên hoặc chuyển giao các máy chủ và thiết bị lưu trữ cũ (Cold Storage), cần thực hiện ghi đè ngẫu nhiên nhiều lần (shred / wipe) để xóa sạch dấu vết dữ liệu nhạy cảm.
