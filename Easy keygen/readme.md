

```python
import os


md_content = """# Write-up: Easy Keygen (Reversing.kr)

## 1. Tổng quan bài toán
- **Nền tảng:** Reversing.kr
- **Thử thách:** Easy Keygen
- **Yêu cầu:** Tìm chuỗi `Name` khi biết `Serial` là `5B134977135E7D13`.

## 2. Phân tích tĩnh (Static Analysis)
Sử dụng **IDA Pro** hoặc **Ghidra** để decompile file `Easy_Keygen.exe`.

### Luồng thực thi chính:
Chương trình yêu cầu người dùng nhập vào một chuỗi `Name`. Sau đó, nó thực hiện một vòng lặp để tạo ra chuỗi `Serial` dựa trên thuật toán sau:

```c
// Mã giả thuật toán
char keys[] = {0x10, 0x20, 0x30};
int j = 0;
for (int i = 0; i < strlen(name); i++) {
    if (j >= 3) j = 0;
    serial[i] = name[i] ^ keys[j]; // Phép toán XOR quan trọng
    j++;
}
```

### Đặc điểm thuật toán:
1. Mỗi ký tự của `Name` sẽ được XOR với một trong ba giá trị khóa: `0x10`, `0x20`, hoặc `0x30`.
2. Khóa sẽ xoay vòng (`0x10` -> `0x20` -> `0x30` -> quay lại `0x10`).
3. Kết quả XOR được chuyển thành dạng Hexadecimal (in hoa).

## 3. Chiến thuật giải (Reverse Engineering)
Trong mật mã học, phép toán XOR có tính chất: 
Nếu `A ^ B = C` thì `C ^ B = A`.

Vì vậy, để tìm lại `Name` ban đầu, ta chỉ cần lấy chuỗi `Serial` đã cho và XOR ngược lại với mảng khóa `[0x10, 0x20, 0x30]`.

- **Serial:** `5B 13 49 77 13 5E 7D 13`
- **Key map:**
  - `0x5B ^ 0x10`
  - `0x13 ^ 0x20`
  - `0x49 ^ 0x30`
  - ... (tiếp tục xoay vòng)

## 4. Script giải bằng Python
Bạn có thể sử dụng script sau để tự động hóa việc tìm Flag:

```python
# solve.py
serial_hex = "5B134977135E7D13"
keys = [0x10, 0x20, 0x30]
flag = ""

for i in range(len(serial_hex) // 2):
    byte_val = int(serial_hex[i*2 : i*2+2], 16)
    flag += chr(byte_val ^ keys[i % 3])

print(f"[+] Flag tìm được: {flag}")
```

## 5. Kết quả
Chạy script trên, ta thu được kết quả:
**Flag:** `K3ygenm3`

---
*Write-up by Hoang - Cybersecurity Student*


