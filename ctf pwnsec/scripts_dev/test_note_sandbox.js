const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));
const http = require("http");

(async () => {
  // First, create a note on http://127.0.0.1:3000
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

  console.log("Created note id:", noteId);

  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--no-sandbox", "--disable-dev-shm-usage"]
  });

  const page = await browser.newPage();
  const APP_ORIGIN = "http://127.0.0.1:3000";

  let aborted = false;
  let allowed = false;

  await page.setRequestInterception(true);
  page.on("request", request => {
    const externalNavigation = page.url().startsWith(`${APP_ORIGIN}/notes/`)
      && request.isNavigationRequest()
      && request.frame() === page.mainFrame()
      && new URL(request.url()).origin !== APP_ORIGIN;

    console.log(`[Request] url=${request.url()} page.url=${page.url()} external=${externalNavigation}`);
    if (externalNavigation) {
      aborted = true;
      request.abort();
    } else {
      if (new URL(request.url()).origin !== APP_ORIGIN) allowed = true;
      request.continue();
    }
  });

  await page.goto(`http://127.0.0.1:3000/notes/${noteId}`, { waitUntil: "domcontentloaded" });
  console.log("On note page:", page.url());

  // Test if note page (sandboxed) can call history.replaceState and navigate
  const evalResult = await page.evaluate(() => {
    try {
      history.replaceState(null, '', '/');
      return { success: true, url: location.href };
    } catch (e) {
      return { success: false, error: e.message };
    }
  });
  console.log("Evaluation result:", evalResult);
  console.log("page.url() after eval:", page.url());

  // Now navigate to external
  await page.evaluate(() => {
    location.href = "https://example.com/";
  });

  await new Promise(r => setTimeout(r, 2000));
  console.log(`Result: aborted=${aborted}, allowed=${allowed}, finalUrl=${page.url()}`);
  await browser.close();
})();
