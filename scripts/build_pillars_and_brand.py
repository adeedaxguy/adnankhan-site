#!/usr/bin/env python3
"""
Build the 4 vertical pillar pages and the brand guide page.
Run: python3 scripts/build_pillars_and_brand.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lofts.studio"
CACHE_VER = "20260622j"

INDEX = ROOT / "index.html"


def load_nav_footer():
    html = INDEX.read_text()
    nav = re.search(r'<header class="nav-bar">.*?</header>', html, re.DOTALL).group(0)
    footer = re.search(r'<footer class="site-footer.*?</footer>', html, re.DOTALL).group(0)
    return nav, footer


# ── Pillar specs ─────────────────────────────────────────────────────────────

PILLARS = [
    {
        "slug": "ecommerce",
        "title": "Ecommerce Engineering",
        "h1": "Senior ecommerce engineering — Shopify, WooCommerce, headless.",
        "tagline": "for founders running serious ecommerce brands",
        "meta": "Senior ecommerce engineering by Lofts Studio. Shopify Plus, WooCommerce, headless commerce. 200+ DTC and B2B builds. Top Rated on Upwork.",
        "kw": "ecommerce developer, shopify plus developer, woocommerce developer, headless commerce, hire ecommerce engineer",
        "summary": "Two hundred-plus DTC, B2B, and marketplace ecommerce builds. Shopify Plus migrations. WooCommerce at scale. Headless commerce on Next.js. The work that runs your store doesn't break when traffic spikes.",
        "what_we_build": [
            ("Shopify (Plus & Standard)", "Custom themes, sections, checkout extensions, B2B catalogs, Plus migrations. Native code — no PageFly, no GemPages."),
            ("WooCommerce at scale", "Subscriptions, multi-vendor, B2B tier scoping, custom shipping logic, performance engineering that survives Black Friday."),
            ("Headless commerce", "Next.js frontends with Shopify Storefront API or WooCommerce REST. Edge-rendered. Sub-1s LCP."),
            ("Custom Shopify apps", "Merchant-specific internal tools, OMS integrations, supplier portals. No App Store revenue share, no third-party data leakage."),
            ("Multi-vendor marketplaces", "Built one for the Mexican restaurant industry (Mercanto). Built one for AI art (Artika). We know the patterns."),
            ("Speed engineering", "Core Web Vitals pass guaranteed. LCP under 2.5s on mobile. Average lift: 25-40%."),
        ],
        "case_studies": ["mercanto", "discova", "jamaicancoffeeclub", "giftful", "lossderma", "miferia-mx"],
        "faqs": [
            ("What does an ecommerce build with Lofts Studio effort?",
             "Stock-theme setups, custom Shopify builds, Shopify Plus migrations, and headless rebuilds are scoped privately after discovery. Every project is milestone-led."),
            ("Do you do Shopify Plus migrations?",
             "Yes — 14 completed in the last five years. Average timeline: 8–12 weeks for a real B2B-enabled migration."),
            ("Can you handle WooCommerce stores doing high traffic?",
             "Yes. Object caching (Redis), proper hosting (managed WooCommerce), and a stripped plugin stack. Most stores we touch see 30-50% TTFB improvement."),
            ("Do you build on Shopify themes or custom?",
             "Both. Stock themes for tight-deadline launches. Custom themes when the brand needs it. We don't use page builders — they slow stores down."),
        ],
        "cta_label": "Brief us on your ecommerce project",
    },
    {
        "slug": "insurance-finance",
        "title": "Insurance & Finance Web Engineering",
        "h1": "Insurance and finance website engineering — for brokers, carriers, and platforms.",
        "tagline": "for brokers, carriers, fintech founders, and reinsurance platforms",
        "meta": "Senior web engineering for insurance brokers, fintech founders, and reinsurance platforms. Compliance-aware design, enquiry flows, agent portals. Lofts Studio.",
        "kw": "insurance website developer, fintech web developer, insurance broker website, reinsurance website, hire wordpress developer for insurance",
        "summary": "Insurance and finance is one of the most regulated, highest-LTV verticals on the web. We've shipped six platforms in this space — from broker websites to multi-entity reinsurance corporate sites — and learned the compliance, the regulator-friendly language, and the underwriter workflow.",
        "what_we_build": [
            ("Broker websites", "Lead routing by line of business, GDPR-compliant lead capture, integration with carrier feeds. PC Insurances is live in Ireland."),
            ("Carrier corporate sites", "American Gulf, Acturion, American Re — all built from premium Figma systems. Agent portals, product/solutions pages, multi-entity contact routing."),
            ("Reinsurance platforms", "B2B financial services sites where the buyer is institutional. Custom animation, structured product taxonomies, careers and team pages."),
            ("Compliance-aware design", "HIPAA, GDPR, KYC patterns. Underwriter-friendly content models. Regulator-passing copy patterns."),
            ("Fintech landing pages", "Conversion-tuned for acquisition traffic at high-intent acquisition clicks. Trust-signal-dense. Compliance-reviewed."),
            ("Agent and underwriter portals", "Custom WordPress + React applications. Role-aware access. Document workflow. Real internal-tools work."),
        ],
        "case_studies": ["americangulf", "acturion", "americanreinsurance", "pcinsurances", "saludcap"],
        "faqs": [
            ("Have you worked with US insurance brokers and carriers?",
             "Yes. American Gulf, Acturion (an integrated insurance and asset management platform), and American Reinsurance Company SPC are all live and operating. All are US-based or US-aligned."),
            ("Do you understand insurance compliance?",
             "We engineer to spec. We are not insurance lawyers. We work alongside your compliance counsel — they review copy, we ship the build. Pattern-wise we know HIPAA, GDPR, KYC, AML touch points."),
            ("How long does an insurance/reinsurance site take to build?",
             "Eight to fourteen weeks for a full Figma-to-code corporate site. Shorter for landing pages or specific products. Multi-entity multi-brand engagements (like the American Gulf / Acturion / Amre suite) run longer."),
            ("What CMS do you use for insurance sites?",
             "WordPress + Elementor for most. WordPress + custom theme for higher-end. Webflow for marketing-led brands. The platform is downstream of the team's editorial needs."),
        ],
        "cta_label": "Brief us on your insurance build",
    },
    {
        "slug": "membership-community",
        "title": "Membership &amp; Community Platforms",
        "h1": "Membership and community platforms — Stripe, Discord, Whop integration.",
        "tagline": "for course creators, coaching brands, and community founders",
        "meta": "Senior engineering for membership platforms — Stripe checkout, Discord auto-role assignment, Whop API, WooCommerce subscriptions. Lofts Studio.",
        "kw": "membership site developer, discord stripe integration, whop api developer, woocommerce subscriptions developer, coaching website developer",
        "summary": "Membership and community is a small market with outsized economics — recurring revenue, low CAC, devoted users. We've built the rare kind of membership tech that actually works: Stripe checkout into auto-Discord-role-assignment, multi-tier paywalls, gated course delivery, and the webhook chains that make all of it run.",
        "what_we_build": [
            ("Stripe + Discord auto-onboarding", "Customer pays via Stripe → webhook hits WordPress → Whop API assigns Discord role → user lands in the right channel. End-to-end engineered."),
            ("Membership tiers", "Free, paid, premium, lifetime. Drip content delivery. Renewal logic. Cancellation flows. The non-glamorous engineering that decides retention."),
            ("LMS + gated content", "WordPress + LMS plugin or custom build. Course progress tracking, certificates, community integration."),
            ("Coaching websites", "Klaviyo email capture, custom checkout flows, Calendly integration, scheduling, intake automation."),
            ("Whop integration", "We've built it. We know the API. The webhook patterns. The race conditions."),
            ("WooCommerce subscriptions at scale", "Subscription products, tier upgrades, dunning management, payment recovery. The pieces nobody warns you about."),
        ],
        "case_studies": ["4th-culture", "coach-carolin", "investorcreator", "venturelibrary"],
        "faqs": [
            ("Can you connect Stripe payments to Discord roles?",
             "Yes — we've shipped this end-to-end for 4th Culture. Stripe webhook → WooCommerce → Whop API → Discord role assignment. Fully automated."),
            ("What stack do you recommend for a membership site?",
             "WordPress + WooCommerce + Subscriptions, with Stripe handling payment and Whop or a custom webhook layer handling community access. Cheaper and more flexible than Mighty Networks or Skool."),
            ("Can you migrate from Kajabi, Mighty Networks, or Skool?",
             "Yes. We've done several. Content, members, subscriptions, and Discord communities all transfer cleanly with the right migration plan."),
            ("How long does a membership platform take to build?",
             "Six to twelve weeks for the full stack including tiering, gated content, and community integration. Faster if you don't need community auto-roles."),
        ],
        "cta_label": "Brief us on your membership platform",
    },
    {
        "slug": "custom-apps",
        "title": "Custom Apps &amp; Integrations",
        "h1": "Custom web applications and integrations — React, Next.js, Node.js.",
        "tagline": "for founders who need software, not just websites",
        "meta": "Custom web app engineering — React, Next.js, Node.js, custom Shopify apps, API integrations. Led by Irfan Khan (Top Rated, 700+ projects). Lofts Studio.",
        "kw": "react developer, nextjs developer, node.js developer, custom web app development, hire full-stack developer, shopify custom app development",
        "summary": "When a website isn't enough. Irfan leads custom application engineering at Lofts Studio — React, Next.js, Node.js, integrations, internal tools, SaaS frontends. 700+ projects under his belt, high-volume tracked client value.",
        "what_we_build": [
            ("SaaS frontends", "Next.js with auth, dashboards, billing, settings, team management. The boring engineering that decides whether users renew."),
            ("Internal tools", "React + Node.js applications for ops teams. Order management, inventory routing, custom reporting. Often replaces duct-taped SaaS."),
            ("Custom Shopify apps", "Merchant-specific apps not on the App Store. Polaris UI, App Bridge, webhooks. Scoped privately after discovery."),
            ("API integrations", "Klaviyo, Mailchimp, Stripe, Plaid, Twilio, HubSpot, Salesforce, Xero, QuickBooks. Connect the systems that already exist."),
            ("WhatsApp Business integration", "We've built three. WhatsApp Cloud API, message templates, business profile, customer-facing chatbots."),
            ("Click funnels", "Custom funnel builds when GoHighLevel or ClickFunnels won't bend the way you need. From sales to upsell to downsell to success page."),
        ],
        "case_studies": ["zoofy", "wovenmedia", "estdept", "klyna", "icloseleads", "freeltools"],
        "faqs": [
            ("Do you build custom Shopify apps or use public ones?",
             "Both. We recommend public apps when they cover 80% of the need. Custom when they don't — internal tools, merchant-specific automation, or anything you don't want to share data with a third party for."),
            ("How do you scope custom web app work?",
             "Simple integrations, mid-complexity apps, and full internal systems are scoped privately after the workflow is mapped."),
            ("Do you do React Native or mobile apps?",
             "No. We focus on web. We will recommend a mobile partner if mobile is critical to your build."),
            ("Can you maintain the app after launch?",
             "Yes — most clients move to a ongoing support (10–40 hours/month) for ongoing feature work, bug fixes, and integration updates."),
        ],
        "cta_label": "Brief us on your custom app",
    },
]


def render_pillar(p, nav, footer, all_pillars):
    capability_html = ""
    for title, desc in p["what_we_build"]:
        capability_html += f'''
      <article data-reveal class="card" style="padding: 2rem; border: 1px solid var(--line); border-radius: var(--r-lg);">
        <h3 class="h-2" style="margin: 0 0 0.75rem;">{title}</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0; line-height: 1.65;">{desc}</p>
      </article>'''

    case_studies_html = ""
    for cs_slug in p["case_studies"]:
        case_studies_html += f'<a href="/portfolio/{cs_slug}.html" class="trust-badge" style="text-decoration: none;">{cs_slug.replace("-", " ").title()} &rarr;</a>'

    faqs_html = ""
    faq_schema = []
    for q, a in p["faqs"]:
        faqs_html += f'''
      <div data-reveal>
        <h3 class="h-2" style="margin: 0 0 0.5rem;">{q}</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0; line-height: 1.7;">{a}</p>
      </div>'''
        faq_schema.append(f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}')

    related_html = ""
    for op in all_pillars:
        if op["slug"] != p["slug"]:
            related_html += f'<a href="/work/{op["slug"]}/" class="btn btn-ghost" style="font-size: 0.86rem;">{op["title"]} &rarr;</a> '

    title = re.sub(r'<[^>]+>', '', p["title"])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>{title} | Lofts Studio</title>
<meta name="description" content="{p["meta"]}" />
<link rel="canonical" href="{SITE}/work/{p["slug"]}/" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="keywords" content="{p["kw"]}" />

<meta property="og:type" content="website" />
<meta property="og:url" content="{SITE}/work/{p["slug"]}/" />
<meta property="og:title" content="{title} | Lofts Studio" />
<meta property="og:description" content="{p["meta"]}" />
<meta property="og:image" content="{SITE}/assets/og.jpg?v=2" />
<meta name="twitter:card" content="summary_large_image" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "{title}",
  "description": "{p["meta"]}",
  "provider": {{ "@type": "Organization", "name": "Lofts Studio", "url": "{SITE}" }},
  "areaServed": [{{"@type":"Country","name":"United States"}},{{"@type":"Country","name":"United Kingdom"}},{{"@type":"Country","name":"Australia"}},{{"@type":"Country","name":"Canada"}},{{"@type":"Country","name":"United Arab Emirates"}}],
  "url": "{SITE}/work/{p["slug"]}/"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{",".join(faq_schema)}]
}}
</script>
<script type="application/ld+json">
{{ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
  {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
  {{"@type":"ListItem","position":2,"name":"Work","item":"{SITE}/portfolio/"}},
  {{"@type":"ListItem","position":3,"name":"{title}","item":"{SITE}/work/{p["slug"]}/"}}
]}}
</script>
</head>
<body>

{nav}

<section class="paper" style="padding: 7rem 0 4rem;">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);" data-reveal>
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <a href="/portfolio/" style="color: var(--muted);">Work</a> <span style="margin: 0 8px;">/</span>
      <span style="color: var(--ink);">{title}</span>
    </nav>

    <div data-reveal style="max-width: 940px;">
      <span class="eyebrow">{title} {p["tagline"]}</span>
      <h1 class="h-display" data-split="words" style="margin-top: 1.5rem;">{p["h1"]}</h1>
      <p class="lead" style="margin-top: 2rem; max-width: 60ch;">{p["summary"]}</p>

      <div style="display: flex; gap: 1rem; margin-top: 2.5rem; flex-wrap: wrap;">
        <a href="/#contact" class="btn btn-primary">{p["cta_label"]} &nbsp;&rarr;</a>
        <a href="/portfolio/" class="btn btn-ghost">See all case studies</a>
      </div>
    </div>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 780px; margin-bottom: 3.5rem;">
      <span class="eyebrow">What we engineer</span>
      <h2 class="h-1" style="margin-top: 1.25rem;">Six capabilities under {title.lower()}.</h2>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
      {capability_html}
    </div>
  </div>
</section>

<section class="section-sm" style="background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 780px; margin-bottom: 2.5rem;">
      <span class="eyebrow">Recent {title.lower()} work</span>
      <h2 class="h-1" style="margin-top: 1.25rem;">Live engagements you can verify.</h2>
    </div>
    <div data-reveal style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
      {case_studies_html}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div data-reveal style="max-width: 780px; margin-bottom: 3rem;">
      <span class="eyebrow">FAQs</span>
      <h2 class="h-1" style="margin-top: 1.25rem;">Common questions about {title.lower()}.</h2>
    </div>

    <div style="display: grid; gap: 2.5rem; max-width: 780px;">
      {faqs_html}
    </div>
  </div>
</section>

<section class="section-sm" style="background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 780px; margin-bottom: 1.5rem;">
      <span class="eyebrow">Related capabilities</span>
      <h2 class="h-1" style="margin-top: 1.25rem;">Other things we build.</h2>
    </div>
    <div data-reveal style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
      {related_html}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div data-reveal style="background: var(--ink); color: var(--bg); padding: 4rem 3rem; border-radius: var(--r-lg); text-align: center; max-width: 900px; margin: 0 auto;">
      <span style="font-family: var(--font-sans); font-size: 0.72rem; color: rgba(244,240,234,0.6); text-transform: uppercase; letter-spacing: 0.22em;">If you got this far</span>
      <h2 class="h-1" style="color: var(--bg); margin: 1.5rem 0;">Send your URL or your brief.<br/><span class="italic-serif">We&rsquo;ll audit it before the call.</span></h2>
      <p style="font-family: var(--font-serif); font-size: 1.15rem; line-height: 1.6; color: rgba(244,240,234,0.85); max-width: 56ch; margin: 0 auto 2.5rem;">Four-hour reply window. Three specific suggestions you can act on whether you hire us or not.</p>
      <a href="/#contact" class="btn" style="background: var(--bg); color: var(--ink); padding: 1rem 2rem;">{p["cta_label"]} &nbsp;&rarr;</a>
    </div>
  </div>
</section>

{footer}

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/main.js?v={CACHE_VER}" defer></script>
<script src="/assets/widgets.js?v={CACHE_VER}" defer></script>
</body>
</html>
'''


def render_brand_guide(nav, footer):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>Brand Guide | Lofts Studio</title>
<meta name="description" content="The Lofts Studio brand system — voice, palette, type, mark, lockup, OG, and usage rules." />
<link rel="canonical" href="{SITE}/brand.html" />
<meta name="robots" content="noindex,follow" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />

<style>
  .swatch {{ aspect-ratio: 1; border-radius: var(--r-md); display: flex; flex-direction: column; justify-content: flex-end; padding: 1rem; font-family: var(--font-mono); font-size: 0.74rem; color: var(--bg); }}
  .swatch.light {{ color: var(--ink); border: 1px solid var(--line); }}
  .brand-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; }}
  .logo-frame {{ background: var(--bg); padding: 3rem; border: 1px solid var(--line); border-radius: var(--r-lg); display: flex; align-items: center; justify-content: center; }}
  .logo-frame.dark {{ background: var(--ink); }}
  .type-sample {{ padding: 2rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-md); margin-bottom: 1.5rem; }}
</style>
</head>
<body>

{nav}

<section class="paper" style="padding: 7rem 0 4rem;">
  <div class="container">
    <span class="eyebrow">Brand system</span>
    <h1 class="h-display" style="margin-top: 1.5rem;">Lofts Studio<br/><span class="italic-serif">brand guide.</span></h1>
    <p class="lead" style="margin-top: 2rem; max-width: 60ch;">A quiet, considered system. Inspired by editorial print, architectural drawings, and the way senior engineers think about the work — slowly, then all at once.</p>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <span class="eyebrow">1. The mark</span>
    <h2 class="h-1" style="margin: 1rem 0 2rem;">Two beams. Two studios. <span class="italic-serif">One craft.</span></h2>
    <p style="font-family: var(--font-serif); color: var(--ink-soft); max-width: 60ch; margin-bottom: 2.5rem;">The mark is two stacked horizontal beams — a small architectural section drawing. The top beam is the Multan loft. The lower beam is the Dubai loft. The small accent stroke at the base is the founder line.</p>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
      <div class="logo-frame"><img src="/assets/brand/logo-mark.svg" alt="Lofts Studio mark" style="width: 96px; height: 96px;"/></div>
      <div class="logo-frame dark"><img src="/assets/brand/logo-mark.svg" alt="Lofts Studio mark on dark" style="width: 96px; height: 96px; filter: invert(0);"/></div>
    </div>

    <h3 style="margin-top: 3rem;">Full lockup</h3>
    <div class="logo-frame" style="margin-top: 1rem;"><img src="/assets/brand/logo-lockup.svg" alt="Lofts Studio lockup" style="height: 60px;"/></div>

    <h3 style="margin-top: 3rem;">Wordmark only</h3>
    <div class="logo-frame" style="margin-top: 1rem;"><img src="/assets/brand/logo-wordmark.svg" alt="Lofts Studio wordmark" style="height: 60px;"/></div>
  </div>
</section>

<section class="section" style="background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
  <div class="container">
    <span class="eyebrow">2. Palette</span>
    <h2 class="h-1" style="margin: 1rem 0 2.5rem;">Warm. <span class="italic-serif">Earned, not loud.</span></h2>

    <div class="brand-grid">
      <div class="swatch light" style="background: #F4F0EA;">--bg<br/>#F4F0EA</div>
      <div class="swatch light" style="background: #ECE7DE;">--bg-soft<br/>#ECE7DE</div>
      <div class="swatch light" style="background: #FBF8F2;">--surface<br/>#FBF8F2</div>
      <div class="swatch" style="background: #1A1612;">--ink<br/>#1A1612</div>
      <div class="swatch" style="background: #2A241E;">--ink-soft<br/>#2A241E</div>
      <div class="swatch" style="background: #6C6258;">--muted<br/>#6C6258</div>
      <div class="swatch" style="background: #8B3A1F;">--accent<br/>#8B3A1F</div>
      <div class="swatch" style="background: #6F2C16;">--accent-deep<br/>#6F2C16</div>
      <div class="swatch light" style="background: #F0E4DC;">--accent-soft<br/>#F0E4DC</div>
      <div class="swatch light" style="background: #D9D2C4;">--line<br/>#D9D2C4</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <span class="eyebrow">3. Typography</span>
    <h2 class="h-1" style="margin: 1rem 0 2.5rem;">Two faces. <span class="italic-serif">Both deliberate.</span></h2>

    <div class="type-sample">
      <p style="font-family: var(--font-sans); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em; color: var(--muted); margin: 0 0 1rem;">Display &amp; UI — Inter Tight</p>
      <p style="font-family: var(--font-display); font-size: 3.2rem; line-height: 1.05; letter-spacing: -0.035em; font-weight: 500; margin: 0; color: var(--ink);">Two brothers. A long delivery record.</p>
    </div>

    <div class="type-sample">
      <p style="font-family: var(--font-sans); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em; color: var(--muted); margin: 0 0 1rem;">Editorial — Source Serif 4</p>
      <p style="font-family: var(--font-serif); font-size: 1.25rem; line-height: 1.65; color: var(--ink-soft); margin: 0;">Lofts Studio is the senior web engineering team of brothers Adnan and Irfan Khan. <em>Two cities. One craft.</em></p>
    </div>

    <div class="type-sample">
      <p style="font-family: var(--font-sans); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em; color: var(--muted); margin: 0 0 1rem;">Monospace — JetBrains Mono</p>
      <p style="font-family: var(--font-mono); font-size: 0.92rem; color: var(--ink); margin: 0;">// long delivery record · almost 15 years · 100% JSS · founder-led work</p>
    </div>
  </div>
</section>

<section class="section" style="background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
  <div class="container">
    <span class="eyebrow">4. Voice</span>
    <h2 class="h-1" style="margin: 1rem 0 2.5rem;">Editorial. Direct. <span class="italic-serif">Earned authority.</span></h2>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; max-width: 1000px;" class="two-col">
      <div>
        <h3 style="font-family: var(--font-display); font-size: 1.2rem; color: var(--ink); margin: 0 0 1rem;">We sound like</h3>
        <ul style="font-family: var(--font-serif); color: var(--ink-soft); line-height: 1.8; padding-left: 1.2rem;">
          <li>A senior engineer explaining their work over coffee.</li>
          <li>Specific numbers. Specific outcomes. Specific tradeoffs.</li>
          <li>Long sentences when warranted. Short sentences when they hit.</li>
          <li>Opinionated. Willing to say no. Willing to say <em>this is a bad idea.</em></li>
          <li>Quiet confidence — the proof is in the work, not the language.</li>
        </ul>
      </div>
      <div>
        <h3 style="font-family: var(--font-display); font-size: 1.2rem; color: var(--ink); margin: 0 0 1rem;">We don&rsquo;t sound like</h3>
        <ul style="font-family: var(--font-serif); color: var(--ink-soft); line-height: 1.8; padding-left: 1.2rem;">
          <li>An agency pitch deck. <em>&ldquo;We empower brands to scale through&hellip;&rdquo;</em> &mdash; no.</li>
          <li>A junior dev imitating Twitter threads.</li>
          <li>Aspirational marketing fluff. <em>&ldquo;World-class.&rdquo;</em> &mdash; never.</li>
          <li>Defensive or apologetic about scope or timeline.</li>
          <li>Loud. We earn attention through the work, not the volume.</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <span class="eyebrow">5. Tagline system</span>
    <h2 class="h-1" style="margin: 1rem 0 2.5rem;">Three lines. <span class="italic-serif">Use the right one.</span></h2>

    <div style="display: grid; gap: 2rem; max-width: 760px;">
      <div style="padding: 2rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-md);">
        <p style="font-family: var(--font-sans); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em; color: var(--muted); margin: 0 0 0.75rem;">Primary</p>
        <p style="font-family: var(--font-display); font-size: 1.6rem; font-weight: 500; color: var(--ink); margin: 0; letter-spacing: -0.025em;">Senior web engineering for founders.</p>
      </div>

      <div style="padding: 2rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-md);">
        <p style="font-family: var(--font-sans); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em; color: var(--muted); margin: 0 0 0.75rem;">Long form</p>
        <p style="font-family: var(--font-serif); font-size: 1.3rem; line-height: 1.5; color: var(--ink); margin: 0;">Two brothers. A long delivery record. <em>One studio that still answers its own email.</em></p>
      </div>

      <div style="padding: 2rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-md);">
        <p style="font-family: var(--font-sans); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em; color: var(--muted); margin: 0 0 0.75rem;">Verification line (always under hero stats)</p>
        <p style="font-family: var(--font-mono); font-size: 0.95rem; color: var(--ink); margin: 0;">2 Top Rated Upwork operators · high-volume delivery · 100% JSS · almost 15 years</p>
      </div>
    </div>
  </div>
</section>

<section class="section" style="background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
  <div class="container">
    <span class="eyebrow">6. Spacing &amp; radii</span>
    <h2 class="h-1" style="margin: 1rem 0 2rem;">Tight grids. <span class="italic-serif">Generous air.</span></h2>
    <pre style="background: var(--ink); color: #E8E8E8; padding: 1.5rem 2rem; border-radius: var(--r-md); font-family: var(--font-mono); font-size: 0.88rem; line-height: 1.7;">--r-sm: 2px
--r-md: 4px
--r-lg: 6px
--r-xl: 10px

Spacing: 1rem (16px) base. 1.5rem, 2rem, 2.5rem, 3rem standard.
Section padding: 5rem 0 desktop, 3.5rem 0 mobile.
Container max-width: 1200px. Container-narrow: 760px.</pre>
  </div>
</section>

<section class="section">
  <div class="container">
    <span class="eyebrow">7. Don&rsquo;ts</span>
    <h2 class="h-1" style="margin: 1rem 0 2rem;">What we won&rsquo;t do. <span class="italic-serif">Ever.</span></h2>
    <ul style="font-family: var(--font-serif); color: var(--ink-soft); line-height: 1.8; padding-left: 1.2rem; max-width: 60ch;">
      <li>Use emojis in body copy. (Permissible in inline navigation chrome only.)</li>
      <li>Use stock photography of laptops, handshakes, or diverse-team-pointing-at-screen tropes.</li>
      <li>Use the accent rust color (#8B3A1F) on more than one element per fold.</li>
      <li>Use the wordmark smaller than 16px tall, or the lockup smaller than 32px tall.</li>
      <li>Place the mark on backgrounds outside the brand palette without an explicit color override.</li>
      <li>Italicize anything other than the editorial serif italic for emphasis.</li>
    </ul>
  </div>
</section>

{footer}

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/main.js?v={CACHE_VER}" defer></script>
</body>
</html>
'''


def main():
    nav, footer = load_nav_footer()
    work_dir = ROOT / "work"
    work_dir.mkdir(exist_ok=True)
    for p in PILLARS:
        pillar_dir = work_dir / p["slug"]
        pillar_dir.mkdir(exist_ok=True)
        (pillar_dir / "index.html").write_text(render_pillar(p, nav, footer, PILLARS))
        print(f"  ✓ work/{p['slug']}/index.html")

    (ROOT / "brand.html").write_text(render_brand_guide(nav, footer))
    print("  ✓ brand.html")


if __name__ == "__main__":
    main()
