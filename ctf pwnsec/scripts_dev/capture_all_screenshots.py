import time
from playwright.sync_api import sync_playwright

target_url = "https://65b68ef3c79fb356.chal.ctf.ae"
pickle_url = "https://0c6523a28168f7fd.chal.ctf.ae"
webhook_url = "https://webhook.site/#!/08470564-f80c-4271-b2f2-8acc4f44a5a9"
evil_url = f"{pickle_url}/static/evil.html"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)

    # 1. Capture Neon Skies Homepage
    print("[*] Capturing Homepage...", flush=True)
    page1 = browser.new_page(viewport={"width": 1280, "height": 800})
    page1.goto(target_url, wait_until="domcontentloaded", timeout=15000)
    time.sleep(1.5)
    page1.screenshot(path="images/step1_neon_skies_home.png")
    page1.close()
    print("Saved images/step1_neon_skies_home.png", flush=True)

    # 2. Capture Report Desk (filled with evil.html URL)
    print("[*] Capturing Report Desk with evil.html input...", flush=True)
    page2 = browser.new_page(viewport={"width": 1280, "height": 800})
    page2.goto(f"{target_url}/report", wait_until="domcontentloaded", timeout=15000)
    time.sleep(1)
    page2.fill('input[name="url"]', evil_url)
    page2.screenshot(path="images/step2_report_desk_input.png")
    page2.close()
    print("Saved images/step2_report_desk_input.png", flush=True)

    # 3. Capture Pickle Webapp
    print("[*] Capturing Pickle Webapp...", flush=True)
    page3 = browser.new_page(viewport={"width": 1280, "height": 800})
    page3.goto(pickle_url, wait_until="domcontentloaded", timeout=15000)
    time.sleep(1)
    page3.screenshot(path="images/step3_pickle_instance.png")
    page3.close()
    print("Saved images/step3_pickle_instance.png", flush=True)

    # 4. Capture Webhook.site with captured requests
    print("[*] Capturing Webhook.site UI...", flush=True)
    page4 = browser.new_page(viewport={"width": 1400, "height": 850})
    page4.goto(webhook_url, wait_until="domcontentloaded", timeout=20000)
    time.sleep(4)  # Wait for Angular dashboard to render
    page4.screenshot(path="images/step5_webhook_live.png")
    page4.close()
    print("Saved images/step5_webhook_live.png", flush=True)

    browser.close()
    print("[+] All live screenshots captured successfully!", flush=True)
