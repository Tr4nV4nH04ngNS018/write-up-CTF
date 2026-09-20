# Writeup: CRYPTO CHALLENGE 3 (VinAI Sessions)

> **Event:** DDC CTF  
> **Category:** Crypto  
> **Difficulty:** Medium  
> **Points:** ~100  
> **Description:** *VinAI Sessions is the internal auth service. Cookies are minted with AES-CBC-PKCS7 and validated on the API. Ciphertext is public; plaintext is not. You have the oracle.*  
> **Flag:** `flag{6d2dd554-c004-44cd-ab31-fdeddd7d9d4a}`

---

## 1. Tóm tắt (TL;DR)

1. Thử thách cung cấp dịch vụ web **VinAI Sessions — Auth v2**. Cookie xác thực phiên làm việc được mã hóa bằng thuật toán đối xứng:
   - **Mode:** AES-CBC-128 với PKCS#7 padding.
   - **Format:** `IV (16 bytes) || Ciphertext`.
2. Endpoint `POST /api/login` đóng vai trò là một **Padding Oracle**:
   - HTTP **400** `{"error":"invalid padding"}`: Padding PKCS#7 sai.
   - HTTP **401** `{"error":"invalid credentials"}`: Padding hợp lệ nhưng thông tin session không hợp lệ.
   - HTTP **200** `{"authorized":true,...}`: Session hợp lệ.
3. Trang web tiết lộ ciphertext của Admin cookie tại `GET /api/admin/cookie`:
   - Ghi chú: *"encrypted with the session key; you have the oracle."*
4. Thực hiện tấn công **Padding Oracle Attack** để giải mã toàn bộ ciphertext của Admin cookie mà không cần biết khóa AES secret key.
5. Để vượt qua cơ chế rate limiting (HTTP 503 từ nginx) và tối ưu thời gian giải, thuật toán được cải tiến bằng **Plaintext Character Priority** (thử theo phân phối tần suất các ký tự JSON/ASCII thay vì brute-force tuyến tính 0..255), giảm số lượng request từ ~128 reqs/byte xuống còn ~25 reqs/byte.
6. Toàn bộ nội dung plaintext sau khi giải mã:
   ```json
   {"user":"audit-service","role":"flag{6d2dd554-c004-44cd-ab31-fdeddd7d9d4a}","exp":4102444800}
   ```
   Flag nằm ngay tại trường `role`: `flag{6d2dd554-c004-44cd-ab31-fdeddd7d9d4a}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ
- Dịch vụ cung cấp thông tin tại `GET /api/whoami`:
  ```json
  {
    "cookie_format": "iv(16) || AES-CBC-PKCS7(session-json)",
    "note": "cookies decrypt to JSON with fields 'user', 'role', 'exp'",
    "service": "VinAI Sessions",
    "you_are": "guest",
    "your_cookie": "b3602815874491dc3f5f88568a3a1ea9..."
  }
  ```
- Endpoint lấy Admin ciphertext `GET /api/admin/cookie`:
  ```json
  {
    "cookie": "e99413ec044e62f868111a0d2e110d07cb4b498260ef33b98a76b13727ab4de946d3e8794c238627e0f946243cfacd7a5f5294eaa2eb8ef7ccb86e7dfd6c1bbb3db5575ff9f017b73f30be1f2a6e0d6404a59573eec2db1aee73ebe0238f39560018febbebea5c0a8d32de60d71903ab",
    "note": "encrypted with the session key; you have the oracle.",
    "role": "admin"
  }
  ```
  Ciphertext dài 112 bytes = 1 block IV (16 bytes) + 6 block Ciphertext (96 bytes).

- Endpoint xác thực `POST /api/login`:
  - Trả về mã HTTP phân biệt rõ ràng giữa lỗi padding và lỗi nội dung:
    - 400: `{"error": "invalid padding"}`
    - 401: `{"error": "invalid credentials"}`

### Bước 2: Nguyên lý tấn công Padding Oracle
Trong chế độ mã hóa AES-CBC:
$$P_i = \text{AES\_Decrypt}(C_i) \oplus C_{i-1}$$

Khi gửi 2 block tới oracle gồm một block giả lập $C'_{prev}$ và block mục tiêu $C_i$:
- Server giải mã $I_i = \text{AES\_Decrypt}(C_i)$.
- Plaintext giả lập nhận được: $P'_i = I_i \oplus C'_{prev}$.
- Server kiểm tra padding PKCS#7 của $P'_i$.

Để giải mã byte tại vị trí $k \in [15, \dots, 0]$:
1. Đặt padding mong muốn là $pad\_val = 16 - k$.
2. Với các byte đã tìm được phía sau ($j > k$), điều chỉnh:
   $$C'_{prev}[j] = I_i[j] \oplus pad\_val$$
3. Duyệt giá trị $guess$ cho byte tại vị trí $k$:
   $$C'_{prev}[k] = guess$$
4. Gửi tới `/api/login`. Nếu server trả về $401$ (hoặc $200$), padding hợp lệ:
   $$I_i[k] = guess \oplus pad\_val$$
5. Plaintext thực tế được tính bằng:
   $$P_i[k] = I_i[k] \oplus C_{i-1}[k]$$

### Bước 3: Tối ưu hóa Plaintext Character Priority
Thông thường, thử tuyến tính $guess \in [0, 255]$ tốn trung bình 128 request cho mỗi byte. Vì plaintext là chuỗi JSON ASCII có thể đọc được, ta có thể tính trực tiếp $guess$ tương ứng với ký tự mong đợi:
$$guess = expected\_char \oplus C_{i-1}[k] \oplus pad\_val$$

Thứ tự ưu tiên ký tự $expected\_char$:
1. Ký tự chữ thường, số, chữ hoa: `a-z`, `0-9`, `A-Z`.
2. Ký tự đặc biệt JSON: `{"}:,-_ `
3. Byte padding PKCS#7: `\x01` .. `\x10`.
4. Các byte còn lại.

Nhờ tối ưu này, mỗi byte chỉ cần trung bình ~25 request để tìm ra kết quả, toàn bộ 80 byte ciphertext được giải mã trong chưa đầy 2 phút.

---

## 3. Kết quả giải mã

Chạy solver [solve_crypto3.py](../solvers/solve_crypto3.py):
```
[*] Target: https://8e7837a9-3a79-412b-88e5-7590ee61466e.172.31.102.101.nip.io
[+] Admin cookie: e99413ec... (112 bytes = 7 blocks)

[*] Decrypting block 1/6... -> b'{"user":"audit-s'
[*] Decrypting block 2/6... -> b'ervice","role":"'
[*] Decrypting block 3/6... -> b'flag{6d2dd554-c0'
[*] Decrypting block 4/6... -> b'04-44cd-ab31-fde'
[*] Decrypting block 5/6... -> b'ddd7d9d4a}","exp'
[*] Decrypting block 6/6... -> b'":4102444800}\x03\x03\x03'

========================================================
[+] Decryption complete in 116.0s (2974 requests)!
[+] Unpadded plaintext: {"user":"audit-service","role":"flag{6d2dd554-c004-44cd-ab31-fdeddd7d9d4a}","exp":4102444800}
========================================================
```

**Flag:** `flag{6d2dd554-c004-44cd-ab31-fdeddd7d9d4a}`

---

## 4. Biện pháp khắc phục (Remediation)
- **Sử dụng AEAD (Authenticated Encryption with Associated Data):** Thay thế AES-CBC bằng AES-GCM hoặc ChaCha20-Poly1305 để đảm bảo tính toàn vẹn dữ liệu trước khi giải mã.
- **Encrypt-then-MAC:** Nếu bắt buộc dùng CBC mode, phải tính HMAC trên bản mã và kiểm tra HMAC trước khi thực hiện giải mã hoặc unpad.
- **Tránh rò rỉ thông tin padding:** Tuyệt đối không trả về thông báo lỗi chi tiết phân biệt giữa "invalid padding" và "invalid credentials".
