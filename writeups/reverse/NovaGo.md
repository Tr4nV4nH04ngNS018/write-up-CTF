# Writeup — REVERSE CHALLENGE 1 (NovaGo)

> **Category:** Reverse Engineering  
> **Difficulty:** Easy  
> **Points:** 28  
> **Challenge Prompt:** *"The Assistant Ships With Its Own Little Secret, Packed Between Two Curiously Named Markers."*  
> **Flag:** `flag{5436b115-3896-4ca7-82db-8a75f272f519}`

---

## 1. Tóm tắt (TL;DR)

1. Đề bài cung cấp ứng dụng CLI viết bằng Go mang tên **NovaGo** (`x86_64 Linux`, Go 1.22).
2. Dựa vào mô tả *"Packed Between Two Curiously Named Markers"*, ta quét chuỗi trong file nhị phân `novago` và tìm thấy 2 marker ranh giới:
   - `NVGO_ENC_FLAG_START_MARKER_ZONE_`
   - `NVGO_ENC_FLAG_END_MARKER_ZONE___`
3. Nằm giữa hai marker là một khối dữ liệu 64 bytes. Quan sát phần đệm (padding) kết thúc bằng chuỗi ký tự `'Z'` (`0x5A`), và ký tự đầu tiên `0x3C` (`<`) XOR với `'f'` (`0x66`) cho kết quả đúng bằng `0x5A`.
4. Toàn bộ chuỗi được mã hóa XOR đơn giản với byte khóa `0x5A`. Khi giải mã ra:
   `flag{5436b115-3896-4ca7-82db-8a75f272f519}`.
5. Dịch ngược hàm `main.main` cũng cho thấy tham số bí mật để chương trình tự in flag qua lệnh `reveal` chính là token `"sudo"`:
   `./novago reveal sudo`.

---

## 2. Khảo sát ban đầu (Reconnaissance)

Trang dashboard thử thách cung cấp link tải binary `novago`:
- **File:** `novago` (ELF 64-bit LSB executable, x86-64, Go 1.22)
- **Dung lượng:** ~1.89 MB
- **Gợi ý sử dụng trên trang:**
  ```bash
  $ chmod +x novago
  $ ./novago                  # help banner
  $ ./novago status           # print model + version
  $ ./novago reveal <token>   # reveal internal licence, if you know the token
  ```

---

## 3. Phân tích tĩnh & Khai thác Markers (Static Analysis)

Gợi ý của đề bài nhấn mạnh:
> *"The Assistant Ships With Its Own Little Secret, Packed Between Two Curiously Named Markers."*

Ta tiến hành tìm kiếm các chuỗi chứa từ khóa `marker` trong binary:

```python
import re

with open('novago', 'rb') as f:
    data = f.read()

markers = set(re.findall(rb'[a-zA-Z0-9_\-\.]{3,30}marker[a-zA-Z0-9_\-\.]*', data, re.IGNORECASE))
print(markers)
```

Kết quả trả về 2 marker cực kỳ rõ ràng:
- `NVGO_ENC_FLAG_START_MARKER_ZONE_` (tại offset `1197792`)
- `NVGO_ENC_FLAG_END_MARKER_ZONE___` (tại offset `1197888`)

Trích xuất 64 bytes nằm giữa 2 marker này:
```text
Raw bytes: b"<6;=!onil8kkowibclwn9;mwbh>8wb;mo<hmh<okc'ZZZZZZZZZZZZZZZZZZZZZZ"
Hex: 3c363b3d216f6e696c386b6b6f776962636c776e393b6d7762683e3877623b6d6f3c686d683c6f6b63275a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a
```

### Nhận định toán học / Mã hóa:
- Độ dài phần chuỗi trước padding là 42 ký tự.
- Ký tự đầu tiên: `0x3C` (`<`). Ta biết flag bắt đầu bằng `flag{` (`0x66`).
  $$\text{Key} = 0x3C \oplus 0x66 = 0x5A \quad (\text{ký tự } 'Z')$$
- Đuôi của khối dữ liệu được đệm bằng hàng loạt ký tự `'Z'` (`0x5A`), tương ứng với byte null `0x00 \oplus 0x5A = 0x5A`.

Thực hiện giải mã XOR với khóa `0x5A`:

```python
chunk_hex = '3c363b3d216f6e696c386b6b6f776962636c776e393b6d7762683e3877623b6d6f3c686d683c6f6b6327'
chunk = bytes.fromhex(chunk_hex)
flag = bytes([b ^ 0x5A for b in chunk]).decode()
print("Flag:", flag)
# Flag: flag{5436b115-3896-4ca7-82db-8a75f272f519}
```

---

## 4. Dịch ngược chuyên sâu hàm `main.main` (Deep Reversing)

Để hiểu trọn vẹn cơ chế xác thực token của lệnh `./novago reveal <token>`, ta phân tích mã máy của hàm `main.main` tại địa chỉ `0x480b20`:

```asm
; Kiểm tra subcommand argv[1] có phải là "reveal" không
0x480b61:  cmp dword ptr [r9], 0x65766572   ; "reve"
0x480b68:  cmp word ptr [r9 + 4], 0x6c61   ; "al"

; Kiểm tra tham số token argv[2]
0x480b80:  cmp rdx, 3                       ; số lượng tham số argc >= 3
0x480b86:  cmp qword ptr [r8 + 0x28], 4     ; độ dài chuỗi token == 4
0x480b91:  cmp dword ptr [rdx], 0x6f647573   ; "sudo" (0x73, 0x75, 0x64, 0x6f little-endian)

; Vòng lặp giải mã flag nếu token == "sudo"
0x480bb1:  mov eax, 0x20                    ; offset bắt đầu 0x20 (sau START_MARKER)
0x480ca0:  cmp rax, 0x60                    ; quét tới offset 0x60 (tổng cộng 64 bytes)
0x480ca6:  lea r8, [rip + 0xa3a33]          ; con trỏ tới main.kFlagRegion
0x480cad:  movzx r9d, byte ptr [r8 + rax]    ; lấy từng byte dữ liệu mã hóa
0x480cb2:  xor r9d, 0x5a                    ; XOR với 0x5A
0x480cb6:  test r9b, r9b                    ; kiểm tra byte null kết thúc
0x480cb9:  je 0x480d02
...
0x480d52:  call 0x47b880                    ; In flag ra màn hình
```

Từ đây ta thấy:
- Token mà lệnh `reveal` yêu cầu chính là: **`sudo`**.
- Khi chạy lệnh:
  ```bash
  $ ./novago reveal sudo
  flag{5436b115-3896-4ca7-82db-8a75f272f519}
  ```

---

## 5. Script giải tự động (Solver Script)

```python
#!/usr/bin/env python3
"""
NovaGo RE Challenge 1 Solver
"""
import sys

def solve(binary_path='novago'):
    with open(binary_path, 'rb') as f:
        data = f.read()

    start_marker = b'NVGO_ENC_FLAG_START_MARKER_ZONE_'
    end_marker = b'NVGO_ENC_FLAG_END_MARKER_ZONE___'

    p1 = data.find(start_marker)
    p2 = data.find(end_marker)

    if p1 == -1 or p2 == -1:
        print("[-] Markers not found!")
        return

    encrypted_blob = data[p1 + len(start_marker):p2]
    
    # Giải mã XOR với 0x5A
    decrypted = bytes([b ^ 0x5A for b in encrypted_blob])
    # Cắt bỏ phần null bytes đệm ở cuối
    flag = decrypted.split(b'\x00')[0].decode('utf-8')

    print("[+] Found Flag:", flag)
    return flag

if __name__ == '__main__':
    binary = sys.argv[1] if len(sys.argv) > 1 else 'novago'
    solve(binary)
```

---

## 6. Kết luận

- **Flag:** `flag{5436b115-3896-4ca7-82db-8a75f272f519}`
- **Kỹ thuật cốt lõi:**
  - Pattern Search theo mô tả đề bài (Custom Markers trong file nhị phân Go).
  - Phân tích phép mã hóa đối xứng cơ bản (Single-byte XOR).
  - Reverse Engineering luồng so sánh chuỗi trong hàm `main.main` (tìm token `sudo`).
