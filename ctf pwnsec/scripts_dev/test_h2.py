import socket
import ssl

hostname = "65b68ef3c79fb356.chal.ctf.ae"
port = 443

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ctx.set_alpn_protocols(['h2', 'http/1.1'])

s = socket.create_connection((hostname, port), timeout=10)
ss = ctx.wrap_socket(s, server_hostname=hostname)

print("Negotiated ALPN protocol:", ss.selected_alpn_protocol())
ss.close()
