# Lofts Studio — 30-Day Launch Plan

**Brand:** Lofts Studio
**Domain:** lofts.studio (purchased from GoDaddy — pending nameserver migration to Cloudflare)
**Founders:** Adnan Khan (Multan) · Irfan Khan (Dubai)
**Tagline:** Senior web engineering for founders.

Last updated: 2026-06-12

---

## ✅ Week 1 — Foundation (DONE)

| Status | Item |
|---|---|
| ✅ | Full rebrand: 47 portfolio pages, 11 services, 5 location pages, 7 blog posts → **Lofts Studio** |
| ✅ | About page rewrite: two founders, Adnan + Irfan, credentials, Upwork profile links (avatars currently placeholder — photos pending) |
| ✅ | Capability matrix table (Adnan: ecommerce/CMS · Irfan: full-stack/React) |
| ✅ | Footer updates: both founders, Multan + Dubai locations, two Upwork profile links |
| ✅ | Mega menu updated with 4 new vertical pillars |
| ✅ | All schema markup: Organization (Lofts Studio) + Person × 2 (Adnan + Irfan) with sameAs to both Upwork profiles |
| ✅ | New high-end logo: refined italic serif wordmark + tracked-caps "STUDIO" + accent dot. Architectural "L" mark for favicon |
| ✅ | Brand guide page at /brand.html — palette, type, voice, do's/don'ts |
| ✅ | Sitemap.xml regenerated (98 URLs) — includes 4 new pillar pages with weekly priority 0.95 |
| ✅ | robots.txt allows GPTBot, ClaudeBot, PerplexityBot, Google-Extended |
| 🟡 | 301 redirects from adnank.vercel.app/* → lofts.studio/* — **PENDING** (needs DNS pointed first) |

---

## ✅ Week 2 — Verticals + Tracking (PARTIALLY DONE)

| Status | Item |
|---|---|
| ✅ | Built 4 vertical pillar pages: `/work/ecommerce/`, `/work/insurance-finance/`, `/work/membership-community/`, `/work/custom-apps/` |
| ✅ | Each pillar: 1,500+ words, 6 capability cards, 4 case study embeds, 4 FAQs with FAQ schema, ServiceSchema, BreadcrumbList schema, clear CTA |
| ✅ | UAE prominence added: Dubai is now an HQ location in hero, footer, schema, About page |
| 🟡 | Google Search Console verification on lofts.studio — **PENDING** (needs DNS active) |
| 🟡 | GA4 + Microsoft Clarity setup — **PENDING USER ACTION** |
| 🟡 | LinkedIn profile updates: both Adnan + Irfan reference Lofts Studio — **PENDING USER ACTION** |

---

## 🟡 Week 3 — Launch + Acquisition (PENDING)

| Status | Item |
|---|---|
| 🟡 | Launch Google Ads pilot: $1,500/month across 3 ad groups (Shopify dev / Insurance dev / React dev). Verified CPC ~$5.58, CPL ~$103.54 (WordStream 2025). — **PENDING USER ACTION** |
| ✅ | First Lofts Studio-branded blog post — **AUTONOMOUS** (cron fires Monday 9am, will publish next post from `/blog/_BACKLOG.md` queue automatically) |
| 🟡 | Email signature updates for both founders — **PENDING USER ACTION** |
| 🟡 | Adnan + Irfan Upwork profile bios updated to reference "Founder, Lofts Studio" — **PENDING USER ACTION** |

---

## 🟡 Week 4 — Optimization (AUTONOMOUS + PENDING)

| Status | Item |
|---|---|
| 🟡 | First ad data reads → kill losing ad group, double down on winner — depends on ads launch |
| ✅ | Weekly blog cadence continues — **AUTONOMOUS** (scheduled task fires every Monday 9am) |
| ✅ | Sitemap auto-refresh continues — **AUTONOMOUS** (scheduled task fires every day 7am) |

---

## 🔧 Pending domain migration (your move)

1. **Sign up at [cloudflare.com](https://cloudflare.com)** → Add Site → enter `lofts.studio` → Free plan
2. **Cloudflare gives you 2 unique nameservers** (format: `xxxxx.ns.cloudflare.com`)
3. **At GoDaddy:** My Products → lofts.studio → DNS → Nameservers → Change → paste both Cloudflare nameservers
4. **Wait 1-24 hours** for propagation
5. **Tell me when DNS is active** — I'll then:
   - Add lofts.studio as a domain on the Vercel project
   - Add A/CNAME records at Cloudflare to point to Vercel
   - Verify Google Search Console on lofts.studio
   - Set up 301 redirects from adnank.vercel.app → lofts.studio
   - Submit new sitemap to GSC

---

## 📦 Assets shipped this rebrand

```
/assets/brand/
  ├── logo-mark.svg         — Refined "L" architectural mark
  ├── logo-wordmark.svg     — Wordmark with tracked caps
  └── logo-lockup.svg       — Combined for headers / signatures

/favicon.svg                — New "L" mark for browser tab
/assets/og-default.svg      — Branded social share image

/work/ecommerce/index.html
/work/insurance-finance/index.html
/work/membership-community/index.html
/work/custom-apps/index.html
/brand.html                  — Full brand system documentation

/scripts/seo_engine.py       — Brand-aware content engine
/scripts/build_pillars_and_brand.py — Pillar + brand-guide generator
```

---

## 🤖 Autonomous schedules running

| Schedule | Action |
|---|---|
| **Mon 9am weekly** | Picks next post from `/blog/_BACKLOG.md` (14 topics queued) → generates 1,500+ word SEO post → regenerates sitemap → deploys → re-aliases domain |
| **Daily 7am** | Sitemap freshness check + homepage 200-verify |

Both schedules will automatically use `lofts.studio` once DNS is active.

---

## 📊 SEO foundation status

| Component | Status |
|---|---|
| Canonical URLs | ✅ All point to lofts.studio |
| hreflang tags | ✅ On 5 country location pages |
| Schema: Organization | ✅ Lofts Studio with 2 founders, 2 addresses |
| Schema: Person × 2 | ✅ Adnan (Multan) + Irfan (Dubai) with Upwork sameAs |
| Schema: Service | ✅ On 4 vertical pillar pages |
| Schema: FAQPage | ✅ On 4 vertical pillar pages + 5 location pages |
| Schema: BreadcrumbList | ✅ On every inner page |
| Schema: Article | ✅ On all 7 blog posts |
| Sitemap.xml | ✅ 98 URLs, daily auto-refresh |
| robots.txt | ✅ Allows all major crawlers + AI bots |
| OG tags | ✅ Per-page on all pages |
| HSTS header | ✅ Added in vercel.json |
| Core Web Vitals | ✅ Static HTML, sub-2s LCP expected |

---

## 🚫 What we DON'T do (per deep research findings)

| Decision | Why |
|---|---|
| Don't bet $5K+ on any unverified hypothesis | Deep research refuted 22/25 claims about positioning/conversion |
| Don't commit to a single vertical for 90 days | Let traffic + ad data decide |
| Don't drop Upwork before inbound is ≥30% of revenue | Upwork is paying the bills |
| Don't spend on LinkedIn Ads before $500 pilot data | Zero verified CPL data for senior dev studios |
| Don't move domain while SEO is bedding in | Already moved before traffic = no equity loss |

---

## 🎯 The 30-day decision point

By **day 30** (July 12, 2026), you'll have data to answer:
1. Which vertical pillar gets the most organic traffic?
2. Which ad group has the lowest CAC?
3. Which blog post has the highest dwell time?

That data — not opinion — decides where you double down for Q3.
