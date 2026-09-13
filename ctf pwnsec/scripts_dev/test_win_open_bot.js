const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));
const http = require("http");

(async () => {
  // Simple attacker server
  const server = http.createServer((req, res) => {
    res.setHeader("Content-Type", "text/html");
    res.end(`<!doctype html>
<html>
<body>
<script>
console.log("Attacker page loaded");
const w = window.open("about:blank", "testwin");
console.log("window.open returned:", w ? "WINDOW_OBJECT" : "NULL");
if (w) {
  w.location = "http://127.0.0.1:3000/notes";
  console.log("Navigated w to /notes");
}
</script>
</body>
</html>`);
  });

  await new Promise(r => server.listen(9876, r));

  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--no-sandbox", "--disable-dev-shm-usage"]
  });

  const page = await browser.newPage();
  page.on("console", msg => console.log("[BOT CONSOLE]", msg.type(), msg.text()));

  await page.goto("http://127.0.0.1:9876/", { waitUntil: "domcontentloaded" });
  await new Promise(r => setTimeout(r, 2000));

  const targets = browser.targets().map(t => t.url());
  console.log("Browser targets:", targets);

  await browser.close();
  server.close();
})();
