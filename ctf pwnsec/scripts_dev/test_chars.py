import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

chars = "<>\"'&/\\;%#?{}()[]`~^|: \t\r\n"
url = 'https://65b68ef3c79fb356.chal.ctf.ae/'

for c in chars:
    path = f"/test{c}test"
    try:
        # urlencode only if necessary
        req_url = 'https://65b68ef3c79fb356.chal.ctf.ae' + path
        with urllib.request.urlopen(req_url, context=ctx, timeout=5) as resp:
            pass
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        for l in body.splitlines():
            if 'record of' in l:
                print(f"Char {repr(c)}: {l.strip()}")
    except Exception as e:
        print(f"Char {repr(c)}: {e}")
