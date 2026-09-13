import os

plugins_dir = 'challenge_mouse/prism_repo/src/plugins'
for p in os.listdir(plugins_dir):
    p_path = os.path.join(plugins_dir, p)
    if os.path.isdir(p_path):
        js_files = [f for f in os.listdir(p_path) if f.endswith('.js')]
        for jf in js_files:
            file_path = os.path.join(p_path, jf)
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # print summary
            print(f"=== Plugin: {p}/{jf} ({len(content)} bytes) ===")
            for line in content.splitlines():
                if any(k in line.lower() for k in ['eval', 'script', 'document.', 'window.', 'import', 'xhr', 'fetch', 'innerhtml']):
                    print('  ', line.strip()[:100])
