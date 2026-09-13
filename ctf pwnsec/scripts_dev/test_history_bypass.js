const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));

(async () => {
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

  // Navigate to local challenge note
  // First create a note or visit /notes
  await page.goto("http://127.0.0.1:3000/", { waitUntil: "domcontentloaded" });
  console.log("On home:", page.url());

  // Test history.replaceState
  await page.evaluate(() => {
    history.replaceState(null, '', '/notes/test1234');
  });
  console.log("After replaceState to /notes/test1234:", page.url());

  // Now replaceState to /
  await page.evaluate(() => {
    history.replaceState(null, '', '/');
  });
  console.log("After replaceState to /:", page.url());

  // Now navigate to external
  try {
    await page.evaluate(() => {
      location.href = "https://example.com/";
    });
    await new Promise(r => setTimeout(r, 2000));
  } catch (e) {
    console.log("Nav error:", e.message);
  }

  console.log(`Result: aborted=${aborted}, allowed=${allowed}, finalUrl=${page.url()}`);
  await browser.close();
})();
