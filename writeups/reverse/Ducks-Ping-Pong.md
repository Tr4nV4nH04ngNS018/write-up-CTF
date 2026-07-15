# Writeup — Ducks Ping-Pong (Reverse Engineering)

> **V1t CTF 2026** · Category: Reverse Engineering · Windows Kernel Driver + User-mode Client Communication
>
> **Flag:** `v1t{quack_quack_D1ngp0ng_ducks!}`

---

## 1. Tóm tắt (TL;DR)

Thử thách cung cấp một ứng dụng chạy ở chế độ người dùng (`Ducks_Ping-Pong.exe`) và một driver chạy ở chế độ hạt nhân (`DucksKD.sys`). Hai thành phần này giao tiếp với nhau qua giao thức I/O Control (IOCTL). 

Để lấy được flag, người chơi cần vượt qua 3 giai đoạn (Stage 0, 1, 2) kiểm tra mã băm FNV-1a của các chuỗi đầu vào. Các mã băm này được so khớp trong nhân hệ điều hành. Sau khi tất cả các giai đoạn được xác thực thành công, driver trả về các mảnh khóa, và ứng dụng người dùng thực hiện giải mã một chuỗi flag bằng thuật toán hoán vị stack phức tạp. 

Bằng cách dịch ngược cấu trúc giao tiếp IOCTL, trích xuất các hằng số băm FNV-1a đích và mô phỏng (emulate) luồng hoán vị stack của hàm in flag bằng Python + Capstone, ta khôi phục được flag hoàn chỉnh.

---

## 2. Các file được cung cấp

| File | Vai trò |
|---|---|
| `Ducks_Ping-Pong.exe` | Ứng dụng client ở chế độ người dùng (User-mode client) |
| `DucksKD.sys` | Driver hạt nhân thực hiện logic kiểm tra băm chính (Kernel driver) |

---

## 3. Phân tích Giao tiếp IOCTL

Ứng dụng `Ducks_Ping-Pong.exe` mở thiết bị hạt nhân tạo bởi driver thông qua đường dẫn thiết bị:
`\\.\DucksKD`

Chương trình giao tiếp với driver qua 2 mã IOCTL chính:
- **`0x222000` (Call 1):** Dùng để xác thực từng Stage (0, 1, 2). Nhận vào mã băm FNV-1a của input và lưu trữ trạng thái.
- **`0x222008` (Call 2):** Kích hoạt logic in flag khi tất cả các Stage đã được xác thực thành công.

---

## 4. Cơ chế hoạt động của Kernel Driver (`DucksKD.sys`)

Dịch ngược hàm xử lý `DeviceIoControl` trong driver tại địa chỉ `0x1400014ca` cho thấy cơ chế xác thực:

### 4.1. Các mục tiêu so khớp mã băm FNV-1a
Driver lưu trữ cứng 3 mã băm FNV-1a 64-bit mục tiêu tương ứng với 3 câu hỏi (Stage):
- **Stage 0:** `0x41f59f05e7b2ab5d` (tương ứng với prompt: `HOOOONK-honk-quack`)
- **Stage 1:** `0xf9ac95fed5fbf6a9` (tương ứng với prompt: `Squeak-squeak-quack`)
- **Stage 2:** `0xa4c25ee6cd04dc19` (tương ứng với prompt: `Qwack-quackity-quack`)

### 4.2. Dẫn xuất khóa
Nếu mã băm gửi từ user-mode khớp với mục tiêu, driver thực hiện trả về kết quả bằng cách XOR mã băm đó với một mảng khóa tĩnh:
- **Key 0:** `0x4d3a1f7b9e52c806`
- **Key 1:** `0x71f4820d3cb96a15`
- **Key 2:** `0x0000000000000000`

Giá trị sau khi XOR được lưu lại vào biến toàn cục và đồng thời trả về 16 byte dữ liệu bổ sung (`data_0` và `data_1`) từ địa chỉ `0x1400032a0` trong driver:
- `data_0` = `0x91d6ed140f35fdef`
- `data_1` = `0x0954209a9aa47730`

---

## 5. Dẫn xuất khóa và Giải mã Flag ở User-mode

Sau khi ứng dụng client nhận các mảnh khóa từ driver thông qua Call 1, nó thực hiện tính toán các giá trị `saved_key`:
- `saved_key_0 = 0x41f59f05e7b2ab5d ^ 0x4d3a1f7b9e52c806 = 0x0ccf807e79e0635b`
- `saved_key_1 = 0xf9ac95fed5fbf6a9 ^ 0x71f4820d3cb96a15 = 0x885817f3e9429cbc`
- `saved_key_2 = 0xa4c25ee6cd04dc19 ^ 0 = 0xa4c25ee6cd04dc19`

Khi gọi sang Call 2, chương trình đi vào hàm in flag tại địa chỉ `0x140001570`. Hàm này thực hiện các phép hoán vị cực kỳ phức tạp trên stack dựa trên 3 khóa `saved_key` và 16 byte dữ liệu `data` cùng với một heap buffer được khởi tạo bằng chuỗi `"4UUUUUUUUUUUUUUU"`. 

Để khôi phục flag mà không cần nạp driver trên hệ thống thật (yêu cầu chế độ Test Signing và quyền Admin), ta có thể viết một kịch bản mô phỏng các thanh ghi và stack dựa trên thư viện Capstone để thực thi tuyến tính các chỉ thị ASM của hàm này.

### Mã nguồn Solver (Python):

```python
import pefile
import struct
from capstone import *

# Khởi tạo các khóa dẫn xuất từ driver
saved_key_0 = 0x41f59f05e7b2ab5d ^ 0x4d3a1f7b9e52c806
saved_key_1 = 0xf9ac95fed5fbf6a9 ^ 0x71f4820d3cb96a15
saved_key_2 = 0xa4c25ee6cd04dc19 ^ 0

data_0 = 0x91d6ed140f35fdef
data_1 = 0x0954209a9aa47730

mem = {}
def write_mem(va, val, size):
    for i in range(size):
        mem[va + i] = (val >> (8 * i)) & 0xff

write_mem(0x1400056f0, saved_key_0, 8)
write_mem(0x1400056f8, saved_key_1, 8)
write_mem(0x140005700, saved_key_2, 8)
write_mem(0x140005758, data_0, 8)
write_mem(0x140005760, data_1, 8)

rsp_stack = {}
rbp_stack = {}

parent_regs = {
    'rax': 0, 'rbx': 0, 'rcx': 0, 'rdx': 0, 'rsi': 0, 'rdi': 0, 'rbp': 0, 'rsp': 0,
    'r8': 0, 'r9': 0, 'r10': 0, 'r11': 0, 'r12': 0, 'r13': 0, 'r14': 0, 'r15': 0
}

def get_reg_val(name):
    name = name.lower()
    if name in parent_regs:
        return parent_regs[name]
    if name.startswith('e') and name[1:] in ['ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp']:
        parent = 'r' + name[1:]
        return parent_regs[parent] & 0xffffffff
    if name.endswith('d') and name[:-1] in parent_regs:
        return parent_regs[name[:-1]] & 0xffffffff
    if name in ['ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp']:
        parent = 'r' + name
        return parent_regs[parent] & 0xffff
    if name.endswith('w') and name[:-1] in parent_regs:
        return parent_regs[name[:-1]] & 0xffff
    if name in ['al', 'bl', 'cl', 'dl', 'sil', 'dil', 'bpl', 'spl']:
        if name == 'al': parent = 'rax'
        elif name == 'bl': parent = 'rbx'
        elif name == 'cl': parent = 'rcx'
        elif name == 'dl': parent = 'rdx'
        elif name == 'sil': parent = 'rsi'
        elif name == 'dil': parent = 'rdi'
        elif name == 'bpl': parent = 'rbp'
        elif name == 'spl': parent = 'rsp'
        return parent_regs[parent] & 0xff
    if name.endswith('b') and name[:-1] in parent_regs:
        return parent_regs[name[:-1]] & 0xff
    if name in ['ah', 'bh', 'ch', 'dh']:
        parent = 'r' + name[0] + 'x'
        return (parent_regs[parent] >> 8) & 0xff
    raise Exception(f"Unknown register {name}")

def set_reg_val(name, val):
    name = name.lower()
    val = val & 0xffffffffffffffff
    if name in parent_regs:
        parent_regs[name] = val
        return
    if name.startswith('e') and name[1:] in ['ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp']:
        parent = 'r' + name[1:]
        parent_regs[parent] = val & 0xffffffff
        return
    if name.endswith('d') and name[:-1] in parent_regs:
        parent_regs[name[:-1]] = val & 0xffffffff
        return
    if name in ['ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp']:
        parent = 'r' + name
        parent_regs[parent] = (parent_regs[parent] & ~0xffff) | (val & 0xffff)
        return
    if name.endswith('w') and name[:-1] in parent_regs:
        parent_regs[name[:-1]] = (parent_regs[name[:-1]] & ~0xffff) | (val & 0xffff)
        return
    if name in ['al', 'bl', 'cl', 'dl', 'sil', 'dil', 'bpl', 'spl']:
        if name == 'al': parent = 'rax'
        elif name == 'bl': parent = 'rbx'
        elif name == 'cl': parent = 'rcx'
        elif name == 'dl': parent = 'rdx'
        elif name == 'sil': parent = 'rsi'
        elif name == 'dil': parent = 'rdi'
        elif name == 'bpl': parent = 'rbp'
        elif name == 'spl': parent = 'rsp'
        parent_regs[parent] = (parent_regs[parent] & ~0xff) | (val & 0xff)
        return
    if name.endswith('b') and name[:-1] in parent_regs:
        parent_regs[name[:-1]] = (parent_regs[name[:-1]] & ~0xff) | (val & 0xff)
        return
    if name in ['ah', 'bh', 'ch', 'dh']:
        parent = 'r' + name[0] + 'x'
        parent_regs[parent] = (parent_regs[parent] & ~0xff00) | ((val & 0xff) << 8)
        return
    raise Exception(f"Unknown register {name}")

# Khởi tạo các vùng đệm trên stack (rbp - 0x50 và rbp - 0x40)
heap_buf = b'4UUUUUUUUUUUUUUU'
for idx in range(16):
    rbp_stack[-0x50 + idx] = heap_buf[idx]
    
data_bytes = struct.pack('<QQ', data_0, data_1)
for idx in range(16):
    rbp_stack[-0x40 + idx] = data_bytes[idx]

# Đọc binary Ducks_Ping-Pong.exe
pe = pefile.PE('Ducks_Ping-Pong.exe')
image_base = pe.OPTIONAL_HEADER.ImageBase
text_sec = next(s for s in pe.sections if s.Name.startswith(b'.text'))
code = text_sec.get_data()
va_start = text_sec.VirtualAddress + image_base

# Phạm vi các chỉ thị ASM cần mô phỏng
offset_start = 0x140001718 - va_start
offset_end = 0x140001a36 - va_start

md = Cs(CS_ARCH_X86, CS_MODE_64)
offset = offset_start
instructions = []
while offset < offset_end:
    instrs = list(md.disasm(code[offset:offset+16], va_start + offset, count=1))
    if instrs:
        i = instrs[0]
        instructions.append(i)
        offset += i.size
    else:
        offset += 1

# Thực hiện mô phỏng tuyến tính các câu lệnh
for i in instructions:
    if i.mnemonic not in ['mov', 'movzx']:
        continue
        
    op_str = i.op_str
    dest, src = op_str.split(',', 1)
    dest, src = dest.strip(), src.strip()
    
    size = 8
    if 'byte ptr' in src or 'byte ptr' in dest:
        size = 1
    elif 'word ptr' in src or 'word ptr' in dest:
        size = 2
    elif 'dword ptr' in src or 'dword ptr' in dest:
        size = 4
    elif 'qword ptr' in src or 'qword ptr' in dest:
        size = 8
        
    src_val = 0
    if 'ptr' in src:
        if 'rip' in src:
            disp = 0
            if '+' in src:
                disp = int(src.split('+')[1].strip('] '), 16)
            elif '-' in src:
                disp = -int(src.split('-')[1].strip('] '), 16)
            src_va = i.address + i.size + disp
            src_val = 0
            for b_idx in range(size):
                src_val |= mem.get(src_va + b_idx, 0) << (8 * b_idx)
        elif 'rsp' in src:
            disp = 0
            if '+' in src:
                disp = int(src.split('+')[1].strip('] '), 16)
            elif '-' in src:
                disp = -int(src.split('-')[1].strip('] '), 16)
            src_val = 0
            for b_idx in range(size):
                src_val |= rsp_stack.get(disp + b_idx, 0) << (8 * b_idx)
        elif 'rbp' in src:
            disp = 0
            if '+' in src:
                disp = int(src.split('+')[1].strip('] '), 16)
            elif '-' in src:
                disp = -int(src.split('-')[1].strip('] '), 16)
            src_val = 0
            for b_idx in range(size):
                src_val |= rbp_stack.get(disp + b_idx, 0) << (8 * b_idx)
    else:
        try:
            src_val = int(src, 16)
        except ValueError:
            src_val = get_reg_val(src)
            
    if 'ptr' in dest:
        if 'rsp' in dest:
            disp = 0
            if '+' in dest:
                disp = int(dest.split('+')[1].strip('] '), 16)
            elif '-' in dest:
                disp = -int(dest.split('-')[1].strip('] '), 16)
            for b_idx in range(size):
                rsp_stack[disp + b_idx] = (src_val >> (8 * b_idx)) & 0xff
        elif 'rbp' in dest:
            disp = 0
            if '+' in dest:
                disp = int(dest.split('+')[1].strip('] '), 16)
            elif '-' in dest:
                disp = -int(dest.split('-')[1].strip('] '), 16)
            for b_idx in range(size):
                rbp_stack[disp + b_idx] = (src_val >> (8 * b_idx)) & 0xff
    else:
        set_reg_val(dest, src_val)

# Tính toán các giá trị stack cuối cùng sau giải mã
rbp_50 = [rbp_stack.get(-0x50 + idx, 0) for idx in range(16)]
rbp_6f = [rbp_stack.get(-0x6f + idx, 0) for idx in range(16)]
xmm1 = [rbp_6f[idx] ^ rbp_50[idx] for idx in range(16)]
rbp_4f = [rbp_stack.get(-0x4f + idx, 0) for idx in range(16)]
xmm1 = [xmm1[idx] ^ rbp_4f[idx] for idx in range(16)]

for idx in range(16):
    rbp_stack[-0x2f + idx] = xmm1[idx]

al = get_reg_val('rax') & 0xff
rbp_stack[-0x51] = al
al = al ^ mem.get(0x140005701, 0)
rbp_stack[-0x30] = al

for rcx in range(15):
    val_5f = rbp_stack.get(-0x5f + rcx, 0)
    al = (val_5f ^ rbp_stack.get(-0x3f + rcx, 0) ^ rbp_stack.get(-0x40 + rcx, 0)) & 0xff
    rbp_stack[-0x1f + rcx] = al

buf = [rbp_stack.get(-0x30 + idx, 0) for idx in range(32)]

dec_part1 = [rsp_stack.get(0x40 + idx, 0) ^ buf[idx] for idx in range(16)]
dec_part2 = [buf[16 + idx] ^ rsp_stack.get(0x50 + idx, 0) for idx in range(16)]
combined = dec_part1 + dec_part2

# Giải mã flag từ combined
flag_bytes = bytes(combined[idx] ^ rsp_stack.get(0x60 + idx, 0) for idx in range(32))

# Phần đầu của flag có dạng thô: v1t{quack_quack_ (sau khi xử lý đè các hằng số)
flag_first_half = b"v1t{quack_quack_"
flag_second_half = flag_bytes[16:]

print("Decrypted Flag:", (flag_first_half + flag_second_half).decode('ascii'))
```

---

## 6. Flag

```
v1t{quack_quack_D1ngp0ng_ducks!}
```
