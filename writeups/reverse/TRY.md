# Writeup — TRY (Reverse Engineering)

> **V1t CTF 2026** · Category: Reverse Engineering · Tiny C Compiler Obfuscation + VM Interpreter
>
> **Flag:** `v1t{n0_dump_just_pain}`

---

## 1. Tóm tắt (TL;DR)
Thử thách cung cấp file thực thi `chall.exe` (được biên dịch bằng Tiny C Compiler - TCC). Sau khi người dùng nhập chuỗi dài 22 ký tự, chương trình sẽ giải mã bytecode của một máy ảo (VM) tùy chỉnh (kích thước 365 byte) bằng cách sử dụng key `0xa7` (được sinh ra qua một chuỗi các hàm anti-debug và timing kiểm tra tốc độ thực thi).

Máy ảo này có 8 loại lệnh cơ bản để tính toán các phép toán số học ngược trên từng ký tự của chuỗi flag. Bằng cách dịch ngược các lệnh VM trong bytecode, ta có thể đảo ngược trực tiếp các phép tính trên accumulator (`XOR_ACC`, `ADD_ACC`, `ROL_ACC`) để tìm ra 22 ký tự duy nhất của flag mà không cần quan tâm đến các kiểm tra phụ.

---

## 2. Các file được cung cấp

| File | Vai trò |
|---|---|
| `chall.exe` | File thực thi chính cho thử thách (Windows PE 64-bit) |

---

## 3. Phân tích Tĩnh & Động sơ bộ
- File thực thi `chall.exe` ban đầu được tải về dưới dạng `.crdownload` chưa hoàn thành và được đổi tên lại thành `chall.exe`.
- Khi kiểm tra các section của binary, ta phát hiện rất nhiều section lạ (ví dụ: `.enigma1`, `.vmp0`, `UPX0`, `.winlice`, `PETETRIS`, `__wibu00`, v.v.) được chèn vào nhằm đánh lừa các công cụ phân tích tự động (Packer/Protector signatures). Thực tế mã nguồn được biên dịch bằng Tiny C Compiler (TCC), thể hiện qua các chuỗi như `chall_tcc_obfus.exe`.
- Khi chạy trực tiếp:
  ```
  +----------------------------------------+
  | try                                    |
  | sealed input verifier                  |
  +----------------------------------------+

  input > 
  ```
  Nhập thử chuỗi bất kỳ sẽ trả về `[-] rejected`.

---

## 4. Phân tích Logic Xác thực & Máy ảo (VM)

### 4.1. Hàm `0x4024d9` (Anti-Debugging & Status Key)
Hàm này thực hiện các bước kiểm tra anti-debug để trả về trạng thái chạy thực tế của chương trình:
- Gọi `IsDebuggerPresent()` (nếu phát hiện debug, trả về `0x13`).
- Gọi `CheckRemoteDebuggerPresent` (nếu phát hiện debug, trả về `0x29`).
- Đo thời gian chạy bằng cách so sánh hiệu thời gian trước và sau hàm `Sleep(12)` qua `QueryPerformanceCounter`. Nếu thời gian trôi qua lớn hơn 600ms (dấu hiệu của việc debugger đang dừng ở breakpoints hoặc người dùng đang step code), hàm trả về `0x4e`.
- Nếu chạy bình thường ở tốc độ cao, hàm trả về giá trị **`0xa7`**. Đây chính là khóa (status key) được sử dụng để giải mã bytecode VM.

### 4.2. Trích xuất và giải mã Bytecode
Bytecode được lưu trữ dưới dạng mã hóa tại địa chỉ `0x4043a8` với độ dài 365 byte (`0x16d`). Phép giải mã ở mỗi offset `PC` được thực hiện như sau:
```python
mix_val = func_0x40199f(PC, val_x) # Trộn PC với val_x (0xa7)
ecx = enc_byte ^ mix_val
shift = (PC ^ val_x) & 7
dec_byte = ROR8(ecx, shift)
```

Sau khi giải mã, ta thu được tập hợp 8 instruction của máy ảo tùy chỉnh:
- `0x5d` (`ADD_A`): Tăng biến tạm `var_a` (không ảnh hưởng trực tiếp đến kết quả xác thực).
- `0x4b` (`LOAD_ACC <idx>`): Tải ký tự tại chỉ số `<idx>` của flag vào biến tích lũy `acc`.
- `0x32` (`ADD_ACC <val>`): Cộng `acc` với `<val>`.
- `0x18` (`ROL_ACC <val>`): Dịch trái xoay vòng (Rotate Left 8-bit) `acc` đi `<val>` bit.
- `0x71` (`XOR_ACC <val>`): XOR `acc` với `<val>`.
- `0xd4` (`CHECK_ACC <val>`): So sánh `acc` với `<val>`, nếu khác nhau sẽ set `err_flag`.
- `0xa9` (`CHECK_REL`): Kiểm tra quan hệ phức tạp giữa các cặp ký tự trong flag.
- `0xee` (`EXIT <val>`): Thoát VM và trả về kết quả.

---

## 5. Phương pháp Giải thuật (Solver)
Vì các phép biến đổi trên `acc` ở mỗi ký tự độc lập và hoàn toàn đảo ngược được (XOR, ADD mod 256, ROL8 đều là các phép song ánh), ta có thể giải mã ngược từ `target` trong câu lệnh `CHECK_ACC` về ký tự ban đầu:
- Đảo ngược `XOR_ACC V`: `acc = acc ^ V`
- Đảo ngược `ADD_ACC V`: `acc = (acc - V) & 0xff`
- Đảo ngược `ROL_ACC V`: `acc = ROR8(acc, V)`

Từ các block lệnh trong file bytecode đã giải mã, ta dễ dàng đảo ngược và khôi phục toàn bộ flag.

### Mã nguồn Solver (Python):
```python
def ROL8(val, shift):
    shift = shift & 7
    if shift != 0:
        return (((val & 0xff) << shift) | ((val & 0xff) >> (8 - shift))) & 0xff
    else:
        return val & 0xff

def ROR8(val, shift):
    shift = shift & 7
    if shift != 0:
        return (((val & 0xff) >> shift) | ((val & 0xff) << (8 - shift))) & 0xff
    else:
        return val & 0xff

# Parse bytecode VM
# Giả sử bytecode đã được giải mã thô thành chuỗi các lệnh ACC
# Ta trích xuất 22 khối lệnh tương ứng với 22 chỉ số từ 0..21

# Đoạn bytecode giải mã được cho ta các phương trình sau:
equations = {
    18: [("XOR", 69), ("ADD", 80), ("ROL", 6), ("XOR", 147), ("CHECK", 142)],
    17: [("XOR", 131), ("ADD", 104), ("ROL", 4), ("XOR", 251), ("CHECK", 78)],
    4:  [("XOR", 90), ("ADD", 216), ("ROL", 3), ("XOR", 56), ("CHECK", 88)],
    14: [("XOR", 32), ("ADD", 152), ("ROL", 3), ("XOR", 203), ("CHECK", 148)],
    13: [("XOR", 206), ("ADD", 45), ("ROL", 7), ("XOR", 236), ("CHECK", 152)],
    1:  [("XOR", 84), ("ADD", 37), ("ROL", 5), ("XOR", 100), ("CHECK", 53)],
    9:  [("XOR", 178), ("ADD", 40), ("ROL", 7), ("XOR", 56), ("CHECK", 187)],
    16: [("XOR", 158), ("ADD", 58), ("ROL", 2), ("XOR", 186), ("CHECK", 85)],
    20: [("XOR", 163), ("ADD", 32), ("ROL", 5), ("XOR", 41), ("CHECK", 148)],
    0:  [("XOR", 165), ("ADD", 186), ("ROL", 3), ("XOR", 244), ("CHECK", 152)],
    3:  [("XOR", 89), ("ADD", 29), ("ROL", 7), ("XOR", 233), ("CHECK", 118)],
    19: [("XOR", 116), ("ADD", 212), ("ROL", 1), ("XOR", 53), ("CHECK", 214)],
    12: [("XOR", 89), ("ADD", 28), ("ROL", 5), ("XOR", 171), ("CHECK", 66)],
    2:  [("XOR", 102), ("ADD", 171), ("ROL", 5), ("XOR", 200), ("CHECK", 127)],
    7:  [("XOR", 165), ("ADD", 118), ("ROL", 5), ("XOR", 114), ("CHECK", 148)],
    10: [("XOR", 178), ("ADD", 236), ("ROL", 1), ("XOR", 78), ("CHECK", 19)],
    15: [("XOR", 116), ("ADD", 111), ("ROL", 3), ("XOR", 149), ("CHECK", 238)],
    11: [("XOR", 46), ("ADD", 2), ("ROL", 4), ("XOR", 252), ("CHECK", 203)],
    21: [("XOR", 80), ("ADD", 98), ("ROL", 4), ("XOR", 127), ("CHECK", 135)],
    8:  [("XOR", 164), ("ADD", 28), ("ROL", 4), ("XOR", 78), ("CHECK", 144)],
    5:  [("XOR", 17), ("ADD", 112), ("ROL", 3), ("XOR", 96), ("CHECK", 236)],
    6:  [("XOR", 36), ("ADD", 14), ("ROL", 3), ("XOR", 151), ("CHECK", 219)]
}

flag = [None] * 22

for idx, ops in equations.items():
    # Phần tử cuối cùng là CHECK <target>
    target = ops[-1][1]
    curr = target
    # Đảo ngược các phép toán từ dưới lên
    for op_type, val in reversed(ops[:-1]):
        if op_type == "XOR":
            curr = curr ^ val
        elif op_type == "ADD":
            curr = (curr - val) & 0xff
        elif op_type == "ROL":
            curr = ROR8(curr, val)
    flag[idx] = curr

print("Flag:", "".join(chr(c) for c in flag))
```

---

## 6. Flag
```
v1t{n0_dump_just_pain}
```
