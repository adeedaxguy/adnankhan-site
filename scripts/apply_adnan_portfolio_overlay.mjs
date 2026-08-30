import { cp, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const repo = process.cwd();
const overlay = path.resolve(process.argv[2] || '');
const site = path.join(overlay, 'site');
const upwork = 'https://www.upwork.com/freelancers/wordpressandshopifydeveloper';
const productionRobots = '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />';
const upworkCta = `<a class="btn btn-primary" href="${upwork}" target="_blank" rel="noopener noreferrer">Continue on Upwork ↗</a>`;

if (!overlay || !(await exists(path.join(site, 'index.html')))) {
  throw new Error('Pass the local Adnan portfolio project directory.');
}

const overlays = [
  ['index.html', 'index.html'],
  ['about.html', 'about.html'],
  ['404.html', '404.html'],
  ['accessibility.html', 'accessibility.html'],
  ['brand.html', 'brand.html'],
  ['cookie-policy.html', 'cookie-policy.html'],
  ['privacy.html', 'privacy.html'],
  ['terms.html', 'terms.html'],
  ['process', 'process'],
  ['reviews', 'reviews'],
  ['free-audit', 'free-audit'],
  ['tools', 'tools'],
  ['now', 'now'],
  ['services/index.html', 'services/index.html'],
  ['downloads', 'downloads'],
  ['assets/rebuild.css', 'assets/rebuild.css'],
  ['assets/rebuild.js', 'assets/rebuild.js'],
  ['assets/reviews.css', 'assets/reviews.css'],
  ['assets/reviews.js', 'assets/reviews.js'],
  ['assets/reviews.json', 'assets/reviews.json'],
  ['assets/fonts', 'assets/fonts'],
  ['assets/vendor', 'assets/vendor'],
  ['assets/work/portfolio-hd', 'assets/work/portfolio-hd'],
];

const productionized = new Set();
const trackedPortfolio = new Set(
  execFileSync('git', ['ls-tree', '-r', '--name-only', 'HEAD', 'portfolio'], { cwd: repo, encoding: 'utf8' })
    .trim()
    .split('\n')
    .filter(Boolean)
);

for (const relative of trackedPortfolio) {
  if (!relative.endsWith('.html') || relative === 'portfolio/index.html') continue;
  const original = execFileSync('git', ['show', `HEAD:${relative}`], { cwd: repo, encoding: 'utf8' });
  await writeFile(path.join(repo, relative), original);
}

for (const source of await walk(path.join(site, 'portfolio'))) {
  if (!source.endsWith('.html')) continue;
  const relative = `portfolio/${path.basename(source)}`;
  if (relative !== 'portfolio/index.html' && trackedPortfolio.has(relative)) continue;
  const destination = path.join(repo, relative);
  await cp(source, destination, { force: true });
  productionized.add(destination);
}

for (const [from, to] of overlays) {
  const source = path.join(site, from);
  if (!(await exists(source))) continue;
  const destination = path.join(repo, to);
  await cp(source, destination, { recursive: true, force: true });
  if ((await stat(source)).isDirectory()) {
    for (const file of await walk(destination)) if (file.endsWith('.html')) productionized.add(file);
  } else if (destination.endsWith('.html')) {
    productionized.add(destination);
  }
}

for (const file of await walk(repo)) {
  if (!file.endsWith('.html') || file.includes(`${path.sep}.git${path.sep}`) || file.includes(`${path.sep}admin${path.sep}`)) continue;
  let html = await readFile(file, 'utf8');
  const isOverlay = productionized.has(file);

  html = html
    .replaceAll('https://adnan-portfolio.invalid', 'https://lofts.studio')
    .replace(/\sdata-domain-pending=["']true["']/gi, '')
    .replace(/\/assets\/rebuild\.css\?v=\d+/g, '/assets/rebuild.css?v=20')
    .replace(/\/assets\/rebuild\.js\?v=\d+/g, '/assets/rebuild.js?v=20')
    .replace(/((?:\/|\.\.\/)assets\/widgets\.js)\?v=[^"']+/g, '$1?v=20260830a');

  if (isOverlay) {
    const robots = /<meta\b(?=[^>]*\bname=["']robots["'])[^>]*>/i;
    html = robots.test(html) ? html.replace(robots, productionRobots) : html.replace(/<head>/i, `<head>\n${productionRobots}`);
  }

  if (!/\/assets\/rebuild\.css\?v=20/i.test(html)) {
    html = html.replace(/<\/head>/i, '<link rel="stylesheet" href="/assets/rebuild.css?v=20" />\n</head>');
  }
  if (!/\/assets\/rebuild\.js\?v=20/i.test(html)) {
    html = html.replace(/<\/body>/i, '<script src="/assets/rebuild.js?v=20" defer></script>\n</body>');
  }

  html = html
    .replace(/<li>\s*<a\b[^>]*href=["']https:\/\/www\.upwork\.com\/freelancers\/irfankhan[^"']*["'][^>]*>[\s\S]*?<\/a>\s*<\/li>/gi, '')
    .replace(/\s*<a\b[^>]*href=["']https:\/\/www\.upwork\.com\/freelancers\/wordpressandshopifydeveloper[^"']*["'][^>]*>Irfan(?: Khan)?['’]s profile<\/a>/gi, '')
    .replace(/https:\/\/www\.upwork\.com\/freelancers\/irfankhan[^"'\s<]*/gi, upwork)
    .replace(/Directly with Adnan who write the code\s*(?:&mdash;|—|\\u2014)\s*Adnan and Irfan, both Top Rated on Upwork\. No account managers, no junior handoffs\. You can hire us directly or run the project documented and milestone-led through Upwork\./gi, 'Directly with Adnan Khan, the senior specialist who plans and builds the work. No account managers and no junior handoffs. Projects originating on Upwork stay documented and milestone-led there.')
    .replace(/When a website isn['’]t enough\. (?:Irfan|Adnan) leads custom application engineering at (?:Lofts Studio|Adnan Khan)\s*(?:&mdash;|—)\s*React, Next\.js, Node\.js, integrations, internal tools, SaaS frontends\. 700\+ projects under (?:his|their) belt, high-volume tracked client value\./gi, 'When a website is not enough, Adnan leads the application engineering directly — React, Next.js, Node.js, integrations, internal tools, and SaaS frontends — backed by a verified Upwork delivery history.')
    .replace(/Custom web app engineering\s*(?:&mdash;|—)\s*React, Next\.js, Node\.js, custom Shopify apps, API integrations\. Led by (?:Irfan|Adnan)(?: Khan)? \(Top Rated, 700\+ projects\)\. (?:Lofts Studio|Adnan Khan)\./gi, 'Custom web app engineering — React, Next.js, Node.js, custom Shopify apps, and API integrations, led directly by Adnan Khan with a verified Upwork delivery history.')
    .replace(/4\.8\/5 across 699 public reviews\./gi, 'a verified public work history.')
    .replace(/Adnan Khan \(Multan\) leads ecommerce\. Irfan Khan \(Dubai\) leads full-stack\. Both Top Rated on Upwork\./gi, 'Adnan Khan leads ecommerce, frontend, full-stack implementation, and technical delivery, backed by a verified Upwork work history.')
    .replace(/Two founders\. Two cities\./gi, 'One senior owner. Direct delivery.')
    .replace(/Meet the founders/gi, 'Meet Adnan')
    .replace(/You work directly with the brothers who write the code\s*(?:&mdash;|—)\s*Adnan in Multan, Irfan in Dubai\.[\s\S]*?your call\./gi, 'You work directly with Adnan Khan, the senior specialist who plans and builds the work. Projects originating on Upwork stay documented and milestone-led there.')
    .replace(/Senior web engineering led by brothers[\s\S]*?Built for (?:owners|founders) who can tell the difference between a site that merely launches and one that earns its keep\./gi, 'Senior web engineering led directly by Adnan Khan. Strategy, interface, implementation, and QA stay with one accountable owner.')
    .replace(/Senior web engineering led by brothers Adnan Khan and Irfan Khan\./gi, 'Senior web engineering led directly by Adnan Khan.')
    .replace(/\bIrfan Khan\b/gi, 'Adnan Khan')
    .replace(/\bIrfan\b/gi, 'Adnan')
    .replace(/Adnan(?: Khan)?\s+(?:and|&)\s+Adnan(?: Khan)?/gi, 'Adnan Khan')
    .replace(/Multan, Pakistan\s*(?:&nbsp;)?(?:&middot;|·)(?:&nbsp;)?\s*Dubai, UAE\s*(?:&nbsp;)?(?:&middot;|·)(?:&nbsp;)?/gi, 'Multan, Pakistan &nbsp;&middot;&nbsp; ')
    .replace(/Multan, Pakistan\s*(?:&nbsp;)?(?:&middot;|·)(?:&nbsp;)?\s*Dubai, UAE/gi, 'Multan, Pakistan')
    .replace(/\bthe brothers\b/gi, 'Adnan')
    .replace(/\bbrothers\b/gi, 'senior specialist')
    .replace(/\bLofts Studio\b/gi, 'Adnan Khan')
    .replace(/\bLofts\b(?![\w-]|\.studio)/g, 'Adnan')
    .replace(/<form\b[^>]*>[\s\S]*?<\/form>/gi, form => /\bid=["'](?:auditForm|aeoForm)["']/i.test(form) ? form : `<div class="upwork-only-cta">${upworkCta}</div>`)
    .replace(/<a\b[^>]*href=["'](?:mailto:|tel:)[^"']*["'][^>]*>[\s\S]*?<\/a>/gi, upworkCta)
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, 'Upwork Messages');

  html = html.replace(/[ \t]+$/gm, '');

  await writeFile(file, html);
}

const sitemapPath = path.join(repo, 'sitemap.xml');
let sitemap = await readFile(sitemapPath, 'utf8');
const known = new Set([...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]));
const portfolioFiles = (await walk(path.join(repo, 'portfolio'))).filter(file => file.endsWith('.html') && !file.endsWith(`${path.sep}index.html`));
const additions = [];
for (const file of portfolioFiles) {
  const route = `https://lofts.studio/portfolio/${path.basename(file)}`;
  if (known.has(route)) continue;
  additions.push(`  <url>\n    <loc>${route}</loc>\n    <lastmod>2026-08-30</lastmod>\n    <changefreq>yearly</changefreq>\n    <priority>0.55</priority>\n  </url>`);
}
if (additions.length) sitemap = sitemap.replace(/\s*<\/urlset>/, `\n${additions.join('\n')}\n</urlset>`);
await writeFile(sitemapPath, sitemap);

process.stdout.write(`Applied Adnan portfolio overlay: ${productionized.size} authored pages and ${additions.length} new sitemap entries.\n`);

async function exists(file) {
  try { await stat(file); return true; } catch { return false; }
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
