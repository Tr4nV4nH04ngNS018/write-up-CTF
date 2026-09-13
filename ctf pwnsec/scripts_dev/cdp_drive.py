import sys, json, time, base64, urllib.request
import websocket

def new_tab():
    req = urllib.request.Request("http://127.0.0.1:9222/json/new?about:blank", method="PUT")
    d = json.load(urllib.request.urlopen(req))
    return d["webSocketDebuggerUrl"], d["id"]

def drive(url, expr_js="document.body.innerText", wait=9, exprs=None):
    ws_url, tid = new_tab()
    ws = websocket.create_connection(ws_url, timeout=120)
    mid = 0
    def send(method, params=None):
        nonlocal mid
        mid += 1
        ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid:
                return msg
    send("Page.enable")
    send("Runtime.enable")
    send("Page.navigate", {"url": url})
    deadline = time.time() + 60
    while time.time() < deadline:
        ws.settimeout(5)
        try:
            msg = json.loads(ws.recv())
            if msg.get("method") == "Page.loadEventFired":
                break
        except Exception:
            break
    time.sleep(wait)
    out = {}
    for name, expr in (exprs or {"text": expr_js}).items():
        r = send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        v = r.get("result", {}).get("result", {})
        out[name] = v.get("value") if v.get("type") != "undefined" else None
    ws.close()
    return out

if __name__ == "__main__":
    url = sys.argv[1]
    res = drive(url)
    print(json.dumps(res, ensure_ascii=False)[:20000])