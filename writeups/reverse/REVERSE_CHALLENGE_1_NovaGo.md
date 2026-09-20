# Writeup: REVERSE CHALLENGE 1 (NovaGo)

> **Event:** DDC CTF  
> **Category:** Reverse Engineering  
> **Difficulty:** Easy  
> **Points:** 28  
> **Description:** *"The Assistant Ships With Its Own Little Secret, Packed Between Two Curiously Named Markers."*  
> **Flag:** `flag{5436b115-3896-4ca7-82db-8a75f272f519}`

---

## 1. Tóm tắt (TL;DR)

1. Tải file thực thi `novago` (Go binary, x86_64 Linux, Go 1.22).
2. Dựa vào mô tả đề bài *"Packed Between Two Curiously Named Markers"*, ta quét chuỗi tìm marker trong file nhị phân:
   - Start Marker: `NVGO_ENC_FLAG_START_MARKER_ZONE_`
   - End Marker: `NVGO_ENC_FLAG_END_MARKER_ZONE___`
3. Khối 64 bytes nằm giữa 2 marker được mã hóa bằng **XOR đơn giản** với byte khóa `0x5A` (`'Z'`).
4. Giải mã XOR ra ngay flag: `flag{5436b115-3896-4ca7-82db-8a75f272f519}`.
5. Dịch ngược hàm `main.main` cũng chỉ ra token bí mật của chương trình là `"sudo"`:
   Chạy lệnh `./novago reveal sudo` để chương trình tự giải mã và in flag.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát file nhị phân
- Tải file từ trang dashboard: `/novago`
- Định dạng: ELF 64-bit LSB executable, x86-64, Go 1.22 (symbols kept).

### Bước 2: Tìm kiếm Custom Markers
Mô tả đề bài cho biết bí mật nằm giữa 2 markers. Dùng regex quét binary:
```python
import re
with open('novago', 'rb') as f:
    data = f.read()

markers = set(re.findall(rb'[a-zA-Z0-9_\-\.]{3,30}marker[a-zA-Z0-9_\-\.]*', data, re.IGNORECASE))
print(markers)
# {b'NVGO_ENC_FLAG_START_MARKER_ZONE_', b'NVGO_ENC_FLAG_END_MARKER_ZONE___'}
```

Khối dữ liệu nằm giữa 2 marker (từ offset 1197824 đến 1197888):
```text
3c363b3d216f6e696c386b6b6f776962636c776e393b6d7762683e3877623b6d6f3c686d683c6f6b63275a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a
```

### Bước 3: Phân tích phép mã hóa XOR
- Đoạn padding ở đuôi lặp lại ký tự `'Z'` (`0x5A`), chính là null bytes `0x00 ^ 0x5A = 0x5A`.
- Byte đầu tiên `0x3C` (`<`) XOR với ký tự `'f'` (`0x66`) = `0x5A`.
- Thực hiện giải mã với key `0x5A`:
```python
chunk_hex = '3c363b3d216f6e696c386b6b6f776962636c776e393b6d7762683e3877623b6d6f3c686d683c6f6b6327'
flag = bytes([b ^ 0x5A for b in bytes.fromhex(chunk_hex)]).decode()
print(flag) # flag{5436b115-3896-4ca7-82db-8a75f272f519}
```

### Bước 4: Dịch ngược mã máy (Disassembly)
Trong hàm `main.main` tại địa chỉ `0x480b20`:
- Chương trình so sánh subcommand đầu vào với chuỗi `"reveal"`.
- Token kiểm tra tiếp theo có độ dài 4 bytes và giá trị `0x6f647573` (`"sudo"`).
- Khi token đúng, chương trình đọc `main.kFlagRegion[0x20:0x60]` và thực hiện:
  ```asm
  0x480cb2:  xor r9d, 0x5a
  0x480cb6:  test r9b, r9b
  0x480cb9:  je 0x480d02
  ```
- Do đó ta có thể chạy trực tiếp:
  ```bash
  $ ./novago reveal sudo
  flag{5436b115-3896-4ca7-82db-8a75f272f519}
  ```

---

## 3. Script giải tự động (`solve_re1.py`)

```python
#!/usr/bin/env python3
import sys

def solve(binary_path='novago'):
    with open(binary_path, 'rb') as f:
        data = f.read()

    start = b'NVGO_ENC_FLAG_START_MARKER_ZONE_'
    end = b'NVGO_ENC_FLAG_END_MARKER_ZONE___'

    p1 = data.find(start)
    p2 = data.find(end)
    if p1 == -1 or p2 == -1:
        print("[-] Markers not found!")
        return

    encrypted = data[p1 + len(start):p2]
    decrypted = bytes([b ^ 0x5A for b in encrypted])
    flag = decrypted.split(b'\x00')[0].decode('utf-8')
    print("[+] Flag:", flag)
    return flag

if __name__ == '__main__':
    binary = sys.argv[1] if len(sys.argv) > 1 else 'novago'
    solve(binary)
```
