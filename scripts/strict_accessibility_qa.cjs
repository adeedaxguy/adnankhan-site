const { chromium } = require('playwright-core');
const { source: axeSource } = require('axe-core');
const fs = require('fs');

const baseUrl = process.env.QA_BASE_URL || 'http://127.0.0.1:4196';
const outputFile = process.env.QA_OUTPUT_FILE || '/tmp/lofts-accessibility-qa.json';
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const routes = [
  '/',
  '/portfolio/',
  '/services/',
  '/websites/',
  '/locations/usa/',
  '/blog/',
  '/blog/website-structure-audit-report.html',
  '/tools/',
  '/free-audit/',
  '/about.html',
  '/process/',
  '/portfolio/discova.html',
  '/privacy.html',
  '/accessibility.html'
];

(async () => {
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

    for (const route of routes) {
      const response = await page.goto(baseUrl + route, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(900);
      await page.addScriptTag({ content: axeSource });
      const violations = await page.evaluate(async () => {
        const report = await window.axe.run(document, {
          runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] }
        });
        return report.violations.map(violation => ({
          id: violation.id,
          impact: violation.impact,
          help: violation.help,
          nodes: violation.nodes.map(node => ({ target: node.target, summary: node.failureSummary }))
        }));
      });
      results.push({ route, mode, status: response ? response.status() : 0, violations });
    }
    await context.close();
  }

  await browser.close();
  const failures = results.filter(result => result.status !== 200 || result.violations.length);
  fs.writeFileSync(outputFile, JSON.stringify({ generatedAt: new Date().toISOString(), baseUrl, results, failures }, null, 2));
  console.log(JSON.stringify({ checked: results.length, failures: failures.length, outputFile }, null, 2));
  if (failures.length) process.exitCode = 1;
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
