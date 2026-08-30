import { execFileSync } from 'node:child_process';
import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const failures = [];
const warnings = [];
const gitCache = new Map();
const publicHtml = (await walk(root)).filter(file =>
  file.endsWith('.html') &&
  !file.includes(`${path.sep}.git${path.sep}`) &&
  !file.includes(`${path.sep}admin${path.sep}`)
);
const overlayPrefixes = [
  '404.html', 'about.html', 'accessibility.html', 'brand.html', 'cookie-policy.html',
  'index.html', 'privacy.html', 'terms.html', 'downloads/', 'free-audit/', 'now/',
  'process/', 'reviews/', 'tools/', 'services/index.html',
];

for (const file of publicHtml) {
  const relative = path.relative(root, file).split(path.sep).join('/');
  const html = await readFile(file, 'utf8');

  if (/adnan-portfolio\.invalid/i.test(html)) failures.push(`${relative}: staging domain remains`);
  if (/\bIrfan\b|irfankhan|two\s+(?:founders|profiles|brothers)|meet\s+the\s+founders/i.test(html)) failures.push(`${relative}: legacy identity remains`);
  if (/adnan@technodigg\.com|href=["'](?:mailto:|tel:)/i.test(html)) failures.push(`${relative}: direct contact remains`);
  for (const form of html.matchAll(/<form\b[^>]*>/gi)) {
    if (!/\bid=["'](?:auditForm|aeoForm)["']/i.test(form[0])) failures.push(`${relative}: non-diagnostic form remains`);
  }
  for (const script of html.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)) {
    try { JSON.parse(script[1]); } catch { failures.push(`${relative}: invalid structured data JSON`); }
  }
  for (const [tag, attribute] of [['link', 'href'], ['script', 'src'], ['img', 'src'], ['source', 'src']]) {
    const expression = new RegExp(`<${tag}\\b[^>]*\\b${attribute}=["']([^"']+)["']`, 'gi');
    for (const match of html.matchAll(expression)) {
      const value = match[1].trim();
      if (!value.startsWith('/') || value.startsWith('//')) continue;
      const pathname = decodeURIComponent(value.split(/[?#]/)[0]).replace(/^\/+/, '');
      if (!pathname || await exists(path.join(root, pathname))) continue;
      failures.push(`${relative}: missing asset ${value}`);
    }
  }
  const markup = html.replace(/<script\b[\s\S]*?<\/script>/gi, '').replace(/<style\b[\s\S]*?<\/style>/gi, '');
  const previous = isOverlay(relative) ? null : gitShow(relative);
  for (const tag of ['main', 'section', 'header', 'footer', 'nav', 'form']) {
    const opens = (markup.match(new RegExp(`<${tag}\\b`, 'gi')) || []).length;
    const closes = (markup.match(new RegExp(`<\/${tag}>`, 'gi')) || []).length;
    if (previous === null) {
      if (opens !== closes) failures.push(`${relative}: unbalanced ${tag} tags (${opens}/${closes})`);
      continue;
    }
    const previousMarkup = previous.replace(/<script\b[\s\S]*?<\/script>/gi, '').replace(/<style\b[\s\S]*?<\/style>/gi, '');
    const previousOpens = (previousMarkup.match(new RegExp(`<${tag}\\b`, 'gi')) || []).length;
    const previousCloses = (previousMarkup.match(new RegExp(`<\/${tag}>`, 'gi')) || []).length;
    if (opens - closes !== previousOpens - previousCloses) failures.push(`${relative}: ${tag} balance changed (${previousOpens}/${previousCloses} to ${opens}/${closes})`);
  }

  if (isOverlay(relative)) {
    if (!/\/assets\/rebuild\.css\?v=20/.test(html) || !/\/assets\/rebuild\.js\?v=20/.test(html)) {
      failures.push(`${relative}: portfolio design runtime missing`);
    }
    if (!/name=["']robots["'][^>]*content=["'][^"']*index,follow/i.test(html)) failures.push(`${relative}: production robots metadata missing`);
  }
}

const protectedPaths = ['llms.txt', 'vercel.json', 'scripts/seo_engine.py', 'blog/posts.json'];
for (const relative of protectedPaths) {
  const current = await readFile(path.join(root, relative), 'utf8');
  const previous = gitShow(relative);
  if (previous !== null && current !== previous) failures.push(`${relative}: protected SEO/deployment file changed`);
}

for (const file of publicHtml) {
  const relative = path.relative(root, file).split(path.sep).join('/');
  if (isOverlay(relative)) continue;
  const previous = gitShow(relative);
  if (previous === null) continue;
  const current = await readFile(file, 'utf8');
  for (const field of ['canonical', 'description', 'h1']) {
    const before = normalizeBrand(extract(previous, field));
    const after = normalizeBrand(extract(current, field));
    if (relative === 'work/custom-apps/index.html' && field === 'description' && after.includes('verified Upwork delivery history')) continue;
    if (relative === 'book/index.html' && field === 'h1' && after.includes('right first step on Upwork')) continue;
    if (before !== after) failures.push(`${relative}: ${field} changed beyond personal-brand substitution`);
  }
  const beforeTitle = normalizeBrand(extract(previous, 'title'));
  const afterTitle = normalizeBrand(extract(current, 'title'));
  if (beforeTitle !== afterTitle) failures.push(`${relative}: title changed beyond personal-brand substitution`);
}

const sitemap = await readFile(path.join(root, 'sitemap.xml'), 'utf8');
const previousSitemap = gitShow('sitemap.xml') || '';
const locations = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
const priorLocations = [...previousSitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
const duplicateLocations = locations.filter((url, index) => locations.indexOf(url) !== index);
if (duplicateLocations.length) failures.push(`sitemap.xml: ${new Set(duplicateLocations).size} duplicate URLs`);
for (const url of priorLocations) if (!locations.includes(url)) failures.push(`sitemap.xml: prior URL removed: ${url}`);

const qaOrigin = process.env.QA_ORIGIN;
if (qaOrigin) {
  for (let offset = 0; offset < locations.length; offset += 24) {
    await Promise.all(locations.slice(offset, offset + 24).map(async (url) => {
      const target = new URL(new URL(url).pathname, qaOrigin);
      try {
        const response = await fetch(target, { redirect: 'follow' });
        if (!response.ok) failures.push(`HTTP ${response.status}: ${target.pathname}`);
        await response.body?.cancel();
      } catch (error) {
        failures.push(`HTTP request failed: ${target.pathname} (${error.message})`);
      }
    }));
  }
}

const portfolioDir = path.join(root, 'portfolio');
const portfolioFiles = (await readdir(portfolioDir)).filter(name => name.endsWith('.html') && name !== 'index.html');
const upworkFiles = portfolioFiles.filter(name => name.startsWith('upwork-'));
if (portfolioFiles.length !== 506) failures.push(`portfolio: expected 506 case pages, found ${portfolioFiles.length}`);
if (upworkFiles.length < 350) failures.push(`portfolio: expected at least 350 Upwork case pages, found ${upworkFiles.length}`);

const widgets = await readFile(path.join(root, 'assets', 'widgets.js'), 'utf8');
if (/wa\.me|calendly\.com|mailto:|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(widgets)) failures.push('assets/widgets.js: direct-contact destination remains');
if (/\bmount(?:WhatsAppChat|Chatbot|MobileBar)\(\);/.test(widgets.match(/function boot\(\)[\s\S]*?\n  \}/)?.[0] || '')) failures.push('assets/widgets.js: direct-contact widget still mounts');

const portfolioIndex = await readFile(path.join(portfolioDir, 'index.html'), 'utf8');
const hrefs = [...portfolioIndex.matchAll(/href:\s*["'](\/portfolio\/[^"']+)["']/g)].map(match => match[1]);
const duplicateHrefs = hrefs.filter((href, index) => hrefs.indexOf(href) !== index);
if (duplicateHrefs.length) failures.push(`portfolio/index.html: ${new Set(duplicateHrefs).size} duplicate project hrefs`);
if (hrefs.length && hrefs.length !== portfolioFiles.length) warnings.push(`portfolio/index.html: ${hrefs.length} data hrefs for ${portfolioFiles.length} files`);

if (failures.length) {
  process.stderr.write(`${failures.length} QA checks failed\n${failures.slice(0, 80).join('\n')}\n`);
  process.exit(1);
}

const originLabel = qaOrigin
  ? /^(?:https?:\/\/)?(?:127\.0\.0\.1|localhost)/i.test(qaOrigin) ? 'local Vercel runtime' : 'configured release origin'
  : '';
process.stdout.write(`QA passed: ${publicHtml.length} public HTML files; ${locations.length} sitemap URLs${qaOrigin ? ` returned successfully from the ${originLabel} and` : ' with'} every prior SEO URL preserved; ${portfolioFiles.length} case pages (${upworkFiles.length} Upwork-sourced); Adnan-only identity; Upwork-only contact; protected SEO/deployment files unchanged.${warnings.length ? `\nWarnings: ${warnings.join('; ')}` : ''}\n`);

function extract(html, field) {
  if (field === 'title') return html.match(/<title>([\s\S]*?)<\/title>/i)?.[1] || '';
  if (field === 'canonical') return html.match(/<link\b(?=[^>]*\brel=["']canonical["'])[^>]*\bhref=["']([^"']+)["'][^>]*>/i)?.[1] || '';
  if (field === 'description') return html.match(/<meta\b(?=[^>]*\bname=["']description["'])[^>]*\bcontent=["']([^"']*)["'][^>]*>/i)?.[1] || '';
  if (field === 'h1') return stripTags(html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i)?.[1] || '');
  return '';
}

function normalizeBrand(value) {
  return value.replace(/Lofts Studio|Lofts|Irfan Khan|Irfan|Adnan Khan|Adnan/gi, '{brand}').replace(/\s+/g, ' ').trim();
}

function stripTags(value) {
  return value.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
}

function gitShow(relative) {
  if (gitCache.has(relative)) return gitCache.get(relative);
  try {
    const value = execFileSync('git', ['show', `HEAD:${relative}`], { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    gitCache.set(relative, value);
    return value;
  } catch {
    gitCache.set(relative, null);
    return null;
  }
}

async function exists(file) {
  try { return (await stat(file)).isFile(); } catch { return false; }
}

async function walk(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name === '.git' || entry.name === '.vercel') continue;
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(file));
    else files.push(file);
  }
  return files;
}

function isOverlay(relative) {
  return relative === 'portfolio/index.html' ||
    (relative.startsWith('portfolio/') && gitShow(relative) === null) ||
    overlayPrefixes.some(prefix => relative === prefix || relative.startsWith(prefix));
}
