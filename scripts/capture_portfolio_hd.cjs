#!/usr/bin/env node
const { chromium } = require("playwright-core");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const DATA_FILE = path.join(ROOT, "portfolio", "portfolio.json");
const OUT_DIR = path.join(ROOT, "assets", "work", "portfolio-hd");
const TEMP_DIR = path.join(OUT_DIR, ".tmp");
const WIDTH = 2200;
const HEIGHT = 1375;
const CONCURRENCY = Number(process.env.PORTFOLIO_HD_CONCURRENCY || 4);
const LIVE_TIMEOUT = Number(process.env.PORTFOLIO_HD_LIVE_TIMEOUT || 12000);
const ITEM_TIMEOUT = Number(process.env.PORTFOLIO_HD_ITEM_TIMEOUT || 30000);
const FORCE = process.argv.includes("--force");
const CHROME_PATHS = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium"
].filter(Boolean);

function findExecutable(candidates) {
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  return null;
}

const chromePath = findExecutable(CHROME_PATHS);
if (!chromePath) {
  console.error("Chrome was not found. Set CHROME_PATH to a Chromium-compatible executable.");
  process.exit(1);
}

function slugify(input) {
  return String(input || "portfolio")
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "portfolio";
}

function normalizeUrl(input) {
  const raw = String(input || "").trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;
  return `https://${raw}`;
}

function escapeHtml(input) {
  return String(input || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fallbackHtml(item) {
  const name = escapeHtml(item.name || item.slug || "Selected work");
  const platform = escapeHtml(item.platform || "Website");
  const category = escapeHtml((item.category || "").split("·")[0].trim() || "Lofts Studio");
  const year = escapeHtml(item.year || "Shipped work");
  return `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8" />
      <style>
        @font-face {
          font-family: "Libertinus Math";
          src: local("Libertinus Math");
        }
        :root {
          color-scheme: light;
          --ink: #171310;
          --muted: #726a60;
          --paper: #f6f1e9;
          --line: #d8cdbc;
          --accent: #a9452c;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          width: ${WIDTH}px;
          height: ${HEIGHT}px;
          overflow: hidden;
          background:
            radial-gradient(circle at 80% 18%, rgba(169, 69, 44, .12), transparent 28%),
            linear-gradient(135deg, #fbf8f1 0%, #f2eadf 56%, #e7d7c2 100%);
          color: var(--ink);
          font-family: "Libertinus Math", Georgia, serif;
        }
        .frame {
          position: absolute;
          inset: 72px;
          border: 1px solid rgba(56, 45, 35, .24);
          border-radius: 28px;
          overflow: hidden;
          background:
            linear-gradient(rgba(99, 83, 66, .055) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 83, 66, .055) 1px, transparent 1px),
            rgba(255,255,255,.22);
          background-size: 72px 72px;
          box-shadow: 0 44px 110px rgba(44, 32, 24, .18);
        }
        .bar {
          height: 76px;
          border-bottom: 1px solid rgba(56, 45, 35, .18);
          background: rgba(246, 241, 233, .72);
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 0 36px;
        }
        .dot { width: 12px; height: 12px; border-radius: 50%; background: #a9452c; opacity: .9; }
        .dot:nth-child(2) { background: #c09b62; }
        .dot:nth-child(3) { background: #8ca081; }
        .content {
          position: absolute;
          left: 112px;
          right: 112px;
          bottom: 112px;
        }
        .kicker {
          font: 700 28px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
          letter-spacing: .22em;
          text-transform: uppercase;
          color: var(--muted);
          margin-bottom: 42px;
        }
        h1 {
          max-width: 13ch;
          margin: 0;
          font-size: 138px;
          line-height: .92;
          letter-spacing: -.045em;
          font-weight: 400;
        }
        .pill {
          display: inline-flex;
          margin-top: 48px;
          padding: 18px 30px 16px;
          border: 1px solid rgba(56, 45, 35, .18);
          border-radius: 999px;
          background: rgba(255,255,255,.64);
          color: var(--muted);
          font-size: 34px;
        }
        .meta {
          position: absolute;
          right: 112px;
          bottom: 116px;
          max-width: 430px;
          color: var(--muted);
          font: 700 26px/1.45 ui-monospace, SFMono-Regular, Menlo, monospace;
          letter-spacing: .1em;
          text-transform: uppercase;
          text-align: right;
        }
        .mark {
          position: absolute;
          top: 155px;
          right: 128px;
          width: 340px;
          height: 340px;
          border-radius: 42px;
          border: 1px solid rgba(56, 45, 35, .12);
          transform: rotate(-8deg);
          background:
            linear-gradient(145deg, rgba(255,255,255,.74), rgba(196,156,102,.15)),
            radial-gradient(circle at 68% 24%, rgba(169,69,44,.34), transparent 28%);
        }
      </style>
    </head>
    <body>
      <div class="frame">
        <div class="bar"><i class="dot"></i><i class="dot"></i><i class="dot"></i></div>
        <div class="mark"></div>
        <main class="content">
          <div class="kicker">Portfolio preview</div>
          <h1>${name}</h1>
          <div class="pill">${category}</div>
        </main>
        <div class="meta">${platform}<br>${year}</div>
      </div>
    </body>
  </html>`;
}

function webpFromPng(source, target) {
  execFileSync("cwebp", ["-quiet", "-q", "88", "-sharp_yuv", source, "-o", target], {
    stdio: ["ignore", "ignore", "pipe"]
  });
}

async function captureLive(page, item, pngPath) {
  const url = normalizeUrl(item.url);
  if (!url) return { ok: false, reason: "no-url" };
  let response;
  try {
    response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: LIVE_TIMEOUT });
    await page.waitForLoadState("networkidle", { timeout: 2600 }).catch(() => {});
    await page.waitForTimeout(650);
  } catch (error) {
    return { ok: false, reason: String(error.message || error).slice(0, 180) };
  }

  const status = response ? response.status() : 0;
  const blocked = await page.evaluate(() => {
    const text = document.body ? document.body.innerText.slice(0, 900).toLowerCase() : "";
    const title = document.title.toLowerCase();
    return /403 forbidden|access denied|temporarily unavailable|server error|this site can.t be reached/.test(`${title} ${text}`);
  }).catch(() => false);

  if (status >= 400 || blocked) {
    return { ok: false, reason: `http-or-blocked-${status}` };
  }

  await page.screenshot({ path: pngPath, type: "png", fullPage: false, animations: "disabled", timeout: 7000 });
  return { ok: true, reason: "live" };
}

async function captureFallback(page, item, pngPath) {
  await page.setViewportSize({ width: WIDTH, height: HEIGHT });
  await page.setContent(fallbackHtml(item), { waitUntil: "domcontentloaded", timeout: 5000 });
  await page.screenshot({ path: pngPath, type: "png", fullPage: false, animations: "disabled", timeout: 5000 });
  return { ok: true, reason: "fallback" };
}

function withTimeout(task, timeoutMs, label) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${label} timed out after ${timeoutMs}ms`)), timeoutMs);
  });
  return Promise.race([task, timeout]).finally(() => clearTimeout(timer));
}

async function newCapturePage(browser) {
  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 1,
    colorScheme: "light",
    reducedMotion: "reduce",
    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
  });
  const page = await context.newPage();
  page.setDefaultTimeout(LIVE_TIMEOUT);
  return { context, page };
}

async function processItem(browser, item, index, total) {
  const slug = slugify(item.slug || item.name);
  const target = path.join(OUT_DIR, `${slug}.webp`);
  if (!FORCE && fs.existsSync(target)) {
    return { slug, mode: "kept", target: path.relative(ROOT, target) };
  }

  const pngPath = path.join(TEMP_DIR, `${slug}.png`);
  let result;
  let liveContext;
  try {
    const live = await newCapturePage(browser);
    liveContext = live.context;
    result = await withTimeout(captureLive(live.page, item, pngPath), ITEM_TIMEOUT, `${slug} live capture`);
  } catch (error) {
    result = { ok: false, reason: String(error.message || error).slice(0, 180) };
  } finally {
    if (liveContext) await liveContext.close().catch(() => {});
  }

  if (!result || !result.ok) {
    let fallbackContext;
    try {
      const fallback = await newCapturePage(browser);
      fallbackContext = fallback.context;
      result = await withTimeout(captureFallback(fallback.page, item, pngPath), 10000, `${slug} fallback capture`);
    } finally {
      if (fallbackContext) await fallbackContext.close().catch(() => {});
    }
  }

  webpFromPng(pngPath, target);
  fs.rmSync(pngPath, { force: true });
  console.log(`${String(index + 1).padStart(3, "0")}/${total} ${slug} ${result.reason}`);
  return { slug, mode: result.reason, target: path.relative(ROOT, target) };
}

async function runQueue(items, worker) {
  const results = [];
  let index = 0;
  async function next() {
    while (index < items.length) {
      const current = index++;
      results[current] = await worker(items[current], current);
    }
  }
  await Promise.all(Array.from({ length: Math.min(CONCURRENCY, items.length) }, next));
  return results;
}

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.mkdirSync(TEMP_DIR, { recursive: true });
  const data = JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
  const items = data.items || [];
  const browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const results = await runQueue(items, (item, index) => processItem(browser, item, index, items.length));
  await browser.close();

  const bySlug = new Map(results.map((result) => [result.slug, result]));
  for (const item of items) {
    const slug = slugify(item.slug || item.name);
    const result = bySlug.get(slug);
    if (!result) continue;
    item.image = `/assets/work/portfolio-hd/${slug}.webp`;
    item.imageWidth = WIDTH;
    item.imageHeight = HEIGHT;
    delete item.hideScreenshot;
  }

  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2) + "\n");
  fs.rmSync(TEMP_DIR, { recursive: true, force: true });

  const summary = results.reduce((acc, result) => {
    acc[result.mode] = (acc[result.mode] || 0) + 1;
    return acc;
  }, {});
  console.log(JSON.stringify({ total: items.length, summary }, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
