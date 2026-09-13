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

  // First set bot session header on session
  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto("http://127.0.0.1:3000/bot/session", { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  // Now create a note
  // Or navigate to a note
  const postData = "title=test&body=hello";
  const noteId = await new Promise(resolve => {
    const req = http.request("http://127.0.0.1:3000/notes", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": postData.length,
        "Sec-Fetch-Mode": "navigate"
      }
    }, res => {
      const loc = res.headers.location;
      resolve(loc.split("/").pop());
    });
    req.write(postData);
    req.end();
  });

  await page.goto(`http://127.0.0.1:3000/notes/${noteId}`, { waitUntil: "domcontentloaded" });

  // Test fetch from inside note page
  const fetchResult = await page.evaluate(async () => {
    const results = {};
    // Test 1: fetch('/notes/')
    try {
      const r1 = await fetch('/notes/');
      results['fetch_slash'] = { status: r1.status, text: await r1.text() };
    } catch (e) {
      results['fetch_slash'] = { error: e.message };
    }

    // Test 2: fetch('/notes')
    try {
      const r2 = await fetch('/notes');
      results['fetch_noslash'] = { status: r2.status, text: await r2.text() };
    } catch (e) {
      results['fetch_noslash'] = { error: e.message };
    }

    // Test 3: fetch('/notes/?search=')
    try {
      const r3 = await fetch('/notes/?search=');
      results['fetch_search'] = { status: r3.status, text: await r3.text() };
    } catch (e) {
      results['fetch_search'] = { error: e.message };
    }

    return results;
  });

  console.log("Fetch results from inside note page:");
  console.log(JSON.stringify(fetchResult, null, 2));

  await browser.close();
})();
