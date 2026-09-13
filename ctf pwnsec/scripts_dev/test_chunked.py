import socket
import ssl

hostname = "65b68ef3c79fb356.chal.ctf.ae"
port = 443

def send_raw(raw_data):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    s = socket.create_connection((hostname, port), timeout=10)
    ss = ctx.wrap_socket(s, server_hostname=hostname)
    ss.sendall(raw_data)
    response = b""
    ss.settimeout(3)
    try:
        while True:
            chunk = ss.recv(4096)
            if not chunk:
                break
            response += chunk
    except socket.timeout:
        pass
    ss.close()
    return response

# Test 1: Standard chunked POST
body = b"4\r\ntest\r\n0\r\n\r\n"
req = (
    f"POST /login HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Content-Type: application/x-www-form-urlencoded\r\n"
    f"Connection: keep-alive\r\n"
    f"\r\n"
).encode() + body

res = send_raw(req)
print("Standard chunked POST response:")
print(res.decode('utf-8', errors='ignore')[:300])
