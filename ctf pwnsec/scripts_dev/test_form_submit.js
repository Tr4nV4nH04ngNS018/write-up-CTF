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
  page.on("console", msg => console.log("[BROWSER CONSOLE]", msg.type(), msg.text()));

  // Setup bot session
  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto("http://127.0.0.1:3000/bot/session", { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  // Create a note
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
      resolve(res.headers.location.split("/").pop());
    });
    req.write(postData);
    req.end();
  });

  await page.goto(`http://127.0.0.1:3000/notes/${noteId}`, { waitUntil: "domcontentloaded" });
  console.log("On note page:", page.url());

  // Try form.submit()
  const formRes = await page.evaluate(() => {
    try {
      const f = document.createElement("form");
      f.action = "/notes";
      f.method = "GET";
      const inp = document.createElement("input");
      inp.name = "search";
      inp.value = "test";
      f.appendChild(inp);
      document.body.appendChild(f);
      f.submit();
      return { success: true };
    } catch (e) {
      return { success: false, error: e.message };
    }
  });

  console.log("Form submit eval result:", formRes);
  await new Promise(r => setTimeout(r, 2000));
  console.log("Page URL after form submit:", page.url());

  await browser.close();
})();
