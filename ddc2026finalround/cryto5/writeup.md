# Writeup: CRYPTO CHALLENGE 5 - Three Partners Bounty

**Challenge Name:** CRYPTO CHALLENGE 5  
**Category:** Cryptography / RSA Hastad's Broadcast Attack  
**Flag:** `flag{f1072f49-fd74-440f-89d2-aea2732bd484}`

---

## 1. Phân tích tổng quan (Overview)

Đề bài đưa ra mô tả:  
> *"The KMS Announces the Bounty to Three Partners, and Only Encrypts It Three Times."*

Ứng dụng web **Trikey KMS** thực hiện mã hóa cùng một thông điệp bí mật $m$ (Bounty/Flag) bằng thuật toán **RSA** dùng số mũ mã hóa nhỏ cố định $e = 3$ và gửi tới **3 đối tác** khác nhau (**HUTECH**, **DN-University**, **FPT-University**) sở hữu 3 khóa công khai ($N_1, N_2, N_3$).

Mục tiêu: Khôi phục thông điệp gốc $m$ (Flag) từ 3 bản mã $c_1, c_2, c_3$ thu thập được từ hệ thống.

---

## 2. Phân tích chi tiết (Cryptography Analysis)

### A. Mô hình mã hóa RSA (RSA Encryption)
Thông điệp $m$ được mã hóa cho 3 người nhận khác nhau với các cặp khóa $(N_1, e=3), (N_2, e=3), (N_3, e=3)$ thu được 3 bản mã tương ứng:
$$c_1 \equiv m^3 \pmod{N_1}$$
$$c_2 \equiv m^3 \pmod{N_2}$$
$$c_3 \equiv m^3 \pmod{N_3}$$

Trong đó, các số modulo $N_1, N_2, N_3$ nguyên tố cùng nhau từng cặp ($\gcd(N_i, N_j) = 1$).

### B. Tấn công Hastad's Broadcast Attack
Sử dụng **Định lý Số dư Trung Hoa (Chinese Remainder Theorem - CRT)**, ta có thể tìm được một số $C$ duy nhất trong khoảng $[0, N_1 N_2 N_3 - 1]$ thỏa mãn hệ phương trình đồng dư:
$$C \equiv m^3 \pmod{N_1 N_2 N_3}$$

Công thức tính $C$:
$$C = \left( \sum_{i=1}^{3} c_i \cdot M_i \cdot (M_i^{-1} \pmod{N_i}) \right) \pmod{N_1 N_2 N_3}$$
Trong đó:
$$N = N_1 \cdot N_2 \cdot N_3, \quad M_i = \frac{N}{N_i}$$

Do thông điệp $m < N_i$, ta có $m^3 < N_1 \cdot N_2 \cdot N_3$.  
Điều này đồng nghĩa phép chia lấy dư modulo $N_1 N_2 N_3$ chưa bị tràn (no modular wrap-around):
$$C = m^3 \quad (\text{trên tập số nguyên } \mathbb{Z})$$

Do đó, ta chỉ cần lấy căn bậc 3 của $C$ trên tập số nguyên để khôi phục trực tiếp $m$:
$$m = \sqrt[3]{C}$$

---

## 3. Exploit Script (Python)

```python
import urllib.request
import ssl
import re

def integer_cube_root(n):
    """Tính căn bậc 3 chính xác trên tập số nguyên bằng Binary Search"""
    low, high = 0, n
    while low <= high:
        mid = (low + high) // 2
        mid3 = mid ** 3
        if mid3 == n:
            return mid
        elif mid3 < n:
            low = mid + 1
        else:
            high = mid - 1
    return high

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    return gcd, y1 - (b // a) * x1, x1

def modinv(a, m):
    gcd, x, _ = extended_gcd(a, m)
    return (x % m + m) % m

def solve():
    base = 'https://a79bb194-6b7b-4c90-bd94-d413243d759f.172.31.102.101.nip.io'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    N_list, C_list = [], []
    for i in range(3):
        url = f'{base}/broadcasts/{i}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            hexs = re.findall(r'0x[0-9a-fA-F]{100,}', html)
            C_list.append(int(hexs[0], 16))
            N_list.append(int(hexs[1], 16))

    n1, n2, n3 = N_list[0], N_list[1], N_list[2]
    c1, c2, c3 = C_list[0], C_list[1], C_list[2]

    # CRT calculation
    N = n1 * n2 * n3
    N1, N2, N3 = N // n1, N // n2, N // n3

    u1 = modinv(N1, n1)
    u2 = modinv(N2, n2)
    u3 = modinv(N3, n3)

    C = (c1 * N1 * u1 + c2 * N2 * u2 + c3 * N3 * u3) % N

    # Exact cube root
    m = integer_cube_root(C)

    flag_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
    flag_str = flag_bytes.decode('utf-8', errors='replace')

    print(f"Full Decrypted Plaintext: {flag_str}")
    clean_flag = re.search(r'flag\{[^}]+\}', flag_str)
    if clean_flag:
        print(f"FLAG: {clean_flag.group(0)}")

if __name__ == "__main__":
    solve()
```

---

## 4. Kết quả (Result)

```text
Full Decrypted Plaintext: flag{f1072f49-fd74-440f-89d2-aea2732bd484}|-broadcast-KMS-1.0|4ebf6d07c2db83b8add5447e9e33a7e773
FLAG: flag{f1072f49-fd74-440f-89d2-aea2732bd484}
```
