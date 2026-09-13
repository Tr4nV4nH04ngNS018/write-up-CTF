import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://65b68ef3c79fb356.chal.ctf.ae/test<foo>"\'bar'
try:
    with urllib.request.urlopen(url, context=ctx, timeout=10) as resp:
        print('Status:', resp.status)
        body = resp.read().decode('utf-8', errors='ignore')
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    body = e.read().decode('utf-8', errors='ignore')
except Exception as e:
    print('Error:', e)
    body = ""

for line in body.splitlines():
    if 'test' in line:
        print("MATCH:", line)
