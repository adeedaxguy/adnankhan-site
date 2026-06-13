# Blog Publishing Workflow

This blog is designed for **daily publishing via Claude** — minimal friction, no CMS.

## One-command publishing

Tell Claude:

> Publish a new blog post titled "[POST TITLE]" targeting the keyword "[PRIMARY KEYWORD]" with funnel to /services/[SERVICE].html

Claude will:
1. Read `posts.json` and `_template.html`
2. Write a new `/blog/<slug>.html` from the template, filling in title, meta, body, schema
3. Prepend a new entry to `posts.json` (newest first)
4. Edit `/blog/index.html` to insert a new post-card between the `<!-- POSTS_START -->` and `<!-- POSTS_END -->` markers
5. Add the URL to `/sitemap.xml`
6. Print the new local path so you can preview before pushing

## File structure

```
/blog/
  ├── index.html              ← listing page (has POSTS_START/POSTS_END markers)
  ├── posts.json              ← registry of all posts (newest first)
  ├── _template.html          ← skeleton for new posts (do not modify)
  ├── PUBLISHING.md           ← this file
  └── <slug>.html             ← one file per post
```

## Required fields per post (in posts.json)

| Field | Format | Example |
|---|---|---|
| `slug` | kebab-case, matches filename | `passing-core-web-vitals-on-shopify` |
| `title` | Full SEO title (under 65 chars ideal) | `How to Pass Core Web Vitals on Shopify in 2026` |
| `excerpt` | 1–2 sentence summary | `The four metrics that matter…` |
| `category` | One of: Speed, CRO, Shopify, WooCommerce, AI & Automation, Custom Apps, Design, Migration, SEO, Process | `Speed` |
| `date` | ISO 8601 | `2026-06-11` |
| `readingTime` | Estimated, e.g. `12 min` | `8 min` |
| `primaryKeyword` | Main SEO target | `shopify core web vitals` |
| `secondaryKeyword` | Supporting keyword | `fix shopify lcp` |
| `funnelTo` | Service page path the post drives to | `/services/speed-optimization.html` |
| `featured` | Is this the homepage hero post? Only one at a time | `true` / `false` |
| `published` | Is it live? Drafts use `false` | `true` |

## SEO checklist (Claude will handle these automatically per the template)

- Unique `<title>` (under 65 chars)
- Unique `<meta description>` (under 160 chars)
- Canonical URL set
- Open Graph + Twitter Card meta
- Article schema (JSON-LD) with author, datePublished, dateModified
- BreadcrumbList schema
- H1 once, H2/H3 nested cleanly
- Primary keyword in title, H1, first 100 words, and at least one H2
- Secondary keyword in at least one H2
- Internal link to funnel target service page (in body + CTA at end)
- Reading time in author block
- Alt text on every image
- All links open in-tab unless external (then `target="_blank" rel="noopener"`)

## Topic backlog

See `/Users/adeedaxguy/Downloads/adnan-site/blog/_BACKLOG.md` for the 25 researched post ideas. Pick the next one or paste your own topic.

## Going live (when you buy a domain)

When you swap `lofts.studio` for your real domain, all blog URLs auto-update — they all use root-relative paths and the canonical+OG tags reference `https://lofts.studio/` which gets globally replaced. One Python find-and-replace, one deploy, done.
