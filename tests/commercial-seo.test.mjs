import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const read = file => readFile(resolve(root, file), 'utf8');

const pages = [
  ['services/shopify-development.html', 'https://lofts.studio/services/shopify-development.html'],
  ['services/technical-seo-audit.html', 'https://lofts.studio/services/technical-seo-audit.html'],
  ['services/website-redesign.html', 'https://lofts.studio/services/website-redesign.html'],
];

test('priority commercial pages are indexable, canonical, structured, and offer-specific', async () => {
  for (const [file, canonical] of pages) {
    const html = await read(file);
    assert.equal((html.match(/<h1\b/gi) || []).length, 1, `${file} must have one H1`);
    assert.match(html, /<meta name="robots" content="index,follow/i);
    assert.ok(html.includes(`<link rel="canonical" href="${canonical}"`), `${file} canonical`);
    assert.match(html, /"@type"\s*:\s*"Service"/);
    assert.match(html, /"@type"\s*:\s*"BreadcrumbList"/);
    assert.match(html, /<form[^>]+data-lead[^>]+data-service=/);
    assert.match(html, /name="offer"/);
    assert.match(html, /name="service"/);
    assert.ok(html.lastIndexOf('</body>') < html.lastIndexOf('</html>'), `${file} closes body before html`);
    assert.equal(html.slice(html.lastIndexOf('</body>') + 7, html.lastIndexOf('</html>')).trim(), '', `${file} has content after body`);
    for (const raw of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/gi)) JSON.parse(raw[1]);
  }
});

test('website redesign page publishes a useful migration artifact and is discoverable', async () => {
  const [html, sitemap, llms, services, guide] = await Promise.all([
    read('services/website-redesign.html'), read('sitemap.xml'), read('llms.txt'), read('services/index.html'), read('blog/b2b-website-redesign.html'),
  ]);
  assert.match(html, /URL preservation control sheet/i);
  assert.match(html, /Observed evidence|Known value/);
  assert.ok(sitemap.includes('<loc>https://lofts.studio/services/website-redesign.html</loc>'));
  assert.ok(llms.includes('https://lofts.studio/services/website-redesign.html'));
  assert.ok(services.includes('/services/website-redesign.html'));
  assert.ok(guide.includes('/services/website-redesign.html'));
});

test('Shopify page avoids unsupported fixed outcomes and records service context', async () => {
  const html = await read('services/shopify-development.html');
  for (const claim of ['+42%', 'paid for itself', 'in 14 days', 'sub-2s mobile load', '30 days of post-launch support is included', 'stays 30 days post-launch', '68% of revenue', 'within 4 hours']) {
    assert.equal(html.toLowerCase().includes(claim.toLowerCase()), false, `unsupported claim remains: ${claim}`);
  }
  assert.match(html, /name="source" value="shopify-development-review"/);
  assert.match(html, /data-offer="shopify-store-review"/);
});

test('lead analytics include safe attribution, device, offer, and service context', async () => {
  const js = await read('assets/main.js');
  for (const marker of ['safeMarketingUrl', 'device_category', 'service_inquiry_submitted', 'leadContext', "formData.append('source_path'"]) {
    assert.ok(js.includes(marker), `missing analytics marker: ${marker}`);
  }
});

test('shared commercial proof avoids inconsistent project-count claims', async () => {
  const js = await read('assets/main.js');
  assert.doesNotMatch(js, /var proofValue[^\n]*3,400\+/);
  assert.match(js, /available to inspect in the project archive/);
});

test('robots separates answer discovery from model-training crawlers', async () => {
  const robots = await read('robots.txt');
  for (const agent of ['OAI-SearchBot', 'ChatGPT-User', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot']) {
    assert.match(robots, new RegExp(`User-agent: ${agent}\\nAllow: /`));
  }
  assert.doesNotMatch(robots, /User-agent: (?:GPTBot|ClaudeBot|Google-Extended)\nAllow: \//);
});
