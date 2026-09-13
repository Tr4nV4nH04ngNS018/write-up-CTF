const path = require("path");
const http = require("http");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));

const APP = "http://127.0.0.1:3000";
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

(async () => {
  const browser = await puppeteer.launch({
    headless: "new", executablePath: CHROME,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--js-flags=--jitless"]
  });
  const page = await browser.newPage();
  page.on("console", m => console.log("[CONSOLE]", m.text()));

  await page.setRequestInterception(true);
  page.on("request", request => {
    const externalNavigation = page.url().startsWith(`${APP}/notes/`)
      && request.isNavigationRequest()
      && request.frame() === page.mainFrame()
      && new URL(request.url()).origin !== APP;
    externalNavigation ? request.abort() : request.continue();
  });

  // bot session
  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto(`${APP}/bot/session`, { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  // --- T1: cache read-back ---
  // seed: open a popup to /notes (has bot session, mode navigate)
  console.log("=== T1: cache seed via popup ===");
  const seed = await page.evaluate(() => {
    const w = window.open("http://127.0.0.1:3000/notes");
    return w ? "opened" : "popup blocked";
  });
  console.log("seed popup:", seed);
  await new Promise(r => setTimeout(r, 1500));

  // now force-cache fetch from a NEW same-origin page
  const t1 = await page.evaluate(async () => {
    try {
      const r = await fetch("/notes", { cache: "force-cache" });
      const t = await r.text();
      return { status: r.status, len: t.length, head: t.slice(0, 80) };
    } catch (e) { return { error: e.message }; }
  });
  console.log("T1 force-cache readback (cors-mode should 404 if NOT cached):", t1);

  // --- T2: replaceState then external navigation under interception ---
  console.log("=== T2: replaceState + external nav ===");
  await page.goto(`${APP}/notes/nonexistent`, { waitUntil: "domcontentloaded" });
  const t2 = await page.evaluate(() => {
    try {
      history.replaceState(null, "", "/");
      return { ok: true, url: location.href };
    } catch (e) { return { ok: false, error: e.message }; }
  });
  console.log("replaceState:", t2, "page.url() now:", page.url());

  const before = page.url();
  await page.evaluate(() => { location.href = "http://127.0.0.1:9999/ext?x=1"; });
  await new Promise(r => setTimeout(r, 2500));
  console.log("after external nav: page.url() =", page.url(), "| was:", before);

  await browser.close();
  process.exit(0);
})();