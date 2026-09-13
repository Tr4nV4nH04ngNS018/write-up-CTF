const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../challenge_mouse/bot/node_modules/puppeteer-core"));
const http = require("http");

(async () => {
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

  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--no-sandbox", "--disable-dev-shm-usage"]
  });

  const page = await browser.newPage();
  page.on("console", msg => console.log("[BROWSER CONSOLE]", msg.type(), msg.text()));
  await page.setExtraHTTPHeaders({ "X-Bot-Token": "bot-token" });
  await page.goto("http://127.0.0.1:3000/bot/session", { waitUntil: "domcontentloaded" });
  await page.setExtraHTTPHeaders({});

  await page.goto(`http://127.0.0.1:3000/notes/${noteId}`, { waitUntil: "domcontentloaded" });

  const result = await page.evaluate(async () => {
    return new Promise(resolve => {
      const ifr = document.createElement("iframe");
      ifr.src = "/notes";
      ifr.onload = () => {
        try {
          resolve({ status: "LOADED", content: ifr.contentDocument.body.innerHTML });
        } catch (e) {
          resolve({ status: "LOADED_BLOCKED", error: e.message });
        }
      };
      ifr.onerror = (e) => resolve({ status: "ERROR" });
      document.body.appendChild(ifr);
      setTimeout(() => resolve({ status: "TIMEOUT" }), 2000);
    });
  });

  console.log("Iframe test result:", result);
  await browser.close();
})();
