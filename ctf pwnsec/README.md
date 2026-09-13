# 🛡️ PwnSec CTF 2026 — Write-ups & Exploit Repository

Kho lưu trữ tài liệu phân tích kỹ thuật (Write-ups), kịch bản khai thác tự động (Exploit Scripts), và mã nguồn các thử thách trong giải đấu **PwnSec CTF 2026**.

---

## 🏆 BẢNG TỔNG HỢP CÁC THỬ THÁCH ĐÃ GIẢI

| Thử Thách | Phân Loại | Độ Khó | Điểm Số | Flag Thu Được | Tài Liệu Chi Tiết | Script Khai Thác |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| **`pickle`** | Web / Deserialization | Medium / Hard | ~300 | `pwnsec{ce3a3177fb14adae}` | [WRITEUP_PICKLE.md](writeups/WRITEUP_PICKLE.md) | [exploit_pickle.py](exploits/pickle/exploit_pickle.py) |
| **`PHAULT`** | Web / SQLi | Easy | 196 | `pwnsec{0e2de77060a05e91}` | [WRITEUP_PHAULT.md](writeups/WRITEUP_PHAULT.md) | [exploit_phault.py](exploits/phault/exploit_phault.py) |
| **`Neon Skies`** | Web / XSS / Cookie Tossing | Medium | 500 | `pwnsec{9abdf66a5f2afecb}` | [WRITEUP_NEON_SKIES.md](writeups/WRITEUP_NEON_SKIES.md) | [solve_neon.py](exploits/neon_skies/solve_neon.py) |
| **`Easy-leak`** | Web / XSS / CSP Bypass | Medium | 500 | `pwnsec{6dc1bc8a44647ab0}` | [WRITEUP_EASY_LEAK.md](writeups/WRITEUP_EASY_LEAK.md) | [solve_easy_leak.py](scripts_dev/solve_easy_leak.py) |
| **`readonce`** | Web / Race Condition / State Machine | Medium / Hard | 500 | `pwnsec{62c62c2f6d2f9a7447ee56faeb7e7b68}` | [WRITEUP_READONCE.md](writeups/WRITEUP_READONCE.md) | [solve_readonce.py](scripts_dev/solve_readonce.py) |

> 📖 **Xem các báo cáo phân tích chi tiết trong thư mục:**  
> 👉 [**writeups/**](writeups/)

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```text
ctf pwnsec/
├── README.md                      # Mục lục và giới thiệu tổng quan toàn bộ giải đấu
│
├── writeups/                      # Tài liệu Write-up chi tiết kèm hình ảnh từng bước
│   ├── WRITEUP.md                 # Báo cáo tổng hợp toàn diện các thử thách
│   ├── WRITEUP_PICKLE.md          # Phân tích chuyên sâu bài pickle (Insecure Deserialization)
│   ├── WRITEUP_PHAULT.md          # Phân tích chuyên sâu bài PHAULT (PHP Fatal Error SQLi Oracle)
│   ├── WRITEUP_NEON_SKIES.md      # Phân tích chuyên sâu bài Neon Skies (Cookie Tossing & XSS)
│   ├── WRITEUP_EASY_LEAK.md       # Phân tích chuyên sâu bài Easy-leak (CSP Bypass & Token Leak)
│   └── WRITEUP_READONCE.md        # Phân tích chuyên sâu bài readonce (State Machine & History Navigation)
│
├── exploits/                      # Kịch bản khai thác (PoC / Exploit Scripts)
│   ├── pickle/
│   │   └── exploit_pickle.py      # Script chế tạo bytecode Pickle bypass REDUCE & filter
│   ├── phault/
│   │   └── exploit_phault.py      # Script khai thác SQLi Boolean Oracle đa luồng (16 threads)
│   └── neon_skies/
│       ├── solve_neon.py          # Script tự động hóa toàn bộ chuỗi khai thác Cross-Challenge
│       ├── evil.html              # Stage 1: Payload Cookie Tossing cho domain cha chal.ctf.ae
│       ├── s.js                   # Stage 2: Payload XSS xóa cookie rác, cào cờ và phát beacon
│       └── server.py              # Server kiểm thử payload cục bộ
│
├── challenge/                     # Source code và tài nguyên thử thách do BTC cung cấp
│   ├── pickle/                    # Mã nguồn backend Python Flask và logic unpickler
│   ├── neon_skies/                # Mã nguồn Crystal web server, Nginx và Playwright Bot
│   └── hunting_01/                # Đề bài phân tích mã độc / Forensics
│
├── images/                        # Toàn bộ hình ảnh minh họa, sơ đồ và screenshot chất lượng cao
├── scripts_dev/                   # Các script phụ trợ phân tích, trinh sát và trích xuất dữ liệu
└── triage/                        # Dữ liệu phục vụ phân tích pháp y số (DFIR) của bài hunting_01
```

---

## 🔍 TÓM TẮT KỸ THUẬT TỪNG THỬ THÁCH

### 1. `pickle` — Python Insecure Deserialization RCE
- **Lỗ hổng:** Ứng dụng Flask sử dụng `pickle.loads()` để khôi phục session.
- **Hàng rào phòng thủ:** Whitelist chỉ cho phép import class từ `sessionstore`, cấm opcode `REDUCE` (`R`), cấm dấu chấm kết thúc `.` (`STOP`), lọc blacklist chuỗi ký tự (`os`, `system`, `eval`,...).
- **Kỹ thuật vượt rào:**
  - Bỏ dấu chấm kết thúc `.` để `pickletools.dis()` văng ngoại lệ `ValueError`, làm vô hiệu hóa bộ lọc `check()`.
  - Dùng hex-escape `\x..` bên trong opcode `S` để giấu chuỗi cấm.
  - Sử dụng dictionary `sessionstore.__builtins__` kết hợp các opcode `INST` (`i`), `BUILD` (`b`), và `OBJ` (`o`) để khởi tạo đối tượng và gọi hàm `eval()` thực thi mã Python đọc file `flag.txt`.
- **Flag:** `pwnsec{ce3a3177fb14adae}`

### 2. `PHAULT` — PHP Fatal Error Boolean Oracle via MySQL `INTO @var`
- **Lỗ hổng:** SQL Injection trực tiếp trong tham số `$_GET["id"]`: `SELECT username FROM users WHERE id = <input>`.
- **Hàng rào phòng thủ:** Cơ chế chống Timing Attack ép độ trễ mọi request tối thiểu 2.0s (`usleep`), kết quả truy vấn không in ra màn hình.
- **Kỹ thuật vượt rào:**
  - Chèn mệnh đề `UNION SELECT 2 WHERE (<condition>) INTO @var`.
  - **Khi điều kiện ĐÚNG:** `UNION` trả về 2 hàng dữ liệu, MySQL báo lỗi cú pháp do `INTO @var` chỉ chấp nhận tối đa 1 dòng. Câu query thất bại sạch sẽ $\rightarrow$ PHP in thông báo mặc định.
  - **Khi điều kiện SAI:** Mệnh đề phụ rỗng, MySQL thực thi thành công và gán biến $\rightarrow$ PHP gọi `$res->fetch_row()` trên giá trị boolean `true`, kích hoạt lỗi `PHP Fatal error: Uncaught Error: Call to a member function fetch_row() on bool`.
  - Sự xuất hiện/biến mất của chuỗi `"Fatal error"` tạo thành kênh Boolean Oracle hoàn hảo, chạy đa luồng rút ngắn thời gian dò tìm 16 ký tự xuống chỉ vài giây.
- **Flag:** `pwnsec{0e2de77060a05e91}`

### 3. `Neon Skies` — Sibling Subdomain Cookie Tossing & Cross-Challenge RCE
- **Lỗ hổng:** Template Crystal `admin.ecr` in biến `@flag` ra màn hình mà không qua hàm lọc `HTML.escape()`. Biến này lấy từ Cookie `FLAG`.
- **Hàng rào phòng thủ:** Bot chạy Chromium Playwright nạp cờ thật vào cookie với thuộc tính `httpOnly: true` và `sameSite: "Strict"`.
- **Kỹ thuật vượt rào:**
  - Áp dụng chuẩn **RFC 6265 (§5.3)**: Mọi subdomain trên `*.chal.ctf.ae` đều có quyền tạo cookie dùng chung cho domain cha `domain=chal.ctf.ae`.
  - **Tấn công liên bài (Cross-Challenge Pivoting):** Khai thác RCE từ bài `pickle` (`0c6523a28168f7fd.chal.ctf.ae`), thay đổi `app.static_folder = '/tmp'` để host 2 file payload `evil.html` và `s.js`.
  - Bot ghé thăm link của `pickle`, bị tiêm cookie XSS, rồi chuyển hướng sang `/admin`. Do cùng họ `chal.ctf.ae`, điều hướng này là Same-Site $\rightarrow$ Cookie `SameSite=Strict` thật vẫn được bảo toàn.
  - Parser Cookie của Crystal (Last-Wins) ưu tiên in cookie tiêm $\rightarrow$ XSS kích hoạt.
  - Script `s.js` xóa cookie tiêm, dùng `fetch('/admin')` để server in cờ thật và gửi về Webhook listener.
- **Flag:** `pwnsec{9abdf66a5f2afecb}`

---

## 🚀 HƯỚNG DẪN CHẠY EXPLOIT

### 1. Khai thác bài `pickle`
```bash
cd exploits/pickle
python exploit_pickle.py <target_host>
# Ví dụ: python exploit_pickle.py bb5a527b7f5c2a59.chal.ctf.ae
```

### 2. Khai thác bài `PHAULT`
```bash
cd exploits/phault
python exploit_phault.py <target_host>
# Ví dụ: python exploit_phault.py 965759d3620573db.chal.ctf.ae
```

### 3. Khai thác bài `Neon Skies`
```bash
cd exploits/neon_skies
python solve_neon.py <pickle_host>
# Ví dụ: python solve_neon.py 0c6523a28168f7fd.chal.ctf.ae
```
