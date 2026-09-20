# Writeup: MISC CHALLENGE 5 — Whisperbox Watermark Preview

> **Sự kiện:** DDC CTF  
> **Danh mục:** Misc / AI  
> **Độ khó:** Medium  
> **Điểm:** 266  
> **Mô tả:** *"The Model Ships With a Watermark You Are Encouraged to Verify, One Averaged Logprob at a Time."*  
> **Target:** `https://6d1fa0d6-6836-4201-882b-0e6dfd061aad.172.31.102.101.nip.io/`  
> **Flag:** `flag{1da51e40cbaa4626a688db2157}`  

---

## 1. Tóm tắt (TL;DR)

1. Thử thách cung cấp dịch vụ web **Whisperbox** (mô hình ngôn ngữ nhỏ có cơ chế Watermark theo phong cách Kirchenbauer et al., 2023).
2. Watermark có kích thước 256 bits (32 bytes) được chia đều cho **32 probes**, mỗi probe mã hoá **8 bits** (1 byte) trong `top_k=8` tokens.
3. Với mỗi bit trong probe:
   - Bit `1` (Green list token): Logprob cơ bản là $HI = -0.30$.
   - Bit `0` (Red list token): Logprob cơ bản là $LO = -3.20$.
   - Nhiễu Gaussian được thêm ngẫu nhiên vào mỗi request với độ lệch chuẩn $\sigma = 0.55$.
4. Ngưỡng phân định nhị phân nằm ở điểm giữa: $Threshold = \frac{HI + LO}{2} = \frac{-0.30 + (-3.20)}{2} = -1.75$.
5. Gửi truy vấn nhiều lần tới endpoint `POST /api/completions` với prompt `probe:<idx>`, tính trung bình logprob của từng token để triệt tiêu nhiễu Gaussian, so sánh với ngưỡng $-1.75$ và ghép bit (MSB-first) thành byte.
6. Kết quả giải mã 32 bytes thu được flag: `flag{1da51e40cbaa4626a688db2157}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát dịch vụ & API

Kiểm tra trang web chính và các endpoint được công bố:
- `GET /api/model/info`:
  ```json
  {
    "hi": -0.3,
    "lo": -3.2,
    "hint": "probe:<index>, index in [0, n_probes)",
    "n_probes": 32,
    "payload_len_bits": 256,
    "sigma": 0.55,
    "top_k": 8,
    "vocab_size": 256
  }
  ```
- `POST /api/completions`:
  Nhận body: `{"prompt": "probe:<idx>", "top_k": 8, "logprobs": true}`
  Trả về danh sách 8 tokens cùng giá trị `logprob` của từng token.

- Trang `/docs` và mã nguồn JavaScript của trang `/verifier`:
  Hệ thống cung cấp sẵn công thức và thuật toán giải mã phía client:
  ```javascript
  const HI = -0.3, LO = -3.2, TOP_K = 8, N_PROBES = 32;
  const mid = (HI + LO) / 2; // -1.75
  // Với mỗi probe idx từ 0 đến 31:
  // Lấy trung bình cộng logprob của từng token qua K lần lặp
  // Nếu avg > mid: bit = 1, ngược lại bit = 0
  // Ghép 8 bits MSB-first thành 1 byte ký tự
  ```

---

### Bước 2: Cơ sở toán học khử nhiễu (Signal Averaging)

Mỗi giá trị `logprob` quan sát được từ API có dạng:
$$X_i = \mu + \epsilon_i, \quad \epsilon_i \sim \mathcal{N}(0, \sigma^2) \text{ với } \sigma = 0.55$$
Trong đó $\mu \in \{-0.30, -3.20\}$.

Khoảng cách từ hai mức giá trị tới ngưỡng phân định $-1.75$ là:
$$\Delta = |-0.30 - (-1.75)| = |-3.20 - (-1.75)| = 1.45$$

Khi lấy trung bình cộng của $K$ mẫu:
$$\bar{X} = \frac{1}{K}\sum_{i=1}^K X_i \sim \mathcal{N}\left(\mu, \frac{\sigma^2}{K}\right)$$
Sai số chuẩn (Standard Error) giảm tỉ lệ nghịch với căn bậc hai của số mẫu:
$$SE = \frac{\sigma}{\sqrt{K}} = \frac{0.55}{\sqrt{K}}$$

- Với $K = 5$: $SE \approx 0.246 \rightarrow Z = \frac{1.45}{0.246} \approx 5.89\sigma$ (xác suất phân loại sai $< 10^{-8}$).
- Với $K = 10$: $SE \approx 0.174 \rightarrow Z \approx 8.3\sigma$ (xác suất lỗi hầu như bằng 0).

Do server có áp dụng rate-limit (khoảng 100 req/s), chọn $K = 6 \sim 10$ mẫu kết hợp `Session` với thời gian trễ nhỏ (50ms) là tối ưu nhất cả về độ chính xác và tốc độ hoàn thành.

---

### Bước 3: Tái tạo Flag từng byte

Ví dụ với `probe:0`:
```json
"tokens": [
  {"id": 0,   "logprob": -3.2017},  // < -1.75 -> bit 0
  {"id": 17,  "logprob": -0.4694},  // > -1.75 -> bit 1
  {"id": 34,  "logprob": -0.3987},  // > -1.75 -> bit 1
  {"id": 51,  "logprob": -3.5603},  // < -1.75 -> bit 0
  {"id": 68,  "logprob": -3.5726},  // < -1.75 -> bit 0
  {"id": 85,  "logprob": -0.0971},  // > -1.75 -> bit 1
  {"id": 102, "logprob": 0.6687},   // > -1.75 -> bit 1
  {"id": 119, "logprob": -3.5052}   // < -1.75 -> bit 0
]
```
- Dãy bit thu được: `0, 1, 1, 0, 0, 1, 1, 0`
- Giá trị nhị phân: `0b01100110` = `0x66` $\rightarrow$ Ký tự ASCII: `'f'`.

Lần lượt với 32 probes:
| Probe | Bit pattern | Hex | Ký tự |
|:---:|:---:|:---:|:---:|
| 0 | `01100110` | `0x66` | `f` |
| 1 | `01101100` | `0x6c` | `l` |
| 2 | `01100001` | `0x61` | `a` |
| 3 | `01100111` | `0x67` | `g` |
| 4 | `01111011` | `0x7b` | `{` |
| 5..30 | Hex string | ... | `1da51e40cbaa4626a688db2157` |
| 31 | `01111101` | `0x7d` | `}` |

---

## 3. Mã khai thác hoàn chỉnh (`solve_misc5.py`)

```python
#!/usr/bin/env python3
"""
Solver for MISC CHALLENGE 5 (Whisperbox Watermark Preview)
Target: https://6d1fa0d6-6836-4201-882b-0e6dfd061aad.172.31.102.101.nip.io
"""
import requests
import urllib3
import time
import sys

urllib3.disable_warnings()

BASE_URL = 'https://6d1fa0d6-6836-4201-882b-0e6dfd061aad.172.31.102.101.nip.io'
HI = -0.30
LO = -3.20
MID = (HI + LO) / 2.0  # -1.75
TOP_K = 8
N_PROBES = 32
SAMPLES_PER_PROBE = 10

def solve(base_url=BASE_URL):
    base_url = base_url.rstrip('/')
    s = requests.Session()

    info = s.get(f"{base_url}/api/model/info", verify=False, timeout=5).json()
    print(f"[*] Connected to {base_url}")
    print(f"[*] Model Info: {info}")

    n_probes = info.get("n_probes", N_PROBES)
    recovered = []

    print("[*] Extracting watermark bytes across 32 probes...")
    start_time = time.time()

    for idx in range(n_probes):
        acc = [0.0] * TOP_K
        success_count = 0

        for attempt in range(SAMPLES_PER_PROBE):
            try:
                r = s.post(
                    f"{base_url}/api/completions",
                    json={"prompt": f"probe:{idx}", "top_k": TOP_K, "logprobs": True},
                    verify=False,
                    timeout=5
                )
                if r.status_code == 200:
                    tokens = r.json().get("tokens", [])
                    if len(tokens) == TOP_K:
                        for i, t in enumerate(tokens):
                            acc[i] += t["logprob"]
                        success_count += 1
                else:
                    time.sleep(0.05)
            except Exception:
                time.sleep(0.05)

        if success_count == 0:
            print(f"[-] Probe {idx} failed completely!")
            recovered.append(ord('?'))
            continue

        avg = [v / success_count for v in acc]
        bits = [1 if v > MID else 0 for v in avg]
        
        byte_val = 0
        for b in bits:
            byte_val = (byte_val << 1) | b
        recovered.append(byte_val)

        char = chr(byte_val) if 32 <= byte_val <= 126 else f'\\x{byte_val:02x}'
        print(f"  Probe {idx:2d} ({success_count} samples): bits={''.join(map(str, bits))} -> '{char}'")

    flag = bytes(recovered).decode('utf-8', errors='replace')
    elapsed = time.time() - start_time
    print(f"\n[+] Extracted in {elapsed:.2f}s")
    print(f"[+] Raw bytes: {bytes(recovered)}")
    print(f"[+] FLAG: {flag}\n")
    return flag

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    solve(url)
```

---

## 4. Kết quả & Flag

```bash
$ python solvers/solve_misc5.py
[*] Connected to https://6d1fa0d6-6836-4201-882b-0e6dfd061aad.172.31.102.101.nip.io
[*] Model Info: {'hi': -0.3, 'hint': 'probe:<index>, index in [0, n_probes)', 'lo': -3.2, 'n_probes': 32, 'payload_len_bits': 256, 'sigma': 0.55, 'top_k': 8, 'vocab_size': 256}
[*] Extracting watermark bytes across 32 probes...
  Probe  0 (10 samples): bits=01100110 -> 'f'
  Probe  1 (10 samples): bits=01101100 -> 'l'
  Probe  2 (10 samples): bits=01100001 -> 'a'
  Probe  3 (10 samples): bits=01100111 -> 'g'
  Probe  4 (7 samples): bits=01111011 -> '{'
  Probe  5 (6 samples): bits=00110001 -> '1'
  Probe  6 (5 samples): bits=01100100 -> 'd'
  Probe  7 (6 samples): bits=01100001 -> 'a'
  Probe  8 (5 samples): bits=00110101 -> '5'
  Probe  9 (6 samples): bits=00110001 -> '1'
  Probe 10 (5 samples): bits=01100101 -> 'e'
  Probe 11 (6 samples): bits=00110100 -> '4'
  Probe 12 (5 samples): bits=00110000 -> '0'
  Probe 13 (6 samples): bits=01100011 -> 'c'
  Probe 14 (5 samples): bits=01100010 -> 'b'
  Probe 15 (6 samples): bits=01100001 -> 'a'
  Probe 16 (5 samples): bits=01100001 -> 'a'
  Probe 17 (6 samples): bits=00110100 -> '4'
  Probe 18 (5 samples): bits=00110110 -> '6'
  Probe 19 (6 samples): bits=00110010 -> '2'
  Probe 20 (5 samples): bits=00110110 -> '6'
  Probe 21 (6 samples): bits=01100001 -> 'a'
  Probe 22 (5 samples): bits=00110110 -> '6'
  Probe 23 (6 samples): bits=00111000 -> '8'
  Probe 24 (5 samples): bits=00111000 -> '8'
  Probe 25 (6 samples): bits=01100100 -> 'd'
  Probe 26 (5 samples): bits=01100010 -> 'b'
  Probe 27 (6 samples): bits=00110010 -> '2'
  Probe 28 (5 samples): bits=00110001 -> '1'
  Probe 29 (6 samples): bits=00110101 -> '5'
  Probe 30 (5 samples): bits=00110111 -> '7'
  Probe 31 (6 samples): bits=01111101 -> '}'

[+] Extracted in 7.83s
[+] Raw bytes: b'flag{1da51e40cbaa4626a688db2157}'
[+] FLAG: flag{1da51e40cbaa4626a688db2157}
```

Flag:
```text
flag{1da51e40cbaa4626a688db2157}
```
