# Lofts Studio — Master Project Context
_Paste this into any Claude session to resume work instantly._

---

## 🏢 About

**Lofts Studio** — senior web engineering studio, two brothers:
- **Adnan Khan** — Multan, Pakistan. Top Rated Plus on Upwork, 100% JSS.
- **Irfan Khan** — Dubai, UAE. Top Rated on Upwork, 100% JSS.
- Combined: **1,000+ projects**, **3,400+ clients** (Upwork + direct + referrals)
- Website: **lofts.studio** · Email: **hi@lofts.studio** (public)
- Target market: US & UK small-to-mid businesses, no/outdated websites

---

## 🔐 Security Rules (NEVER violate)

- `adnan@technodigg.com` → NEVER visible on site. Lives only in Vercel env var `CONTACT_EMAIL`. All contact via `/api/contact` or chatbot.
- **Admin password**: `shipfaster` (client-side only, in `/admin/admin.js`)
- **Cron secret**: set as `CRON_SECRET` in Vercel env (value in Vercel dashboard)

---

## 🛠️ Tech Stack

- **Type**: Static HTML/CSS/JS — no build tooling, no framework
- **Deploy**: Vercel CLI → `cd /Users/adeedaxguy/Downloads/adnan-site && /opt/homebrew/bin/vercel --prod --yes`
- **Project path**: `/Users/adeedaxguy/Downloads/adnan-site/`
- **Vercel project**: `adnanaimanager-3376s-projects/adnan-site`
  - projectId: `prj_k5nfhJrvpExWrUpGkeojXm8RKcXW`
  - orgId: `team_Ezy8R0xRC7D9rpBexkDuXPsv`

---

## 🌐 API Endpoints

| Path | Type | Purpose |
|------|------|---------|
| `/api/contact.js` | Edge | Contact form → email + KV store |
| `/api/chat.js` | Edge | AI chatbot (OpenRouter) |
| `/api/audit.js` | Edge | 22-point website audit |
| `/api/admin/data.js` | Edge | Admin inbox data (password protected) |
| `/api/blog/list.js` | Edge | Blog post list from KV |
| `/api/blog/post.js` | Edge | Single blog post by slug from KV |
| `/api/cron/blog.js` | Cron | Daily AI blog post generator (3:00am UTC) |
| `/api/cron/portfolio.js` | Cron | Asana portfolio sync (3:30am UTC) |

---

## ⚙️ Vercel Env Vars

| Variable | Where used |
|----------|-----------|
| `CONTACT_EMAIL` | `/api/contact.js` — email recipient (hi@lofts.studio) |
| `ADMIN_SECRET` | `/api/admin/data.js` — admin panel token (`shipfaster`) |
| `OPENROUTER_API_KEY` | `/api/chat.js`, `/api/cron/blog.js` |
| `KV_REST_API_URL` | All KV operations (Upstash Redis) |
| `KV_REST_API_TOKEN` | All KV operations |
| `CRON_SECRET` | Secures `/api/cron/*` endpoints |
| `ASANA_TOKEN` | `/api/cron/portfolio.js` — **NEEDS ADDING** |
| `ASANA_PROJECT_ID` | `/api/cron/portfolio.js` — **NEEDS ADDING** |

---

## 📅 Cron Jobs (vercel.json)

```
Blog post: 0 3 * * *     → /api/cron/blog      (3:00am UTC daily)
Portfolio: 30 3 * * *    → /api/cron/portfolio  (3:30am UTC daily)
```

**Note**: Vercel cron requires **Pro plan**. Verify at vercel.com/adnanaimanager-3376s-projects/adnan-site/settings.

---

## 🗄️ KV Store Keys (Upstash Redis)

| Key | Type | Contents |
|-----|------|---------|
| `lofts:submissions` | List | Contact form submissions (JSON) |
| `lofts:chats` | List | Chat logs (JSON) |
| `lofts:blog:posts` | List | Blog post metadata (JSON, newest first) |
| `lofts:blog:slugs` | List | Published slugs (dedup check) |
| `lofts:blog:post:{slug}` | String | Full blog post JSON |
| `lofts:portfolio:items` | List | Portfolio items metadata |
| `lofts:portfolio:item:{slug}` | String | Full portfolio item JSON |
| `lofts:portfolio:slugs` | Set | Published portfolio slugs (dedup) |

---

## 🎨 Design Tokens

```css
--bg:      #F4F0EA   /* warm cream */
--ink:     #1A1612   /* near-black */
--accent:  #8B3A1F   /* terracotta */
--muted:   #7A6E64
--line:    #DDD7CE
--surface: #FDFAF6
--font-serif: 'Fraunces'
--font-sans:  'Inter'
```

---

## 📁 Key Files

```
/Users/adeedaxguy/Downloads/adnan-site/
├── index.html                  ← Homepage (hero, portfolio cards, contact)
├── assets/
│   ├── styles.css              ← All CSS including 3D stack, mobile, popup
│   ├── main.js                 ← Nav, 3D card stack, reveals
│   └── widgets.js              ← Chatbot, mobile bar, conv popup (inline form)
├── api/
│   ├── contact.js              ← Form handler
│   ├── chat.js                 ← OpenRouter chatbot
│   ├── audit.js                ← 22-point website auditor
│   ├── admin/data.js           ← Admin inbox API
│   ├── blog/list.js            ← Blog list from KV
│   ├── blog/post.js            ← Single post from KV
│   └── cron/
│       ├── blog.js             ← Daily blog generator (OpenRouter → KV)
│       └── portfolio.js        ← Asana portfolio sync → KV
├── admin/
│   ├── index.html              ← Portfolio admin (pw: shipfaster)
│   └── inbox.html              ← Submissions + chat logs admin
├── blog/
│   ├── index.html              ← Blog listing page (static posts + KV)
│   └── post/index.html         ← Dynamic post renderer (reads KV by ?slug=)
├── free-audit/index.html       ← Free audit tool UI
└── vercel.json                 ← Cron schedules + redirects + headers
```

---

## 🃏 Hero Card Stack (10 cards, 2s cycle)

1. americangulf.com — WordPress · Finance · Enterprise
2. americanreinsurance.com — WordPress · Insurance · B2B
3. discova.com — WordPress · Travel · B2B
4. pcinsurances.com — WordPress · Insurance · Custom
5. saludcap.com — WordPress · Finance · Editorial
6. mercanto.mx — WordPress · B2B Marketplace
7. zoofy.nl — React · Marketplace · Scale-up
8. estdept.com — Shopify · Fashion · DTC
9. investorcreator.com — WordPress · Finance · Editorial
10. jamaicancoffeeclub.com — Shopify · Subscription

---

## 📋 Homepage Portfolio Cards

| # | Project | Tag |
|---|---------|-----|
| 01 | Discova | WordPress · Travel · B2B |
| 02 | American Gulf | WordPress · Finance |
| 03 | PC Insurances | WordPress · Insurance |
| 04 | Salud Capital | WordPress · Finance |
| 05 | American Reinsurance | WordPress · Insurance · B2B |
| 06 | Moke International | Shopify · Electric Vehicles · Global |
| 07 | Joshi Fresco | WordPress · Restaurant · Fine Dining |
| 08 | Woven Media | WordPress · Media & Publishing · UK |
| 09 | Acturion | (existing) |

---

## 🔧 Pending Setup (action needed)

1. **Asana integration**: Add `ASANA_TOKEN` + `ASANA_PROJECT_ID` in Vercel dashboard → Settings → Environment Variables. Get token from asana.com/0/my-apps. Portfolio cron won't run without these.

2. **Vercel Pro**: Cron jobs require Vercel Pro plan. Check at vercel.com/pricing.

3. **Real portfolio screenshots**: Images at `/assets/work/*.jpg` — add proper screenshots for new clients. Moke International screenshot was auto-fetched via thum.io.

4. **Google Search Console**: Submit sitemap at https://lofts.studio/sitemap.xml

5. **LinkedIn/Upwork**: Both founders should reference lofts.studio in profiles.

---

## 🤖 Blog Automation Keywords (rotating 30-day list)

Shopify development agency, WordPress speed optimization, Shopify Plus migration, custom Shopify theme development, WooCommerce vs Shopify, ecommerce CRO, Shopify store redesign, headless Shopify, WordPress web design agency, Shopify page speed, ecommerce website redesign, Shopify Plus agency UK, WordPress maintenance, Shopify development cost, B2B website design, ecommerce technical SEO, Shopify checkout optimization, Webflow vs WordPress, insurance website design, landing page design agency, Shopify subscription, WordPress plugin development, ecommerce audit, Shopify migration, Next.js websites, website redesign checklist, Shopify theme customization, web design for small business UK, ecommerce development cost, WordPress vs Shopify.

---

## 💬 Chatbot System Prompt (key facts)

- Studio: Lofts Studio
- Founders: Adnan Khan (Multan) + Irfan Khan (Dubai)
- Services: Shopify, WordPress, custom web, speed optimisation, SEO, AI chatbots
- Contact: hi@lofts.studio
- Never mention adnan@technodigg.com
- Tone: warm, helpful, not pushy
- When asked for email: share hi@lofts.studio

---

## 📞 Cold Caller Context

- Target: US & UK businesses with no website or outdated website (5+ years old)
- Lead source: icloseleads.com
- Approach: identify pain (no online presence), offer free audit at lofts.studio/free-audit/
- USP: Two Top Rated Upwork founders, 3,400+ clients, reply within hours, US/UK timezone
