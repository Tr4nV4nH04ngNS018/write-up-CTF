# 🔓 Write-up: Keyfile Authentication (Reverse Engineering)

> **Challenge Name:** `keyfile_auth`  
> **Category:** Reverse Engineering  
> **Flag:** `FLAG{f1l3_p4rs1ng_m4st3ry}`

---

## 📋 Tổng quan

Bài này là một thử thách Reverse Engineering dạng kiểm tra file bản quyền (`license.key`). Nhiệm vụ của chúng ta là phân tích tập tin thực thi `keyfile_auth` để tìm ra cấu trúc định dạng chuẩn của file `license.key` được chương trình kiểm tra, từ đó sinh ra file key hợp lệ để lấy flag.

---

## 🔍 Bước 1: Trinh sát (Static Analysis)

Đầu tiên, kiểm tra định dạng file thực thi:
```bash
file keyfile_auth
```
**Kết quả:**
Đây là một file ELF 64-bit cho hệ điều hành Linux (x86_64).

Tiếp tục sử dụng lệnh `strings` để quét các chuỗi ký tự hiển thị được trong binary:
```bash
strings keyfile_auth
```
**Các chuỗi đáng chú ý:**
```text
Verifying license.key...
license.key
Error: Could not open license.key.
Error: Invalid keyfile size.
Auth failure: Invalid magic.
Auth failure: Insufficient privileges.
Auth failure: Invalid master key.
admin
Auth failure: Unknown user.
Access Granted. FLAG{f1l3_p4rs1ng_m4st3ry}
```
→ Dựa vào các chuỗi này, ta biết chương trình sẽ lần lượt kiểm tra:
1. Sự tồn tại của file `license.key`.
2. Kích thước của file.
3. Magic bytes.
4. Quyền hạn (privileges).
5. Mã khóa chính (master key).
6. Tên người dùng (username), khả năng cao là `"admin"`.

---

## 🧠 Bước 2: Dịch ngược mã nguồn (Reverse Engineering)

Sử dụng IDA Pro hoặc `objdump -d -M intel keyfile_auth` để xem mã máy phân rã. Đoạn mã kiểm tra trong hàm `main` diễn ra như sau:

### 2.1. Đọc file và kiểm tra kích thước
```assembly
1262:    mov    edx,0x20
1267:    mov    esi,0x1
126c:    mov    rdi,rax
126f:    call   10c0 <fread@plt>
1274:    cmp    rax,0x20
1278:    je     129f
```
→ Chương trình đọc tối đa `0x20` (32 bytes) từ `license.key` bằng `fread`. Sau đó so sánh số byte đọc được (`rax`) với `0x20`.
* **Yêu cầu 1**: Kích thước của `license.key` phải đúng **32 bytes**.

### 2.2. Kiểm tra Magic Bytes (Offset 0)
```assembly
12ab:    mov    eax,DWORD PTR [rbp-0x30]
12ae:    cmp    eax,0xdeadc0de
12b3:    je     12ce
```
→ Chương trình so sánh 4 bytes đầu tiên (`rbp-0x30`) với giá trị `0xdeadc0de`.
* **Yêu cầu 2**: 4 bytes đầu tiên phải là `0xdeadc0de`. Do kiến trúc Little Endian của x86_64, các byte này trong file sẽ ghi theo thứ tự: `de c0 ad de`.

### 2.3. Kiểm tra Quyền Hạn - Privilege (Offset 4)
```assembly
12ce:    movzx  eax,BYTE PTR [rbp-0x2c]
12d2:    cmp    al,0xff
12d4:    je     12ec
```
* **Yêu cầu 3**: Byte thứ 5 (offset 4) tại địa chỉ `rbp-0x2c` phải có giá trị `0xff`.

### 2.4. Kiểm tra Master Key (Offset 8)
```assembly
12ec:    mov    rdx,QWORD PTR [rbp-0x28]
12f0:    movabs rax,0x1337beefcafebabe
12fa:    cmp    rdx,rax
```
* **Yêu cầu 4**: 8 bytes (QWORD) tại offset 8 (`rbp-0x28`) phải bằng `0x1337beefcafebabe` (dạng Little Endian trong file: `be ba fe ca ef be 37 13`).

### 2.5. Kiểm tra Tên Người Dùng - Username (Offset 16)
```assembly
1315:    lea    rax,[rbp-0x30]
1319:    add    rax,0x10
131d:    mov    edx,0x5
1322:    lea    rcx,[rip+0xdb1]        # Trỏ tới chuỗi "admin"
132c:    mov    rdi,rax
132f:    call   10a0 <strncmp@plt>
```
* **Yêu cầu 5**: 5 bytes tính từ offset 16 (`rbp-0x30 + 0x10`) phải trùng khớp với chuỗi `"admin"`.

---

## 🛠️ Bước 3: Thiết kế cấu trúc file `license.key`

Để thỏa mãn toàn bộ các điều kiện trên, ta thiết kế file `license.key` có cấu trúc 32 bytes như sau:

| Offset | Kích thước | Giá trị Hex (Little Endian) | Mô tả |
|---|---|---|---|
| `0x00` | 4 bytes | `de c0 ad de` | Magic Bytes (`0xdeadc0de`) |
| `0x04` | 1 byte | `ff` | Privilege Level |
| `0x05 - 0x07` | 3 bytes | `00 00 00` | Padding (Đệm để trường tiếp theo bắt đầu đúng offset 8) |
| `0x08` | 8 bytes | `be ba fe ca ef be 37 13` | Master Key (`0x1337beefcafebabe`) |
| `0x10` | 5 bytes | `61 64 6d 69 6e` | Username `"admin"` |
| `0x15` | 11 bytes | `00 00 ... 00` | Padding thêm cho đủ tổng cộng 32 bytes |

---

## 💻 Bước 4: Tạo Script Python sinh Keyfile

Ta sử dụng thư viện `struct` của Python để đóng gói các trường dữ liệu theo đúng định dạng nhị phân Little Endian:

```python
import struct

# Khởi tạo các trường
magic = struct.pack('<I', 0xdeadc0de)         # 4 bytes
privilege = b'\xff'                           # 1 byte
padding1 = b'\x00\x00\x00'                    # 3 bytes
master_key = struct.pack('<Q', 0x1337beefcafebabe) # 8 bytes
username = b'admin'                           # 5 bytes
padding2 = b'\x00' * 11                       # 11 bytes

# Gộp dữ liệu thành payload 32 bytes
payload = magic + privilege + padding1 + master_key + username + padding2

# Lưu thành file license.key
with open('license.key', 'wb') as f:
    f.write(payload)

print("[+] license.key generated successfully!")
```

Chạy script trên sẽ thu được file `license.key` hợp lệ.

---

## 🏁 Flag

Đặt file `license.key` cùng thư mục với `keyfile_auth` và chạy chương trình trên môi trường Linux/WSL:
```bash
./keyfile_auth
```

**Output:**
```
Verifying license.key...
Access Granted. FLAG{f1l3_p4rs1ng_m4st3ry}
```

**Flag:**
```
FLAG{f1l3_p4rs1ng_m4st3ry}
```

---

## 🧠 Kiến thức rút ra

### Logic xác thực của chương trình

```
      [license.key] (32 bytes)
            │
            ├── Check Size (== 32 bytes) ── [FAIL] ──> "Error: Invalid keyfile size."
            │
            ├── Check Magic (== 0xdeadc0de) ── [FAIL] ──> "Auth failure: Invalid magic."
            │
            ├── Check Privilege (== 0xff) ── [FAIL] ──> "Auth failure: Insufficient privileges."
            │
            ├── Check Master Key (== 0x1337beefcafebabe) ── [FAIL] ──> "Auth failure: Invalid master key."
            │
            └── Check User (== "admin") ── [FAIL] ──> "Auth failure: Unknown user."
            │
            └── [SUCCESS] ──> Access Granted (FLAG!)
```

### Các điểm cần lưu ý khi làm bài RE dạng Keyfile
1. **Kiến trúc Endianness**: Trên x86/x64, các dữ liệu kiểu số nguyên lớn (`int`, `long`, `long long`) được lưu trữ ngược thứ tự byte (Little Endian). Cần chú ý điều này khi ghi đè hoặc đọc bộ nhớ.
2. **Căn lề bộ nhớ (Struct Alignment)**: Do cơ chế alignment của compiler, các biến lớn như QWORD (8 bytes) thường được đặt ở các offset chia hết cho 8. Do đó, cần có padding thích hợp (như `padding1` 3 bytes sau trường privilege 1 byte) để các trường tiếp theo căn đúng vị trí mà chương trình kiểm tra.

---

*Written on 2026-07-10*
