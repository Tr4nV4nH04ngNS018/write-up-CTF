# Writeup — Diddy License Checker (Misc / RE)

> **V1t CTF 2026** · Category: Misc + Reverse Engineering · ELF License Checker
>
> **Flag:** `v1t{435_f1b0_w3bs1t3}`

---

## 1. Tóm tắt (TL;DR)
Thử thách cung cấp một file thực thi ELF `diddy` thực hiện kiểm tra 3 thông tin giấy phép:
1. Con vật nuôi đầu tiên: chuỗi kiểm tra độ dài 4 phải khớp với `duck`.
2. Số may mắn (lucky number): chuỗi độ dài 32. Chữ số đầu tiên phải là `0`. Đối với các chữ số thứ $i$ (từ $1$ đến $31$), giá trị số phải khớp với số Fibonacci thứ $i$ chia dư cho 9 ($F(i) \pmod 9$). Chuỗi thu được là `01123584371808876415628101123584`.
3. Tên giấy phép (license name): chuỗi độ dài 31. Dựa trên các ràng buộc về ký tự XOR với mảng tĩnh `arr` trong binary để tạo ra chuỗi hex hợp lệ, ta khôi phục được tên giấy phép là `license-for-user-deadbeef-diddy`.

Khi vượt qua 3 bước này, chương trình gửi request GET tới `http://v1t.site/license-for-user-deadbeef-diddy`. Do máy chủ sử dụng Cloudflare HTTPS redirection, ta truy cập trực tiếp bằng trình duyệt để lấy nội dung là chuỗi hex chứa khóa IV `7631745f3433355f6b33795f66726672` (`v1t_435_k3y_frfr`). Chương trình thực hiện giải mã AES-128-CBC với Key và IV bị hoán đổi (Key lấy từ chuỗi số may mắn, IV lấy từ nội dung trả về của máy chủ) để giải mã flag.

---

## 2. Các file được cung cấp

| File | Vai trò |
|---|---|
| `diddy` | File thực thi ELF 64-bit thực hiện việc kiểm tra license |

---

## 3. Phân tích Binary & Cơ chế kiểm tra

### 3.1. Câu hỏi 1: Con vật nuôi đầu tiên
Hàm `main` đọc input bằng `%63s` và so sánh 4 byte đầu tiên với `duck` (ở dạng số `0x6b637564` dạng Little-Endian) và byte thứ 5 phải là `\x00`.
* **Đáp án:** `duck`

### 3.2. Câu hỏi 2: Số may mắn
Input là chuỗi 32 ký tự. Ký tự đầu tiên phải là `0`.
Với mỗi vị trí $i$ từ $1$ đến $31$, chương trình tính số Fibonacci thứ $i$ và so sánh chữ số nhập vào tại vị trí đó với $F(i) \pmod 9$.
Dãy số được sinh ra như sau:
* $F(1) = 1 \pmod 9 \to 1$
* $F(2) = 1 \pmod 9 \to 1$
* $F(3) = 2 \pmod 9 \to 2$
* $F(4) = 3 \pmod 9 \to 3$
* $F(5) = 5 \pmod 9 \to 5$
* $F(6) = 8 \pmod 9 \to 8$
* $F(7) = 13 \pmod 9 \to 4$
* ...
* **Chuỗi số may mắn:** `01123584371808876415628101123584`

### 3.3. Câu hỏi 3: Tên giấy phép
Chương trình thực hiện XOR mảng tĩnh `arr` gồm 96 phần tử (mỗi phần tử là số nguyên 32-bit nhưng chỉ lấy byte thấp nhất) tuần hoàn với các ký tự của `license_name`.
Kết quả của phép XOR này phải là một chuỗi hex hợp lệ (chỉ chứa các ký tự `0-9`, `a-f`, `A-F`), độ dài 96 ký tự.
Dựa trên ràng buộc này, ta xác định độ dài tên giấy phép là 31 và khôi phục được tên giấy phép là:
* **Tên giấy phép:** `license-for-user-deadbeef-diddy`

---

## 4. Giải mã Flag

Khi gửi yêu cầu GET tới `https://v1t.site/license-for-user-deadbeef-diddy`, máy chủ trả về chuỗi hex 16-byte:
`7631745f3433355f6b33795f66726672` (đại diện cho chuỗi ASCII `v1t_435_k3y_frfr`).

Trong hàm `main` khi gọi hàm giải mã `EVP_DecryptInit_ex`:
* Tham số `key` nhận giá trị từ chuỗi hex lấy từ **máy chủ** (IV nhận được).
* Tham số `iv` nhận giá trị từ chuỗi hex của **số may mắn** (lucky number).

Hai giá trị này được hoán đổi cho nhau:
* **AES Key:** `7631745f3433355f6b33795f66726672` (chuỗi hex từ máy chủ)
* **AES IV:** `01123584371808876415628101123584` (chuỗi số may mắn)

Ciphertext là kết quả sau khi XOR mảng `arr` với `license_name` và chuyển đổi từ hex string sang byte (độ dài 48 byte).
Thực hiện giải mã AES-128-CBC ta thu được chuỗi hex:
`7631747b3433355f663162305f773362733174337d`

Giải mã hex này sang ASCII ta thu được flag:
`v1t{435_f1b0_w3bs1t3}`

---

## 5. Script giải (Python)

```python
from Crypto.Cipher import AES

# Mảng tĩnh arr trích xuất từ binary
arr = [
    85, 15, 2, 1, 89, 21, 81, 25, 80, 13, 69, 24, 68, 18, 0, 66, 75, 85, 87, 5, 84, 84, 82, 86,
    80, 26, 85, 89, 1, 6, 78, 92, 88, 82, 85, 13, 23, 82, 30, 0, 89, 75, 20, 66, 69, 6, 71, 79,
    2, 0, 5, 85, 1, 80, 1, 5, 27, 80, 90, 86, 6, 65, 84, 91, 80, 1, 95, 64, 82, 21, 86, 86,
    70, 75, 20, 69, 85, 22, 30, 80, 82, 5, 93, 0, 81, 1, 7, 30, 87, 80, 93, 0, 27, 89, 94, 83
]

license_name = "license-for-user-deadbeef-diddy"
L = len(license_name)

# Thực hiện xor_bytes
hex_string_bytes = bytearray()
for i in range(len(arr)):
    c = ord(license_name[i % L])
    hex_string_bytes.append(arr[i] ^ c)

ciphertext = bytes.fromhex(hex_string_bytes.decode('ascii'))

# Giải mã AES-128-CBC với Key và IV hoán đổi
key = bytes.fromhex("7631745f3433355f6b33795f66726672") # Từ server
iv = bytes.fromhex("01123584371808876415628101123584")  # Từ lucky number

cipher = AES.new(key, AES.MODE_CBC, iv=iv)
plaintext = cipher.decrypt(ciphertext)

# Lọc bỏ PKCS7 padding và giải mã hex kết quả
flag_hex = plaintext[:-plaintext[-1]].decode('utf-8')
flag = bytes.fromhex(flag_hex).decode('utf-8')
print("Flag:", flag)
```

---

## 6. Flag
```
v1t{435_f1b0_w3bs1t3}
```
