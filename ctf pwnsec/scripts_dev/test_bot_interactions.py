import urllib.request, http.cookiejar, subprocess, os, json, tempfile

# 1. Setup bot session
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

req = urllib.request.Request('http://127.0.0.1:3000/bot/session', headers={'X-Bot-Token': 'bot-token'})
resp = opener.open(req)
print('Bot session response:', resp.read().decode())
cookies = list(cj)
print('Cookies:', [(c.name, c.value) for c in cookies])
bot_sid = [c.value for c in cookies if c.name == 'sid'][0]

# Now let's test what happens when curl / python requests /notes with that cookie
req_notes = urllib.request.Request('http://127.0.0.1:3000/notes')
try:
    with opener.open(req_notes) as r:
        print('Notes without Sec-Fetch-Mode (urllib):', r.status, r.read().decode()[:200])
except Exception as e:
    print('Notes without Sec-Fetch-Mode (urllib) failed:', e)

# Now test with Sec-Fetch-Mode: cors
req_cors = urllib.request.Request('http://127.0.0.1:3000/notes', headers={'Sec-Fetch-Mode': 'cors'})
try:
    with opener.open(req_cors) as r:
        print('Notes with Sec-Fetch-Mode cors:', r.status)
except Exception as e:
    print('Notes with Sec-Fetch-Mode cors failed:', e)

# Now test with Sec-Fetch-Mode: navigate
req_nav = urllib.request.Request('http://127.0.0.1:3000/notes', headers={'Sec-Fetch-Mode': 'navigate'})
try:
    with opener.open(req_nav) as r:
        print('Notes with Sec-Fetch-Mode navigate:', r.status, r.read().decode()[:300])
except Exception as e:
    print('Notes with Sec-Fetch-Mode navigate failed:', e)
