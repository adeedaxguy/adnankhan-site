# Codex Brief — lofts.studio

## Repo & deploy
- Repo: `github.com/adeedaxguy/adnankhan-site` — branch `main`
- **Always start with `git pull origin main`**
- **Deploy = `git push origin main`** — Vercel auto-deploys in ~30s, no build step

## What this site is
Zero-build static site — plain HTML/CSS/JS. No npm, no bundler, no framework. Vercel hosting.

## Two blog systems — don't confuse them

| System | Storage | URL |
|---|---|---|
| Static hand-authored (16 posts) | Files in repo + `blog/posts.json` | `/blog/slug.html` |
| AI cron-generated (daily, 3am UTC) | Vercel KV only — not in repo | `/blog/post/?slug=…` |

Both appear in the `/blog/` grid. Static cards are hard-coded between `<!-- POSTS_START -->` and `<!-- POSTS_END -->` in `blog/index.html`. KV posts load via a `<script>` block at the bottom of `blog/index.html` (fetches `/api/blog/list`).

## Key files

| File | Purpose |
|---|---|
| `blog/index.html` | Main blog grid |
| `blog/posts.json` | Source of truth for 16 static posts |
| `assets/styles.css` | Single global stylesheet |
| `assets/main.js` | Theme toggle (light/dark), scroll reveals |
| `api/og.js` | Edge fn: dynamic SVG cover `?title=&cat=` |
| `api/blog/list.js` | Edge fn: paginated KV post list |
| `api/blog/post.js` | Edge fn: single KV post by slug |
| `api/cron/blog.js` | Edge cron: daily AI post generator |
| `scripts/seo_engine.py` | Python generator for hand-authored posts |
| `scripts/generate_blog_covers.py` | Pillow-based cover PNG generator |

## CSS / JS rules
- Cache-bust all local asset refs: `?v=20260617b` — bump the letter when changing `styles.css` or `main.js`
- Dark mode via `data-theme="dark"` on `<html>` — always use CSS vars: `--ink`, `--bg`, `--surface`, `--line`, `--accent`
- All CSS goes in `assets/styles.css` — no inline `<style>` blocks in HTML files
- Blog card HTML structure must match exactly:
```html
<article class="post-card" data-reveal>
  <a href="…" class="post-card-link">
    <img class="post-card-img" src="…" width="1200" height="675" loading="lazy" />
    <div class="post-card-body">
      <div class="post-card-meta">
        <span class="tag-pill">Category</span>
        <time datetime="YYYY-MM-DD">DD Mon YYYY</time>
        <span>·</span>
        <span>N min</span>
      </div>
      <h2 class="post-card-title">…</h2>
      <p class="post-card-excerpt">…</p>
      <span class="post-card-cta">Read post →</span>
    </div>
  </a>
</article>
```

## Regenerating static blog posts
After editing `blog/posts.json`:
```bash
python3 scripts/seo_engine.py blog       # regenerates HTML files + blog/index.html grid
python3 scripts/generate_blog_covers.py  # regenerates cover PNGs in assets/blog/
```
Requires Python 3 + Pillow (`pip3 install pillow`).

## SEO blog writing preferences
When the user asks to write, publish, or improve a blog post, use an elite SEO Content Director workflow:
- Start with live keyword research and, when provided, Google Search Console query data. Use the user's actual impressions/clicks as topic signals.
- Prioritize organic lead generation, not generic traffic. Target business owners and decision-makers looking for web design, ecommerce, SaaS, AI agents, SEO/AEO/GEO, technical SEO, conversion audits, and hiring help.
- Build posts as plagiarism-free, human, authoritative content with practical advice in every section. Avoid filler, thin AI phrasing, and aggressively salesy copy.
- For major posts, aim for 2,000+ words unless the user requests a shorter format. Use a pillar/cluster model: one definitive guide plus supporting article ideas and internal links.
- Include SEO basics: meta title under ~60 chars, meta description around 120-160 chars, one clear H1, H2/H3 structure, readable URL slug, and natural keyword coverage.
- Make content snippet-ready: early key takeaways, short direct answers, comparison tables, checklists, FAQs, and schema-ready sections.
- Add at least 3 relevant internal link opportunities and 3-4 credible external citation targets when useful. Prefer official docs, reputable industry reports, and primary sources.
- Include image/chart ideas with descriptive alt text when the topic benefits from visuals.
- Add FAQ JSON-LD or recommend schema where relevant, especially FAQ, HowTo, Article, Breadcrumb, LocalBusiness, Service, or Product/Offer-style comparison schema.
- For ecommerce posts, cover platform choice, rates/costs without conflicting with site policy, implementation risk, SEO, conversion, mobile UX, speed, trust, analytics, and post-launch maintenance.
- For AI/AEO/GEO posts, cover answer-engine visibility, entity signals, schema, crawlability, page experience, topical authority, citations, and conversion path.
- End with a useful next step that naturally points to Lofts Studio's audit, consultation, tools, or relevant service page.

## Security rules — never break these
1. Email `adnan@technodigg.com` must **never appear in any file** — Vercel env var `CONTACT_EMAIL` only
2. Admin password `shipfaster` lives only in `/admin/admin.js` — never commit or log it elsewhere
3. No aggressively salesy copy

## What NOT to do
- Don't create `package.json`, `node_modules`, or any build pipeline
- Don't modify `vercel.json` routes without reading the existing routes first
- Don't hardcode the contact email anywhere
- Don't add comments explaining what code does — only add a comment when the WHY is non-obvious
