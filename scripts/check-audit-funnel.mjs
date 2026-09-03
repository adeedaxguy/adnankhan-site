import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const manifest = JSON.parse(await readFile(resolve(root, 'project-seo/audit-funnel-routes.json'), 'utf8'));
const sitemap = await readFile(resolve(root, 'sitemap.xml'), 'utf8');
const sharedJs = await readFile(resolve(root, 'assets/main.js'), 'utf8');
const vercel = JSON.parse(await readFile(resolve(root, 'vercel.json'), 'utf8'));
const failures = [];

for (const route of manifest.routes) {
  const html = await readFile(resolve(root, route.file), 'utf8');
  const title = html.match(/<title>([^<]+)<\/title>/i)?.[1]?.trim();
  const description = html.match(/<meta\s+name="description"\s+content="([^"]+)"/i)?.[1]?.trim();
  const canonicals = [...html.matchAll(/<link\s+rel="canonical"\s+href="([^"]+)"/gi)].map(match => match[1]);
  const h1s = [...html.matchAll(/<h1\b/gi)];

  if (!title) failures.push(`${route.path}: missing title`);
  if (!description) failures.push(`${route.path}: missing description`);
  if (canonicals.length !== 1 || canonicals[0] !== route.canonical) failures.push(`${route.path}: canonical mismatch`);
  if (h1s.length !== 1) failures.push(`${route.path}: expected one H1, found ${h1s.length}`);
  if (!/name="robots"\s+content="index,follow/i.test(html)) failures.push(`${route.path}: missing indexable robots meta`);
  if (!sitemap.includes(`<loc>${route.canonical}</loc>`)) failures.push(`${route.path}: missing from sitemap`);
  if (html.includes('audited_url') || /event_label:\s*url/.test(html)) failures.push(`${route.path}: analytics payload may include an audited URL`);

  for (const schema of route.schema) {
    if (!new RegExp(`"@type"\\s*:\\s*"${schema}"`).test(html)) failures.push(`${route.path}: missing ${schema} schema`);
  }
  for (const link of route.links) {
    if (!html.includes(link)) failures.push(`${route.path}: missing funnel link to ${link}`);
  }
  for (const event of route.events) {
    if (!html.includes(event) && !sharedJs.includes(event)) failures.push(`${route.path}: missing ${event} hook`);
  }
}

const redirectSources = [
  '/blog/free-seo-audit-report-pdf.html',
  '/blog/free-site-audit-report.html',
  '/blog/site-audit-report-pdf.html',
  '/blog/site-audit-report-sample.html',
  '/blog/website-audit-report-generator-free.html',
  '/blog/website-audit-report-sample-pdf.html',
  '/blog/website-structure-audit-report-pdf.html',
  '/blog/seo-compatibility-checker-free.html',
  '/blog/seo-compatibility-checker-online-free.html',
  '/blog/seo-compatibility-checker-online.html',
  '/blog/website-technical-seo-checker.html'
];

for (const source of redirectSources) {
  const canonical = `https://lofts.studio${source}`;
  const redirect = vercel.redirects.find(item => item.source === source);
  if (!redirect || !redirect.permanent) failures.push(`${source}: missing permanent redirect`);
  if (sitemap.includes(`<loc>${canonical}</loc>`)) failures.push(`${source}: redirect source is still in sitemap`);
}

const noindexSources = [
  '/blog/seo-audit-report-template-for-leads.html',
  '/blog/website-audit-report-template-free-download.html',
  '/blog/website-structure-audit-report-template-excel.html',
  '/blog/website-structure-audit-report-template.html'
];

for (const source of noindexSources) {
  const canonical = `https://lofts.studio${source}`;
  const header = vercel.headers.find(item => item.source === source);
  const hasNoindex = header?.headers?.some(item => item.key === 'X-Robots-Tag' && /noindex/i.test(item.value));
  if (!hasNoindex) failures.push(`${source}: missing noindex header`);
  if (sitemap.includes(`<loc>${canonical}</loc>`)) failures.push(`${source}: noindex route is still in sitemap`);
}

if (process.env.AUDIT_FUNNEL_BASE_URL) {
  const baseUrl = process.env.AUDIT_FUNNEL_BASE_URL.replace(/\/$/, '');
  for (const route of manifest.routes) {
    const response = await fetch(`${baseUrl}${route.path}`, { redirect: 'follow' });
    if (!response.ok) failures.push(`${route.path}: preview returned ${response.status}`);
  }
}

if (failures.length) {
  console.error(failures.join('\n'));
  process.exit(1);
}

console.log(`Audit funnel checks passed for ${manifest.routes.length} routes.`);
