# Writeup — B1tsy-Ducky (Web / RE)

> **V1t CTF 2026** · Category: Web + Reverse Engineering · Go WebAssembly
>
> **Flag:** `v1t{b1tsy_t1psy_duck_w4sm}`

---

## 1. Tóm tắt (TL;DR)

Challenge là một game **Bitsy** nhúng một module **WebAssembly compile từ Go**. Khi người chơi nói chuyện với "con vịt đặc biệt", trang gọi hàm `duckWasmReveal(referrer, room3, picked32)`. Ba chuỗi này được ghép lại làm *passphrase*, rồi dùng để **dẫn xuất khóa AES-256-GCM** giải mã một ciphertext nhúng sẵn → ra flag.

Để giải, ta cần khôi phục chính xác cả 3 input:

| Input | Giá trị | Nguồn |
|---|---|---|
| `referrer` | `https://b1tsy.v1t.site/` | `document.referrer` — **mảnh khó nhất** |
| `room3` | block ROOM 3 đã serialize | dữ liệu game Bitsy trong HTML |
| `picked32` | `797084dac2504482bcfaec15adc048bb` | CF beacon token trong thẻ `<script>` |

---

## 2. Các file được cung cấp

| File | Vai trò |
|---|---|
| `____V1t_CTF_2026____.html` (795 KB) | Trang game Bitsy + script gọi WASM |
| `main.wasm` (2.7 MB) | Module Go-WASM chứa logic giải mã flag |
| `wasm_exec_js.download` (17 KB) | Go WASM runtime glue (chuẩn) |
| `v833ccba57c9e4d2798f2e76cebdd09a1...` (33 KB) | Thư viện **web-vitals** → **mồi nhử (red herring)** |

> 💡 File JS 33 KB chỉ là thư viện analytics `web-vitals` (chứa `onCLS`, `onFCP`, `onINP`…). Hoàn toàn không liên quan tới việc giải flag.

---

## 3. Phân tích luồng game

Game được viết bằng [Bitsy](https://ledoux.itch.io/bitsy). Trong HTML có đoạn script điều khiển việc gọi WASM:

```js
var specialDuckSpriteId = "c";

// Khi nói chuyện đúng con vịt "c" và đứng kề bên (khoảng cách Manhattan == 1)
function isPlayerTalkingToSpecialDuck() { ... }

// Lấy ROOM 3 từ object `room` trong bộ nhớ rồi serialize lại
function serializeRoomBlock(roomId) {
    var lines = ["ROOM " + roomId];
    for (i = 0; i < roomData.tilemap.length; i++)
        lines.push(roomData.tilemap[i].join(","));
    if (roomData.name != null)  lines.push("NAME " + roomData.name);
    // ... WAL / ITM / EXT / END / PAL / AVA / TUNE
    return lines.join("\n");
}

// Tìm chuỗi 32 hex trong attribute của bất kỳ thẻ <script> nào
function pick32() {
    var re = /\b[a-f0-9]{32}\b/i;
    for (var i = document.scripts.length - 1; i >= 0; i--) {
        for (var j = 0; j < document.scripts[i].attributes.length; j++) {
            var match = document.scripts[i].attributes[j].value.match(re);
            if (match) return match[0];
        }
    }
    return "";
}
```

Hàm trigger (được gắn vào `window.__bdx_17a`) ghép input và gọi WASM:

```js
var room3Block = serializeRoomBlock("3");
var referrer   = document.referrer || "";
var picked32   = pick32();

var flag_decrypt = window.duckWasmReveal(referrer, room3Block, picked32);
// Nếu sai input → "some thing go wrong go to start again"
```

→ **WASM nhận 3 input dưới dạng tham số.** Nghĩa là ta có thể chạy thẳng WASM trong Node và tự gọi hàm, không cần trình duyệt.

---

## 4. Khôi phục 3 input

### 4.1. `picked32` — token 32 hex

`pick32()` quét attribute của các thẻ `<script>` tìm chuỗi 32 ký tự hex. Trong HTML chỉ có **đúng một** chuỗi như vậy, nằm trong attribute `data-cf-beacon` của thẻ web-vitals:

```html
<script ... data-cf-beacon='{"version":"2024.11.0","token":"797084dac2504482bcfaec15adc048bb","r":1}'></script>
```

→ `picked32 = 797084dac2504482bcfaec15adc048bb`

### 4.2. `room3` — block ROOM 3

Dữ liệu game Bitsy nằm trong element `id="exportedGameData"`. ROOM 3 không có ITM/WAL/END/AVA nên `serializeRoomBlock("3")` chính bằng block thô:

```
ROOM 3
0,0,0,f,0,g,g,f,0,0,0,0,0,0,0,0
0,0,0,g,0,g,0,g,g,g,g,0,0,0,0,0
0,0,g,0,0,0,0,0,f,0,f,g,d,g,0,0
0,g,d,0,0,0,0,0,0,0,0,0,0,g,g,0
g,f,g,0,a,0,0,0,0,0,a,0,0,0,g,0
g,0,0,a,0,0,0,a,a,0,0,0,0,0,d,0
f,0,a,0,0,0,0,0,0,0,a,0,0,0,g,0
g,g,0,0,0,0,a,0,a,0,0,0,0,0,g,f
0,g,g,0,0,0,0,0,0,0,0,0,a,0,0,g
0,d,0,0,0,a,0,0,0,0,0,0,0,0,g,g
f,g,g,0,0,0,0,0,0,0,a,0,0,0,d,0
g,0,0,0,0,0,0,0,0,0,0,0,0,0,g,0
g,0,0,a,0,0,0,0,a,0,0,0,0,0,g,0
g,f,0,0,0,0,0,0,0,g,d,g,g,g,f,0
0,g,g,0,0,0,f,g,f,g,0,0,0,0,0,0
0,0,0,g,f,g,0,0,0,0,0,0,0,0,0,0
NAME example room copy 2
EXT 4,0 2 4,15
PAL 0
TUNE 2
```

### 4.3. `referrer` — mảnh khó nhất

`document.referrer` là URL trang dẫn tới game. Vì ciphertext cố định, tác giả phải mã hóa bằng **một giá trị referrer cố định**. Sau khi dịch ngược thuật toán (mục 5) và thử các ứng viên, giá trị đúng là:

```
https://b1tsy.v1t.site/
```

---

## 5. Dịch ngược module WASM

`main.wasm` là Go compile sang WASM. Disassemble ra WAT (dùng `wabt` qua npm) và lọc các hàm `main.*`:

```
main.deriveKey
main.decryptHex
main.duckWasmReveal
main.isValidFlag
```

Đường dẫn source nhúng trong binary: `D:/CTF/V1t_CTF/V1t_CTF_2026/web/B1tsy-Ducky/main.go`.

### 5.1. Các hằng số quan trọng (trích từ data section)

| Địa chỉ | Giá trị | Ý nghĩa |
|---|---|---|
| `197509` | `b1tsy-ducky-aesgcm` (18 byte) | Khóa HMAC |
| `187896` | `\|` (1 byte) | Separator giữa 3 input |
| `188691` | `nonce\|` (6 byte) | Prefix dẫn xuất nonce |
| `225365` | hex 84 ký tự (xem dưới) | Ciphertext nhúng sẵn |

Ciphertext (84 hex = 42 byte):

```
9e8c2b395bbf6bd7434230ab998c6e86f3228c503324c8660715ccd0bc74deb7d6346dfcc4a9614e58cb
```

### 5.2. Chuỗi lời gọi trong `duckWasmReveal`

```
syscall_js.Value.String  × N      ; đọc 3 tham số
runtime.concatstring5             ; ghép referrer | SEP | room3 | SEP | picked32
main.decryptHex                   ; giải mã
... kiểm tra định dạng flag ...
```

`concatstring5` ghép: `referrer + "|" + room3 + "|" + picked32` → **passphrase**.

### 5.3. Kiểm tra định dạng flag (inline trong `duckWasmReveal`)

WASM kiểm tra plaintext sau giải mã:

- độ dài **== 28 byte**
- `plaintext[0..3] == "v1t{"` (byte `0x76 0x31 0x74 0x7b`)
- `plaintext[27] == "}"` (`0x7d`)
- `plaintext[4..26]` (23 ký tự): mỗi byte thuộc `[a-z0-9_]`
  (`char - 'a' <= 25`, hoặc `char - '0' <= 9`, hoặc `char == '_'`)

→ **Format flag: `v1t{` + 23 ký tự `[a-z0-9_]` + `}` = 28 byte.**
Nếu giải mã sai (input sai) → plaintext rác → fail check → trả `"some thing go wrong go to start again"`.

### 5.4. Thuật toán crypto (`deriveKey` + `decryptHex`)

```
passphrase = referrer + "|" + room3 + "|" + picked32

key   = HMAC-SHA256(key = "b1tsy-ducky-aesgcm", msg = passphrase)   # 32 byte → AES-256
nonce = SHA256("nonce|" + passphrase)[:12]                          # 12 byte

plaintext = AES-256-GCM-Open(ciphertext, key, nonce)
```

Chi tiết các lời gọi trong `decryptHex`:

```
encoding_hex.DecodeString   ; 84 hex → 42 byte
main.deriveKey              ; HMAC-SHA256 ra key
crypto_aes.NewCipher        ; AES-256
crypto_cipher.NewGCM        ; GCM
crypto_sha256.Sum256        ; SHA256("nonce|" + passphrase) → nonce
runtime.slicebytetostring   ; plaintext
```

> ⚠️ Ciphertext 42 byte mà plaintext 28 byte ⇒ **GCM tag dài 14 byte** (42 = 28 ciphertext + 14 tag).

---

## 6. Script giải (Python)

Vì GCM khi giải mã phần plaintext chỉ là **AES-CTR**, ta tự reproduce mà không cần xác thực tag (bỏ qua tag để lấy plaintext nhanh):

```python
import hmac, hashlib
from Crypto.Cipher import AES   # pip install pycryptodome

HEXCT    = ("9e8c2b395bbf6bd7434230ab998c6e86f3228c503324c8660"
            "715ccd0bc74deb7d6346dfcc4a9614e58cb")
CT       = bytes.fromhex(HEXCT)             # 42 byte = 28 ciphertext + 14 tag
INFO     = b"b1tsy-ducky-aesgcm"
PICKED32 = "797084dac2504482bcfaec15adc048bb"
REFERRER = "https://b1tsy.v1t.site/"

ROOM3 = """ROOM 3
0,0,0,f,0,g,g,f,0,0,0,0,0,0,0,0
0,0,0,g,0,g,0,g,g,g,g,0,0,0,0,0
0,0,g,0,0,0,0,0,f,0,f,g,d,g,0,0
0,g,d,0,0,0,0,0,0,0,0,0,0,g,g,0
g,f,g,0,a,0,0,0,0,0,a,0,0,0,g,0
g,0,0,a,0,0,0,a,a,0,0,0,0,0,d,0
f,0,a,0,0,0,0,0,0,0,a,0,0,0,g,0
g,g,0,0,0,0,a,0,a,0,0,0,0,0,g,f
0,g,g,0,0,0,0,0,0,0,0,0,a,0,0,g
0,d,0,0,0,a,0,0,0,0,0,0,0,0,g,g
f,g,g,0,0,0,0,0,0,0,a,0,0,0,d,0
g,0,0,0,0,0,0,0,0,0,0,0,0,0,g,0
g,0,0,a,0,0,0,0,a,0,0,0,0,0,g,0
g,f,0,0,0,0,0,0,0,g,d,g,g,g,f,0
0,g,g,0,0,0,f,g,f,g,0,0,0,0,0,0
0,0,0,g,f,g,0,0,0,0,0,0,0,0,0,0
NAME example room copy 2
EXT 4,0 2 4,15
PAL 0
TUNE 2"""

def gcm_keystream_decrypt(key, nonce, ct, taglen=14):
    body = ct[:len(ct) - taglen]                 # phần ciphertext thật
    ecb  = AES.new(key, AES.MODE_ECB)
    ks, ctr = b"", int.from_bytes(nonce + b"\x00\x00\x00\x02", "big")  # GCM: J0+1
    while len(ks) < len(body):
        ks += ecb.encrypt(ctr.to_bytes(16, "big"))
        ctr += 1
    return bytes(a ^ b for a, b in zip(body, ks))

passphrase = (REFERRER + "|" + ROOM3 + "|" + PICKED32).encode()
key   = hmac.new(INFO, passphrase, hashlib.sha256).digest()
nonce = hashlib.sha256(b"nonce|" + passphrase).digest()[:12]

flag = gcm_keystream_decrypt(key, nonce, CT)
print(flag.decode())     # v1t{b1tsy_t1psy_duck_w4sm}
```

> Cách thay thế: chạy thẳng WASM trong Node (`require('./wasm_exec.cjs')` → instantiate `main.wasm` → `globalThis.duckWasmReveal(referrer, room3, picked32)`). Hữu ích để dùng làm "oracle" thử nhanh các giá trị `referrer`.

---

## 7. Flag

```
v1t{b1tsy_t1psy_duck_w4sm}
```

---

## 8. Bài học rút ra

- **Đọc kỹ luồng JS trước khi đụng WASM.** WASM chỉ nhận 3 chuỗi làm tham số → có thể chạy độc lập trong Node, biến nó thành oracle.
- **Mồi nhử:** file `web-vitals` 33 KB không liên quan; chuỗi 32 hex thật sự cần là CF beacon token.
- **GCM khi giải mã phần plaintext chỉ là AES-CTR** → có thể bỏ qua xác thực tag để lấy plaintext, không cần đúng tag length cho việc giải.
- **Key dẫn xuất từ cả 3 input** (referrer + room3 + token) buộc người chơi phải chạy trang thật/khôi phục chính xác môi trường; mấu chốt là đoán đúng `document.referrer = https://b1tsy.v1t.site/`.
