import urllib.request
import urllib.parse
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://65b68ef3c79fb356.chal.ctf.ae/login'
data = urllib.parse.urlencode({
    'username': 'test<foo>"\'bar',
    'password': 'wrong'
}).encode('utf-8')

req = urllib.request.Request(url, data=data)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='ignore')

for line in body.splitlines():
    if 'test' in line:
        print("MATCH:", line)
