# Writeup: CRYPTO CHALLENGE 5 (Three Partners Bounty)

> **Sự kiện:** DDC CTF  
> **Danh mục:** Cryptography / RSA Hastad's Broadcast Attack  
> **Độ khó:** Medium  
> **Mô tả đề bài:** *"The KMS Announces the Bounty to Three Partners, and Only Encrypts It Three Times."*  
> **Mục tiêu (Target):** `https://a79bb194-6b7b-4c90-bd94-d413243d759f.172.31.102.101.nip.io/`  
> **Flag:** `flag{f1072f49-fd74-440f-89d2-aea2732bd484}`

---

## 1. Tóm tắt (TL;DR)

1. Ứng dụng web **Trikey KMS** thực hiện mã hóa cùng một thông điệp bí mật $m$ (Bounty / Flag) bằng thuật toán **RSA** dùng số mũ mã hóa nhỏ cố định $e = 3$.
2. Thông điệp được gửi tới **3 đối tác** khác nhau (**HUTECH**, **DN-University**, **FPT-University**) sở hữu 3 khóa công khai độc lập $(N_1, e=3), (N_2, e=3), (N_3, e=3)$.
3. Kẻ tấn công thu thập được 3 bản mã $c_1, c_2, c_3$ từ các route `/broadcasts/0`, `/broadcasts/1`, `/broadcasts/2`.
4. Áp dụng **Định lý Số dư Trung Hoa (Chinese Remainder Theorem - CRT)** để kết hợp 3 bản mã thành $C \equiv m^3 \pmod{N_1 N_2 N_3}$.
5. Vì $m < N_i$, ta có $m^3 < N_1 N_2 N_3$, nghĩa là phép chia lấy dư modulo chưa bị tràn ($C = m^3$ trên tập số nguyên $\mathbb{Z}$).
6. Chỉ cần khai căn bậc 3 chính xác của $C$ trên tập số nguyên là khôi phục trực tiếp được cờ:
   `flag{f1072f49-fd74-440f-89d2-aea2732bd484}`.

---

## 2. Phân tích chi tiết (Cryptographic Analysis)

### Bước 1: Mô hình mã hóa RSA (RSA Broadcast Model)
Thông điệp $m$ được mã hóa cho 3 người nhận khác nhau với các cặp khóa $(N_1, e=3), (N_2, e=3), (N_3, e=3)$:
$$c_1 \equiv m^3 \pmod{N_1}$$
$$c_2 \equiv m^3 \pmod{N_2}$$
$$c_3 \equiv m^3 \pmod{N_3}$$

Trong đó, các số modulo $N_1, N_2, N_3$ nguyên tố cùng nhau từng cặp ($\gcd(N_i, N_j) = 1$).

### Bước 2: Tấn công Hastad's Broadcast Attack
Sử dụng **Định lý Số dư Trung Hoa (CRT)**, ta tìm được số $C$ duy nhất trong khoảng $[0, N_1 N_2 N_3 - 1]$ thỏa mãn hệ phương trình đồng dư:
$$C \equiv m^3 \pmod{N_1 N_2 N_3}$$

Công thức tính $C$:
$$N = N_1 \cdot N_2 \cdot N_3, \quad M_i = rac{N}{N_i}$$
$$C = \left( \sum_{i=1}^{3} c_i \cdot M_i \cdot (M_i^{-1} \pmod{N_i}) \right) \pmod{N}$$

Do độ dài thông điệp $m$ ngắn hơn các modulus ($m < N_i$), tích $m^3$ nhỏ hơn tích $N_1 N_2 N_3$. Do đó:
$$C = m^3 \quad (	ext{trên tập số nguyên } \mathbb{Z})$$

Ta chỉ cần giải căn bậc 3 số nguyên (integer cube root bằng Binary Search) để thu được $m$:
$$m = \sqrt[3]{C}$$

---

## 3. Mã khai thác hoàn chỉnh (`solve_crypto5.py`)

```python
#!/usr/bin/env python3
"""
DDC CTF - CRYPTO CHALLENGE 5: Three Partners Bounty
Exploit: Hastad's Broadcast Attack on RSA (e=3, 3 moduli, CRT)
"""

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

    print("[*] Đang thu thập các bản mã từ Trikey KMS...")
    N_list, C_list = [], []
    for i in range(3):
        url = f'{base}/broadcasts/{i}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            hexs = re.findall(r'0x[0-9a-fA-F]{100,}', html)
            C_list.append(int(hexs[0], 16))
            N_list.append(int(hexs[1], 16))
            print(f"  [+] Đối tác {i}: N bit-length={N_list[-1].bit_length()}, C bit-length={C_list[-1].bit_length()}")

    n1, n2, n3 = N_list[0], N_list[1], N_list[2]
    c1, c2, c3 = C_list[0], C_list[1], C_list[2]

    # Tính toán Định lý Số dư Trung Hoa (CRT)
    print("[*] Đang áp dụng Định lý Số dư Trung Hoa (CRT)...")
    N = n1 * n2 * n3
    N1, N2, N3 = N // n1, N // n2, N // n3

    u1 = modinv(N1, n1)
    u2 = modinv(N2, n2)
    u3 = modinv(N3, n3)

    C = (c1 * N1 * u1 + c2 * N2 * u2 + c3 * N3 * u3) % N

    # Khai căn bậc 3 chính xác trên tập số nguyên
    print("[*] Đang tính căn bậc 3 nguyên của C...")
    m = integer_cube_root(C)

    flag_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
    flag_str = flag_bytes.decode('utf-8', errors='replace')

    print(f"\n[+] Plaintext giải mã đầy đủ: {flag_str}")
    clean_flag = re.search(r'flag\{[^}]+\}', flag_str)
    if clean_flag:
        print(f"[+] FLAG: {clean_flag.group(0)}")
        return clean_flag.group(0)

if __name__ == "__main__":
    solve()
```

---

## 4. Kết quả & Flag

```text
Full Decrypted Plaintext: flag{f1072f49-fd74-440f-89d2-aea2732bd484}|-broadcast-KMS-1.0|4ebf6d07c2db83b8add5447e9e33a7e773
FLAG: flag{f1072f49-fd74-440f-89d2-aea2732bd484}
```

---

## 5. Bài học rút ra (Key Takeaways)

- **Nguy hiểm khi sử dụng số mũ nhỏ $e=3$**: Khi gửi cùng một thông điệp tới $k \ge e$ người nhận mà không sử dụng padding ngẫu nhiên (OAEP), kẻ tấn công luôn có thể dùng CRT và khai căn nguyên bậc $e$ để giải mã hoàn toàn thông điệp mà không cần bẻ khóa modulus $N$.
- **Luôn sử dụng đệm ngẫu nhiên chuẩn (Optimal Asymmetric Encryption Padding - OAEP)**: Đệm ngẫu nhiên đảm bảo cùng một thông điệp khi mã hóa cho các đối tác khác nhau sẽ tạo ra các bản rõ độc lập trước khi lũy thừa, vô hiệu hóa hoàn toàn Hastad's Broadcast Attack.
