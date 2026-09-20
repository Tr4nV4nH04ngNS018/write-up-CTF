# Writeup: REVERSE CHALLENGE 10 — SentryMark Activation Gate v2.0

> **Sự kiện:** DDC CTF  
> **Danh mục:** Reverse Engineering  
> **Độ khó:** Hard  
> **Điểm:** 456  
> **Mô tả đề bài:** *"SentryMark Wrapped The Check In A Switch Statement And Its Arithmetic In A Trigonometry Textbook."*  
> **Target:** `https://f8e0441a-e392-4c0d-a640-ed6c8f7d8002.172.31.102.101.nip.io/`  
> **Flag:** `flag{c2f7fb33-e0e9-40ca-8825-0fdf504e1495}`  

---

## 1. Tóm tắt (TL;DR)

1. Tải về file thực thi ELF 64-bit `sentrymark` từ dashboard dịch vụ.
2. Binary còn nguyên symbols (`gcc 13`, `challenge.c`) và chứa các mảng hằng số định danh rõ ràng: `MARK_KEY0`, `MARK_TRL0`, `MARK_MUL0`, `MARK_PERM0`, `MARK_KEY1`, `MARK_TRL1`, `MARK_MUL1`, `MARK_PERM1`, `MARK_TGT`, `MARK_ROTOR`.
3. Hàm `main` được làm mờ (obfuscate) bằng cơ chế **Switch Dispatch State Machine** (Jump table gồm 16 cases tại `0x4020f8`) và **Mixed Boolean-Arithmetic (MBA)** nhằm che giấu các phép toán số học:
   - $(A + B) - 2(A \ \& \ B) \equiv A \oplus B$ (Phép XOR).
   - $(A \oplus B) + 2(A \ \& \ B) \equiv (A + B) \pmod{256}$ (Phép cộng modulo 256).
   - $A \times M \pmod{256}$ với $M$ là số lẻ (Phép nhân khả nghịch trên vành $\mathbb{Z}/256\mathbb{Z}$).
4. Luồng xử lý thực chất là một mạng thay thế - hoán vị (**Substitution-Permutation Network - SPN**) gồm 2 vòng mã hóa:
   - **Vòng 0:** `XOR KEY0` $\rightarrow$ `ADD TRL0` $\rightarrow$ `MUL MUL0` $\rightarrow$ `PERM0`.
   - **Vòng 1:** `XOR KEY1` $\rightarrow$ `ADD TRL1` $\rightarrow$ `MUL MUL1` $\rightarrow$ `PERM1`.
   - **Kiểm tra:** So sánh với `TGT`.
5. Vì tất cả các phép toán thành phần đều là song ánh (bijections) trên $(\mathbb{Z}/256\mathbb{Z})^{16}$, toàn bộ quá trình biến đổi là **khả nghịch 100%**. Ta giải mã ngược từ `TGT` để thu được mã kích hoạt 16 bytes duy nhất: `b'pocL38BO(R3shuLT'`.
6. Chuyển đổi mã kích hoạt sang dạng chuỗi HEX (`706f634c3338424f2852337368754c54`) và gửi `POST /activate` $\rightarrow$ Server xác thực thành công và trả về flag.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ & Tải file thực thi

Trang chủ SentryMark cung cấp mô tả và liên kết tải file:
```bash
$ wget https://f8e0441a-e392-4c0d-a640-ed6c8f7d8002.172.31.102.101.nip.io/sentrymark
```

Kiểm tra thông tin file:
```bash
$ file sentrymark
sentrymark: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=..., for GNU/Linux 3.2.0, with debug_info, not stripped
```

Kiểm tra bảng ký hiệu (Symbol Table) bằng `readelf -s sentrymark`:
```text
Num:    Value          Size Type    Bind   Vis      Ndx Name
 4: 0000000000404110    32 OBJECT  LOCAL  DEFAULT   24 MARK_MUL0_BLOB
 5: 00000000004040d0    32 OBJECT  LOCAL  DEFAULT   24 MARK_KEY1_BLOB
 6: 00000000004040b0    32 OBJECT  LOCAL  DEFAULT   24 MARK_TRL1_BLOB
 7: 0000000000404150    32 OBJECT  LOCAL  DEFAULT   24 MARK_KEY0_BLOB
 8: 0000000000404050    32 OBJECT  LOCAL  DEFAULT   24 MARK_TGT_BLOB
 9: 0000000000404090    32 OBJECT  LOCAL  DEFAULT   24 MARK_MUL1_BLOB
10: 0000000000404130    32 OBJECT  LOCAL  DEFAULT   24 MARK_TRL0_BLOB
11: 0000000000404070    32 OBJECT  LOCAL  DEFAULT   24 MARK_PERM1_BLOB
12: 00000000004040f0    32 OBJECT  LOCAL  DEFAULT   24 MARK_PERM0_BLOB
13: 0000000000404030    32 OBJECT  LOCAL  DEFAULT   24 MARK_ROTOR_BLOB
44: 0000000000401070   807 FUNC    GLOBAL DEFAULT   14 main
```
Toàn bộ symbol của chương trình vẫn được giữ nguyên. Mỗi BLOB có kích thước 32 bytes, trong đó 16 bytes đầu là chuỗi tag (ví dụ `SMK2-P00-MARK___`) và 16 bytes sau là dữ liệu thực tế.

---

### Bước 2: Phân tích máy trạng thái Switch Dispatch

Tại đầu hàm `main` (`0x401070`):
```assembly
4010a1: mov    ecx, 0xb             ; Khởi tạo state ban đầu = 11 (0xb)
4010b5: cmp    ecx, 0xf             ; Kiểm tra state <= 15
4010b8: ja     4010e7               ; Nếu > 15 -> REJECT
4010ba: mov    eax, ecx
4010bc: jmp    QWORD PTR [rax*8+0x4020f8] ; Nhảy gián tiếp qua Jump Table
```

Bảng nhảy (Jump Table) tại `0x4020f8` chứa các nhánh xử lý:
| Case | State (`ecx`) | Địa chỉ xử lý | Ý nghĩa / Hành vi |
|:---:|:---:|:---:|:---|
| **11** | `0x0b` | `0x4010c8` | Đọc 16 bytes từ stdin vào `[rsp+0x10]` qua hàm `read(0, buf, 16)`. Nếu đủ 16 bytes $\rightarrow$ chuyển state `ecx = 3`. |
| **3**  | `0x03` | `0x4011a0` | Thực hiện biến đổi vòng lặp `rdx = 0..15` với `KEY0`. Sau đó $\rightarrow$ `ecx = 8`. |
| **8**  | `0x08` | `0x401240` | Biến đổi vòng lặp `rdx = 0..15` với `TRL0`. Sau đó $\rightarrow$ `ecx = 14 (0x0e)`. |
| **14** | `0x0e` | `0x401100` | Biến đổi vòng lặp `rdx = 0..15` với `MUL0`. Sau đó $\rightarrow$ `ecx = 6`. |
| **6**  | `0x06` | `0x4012c0` | Hoán vị 16 bytes theo bảng `PERM0`. Sau đó $\rightarrow$ `ecx = 12 (0x0c)`. |
| **12** | `0x0c` | `0x401128` | Biến đổi vòng lặp `rdx = 0..15` với `KEY1`. Sau đó $\rightarrow$ `ecx = 9`. |
| **9**  | `0x09` | `0x401168` | Biến đổi vòng lặp `rdx = 0..15` với `TRL1`. Sau đó $\rightarrow$ `ecx = 15 (0x0f)`. |
| **15** | `0x0f` | `0x401210` | Biến đổi vòng lặp `rdx = 0..15` với `MUL1`. Sau đó $\rightarrow$ `ecx = 1`. |
| **1**  | `0x01` | `0x401280` | Hoán vị 16 bytes theo bảng `PERM1`. Sau đó $\rightarrow$ `ecx = 2`. |
| **2**  | `0x02` | `0x4011e0` | So sánh từng byte của bộ nhớ sau biến đổi với `TGT`. Nếu khớp cả 16 bytes $\rightarrow$ `ecx = 4`. Nếu lệch bất kỳ byte nào $\rightarrow$ nhảy tới `0x4010e7` (REJECT). |
| **4**  | `0x04` | `0x401300` | Sinh licence token, in thông báo `=== SentryMark: activation accepted ===` và trả về mã lỗi 0. |

---

### Bước 3: Hóa giải các biểu thức làm mờ MBA (Mixed Boolean-Arithmetic)

Chương trình sử dụng các hằng đẳng thức Boolean-Số học kinh điển để gây khó khăn cho việc phân tích tĩnh:

1. **Phép biến đổi trong Case 3 và Case 12:**
   ```assembly
   and    al, BYTE PTR [rsp+rdx*1+0x20] ; al = K & x
   add    eax, eax                     ; eax = 2 * (K & x)
   add    sil, BYTE PTR [rsp+rdx*1+0x20] ; sil = K + x
   sub    esi, eax                     ; esi = (K + x) - 2 * (K & x)
   ```
   Theo định lý bù nhị phân:
   $$(A + B) = (A \oplus B) + 2(A \ \& \ B) \iff A \oplus B = (A + B) - 2(A \ \& \ B)$$
   $\rightarrow$ **Thực chất đây là phép XOR:** $x_i = x_i \oplus KEY_i$.

2. **Phép biến đổi trong Case 8 và Case 9:**
   ```assembly
   and    sil, BYTE PTR [rsp+rdx*1+0x20] ; sil = T & x
   xor    al, BYTE PTR [rsp+rdx*1+0x20]  ; al = T ^ x
   lea    eax, [rax+rsi*2]               ; eax = (T ^ x) + 2 * (T & x)
   ```
   Tương tự:
   $$(A \oplus B) + 2(A \ \& \ B) = (A + B) \pmod{256}$$
   $\rightarrow$ **Thực chất đây là phép cộng:** $x_i = (x_i + TRL_i) \pmod{256}$.

3. **Phép nhân trong Case 14 và Case 15:**
   ```assembly
   mul    BYTE PTR [rdx+...]            ; ax = al * MUL[rdx]
   mov    BYTE PTR [rsp+rdx*1+0x20], al ; Lấy byte thấp
   ```
   $\rightarrow$ **Phép nhân modulo 256:** $x_i = (x_i \times MUL_i) \pmod{256}$.
   Mọi phần tử trong `MUL0` và `MUL1` đều là số lẻ:
   $$\gcd(MUL_i, 256) = 1 \implies \exists MUL_i^{-1} \pmod{256}$$

4. **Phép hoán vị trong Case 6 và Case 1:**
   ```assembly
   movzx  ecx, BYTE PTR [rax + PERM]    ; Index đích
   movzx  esi, BYTE PTR [rsp + rax + ...] ; Giá trị byte nguồn
   mov    BYTE PTR [rsp + rcx + ...], sil ; temp[PERM[i]] = x[i]
   ```

---

### Bước 4: Xây dựng thuật toán giải mã ngược (Inversion Algorithm)

Vì toàn bộ các bước mã hóa đều có ánh xạ $1-1$ (nghịch đảo duy nhất), ta chỉ cần đi ngược từ đích `TGT` về đầu vào:

```text
Target (TGT)
     │
     ▼  [Đảo ngược Vòng 1]
1. Hoán vị ngược PERM1:   prev[i] = curr[PERM1[i]]
2. Nhân nghịch đảo MUL1:   prev[i] = (curr[i] * pow(MUL1[i], -1, 256)) mod 256
3. Trừ ngược TRL1:         prev[i] = (curr[i] - TRL1[i]) mod 256
4. XOR ngược KEY1:         prev[i] = curr[i] ^ KEY1[i]
     │
     ▼  [Đảo ngược Vòng 0]
5. Hoán vị ngược PERM0:   prev[i] = curr[PERM0[i]]
6. Nhân nghịch đảo MUL0:   prev[i] = (curr[i] * pow(MUL0[i], -1, 256)) mod 256
7. Trừ ngược TRL0:         prev[i] = (curr[i] - TRL0[i]) mod 256
8. XOR ngược KEY0:         prev[i] = curr[i] ^ KEY0[i]
     │
     ▼
Mã kích hoạt ban đầu (Activation Code)
```

Kiểm chứng bằng Z3 SMT Solver chứng minh rằng nghiệm thu được là **duy nhất tuyệt đối trên toàn không gian $2^{128}$ giá trị**.

Kết quả tính toán:
- Chuỗi byte thô: `b'pocL38BO(R3shuLT'`
- Dạng ASCII: `pocL38BO(R3shuLT`
- Dạng HEX: `706f634c3338424f2852337368754c54`

---

## 3. Mã khai thác hoàn chỉnh (`solve_re10.py`)

File script hoàn chỉnh được lưu tại [solvers/solve_re10.py](file:///c:/Users/ACER/Downloads/ctf/ddcriel/solvers/solve_re10.py):

```python
#!/usr/bin/env python3
"""
Solver for REVERSE CHALLENGE 10 (SentryMark Activation Gate v2.0)
Target: https://f8e0441a-e392-4c0d-a640-ed6c8f7d8002.172.31.102.101.nip.io
"""
import requests
import urllib3
import struct
import sys
import os

urllib3.disable_warnings()

BASE_URL = 'https://f8e0441a-e392-4c0d-a640-ed6c8f7d8002.172.31.102.101.nip.io'

def solve(base_url=BASE_URL):
    base_url = base_url.rstrip('/')
    print(f"[*] Target URL: {base_url}")

    # 1. Tải binary sentrymark từ máy chủ nếu chưa có sẵn
    binary_path = 'sentrymark'
    if not os.path.exists(binary_path) or os.path.getsize(binary_path) == 0:
        print("[*] Downloading binary sentrymark...")
        r = requests.get(f"{base_url}/sentrymark", verify=False, timeout=10)
        with open(binary_path, 'wb') as f:
            f.write(r.content)

    # 2. Trích xuất các mảng hằng số (Blobs) từ file ELF
    with open(binary_path, 'rb') as f:
        elf_data = f.read()

    e_phoff = struct.unpack_from('<Q', elf_data, 32)[0]
    e_phnum = struct.unpack_from('<H', elf_data, 56)[0]
    e_phentsize = struct.unpack_from('<H', elf_data, 54)[0]

    segments = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('<IIQQQQQQ', elf_data, off)
        segments.append((p_vaddr, p_memsz, p_offset, p_filesz))

    def vaddr_to_offset(vaddr):
        for seg_vaddr, seg_memsz, seg_offset, seg_filesz in segments:
            if seg_vaddr <= vaddr < seg_vaddr + seg_memsz:
                return seg_offset + (vaddr - seg_vaddr)
        return None

    def get_blob(addr):
        off = vaddr_to_offset(addr + 16)
        return list(elf_data[off:off+16])

    TGT   = get_blob(0x404050)
    PERM1 = get_blob(0x404070)
    MUL1  = get_blob(0x404090)
    TRL1  = get_blob(0x4040b0)
    KEY1  = get_blob(0x4040d0)
    PERM0 = get_blob(0x4040f0)
    MUL0  = get_blob(0x404110)
    TRL0  = get_blob(0x404130)
    KEY0  = get_blob(0x404150)

    print("[*] Blobs extracted successfully.")

    # 3. Đảo ngược mạng SPN 2 vòng từ TGT
    # Vòng 1
    s = TGT[:]
    prev = [0] * 16
    for i in range(16):
        prev[i] = s[PERM1[i]]
    s = prev[:]

    MUL1_INV = [pow(m, -1, 256) for m in MUL1]
    s = [(s[i] * MUL1_INV[i]) & 0xff for i in range(16)]
    s = [(s[i] - TRL1[i]) & 0xff for i in range(16)]
    s = [s[i] ^ KEY1[i] for i in range(16)]

    # Vòng 0
    prev = [0] * 16
    for i in range(16):
        prev[i] = s[PERM0[i]]
    s = prev[:]

    MUL0_INV = [pow(m, -1, 256) for m in MUL0]
    s = [(s[i] * MUL0_INV[i]) & 0xff for i in range(16)]
    s = [(s[i] - TRL0[i]) & 0xff for i in range(16)]
    s = [s[i] ^ KEY0[i] for i in range(16)]

    activation_bytes = bytes(s)
    hex_code = activation_bytes.hex()
    ascii_code = activation_bytes.decode('utf-8', errors='replace')

    print(f"[+] Activation Code (ASCII): {ascii_code}")
    print(f"[+] Activation Code (HEX):   {hex_code}")

    # 4. Gửi mã hex tới endpoint POST /activate
    print("[*] Submitting hex code to /activate...")
    resp = requests.post(f"{base_url}/activate", json={"code": hex_code}, verify=False, timeout=10)
    data = resp.json()
    print(f"[*] Server Response: {data}")

    flag = data.get("flag")
    if flag:
        print(f"\n[+] SUCCESS! FLAG: {flag}\n")
        return flag
    else:
        print("[-] Activation failed.")
        return None

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    solve(url)
```

---

## 4. Kết quả thực thi thực tế

Chạy solver trực tiếp trên hệ thống:

```bash
$ python solvers/solve_re10.py
[*] Target URL: https://f8e0441a-e392-4c0d-a640-ed6c8f7d8002.172.31.102.101.nip.io
[*] Blobs extracted successfully.
[+] Activation Code (ASCII): pocL38BO(R3shuLT
[+] Activation Code (HEX):   706f634c3338424f2852337368754c54
[*] Submitting hex code to /activate...
[*] Server Response: {'activated': True, 'flag': 'flag{c2f7fb33-e0e9-40ca-8825-0fdf504e1495}'}

[+] SUCCESS! FLAG: flag{c2f7fb33-e0e9-40ca-8825-0fdf504e1495}
```

Flag:
```text
flag{c2f7fb33-e0e9-40ca-8825-0fdf504e1495}
```
