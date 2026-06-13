# Blog Backlog — SEO Content Engine

Topics sorted by commercial intent. Posts are written via specs in `scripts/seo_engine.py` (the POSTS array) and regenerated with `python3 scripts/seo_engine.py blog`.

## ✅ Published

| Date | Slug | Primary keyword |
|---|---|---|
| 2026-06-01 | passing-core-web-vitals-on-shopify | shopify core web vitals |
| 2026-06-12 | hire-shopify-developer-guide-2026 | hire shopify developer |
| 2026-06-13 | shopify-plus-vs-advanced-when-to-upgrade | shopify plus vs advanced |
| 2026-06-14 | shopify-technical-seo-audit-checklist | shopify technical seo audit |
| 2026-06-15 | freelance-shopify-developer-vs-agency | freelance shopify developer vs agency |
| 2026-06-16 | shopify-custom-app-vs-public-app | shopify custom app vs public app |
| 2026-06-17 | speed-up-woocommerce-checklist | speed up woocommerce |

## 🟡 Next 14 (autonomous weekly publish picks the top entry each Monday)

| # | Title | Primary keyword | Funnel |
|---|---|---|---|
| 1 | How to Fix LCP on Shopify Dawn Theme Without Breaking Sections | fix shopify lcp | /services/speed-optimization.html |
| 2 | Shopify Speed Optimization Cost: What $2K Buys You vs What $200 Buys You | shopify speed optimization cost | /services/speed-optimization.html |
| 3 | I Audited 50 Shopify Stores — the 7 Speed Killers I Found in 43 of Them | shopify speed audit | /services/speed-optimization.html |
| 4 | The Real Cost of a Shopify Plus Migration in 2026 | shopify plus migration cost | /services/shopify-plus-migration.html |
| 5 | WooCommerce to Shopify Migration: A Senior Dev's Checklist (60 Items) | woocommerce to shopify migration | /services/shopify-development.html |
| 6 | Elementor vs Custom Theme for High-Traffic WordPress: An Honest Take | elementor vs custom theme | /services/woocommerce-development.html |
| 7 | Shopify Theme Customization: When to Modify, When to Rebuild | shopify theme customization | /services/shopify-development.html |
| 8 | How We Got a DTC Skincare Brand from 1.4% to 3.1% Conversion in 9 Weeks | shopify cro case study | /services/conversion-rate-optimization.html |
| 9 | The Shopify CRO Audit I Send to Every New Client (Free Template) | shopify cro audit | /services/conversion-rate-optimization.html |
| 10 | Landing Page Conversion Benchmarks for DTC, B2B, and SaaS in 2026 | landing page conversion benchmark | /services/landing-page-sprint.html |
| 11 | Shopify SEO: The Platform Quirks That Wreck Rankings | shopify seo issues | /services/technical-seo-audit.html |
| 12 | On-Page SEO for Product Pages: A Template That Survives Algorithm Updates | product page seo | /services/technical-seo-audit.html |
| 13 | Building a Private Shopify App for Internal Ops: A Real Walkthrough | private shopify app development | /services/custom-app-development.html |
| 14 | Zapier vs Make vs n8n for eCommerce Automation in 2026 | zapier vs make for ecommerce | /services/ai-chatbot-automation.html |

## How autonomous publishing works

A scheduled task fires every **Monday at 9am local** and tells Claude to:

1. Read this file, pick the top entry from "Next 14"
2. Append a new POST dict to the `POSTS` array in `scripts/seo_engine.py` (1500+ word body, structured)
3. Run `python3 scripts/seo_engine.py all` → regenerates blog HTML + sitemap.xml + posts.json + blog/index.html
4. Deploy via `vercel --prod --yes`
5. Re-alias `lofts.studio` to the new deploy
6. Move the entry to "Published" above

Result: 1 new SEO-optimised post live every Monday, indefinitely, without manual touch.
