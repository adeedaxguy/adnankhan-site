# Lofts Studio — Claude Context

## What this is
Freelance studio website for Lofts Studio (lofts.studio). Two founders: Adnan Khan (Multan, PK) + Irfan Khan (Dubai, UAE).

## Files & deploy
- **Local path:** `/Users/adeedaxguy/Downloads/adnan-site/`
- **GitHub:** `github.com/adeedaxguy/adnankhan-site` (main branch)
- **Hosting:** Vercel — auto-deploys on every `git push origin main` (~15s)
- **Manual deploy fallback:** `/opt/homebrew/bin/vercel --prod --yes` from the project root

## Deploy workflow
```
git add -A
git commit -m "description"
git push origin main
# Vercel auto-deploys to lofts.studio in ~15 seconds
```

## Cache-busting
All `<link>` and `<script>` tags use `?v=YYYYMMDDX` (e.g. `?v=20260613l`).
**Increment the letter suffix on every deploy that changes CSS or JS.**
Update all HTML files at once:
```bash
find . -name "*.html" -not -path "*/.vercel/*" | xargs sed -i '' 's/styles\.css?v=OLD/styles.css?v=NEW/g'
find . -name "*.html" -not -path "*/.vercel/*" | xargs sed -i '' 's/main\.js?v=OLD/main.js?v=NEW/g'
```

## Tech stack
- Static HTML/CSS/JS — no build tools, no npm, no framework
- Edge function: `/api/contact.js` (contact form proxy)
- Chatbot: `/api/chat.js` via OpenRouter (env var `OPENROUTER_API_KEY` set in Vercel)

## Brand
- **Name:** Lofts Studio
- **Domain:** lofts.studio
- **Colors:** bg `#F4F0EA`, ink `#1A1612`, accent `#8B3A1F`
- **Fonts:** Source Serif 4 (serif), Inter Tight (sans), JetBrains Mono (mono)
- **Tone:** Quiet Luxury — no hype, no aggressive selling

## Key files
| File | Purpose |
|------|---------|
| `index.html` | Homepage |
| `about.html` | About page |
| `services/index.html` | Services parent page (11 services + 5 location cards) |
| `portfolio/index.html` | Portfolio grid |
| `portfolio/portfolio.json` | Single source of truth for 47 portfolio items |
| `assets/styles.css` | All styles |
| `assets/main.js` | All JS |
| `vercel.json` | Redirects + headers |
| `scripts/generate_portfolio_pages.py` | Regenerates all portfolio detail pages |
| `scripts/seo_engine.py` | Generates blog posts + location pages + sitemap |
| `scripts/build_pillars_and_brand.py` | Builds 4 vertical pillar pages + brand.html |

## Site structure
```
/                          Homepage
/about.html                About + Founders
/portfolio/                Portfolio grid (47 items)
/services/                 Services parent page
/services/*.html           11 service pages + 5 location pages
/work/ecommerce/           Ecommerce vertical pillar
/work/insurance-finance/   Insurance/Finance pillar
/work/membership-community/ Membership/Community pillar
/work/custom-apps/         Custom Apps pillar
/blog/                     Blog (7 posts)
/notes/                    Notes / short-form writing
/process/                  Process page
/free-audit/               Free audit page
/locations/                5 country pages
/brand.html                Brand guide
/admin/                    Admin panel (password in /admin/admin.js — never expose)
```

## Mobile nav — important
The `#mobilePanel` div **must be placed outside `<header>`** — the header has `backdrop-filter` which creates a containing block that clips `position: fixed`. Correct structure:

```html
</header>

<!-- Full-screen mobile nav overlay — must be outside <header> -->
<div id="mobilePanel" class="mnav" ...>
```

The mobile nav (`.mnav`) is on all 96 pages. To update it across all pages use a Python script with string replacement — don't edit each file manually.

## Mobile hero card stack
- **Desktop (>880px):** 3D card stack with mouse tilt — 10 cards with `rotateX/Y/translateZ`
- **Mobile (≤880px):** Pure CSS crossfade — cards stack absolutely, `.is-front` gets `opacity: 1`, no 3D transforms
- JS in `assets/main.js` checks `isMobile()` and routes to `applyFade()` or `applySlots()` accordingly

## Regenerate everything
```bash
python3 scripts/generate_portfolio_pages.py
python3 scripts/seo_engine.py all
python3 scripts/build_pillars_and_brand.py
```

## Security rules — never violate
- `adnan@technodigg.com` must NEVER appear visibly on the site (Vercel env var only)
- Admin password lives only in `/admin/admin.js` — never expose or commit elsewhere
- Never push services aggressively in copy

## Current cache-bust version
`v=20260613l` — increment letter on next CSS/JS change
