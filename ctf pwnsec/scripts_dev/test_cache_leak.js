const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--no-sandbox", "--disable-dev-shm-usage"]
  });

  const page = await browser.newPage();
  page.on("console", msg => console.log("[CONSOLE]", msg.text()));

  // 1. Setup session
  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto("http://127.0.0.1:3000/bot/session", { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  // 2. Navigate to /notes as document navigation
  console.log("Navigating to /notes...");
  const res = await page.goto("http://127.0.0.1:3000/notes", { waitUntil: "domcontentloaded" });
  console.log("Response headers for /notes:", res.headers());

  // 3. Now evaluate fetch('/notes') from inside the page!
  const fetchRes = await page.evaluate(async () => {
    try {
      const r = await fetch('/notes', { cache: 'force-cache' });
      return { status: r.status, text: await r.text() };
    } catch (e) {
      return { error: e.message };
    }
  });

  console.log("Fetch result with force-cache:", fetchRes);

  const fetchRes2 = await page.evaluate(async () => {
    try {
      const r = await fetch('/notes', { cache: 'default' });
      return { status: r.status, text: await r.text() };
    } catch (e) {
      return { error: e.message };
    }
  });

  console.log("Fetch result with default cache:", fetchRes2);

  await browser.close();
})();
