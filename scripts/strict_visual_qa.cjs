const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const baseUrl = process.env.QA_BASE_URL || 'http://127.0.0.1:4196';
const outputDir = process.env.QA_OUTPUT_DIR || '/tmp/lofts-strict-qa';
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const routes = [
  '/',
  '/portfolio/',
  '/services/',
  '/services/wordpress-development.html',
  '/websites/',
  '/websites/law-firms/',
  '/locations/usa/',
  '/locations/california/los-angeles-web-design/',
  '/blog/',
  '/blog/?page=2',
  '/blog/website-structure-audit-report.html',
  '/tools/',
  '/free-audit/',
  '/about.html',
  '/process/',
  '/portfolio/discova.html',
  '/privacy.html',
  '/accessibility.html'
];

function slug(route) {
  return route.replace(/^\//, '').replace(/[/?=&.]+/g, '-').replace(/-+$/g, '') || 'home';
}

async function inspect(page, route, mode) {
  const response = await page.goto(baseUrl + route, { waitUntil: 'networkidle', timeout: 30000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(120);

  const failedImages = await page.locator('img').evaluateAll(images => images
    .filter(image => image.complete && image.naturalWidth === 0)
    .map(image => image.currentSrc || image.src));
  const metrics = await page.evaluate(() => {
    const nav = document.querySelector('.nav-bar');
    const hero = document.querySelector('.hero-scroll-scene, .lofts-visual-hero, .page-hero, .services-hero');
    return {
      title: document.title,
      h1Count: document.querySelectorAll('h1').length,
      mainCount: document.querySelectorAll('main').length,
      horizontalOverflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
      navHeight: nav ? Math.round(nav.getBoundingClientRect().height) : 0,
      navVisible: !!nav && getComputedStyle(nav).display !== 'none',
      heroWidth: hero ? Math.round(hero.getBoundingClientRect().width) : 0,
      theme: document.documentElement.getAttribute('data-theme'),
      lenis: !!window.loftsLenis,
      gsap: typeof window.gsap !== 'undefined',
      visibleBlogCards: document.querySelectorAll('[data-blog-card]:not([hidden])').length
    };
  });

  let menu = { available: false, opened: false, closed: false };
  if (mode === 'mobile') {
    const button = page.locator('#menuBtn');
    if (await button.count()) {
      menu.available = true;
      await button.click();
      await page.waitForTimeout(240);
      menu.opened = await page.locator('#mobilePanel').evaluate(element =>
        element.classList.contains('open') || element.getAttribute('aria-hidden') === 'false');
      const close = page.locator('#menuClose');
      if (await close.count()) await close.click();
      await page.waitForTimeout(240);
      menu.closed = await page.locator('#mobilePanel').evaluate(element =>
        !element.classList.contains('open') && element.getAttribute('aria-hidden') !== 'false');
    }
  }

  if (route === '/' && mode === 'desktop') {
    metrics.canvasBeforeInteraction = await page.locator('[data-home-service-world-canvas] canvas').count();
    await page.evaluate(() => scrollTo(0, 2));
    await page.waitForTimeout(900);
    metrics.canvasAfterInteraction = await page.locator('[data-home-service-world-canvas] canvas').count();
    const before = await page.locator('.hero-title').evaluate(element => {
      const rect = element.getBoundingClientRect();
      return { width: rect.width, height: rect.height };
    });
    await page.evaluate(() => scrollTo(0, 620));
    await page.waitForTimeout(100);
    const after = await page.locator('.hero-title').evaluate(element => {
      const rect = element.getBoundingClientRect();
      return { width: rect.width, height: rect.height };
    });
    metrics.heroSizeDelta = {
      width: Math.abs(before.width - after.width),
      height: Math.abs(before.height - after.height)
    };
    await page.evaluate(() => scrollTo(0, 0));
  }

  const file = path.join(outputDir, mode, slug(route) + '.png');
  await page.screenshot({ path: file, fullPage: false });
  return {
    route,
    mode,
    status: response ? response.status() : 0,
    failedImages,
    menu,
    metrics,
    screenshot: file
  };
}

(async () => {
  fs.rmSync(outputDir, { recursive: true, force: true });
  fs.mkdirSync(path.join(outputDir, 'desktop'), { recursive: true });
  fs.mkdirSync(path.join(outputDir, 'mobile'), { recursive: true });
  const browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const results = [];

  for (const mode of ['desktop', 'mobile']) {
    const context = await browser.newContext({
      viewport: mode === 'desktop' ? { width: 1440, height: 1000 } : { width: 390, height: 844 },
      deviceScaleFactor: 1,
      isMobile: mode === 'mobile',
      hasTouch: mode === 'mobile'
    });
    await context.addInitScript(theme => localStorage.setItem('lofts-theme', theme), mode === 'desktop' ? 'light' : 'dark');
    const page = await context.newPage();
    const runtimeErrors = [];
    page.on('pageerror', error => runtimeErrors.push(String(error)));
    for (const route of routes) results.push(await inspect(page, route, mode));
    results.forEach(result => {
      if (result.mode === mode) result.runtimeErrors = runtimeErrors.slice();
    });
    await context.close();
  }

  await browser.close();
  const failures = results.filter(result =>
    result.status !== 200 ||
    result.failedImages.length ||
    result.metrics.h1Count !== 1 ||
    result.metrics.mainCount !== 1 ||
    result.metrics.horizontalOverflow > 2 ||
    result.metrics.lenis ||
    result.metrics.gsap ||
    (result.mode === 'mobile' && result.menu.available && (!result.menu.opened || !result.menu.closed)) ||
    (result.route.startsWith('/blog/') && result.metrics.visibleBlogCards > 10)
  );
  const report = { generatedAt: new Date().toISOString(), baseUrl, results, failures };
  fs.writeFileSync(path.join(outputDir, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ checked: results.length, failures: failures.length, outputDir }, null, 2));
  if (failures.length) process.exitCode = 1;
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
