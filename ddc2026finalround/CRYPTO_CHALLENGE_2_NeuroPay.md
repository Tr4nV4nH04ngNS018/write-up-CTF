# Writeup: CRYPTO CHALLENGE 2 (NeuroPay)

> **Event:** DDC CTF  
> **Category:** Crypto  
> **Difficulty:** Easy  
> **Points:** 82  
> **Description:** *"The Gateway's Tokens Are Cryptographically Secure Because Its README Confidently Says So."*  
> **Flag:** `flag{8d0abac8-204a-4f56-928a-0c6d27e5448e}`

---

## 1. Tóm tắt (TL;DR)

1. Thử thách cung cấp dịch vụ web **NeuroPay — AI Inference Credit Gateway v2.7** tại endpoint public.
2. Ứng dụng giới thiệu cơ chế cấp phát token 16 ký tự alnum (bảng chữ cái 62 ký tự) và thông báo rằng:
   - Token người dùng được mint theo yêu cầu: `GET /api/token`.
   - Token Admin được tạo duy nhất một lần khi container khởi động: *"Admin tokens are minted at container startup and used only by the audit tooling."*
   - Dashboard công khai thời điểm container khởi động: `started_at` (unix timestamp) thông qua API `GET /api/stats`.
3. Kiểm tra các token liên tiếp được mint trong cùng 1 giây cho thấy token hoàn toàn trùng lặp. Điều này chỉ ra token được sinh bởi một bộ sinh số giả ngẫu nhiên (PRNG) không an toàn, được seed bằng chính thời gian timestamp hiện tại.
4. Thuật toán sinh token thực chất sử dụng thư viện chuẩn `random` của Python:
   ```python
   random.seed(timestamp)
   token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
   ```
5. Bằng cách lấy `started_at = 1789796794` từ `/api/stats`, ta tái tạo được chính xác Admin token: `ccJRNWhN6BMI2LgN`.
6. Gửi Admin token này tới `POST /api/admin/flag` và nhận về flag:
   `flag{8d0abac8-204a-4f56-928a-0c6d27e5448e}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ
Truy cập web dashboard NeuroPay, ta thu thập được các thông tin:
- API endpoint `GET /api/stats`:
  ```json
  {
    "service": "NeuroPay -- AI Inference Credits",
    "started_at": 1789796794,
    "uptime_s": 1011,
    "version": "2.7.1"
  }
  ```
- Endpoint mint token `GET /api/token`:
  ```json
  {
    "minted_at": 1789797805,
    "note": "1 token = 1 API call. Do not share.",
    "token": "ldOV5yvk9P3h0TGX"
  }
  ```
- Endpoint xác thực Admin `POST /api/admin/flag`:
  ```json
  { "token": "<admin_token>" }
  ```

### Bước 2: Phân tích cơ chế PRNG
Khi mint nhiều token trong cùng 1 giây:
```
ts=1789797829 -> token=uY1TCxLdEV1rJWVA
ts=1789797829 -> token=uY1TCxLdEV1rJWVA
```
Các token sinh ra hoàn toàn giống nhau. Điều này khẳng định server thực hiện `random.seed(int(time.time()))` mỗi khi sinh token.

Thử nghiệm với Python `random.choices` và bảng ký tự 62 chữ cái `string.ascii_letters + string.digits`:
```python
random.seed(1789797834)
''.join(random.choices(string.ascii_letters + string.digits, k=16))
# Kết quả: 'tUeKsNbhjfpV24ek' -> Trùng khớp 100% với token thực tế từ server
```

### Bước 3: Khai thác lấy Flag
Admin token được tạo lúc container khởi động tại `started_at = 1789796794`.
Ta seed PRNG với `1789796794`:
```python
random.seed(1789796794)
admin_token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
# admin_token = 'ccJRNWhN6BMI2LgN'
```

Gửi Admin token tới server:
```bash
curl -k -X POST https://b61025bc-38d9-4ab3-9dd4-16fa4bf3afbe.172.31.102.101.nip.io/api/admin/flag \
  -H "Content-Type: application/json" \
  -d '{"token":"ccJRNWhN6BMI2LgN"}'
```

Kết quả phản hồi:
```json
{
  "authorized": true,
  "flag": "flag{8d0abac8-204a-4f56-928a-0c6d27e5448e}"
}
```

---

## 3. Script giải tự động ([solve_crypto2.py](file:///c:/Users/ACER/Downloads/ctf/ddcriel/solve_crypto2.py))

```bash
python solve_crypto2.py
```
Output:
```text
[*] Querying stats from https://b61025bc-38d9-4ab3-9dd4-16fa4bf3afbe.172.31.102.101.nip.io/api/stats...
[+] Container started_at timestamp: 1789796794
[*] Reconstructing admin token from PRNG seed...
[+] Admin token found: ccJRNWhN6BMI2LgN (seed=1789796794)
[+] FLAG: flag{8d0abac8-204a-4f56-928a-0c6d27e5448e}
```
