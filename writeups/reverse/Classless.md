# Writeup — Classless (Misc / RE)

> **V1t CTF 2026** · Category: Misc + Reverse Engineering · ELF Virtual Machine
>
> **Flag:** `v1t{trilingual_vtable_babel_6f01a2c9}`

---

## 1. Tóm tắt (TL;DR)
Thử thách cung cấp một binary ELF `objectvm` và một số file sample `.bbl` (chứa định dạng JSON nén zlib + base64 mô tả các class, objects và vtable). 
Bằng cách dịch ngược hoặc trích xuất chuỗi (strings) từ binary `objectvm`, ta phát hiện ra các chuỗi trong chương trình đã bị ẩn bằng cách mã hóa XOR với key `0x5A` (cho các chuỗi thông báo lỗi/tên thuộc tính) và key `0x37` (cho flag). Giải mã chuỗi chứa flag tại offset `79010` với key `0x37` sẽ trực tiếp ra nội dung flag.

---

## 2. Các file được cung cấp

| File | Vai trò |
|---|---|
| `objectvm` | File thực thi ELF 64-bit đóng vai trò là Virtual Machine để chạy các file `.bbl` |
| `classless.zip` | Archive chứa file thực thi và thư mục `samples/` |
| `samples/*.bbl` | Các ví dụ chứa mã nguồn trung gian đã được biên dịch dưới dạng JSON nén |

---

## 3. Phân tích định dạng `.bbl`
Khi giải mã Base64 và giải nén zlib các file mẫu trong thư mục `samples/`, ta thu được cấu trúc JSON mô tả OOP:
```json
{
  "classes": [
    {
      "name": "Hello",
      "dialect": "CPP",
      "parents": [],
      "interfaces": [],
      "final": false,
      "methods": [
        {
          "name": "hello",
          "slot": 0,
          "visibility": "public",
          "body": "print_hello"
        }
      ]
    }
  ],
  "objects": [
    {
      "id": 1,
      "declared_class": "Hello",
      "runtime_class": "Hello",
      "fields": {
        "__task__": "hello"
      },
      "vtable": [...]
    }
  ],
  "entry": 1
}
```

---

## 4. Phân tích Binary & Tìm Flag

Tiến hành dump toàn bộ chuỗi ký tự printable từ binary `objectvm`, ta phát hiện ra các chuỗi lạ ở phần cuối danh sách:
* `CLCE^[^YPBV[hACVU[RhUVUR[h`
* `/36.34` -> XOR với `0x5A` ra `uiltin`
* `6;))` -> XOR với `0x5A` ra `lass`
* `80?9.` -> XOR với `0x5A` ra `bject`
* `96;))` -> XOR với `0x5A` ra `class`

Các từ khoá liên quan đến OOP đều bị mã hoá XOR với key `0x5A`. Thử nghiệm bruteforce key XOR đối với chuỗi dài `CLCE^[^YPBV[hACVU[RhUVUR[h`, ta tìm được key **`0x37`** (thập phân: `55`) giải mã ra:
```
t{trilingual_vtable_babel_
```

Đọc trực tiếp các byte tiếp theo tại vị trí chứa chuỗi này trong binary (offset `79010`):
```python
# Raw bytes
b'CLCE^[^YPBV[hACVU[RhUVUR[h\x01Q\x07\x06V\x05T\x0eJ'
```
Giải mã toàn bộ bằng key `0x37`:
* `\x01 ^ 0x37 = 6`
* `Q ^ 0x37 = f`
* `\x07 ^ 0x37 = 0`
* `\x06 ^ 0x37 = 1`
* `V ^ 0x37 = a`
* `\x05 ^ 0x37 = 2`
* `T ^ 0x37 = c`
* `\x0e ^ 0x37 = 9`
* `J ^ 0x37 = }`

Kết hợp lại ta được chuỗi hoàn chỉnh: `t{trilingual_vtable_babel_6f01a2c9}`.

---

## 5. Script giải (Python)

```python
with open('objectvm', 'rb') as f:
    data = f.read()

# Tìm offset của chuỗi mã hóa
pattern = b'CLCE^[^YPBV[hACVU[RhUVUR[h'
pos = data.find(pattern)

if pos != -1:
    # Đọc đủ độ dài của chuỗi mã hóa flag (35 byte)
    encrypted_flag = data[pos:pos+35]
    
    # Giải mã bằng key 0x37
    decrypted = "".join(chr(b ^ 0x37) for b in encrypted_flag)
    
    # Định dạng flag chuẩn bắt đầu bằng v1
    flag = "v1" + decrypted
    print("Flag:", flag)
else:
    print("Pattern missing from binary.")
```

---

## 6. Flag
```
v1t{trilingual_vtable_babel_6f01a2c9}
```
