import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://65b68ef3c79fb356.chal.ctf.ae/login'
data = urllib.parse.urlencode({
    'username': 'archivist',
    'password': 'local_pass_def_not_the_same_on_remote_trust_me'
}).encode('utf-8')

req = urllib.request.Request(url, data=data)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print('Status:', resp.status)
        print('Headers:', dict(resp.headers))
        print('URL:', resp.geturl())
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    body = e.read().decode('utf-8', errors='ignore')
    for l in body.splitlines():
        if 'rejected' in l or 'alert' in l:
            print(l)
except Exception as e:
    print('Error:', e)
