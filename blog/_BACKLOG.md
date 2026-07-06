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
| 2026-07-03 | fix-shopify-lcp-dawn-theme | fix shopify lcp dawn theme |
| 2026-07-05 | shopify-theme-customization-modify-or-rebuild | shopify theme customization |

## 🟡 Next 12 (brand-safe autonomous picks)

| # | Title | Primary keyword | Funnel |
|---|---|---|---|
| 1 | I Audited 50 Shopify Stores — the 7 Speed Killers I Found in 43 of Them | shopify speed audit | /services/speed-optimization.html |
| 2 | Shopify Plus Migration Checklist for SEO, Redirects, and Launch Safety | shopify plus migration checklist | /services/shopify-plus-migration.html |
| 3 | WooCommerce to Shopify Migration: A Senior Dev's Checklist (60 Items) | woocommerce to shopify migration | /services/shopify-development.html |
| 4 | Elementor vs Custom Theme for High-Traffic WordPress: An Honest Take | elementor vs custom theme | /services/woocommerce-development.html |
| 5 | Shopify CRO Audit: The Checks I Run Before Rebuilding a Store | shopify cro audit | /services/conversion-rate-optimization.html |
| 6 | Landing Page Conversion Benchmarks for DTC, B2B, and SaaS in 2026 | landing page conversion benchmark | /services/landing-page-sprint.html |
| 7 | Shopify SEO: The Platform Quirks That Wreck Rankings | shopify seo issues | /services/technical-seo-audit.html |
| 8 | On-Page SEO for Product Pages: A Template That Survives Algorithm Updates | product page seo | /services/technical-seo-audit.html |
| 9 | Building a Private Shopify App for Internal Ops: A Real Walkthrough | private shopify app development | /services/custom-app-development.html |
| 10 | Zapier vs Make vs n8n for eCommerce Automation in 2026 | zapier vs make for ecommerce | /services/ai-chatbot-automation.html |
| 11 | AI Calling Agent Setup for Local Service Businesses | ai calling agent for service business | /services/ai-calling-agents.html |
| 12 | AEO for Service Pages: How to Make Your Offer Answer-Ready | aeo service page optimization | /services/technical-seo-audit.html |

## How autonomous publishing works

A scheduled task fires every **Monday at 9am local** and tells Claude to:

1. Read this file, pick the top entry from "Next 14"
2. Append a new POST dict to the `POSTS` array in `scripts/seo_engine.py` (1500+ word body, structured)
3. Run `python3 scripts/seo_engine.py all` → regenerates blog HTML + sitemap.xml + posts.json + blog/index.html
4. Deploy via `vercel --prod --yes`
5. Re-alias `lofts.studio` to the new deploy
6. Move the entry to "Published" above

Result: 1 new SEO-optimised post live every Monday, indefinitely, without manual touch.
