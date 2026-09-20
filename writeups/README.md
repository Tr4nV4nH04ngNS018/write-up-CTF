# DDC CTF 2026 — Comprehensive Write-ups & Solvers Repository

Kho tài liệu tổng hợp toàn diện các bài giải (Write-ups) và mã khai thác tự động (Exploit Scripts) cho giải đấu **DDC CTF 2026**.

Toàn bộ các tài liệu đã được gom nhóm, phân loại khoa học theo từng chuyên mục (Category), chuẩn hóa định dạng Markdown và bảo tồn nguyên vẹn 100% dữ liệu gốc.

---

## 📁 Cấu trúc thư mục (Organized Structure)

```
writeups/
├── README.md                                         # Tài liệu mục lục tổng hợp toàn bộ giải đấu
│
├── web/                                              # Web Exploitation
│   ├── WEB_CHALLENGE_1_NovaLingo.md                  # GraphQL Introspection & Unauth Diagnostic Mutation
│   └── WEB_CHALLENGE_DevMateAI.md                    # WebSocket Prototype Pollution & Privilege Escalation
│
├── pwn/                                              # Binary Exploitation (PWN)
│   ├── PWN_CHALLENGE_1_Vault.md                      # Format String (%n$p) leak stack flag
│   ├── PWN_CHALLENGE_2_Sanitizer.md                  # Stack Buffer Overflow -> overwrite slot to win()
│   ├── PWN_CHALLENGE_3_ModelRegistry.md              # gets() 64B Buffer Overflow -> ret2win
│   ├── PWN_CHALLENGE_4_TokenCounter.md               # uint8 integer overflow -> time-based quota bypass
│   ├── PWN_CHALLENGE_5_NexusMind.md                  # Heap UAF + Tcache Poisoning -> emit_hook hijacking
│   └── PWN_CHALLENGE_6_SupportChat.md                # Format String (No-PIE) -> GOT overwrite -> shell
│
├── reverse/                                          # Reverse Engineering
│   ├── REVERSE_CHALLENGE_1_NovaGo.md                 # Go binary custom markers & XOR 0x5A
│   ├── REVERSE_CHALLENGE_8_Chronon.md                # Bytecode unshuffle & XOR key 55
│   └── REVERSE_CHALLENGE_10_SentryMark.md            # Vulkan SPIR-V shader & Linear system inversion
│
├── crypto/                                           # Cryptography
│   ├── CRYPTO_CHALLENGE_2_NeuroPay.md                # Insecure PRNG seed prediction from HTTP timestamp
│   ├── CRYPTO_CHALLENGE_3_VinAISessions.md           # AES-CBC Padding Oracle Attack + Character Priority
│   └── CRYPTO_CHALLENGE_5_ThreePartnersBounty.md     # RSA Hastad's Broadcast Attack (e=3, CRT, Cube Root)
│
└── misc/                                             # Digital Forensics & Misc
    ├── MISC_CHALLENGE_1_HanRiver.md                  # Red Channel LSB Steganography Extraction
    ├── MISC_CHALLENGE_4_ColdStorage.md               # FAT32 Deleted File Directory Parsing & Carving
    └── MISC_CHALLENGE_5_Whisperbox.md                # AI Model Watermark Side-Channel Timing Leakage
```

---

## 🏆 Bảng tổng hợp thành tích & Flags (Master Scoreboard)

| # | Chuyên mục | Thử thách (Challenge) | Điểm | Kỹ thuật cốt lõi (Core Vulnerability) | Flag thu được | Tài liệu chi tiết |
|---|------------|-----------------------|------|---------------------------------------|---------------|-------------------|
| 1 | **Web** | **WEB 1** — NovaLingo | 28 | GraphQL Introspection $\rightarrow$ `diagnosticsDumpEnv` | `flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41}` | [Writeup](web/WEB_CHALLENGE_1_NovaLingo.md) |
| 2 | **Web** | **DevMate AI** | ~150 | WebSocket Prototype Pollution $\rightarrow$ Privilege Escalation | `843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92` | [Writeup](web/WEB_CHALLENGE_DevMateAI.md) |
| 3 | **PWN** | **PWN 1** — Vault (Logging Daemon) | 54 | Format String (`%n$p`) leak chuỗi cờ từ stack | `flag{dd753354-c8fb-4c3d-939e-2b19169f289f}` | [Writeup](pwn/PWN_CHALLENGE_1_Vault.md) |
| 4 | **PWN** | **PWN 2** — Sanitizer | 54 | Off-by-one / Buffer Overflow ghi đè slot thành `win()` | `flag{8b576a25-d44f-4e9a-95e8-da31bff133cd}` | [Writeup](pwn/PWN_CHALLENGE_2_Sanitizer.md) |
| 5 | **PWN** | **PWN 3** — ModelRegistry | 94 | `gets()` 64-byte Buffer Overflow $\rightarrow$ ret2win (`0x4012b6`) | `flag{c42af0f9-527f-4581-81a9-b993437e23a7}` | [Writeup](pwn/PWN_CHALLENGE_3_ModelRegistry.md) |
| 6 | **PWN** | **PWN 4** — TokenCounter | 70 | `uint8_t` Integer Overflow (256 $\rightarrow$ 0) $\rightarrow$ quota race | `flag{da936d94-f4ca-4fbf-b363-6aadfca105ed}` | [Writeup](pwn/PWN_CHALLENGE_4_TokenCounter.md) |
| 7 | **PWN** | **PWN 5** — NexusMind | 274 | Heap UAF + Tcache Poisoning $\rightarrow$ ghi đè `emit_hook` | `flag{27f045b4-b6cd-4397-942d-48c79b2bfea0}` | [Writeup](pwn/PWN_CHALLENGE_5_NexusMind.md) |
| 8 | **PWN** | **PWN 6** — SupportChat | 287 | Format String (No-PIE, offset 6) $\rightarrow$ Libc leak & GOT hijack | *(Exploit Complete / Shell)* | [Writeup](pwn/PWN_CHALLENGE_6_SupportChat.md) |
| 9 | **Reverse** | **REVERSE 1** — NovaGo | 28 | Go binary string markers (`NVGO_ENC`) + XOR `0x5A` | `flag{5436b115-3896-4ca7-82db-8a75f272f519}` | [Writeup](reverse/REVERSE_CHALLENGE_1_NovaGo.md) |
| 10 | **Reverse** | **REVERSE 8** — Chronon | 195 | Bytecode unshuffle + XOR decrypt (key=55) | `flag{e3bca87c-96a8-4d9d-8f81-5f7c39770d47}` | [Writeup](reverse/REVERSE_CHALLENGE_8_Chronon.md) |
| 11 | **Reverse** | **REVERSE 10** — SentryMark | 456 | Vulkan SPIR-V shader reverse & Linear System Inversion | `flag{a10ff24b-3240-410a-8d32-61d00c3b52d9}` | [Writeup](reverse/REVERSE_CHALLENGE_10_SentryMark.md) |
| 12 | **Crypto** | **CRYPTO 2** — NeuroPay | 82 | Insecure PRNG (`random.seed(timestamp)`) $\rightarrow$ predict token | `flag{8d0abac8-204a-4f56-928a-0c6d27e5448e}` | [Writeup](crypto/CRYPTO_CHALLENGE_2_NeuroPay.md) |
| 13 | **Crypto** | **CRYPTO 3** — VinAISessions | ~100 | AES-CBC Padding Oracle Attack + Plaintext Char Priority | `flag{6d2dd554-c004-44cd-ab31-fdeddd7d9d4a}` | [Writeup](crypto/CRYPTO_CHALLENGE_3_VinAISessions.md) |
| 14 | **Crypto** | **CRYPTO 5** — Three Partners | ~150 | RSA Hastad's Broadcast Attack ($e=3$, CRT + $\sqrt[3]{C}$) | `flag{f1072f49-fd74-440f-89d2-aea2732bd484}` | [Writeup](crypto/CRYPTO_CHALLENGE_5_ThreePartnersBounty.md) |
| 15 | **Misc** | **MISC 1** — HanRiver | 28 | LSB Steganography trích xuất từ kênh Red ảnh PNG | `flag{32cea801-8c02-42f1-9318-401f009ef612}` | [Writeup](misc/MISC_CHALLENGE_1_HanRiver.md) |
| 16 | **Misc** | **MISC 4** — ColdStorage | 48 | Khôi phục file đã xóa (`?RAINI~1.TXT`) trên phân vùng FAT32 | `flag{777ee36a-a2ce-46a9-a8be-2f19c90d6362}` | [Writeup](misc/MISC_CHALLENGE_4_ColdStorage.md) |
| 17 | **Misc** | **MISC 5** — Whisperbox | 266 | AI Model Watermark Side-Channel Timing & Logit Leakage | `flag{1da51e40cbaa4626a688db2157}` | [Writeup](misc/MISC_CHALLENGE_5_Whisperbox.md) |

---

## 🛡️ Tóm tắt các kỹ thuật tấn công & phòng thủ

### 1. Web Exploitation
- **GraphQL Introspection**: Luôn vô hiệu hóa introspection trên môi trường production để tránh lộ toàn bộ các truy vấn nội bộ và mutation nhạy cảm.
- **WebSocket Prototype Pollution**: Kiểm soát chặt chẽ các hàm gộp cấu hình (`Object.assign`, deep merge); kiểm tra và loại bỏ triệt để các thuộc tính `__proto__`, `constructor`.

### 2. Binary Exploitation (PWN)
- **Format String Vulnerability**: Tuyệt đối không truyền trực tiếp dữ liệu người dùng vào các hàm họ `printf()`. Bật Full RELRO, PIE và Stack Canary.
- **Heap Exploitation**: Phòng chống Tcache Poisoning và Double Free bằng cách gán con trỏ về `NULL` ngay sau khi giải phóng bộ nhớ (`free(ptr); ptr = NULL;`).
- **Integer Overflow**: Kiểm tra chặt chẽ kiểu dữ liệu độ rộng cố định (`uint8_t`, `uint16_t`) khi thực hiện các phép nhân tính toán quota hoặc kích thước buffer.

### 3. Reverse Engineering
- **Mã hóa chuỗi tĩnh & Marker**: Tránh lưu trữ các khóa hoặc dấu hiệu tĩnh lộ liễu trong binary; sử dụng kỹ thuật Obfuscation kết hợp Control Flow Flattening và MBA.
- **Compute Shader & Đồ họa**: Biên dịch SPIR-V cần được loại bỏ thông tin debug/reflection metadata để tránh bị dịch ngược cấu trúc ma trận tính toán.

### 4. Cryptography
- **Hastad's Broadcast Attack**: Tuyệt đối không tái sử dụng cùng số mũ $e$ nhỏ ($e=3$) khi mã hóa cùng một thông điệp cho nhiều đối tác; luôn áp dụng chuẩn đệm ngẫu nhiên OAEP.
- **Padding Oracle Attack**: Đảm bảo thời gian phản hồi và thông báo lỗi giải mã đồng nhất (Constant-time verification) và sử dụng mã hóa xác thực (Authenticated Encryption - AEAD như AES-GCM).
- **PRNG Seed**: Không bao giờ sử dụng thời gian thực (`time.time()`) làm hạt giống ngẫu nhiên cho các tác vụ mật mã hoặc sinh token bảo mật.

### 5. Digital Forensics
- **FAT32 Recovery**: Thao tác xóa file trên FAT32 chỉ đánh dấu directory entry thành `0xE5` mà không xóa dữ liệu trên cluster. Cần dùng công cụ chuyên dụng (Wipe/Shred) để xóa sạch dữ liệu nhạy cảm.
- **LSB Steganography**: Giấu tin trên các kênh màu RGB có thể dễ dàng bị phát hiện qua phân tích thống kê phân bố bit (Chi-square attack).
