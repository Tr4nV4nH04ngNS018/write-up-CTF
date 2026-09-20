# Writeup: REVERSE CHALLENGE 8 (Chronon eval-harness)

> **Event:** DDC CTF  
> **Category:** Reverse Engineering  
> **Difficulty:** Medium  
> **Points:** 195  
> **Description:** *"The Partner Harness Documents Its Own Shuffle in a Comment You Are Encouraged to Read."*  
> **Flag:** `flag{e3bca87c-96a8-4d9d-8f81-5f7c39770d47}`

---

## 1. Tóm tắt (TL;DR)

1. Tải bundle `aimodel_eval.zip` chứa 2 file: `aimodel_eval.py` (wrapper) + `aimodel_eval.pyc` (bytecode đã shuffle).
2. File `.py` ghi rõ cách unshuffle trong comment: *"every consecutive pair of bytes swapped"* — hoán đổi từng cặp byte liền kề.
3. Unshuffle bytecode rồi dùng `marshal.loads()` để load code object.
4. Tìm hàm `compute_flag`, trích xuất các hằng số: XOR key = `55`, blob mã hóa chứa flag.
5. XOR mỗi byte của blob với `55` → flag trực tiếp, không cần tìm partner key:
   `flag{e3bca87c-96a8-4d9d-8f81-5f7c39770d47}`

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ

Truy cập URL, ta thấy trang **Chronon — Eval harness 0.7**:
- Runtime: CPython 3.11
- Format: pyc (shuffled)
- Download: `aimodel_eval.zip`
- Cách dùng: `python3 -m aimodel_eval --check <partner-key>`

### Bước 2: Đọc source wrapper

File `aimodel_eval.py` chứa comment rất quan trọng (đúng như hint: *"Documents Its Own Shuffle in a Comment"*):

```python
"""
Un-shuffle policy (v0.7):
    The marshal body of aimodel_eval.pyc has every consecutive pair
    of bytes swapped at packaging time.  Un-shuffle by swapping the
    same pairs back before invoking marshal.loads.
"""
```

Hàm unshuffle đơn giản:
```python
def _unshuffle(body: bytes) -> bytes:
    b = bytearray(body)
    for i in range(0, len(b), 2):
        b[i], b[i + 1] = b[i + 1], b[i]
    return bytes(b)
```

### Bước 3: Unshuffle và phân tích bytecode

Áp dụng unshuffle rồi dùng `marshal.loads()` để load code object:

```python
with open("aimodel_eval.pyc", "rb") as f:
    header = f.read(16)       # skip pyc header (16 bytes for Python 3.11)
    shuffled_body = f.read()

b = bytearray(shuffled_body)
for i in range(0, len(b), 2):
    b[i], b[i+1] = b[i+1], b[i]

code = marshal.loads(bytes(b))
```

Trong `code.co_consts` tìm thấy code object `compute_flag`. Kiểm tra các hằng số:

| Index | Giá trị | Ý nghĩa |
|-------|---------|---------|
| 0 | `None` | — |
| 1 | `'chronon-eval-v0.7'` | Salt cho SHA256 |
| 2 | `'9901f639...c902f7'` | SHA256 target hash |
| 3 | `'denied'` | Chuỗi trả về khi sai key |
| 4 | `55` | **XOR key** |
| 5 | `b'Q[VPLR\x04UTV...'` | **Flag blob đã mã hóa XOR** |
| 6 | `0` | Giá trị khởi tạo |

### Bước 4: Giải mã flag

Logic hàm `compute_flag(key_input)`:
1. Tính `h = sha256(key_input + salt).hexdigest()`
2. So sánh `h == target` → nếu sai trả về `"denied"`
3. Nếu đúng, XOR mỗi byte của `blob` với `55`, bỏ null bytes → trả về flag

**Không cần tìm partner key!** Ta có sẵn blob và XOR key, chỉ cần giải mã trực tiếp:

```python
xor_key = 55
blob = b'Q[VPLR\x04UTV\x0f\x00T\x1a\x0e\x01V\x0f\x1a\x03S\x0eS\x1a\x0fQ\x0f\x06\x1a\x02Q\x00T\x04\x0e\x00\x00\x07S\x03\x00J...'

flag = bytes(byte ^ xor_key for byte in blob).split(b'\x00')[0].decode()
# flag = "flag{e3bca87c-96a8-4d9d-8f81-5f7c39770d47}"
```

Xác minh XOR:
```
'Q' (0x51) ^ 55 (0x37) = 0x66 = 'f'
'[' (0x5B) ^ 55 (0x37) = 0x6C = 'l'
'V' (0x56) ^ 55 (0x37) = 0x61 = 'a'
'P' (0x50) ^ 55 (0x37) = 0x67 = 'g'
'L' (0x4C) ^ 55 (0x37) = 0x7B = '{'
```

→ `flag{e3bca87c-96a8-4d9d-8f81-5f7c39770d47}`

---

## 3. Script giải tự động ([solve_re8.py](file:///c:/Users/ACER/Downloads/ctf/ddcriel/solve_re8.py))

```bash
python solve_re8.py
```
Output:
```
[+] XOR key: 55
[+] FLAG: flag{e3bca87c-96a8-4d9d-8f81-5f7c39770d47}
```
