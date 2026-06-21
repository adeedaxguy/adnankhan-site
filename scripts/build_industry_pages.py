#!/usr/bin/env python3
"""
build_industry_pages.py — generates the /websites/ industry hub + one page
per local-business type. Each page has unique, trade-specific copy and full
Service + FAQPage + BreadcrumbList schema. SEO + GEO optimised.

Run:  python3 scripts/build_industry_pages.py
Writes: /websites/index.html  and  /websites/<slug>/index.html
Also rewrites sitemap.xml's <!-- INDUSTRY --> block and llms.txt's section.
"""
import os, html, re, json, pathlib

VER = "20260621k"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://lofts.studio"

# ── Shared chrome (nav + mobile panel + footer + scripts), absolute asset paths,
#    with a new top-level "Websites" link added for site-wide discoverability. ──

NAV = '''<header class="nav-bar">
  <div class="nav-inner">
    <a href="/" class="nav-logo">Lofts<span class="dot">studio</span></a>
    <nav class="nav-links" aria-label="Primary">
      <div class="mega-wrap">
        <button class="nav-link" data-mega-trigger aria-expanded="false" aria-haspopup="true">
          Work
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="mega" role="menu">
          <div class="mega-col">
            <h4>By vertical</h4>
            <a href="/work/ecommerce/" class="mega-link"><div class="mega-link-title">Ecommerce</div><div class="mega-link-desc">Shopify, WooCommerce, headless.</div></a>
            <a href="/work/insurance-finance/" class="mega-link"><div class="mega-link-title">Insurance &amp; Finance</div><div class="mega-link-desc">Brokers, carriers, reinsurance.</div></a>
            <a href="/work/membership-community/" class="mega-link"><div class="mega-link-title">Membership &amp; Community</div><div class="mega-link-desc">Stripe, Discord, Whop.</div></a>
            <a href="/work/custom-apps/" class="mega-link"><div class="mega-link-title">Custom Apps</div><div class="mega-link-desc">React, Next.js, Node.</div></a>
          </div>
          <div class="mega-col">
            <h4>For local business</h4>
            <a href="/websites/" class="mega-link"><div class="mega-link-title">Websites by industry</div><div class="mega-link-desc">Restaurants, clinics, trades &amp; more.</div></a>
            <a href="/services/woocommerce-development.html" class="mega-link"><div class="mega-link-title">WordPress &amp; WooCommerce</div><div class="mega-link-desc">The local-business workhorse.</div></a>
            <a href="/services/shopify-development.html" class="mega-link"><div class="mega-link-title">Shopify Development</div><div class="mega-link-desc">Sell online, done right.</div></a>
            <a href="/free-audit/" class="mega-link"><div class="mega-link-title">Free 15-min Audit</div><div class="mega-link-desc">Why you&rsquo;re not getting found.</div></a>
          </div>
          <div class="mega-col">
            <h4>Performance</h4>
            <a href="/services/speed-optimization.html" class="mega-link"><div class="mega-link-title">Speed Optimization</div><div class="mega-link-desc">90+ Lighthouse. Sub-2s LCP.</div></a>
            <a href="/services/conversion-rate-optimization.html" class="mega-link"><div class="mega-link-title">Conversion Optimization</div><div class="mega-link-desc">Turn visits into calls.</div></a>
            <a href="/services/technical-seo-audit.html" class="mega-link"><div class="mega-link-title">Technical SEO Audit</div><div class="mega-link-desc">Get found on Google.</div></a>
            <a href="/services/landing-page-sprint.html" class="mega-link"><div class="mega-link-title">Landing Page Sprint</div><div class="mega-link-desc">Seven days, fixed scope.</div></a>
          </div>
          <div class="mega-feature">
            <div>
              <span class="tag">Two founders. Two cities.</span>
              <h3 style="font-family: var(--font-display); font-weight: 500; font-size: 1.15rem; line-height: 1.3; margin: 0.6rem 0; color: var(--ink); letter-spacing: -0.025em;">Adnan Khan (Multan) leads ecommerce. Irfan Khan (Dubai) leads full-stack. Both Top Rated on Upwork.</h3>
            </div>
            <a href="/about.html" class="btn-link" style="margin-top: 1rem; font-size: 0.85rem;">
              Meet the founders
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
            </a>
          </div>
        </div>
      </div>
      <a href="/websites/" class="nav-link">Web Design</a>
      <a href="/portfolio/" class="nav-link">Portfolio</a>
      <a href="/process/" class="nav-link">Process</a>
      <a href="/notes/" class="nav-link">Notes</a>
      <a href="/about.html" class="nav-link">About</a>
    </nav>
    <a href="/#contact" class="btn btn-primary">
      Start a conversation
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
    </a>
    <button id="menuBtn" class="menu-btn" aria-label="Open menu" aria-expanded="false">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="21" y1="12" y2="12"/><line x1="3" x2="21" y1="18" y2="18"/></svg>
    </button>
  </div>
</header>

<!-- Full-screen mobile nav overlay — must be outside <header> -->
<div id="mobilePanel" class="mnav" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Navigation">
  <div class="mnav-inner">
    <div class="mnav-top">
      <a href="/" class="mnav-logo">Lofts<span>studio</span></a>
      <button class="mnav-close" id="menuClose" aria-label="Close menu">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <nav class="mnav-primary" aria-label="Main">
      <a href="/websites/" class="mnav-link" data-num="01">Web Design</a>
      <a href="/portfolio/" class="mnav-link" data-num="02">Portfolio</a>
      <a href="/about.html" class="mnav-link" data-num="03">About</a>
      <a href="/process/" class="mnav-link" data-num="04">Process</a>
      <a href="/services/" class="mnav-link" data-num="05">Services</a>
      <a href="/blog/" class="mnav-link" data-num="06">Blog</a>
    </nav>
    <div class="mnav-services">
      <p class="mnav-label">Services</p>
      <div class="mnav-grid">
        <a href="/services/shopify-development.html">Shopify</a>
        <a href="/services/woocommerce-development.html">WooCommerce</a>
        <a href="/services/webflow-development.html">Webflow</a>
        <a href="/services/shopify-plus-migration.html">Shopify Plus</a>
        <a href="/services/speed-optimization.html">Speed Opt.</a>
        <a href="/services/conversion-rate-optimization.html">CRO</a>
        <a href="/services/custom-app-development.html">Custom Apps</a>
        <a href="/services/ai-calling-agents.html">AI Calling</a>
      </div>
    </div>
    <a href="/free-audit/" class="mnav-audit-link">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
      Free 15-min Audit
    </a>
    <div class="mnav-foot">
      <a href="/#contact" class="mnav-cta">
        Start a conversation
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
      </a>
      <p class="mnav-meta">Multan &nbsp;·&nbsp; Dubai &nbsp;·&nbsp; US, UK &amp; CA hours</p>
    </div>
  </div>
</div>'''

FOOTER = '''<footer class="site-footer footer-rich">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="footer-logo">
          <span class="footer-logo-italic">Lofts<span class="footer-logo-dot">.</span></span>
          <span class="footer-logo-caps">STUDIO</span>
        </div>
        <p class="footer-tag">Senior web engineering led by brothers <strong>Adnan Khan</strong> (Multan) and <strong>Irfan Khan</strong> (Dubai). Two Top Rated Upwork operators. A long delivery record. Almost 15 years. Built for owners who can tell the difference between a site that merely launches and one that earns its keep.</p>
        <p class="footer-tag" style="margin-top: 1rem; font-size: 0.86rem; color: var(--muted);">
          <span style="display: inline-block; width: 5px; height: 5px; border-radius: 50%; background: var(--accent); margin-right: 0.4rem; vertical-align: middle;"></span>
          Multan, Pakistan &nbsp;&middot;&nbsp; Dubai, UAE &nbsp;&middot;&nbsp; US, UK &amp; Canada callable hours
        </p>
      </div>
      <div class="footer-newsletter" data-lead-wrap>
        <p class="footer-newsletter-eyebrow">Field notes, occasionally</p>
        <h3 class="footer-newsletter-title">One short essay a month. <span class="italic-serif">No newsletter cadence theater.</span></h3>
        <form data-lead class="footer-newsletter-form" action="/api/contact" method="POST">
          <input type="hidden" name="_subject" value="Newsletter signup — lofts.studio" />
          <input type="hidden" name="_captcha" value="false" />
          <input type="hidden" name="source" value="footer-newsletter" />
          <label class="sr-only" for="footer-newsletter-email">Email address</label>
          <input id="footer-newsletter-email" name="email" type="email" required placeholder="your@email.com" />
          <button type="submit">Subscribe
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </button>
        </form>
        <div data-lead-success class="footer-newsletter-success" style="display: none;">Thanks &mdash; you&rsquo;ll hear from me when the next note goes out.</div>
        <p class="footer-newsletter-note">No sequences. No tracking pixels. Unsubscribe at the bottom of any note.</p>
      </div>
    </div>
    <div class="footer-grid">
      <div>
        <h5>Websites by industry</h5>
        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.7rem; font-size: 0.92rem;">
          <li><a href="/websites/">All industries</a></li>
          <li><a href="/websites/restaurants/">Restaurants</a></li>
          <li><a href="/websites/dentists/">Dentists &amp; clinics</a></li>
          <li><a href="/websites/trades/">Trades &amp; contractors</a></li>
          <li><a href="/websites/law-firms/">Law firms</a></li>
          <li><a href="/websites/real-estate/">Real estate</a></li>
        </ul>
        <h5 style="margin-top: 1.5rem;">Services</h5>
        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.7rem; font-size: 0.92rem;">
          <li><a href="/services/woocommerce-development.html">WordPress &amp; WooCommerce</a></li>
          <li><a href="/services/shopify-development.html">Shopify Development</a></li>
          <li><a href="/services/speed-optimization.html">Speed Optimization</a></li>
          <li><a href="/services/technical-seo-audit.html">Technical SEO</a></li>
        </ul>
      </div>
      <div>
        <h5>Studio</h5>
        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.7rem; font-size: 0.92rem;">
          <li><a href="/about.html">About</a></li>
          <li><a href="/portfolio/">All work (47)</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/process/">Process</a></li>
          <li><a href="/notes/">Notes</a></li>
          <li><a href="/brand.html">Brand</a></li>
        </ul>
        <h5 style="margin-top: 1.5rem;">Founders</h5>
        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.7rem; font-size: 0.92rem;">
          <li><a href="https://www.upwork.com/freelancers/wordpressandshopifydeveloper" target="_blank" rel="noopener">Adnan Khan &middot; Multan</a></li>
          <li><a href="https://www.upwork.com/freelancers/irfankhan" target="_blank" rel="noopener">Irfan Khan &middot; Dubai</a></li>
        </ul>
      </div>
      <div>
        <h5>Talk</h5>
        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.7rem; font-size: 0.92rem;">
          <li class="meta">Mon&ndash;Sat &nbsp;·&nbsp; 4-hour reply</li>
          <li class="meta">US, UK &amp; CA hours covered</li>
          <li><a href="/free-audit/">Free 15-min audit &nbsp;→</a></li>
          <li><a href="/#contact">Send a note &nbsp;→</a></li>
        </ul>
        <h5 style="margin-top: 1.5rem;">Legal</h5>
        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.7rem; font-size: 0.92rem;">
          <li><a href="/privacy.html">Privacy</a></li>
          <li><a href="/terms.html">Terms</a></li>
          <li><a href="/cookie-policy.html">Cookie policy</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="meta" style="margin: 0;">&copy; <span data-year>2026</span> Lofts Studio &middot; Multan, Pakistan &middot; Dubai, UAE &middot; Two Top Rated Upwork operators.</p>
      <p class="meta" style="margin: 0;">CAN-SPAM &amp; UK GDPR compliant &nbsp;·&nbsp; Async, documented delivery</p>
    </div>
  </div>
</footer>
<style>
@media (max-width: 880px) {
  .footer-grid { grid-template-columns: 1fr 1fr !important; gap: 2rem !important; }
}
@media (max-width: 560px) { .footer-grid { grid-template-columns: 1fr !important; } }
.ind-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.25rem; }
.ind-card { display: block; padding: 1.6rem 1.5rem; border: 1px solid var(--line); border-radius: var(--r-lg); background: var(--surface); transition: border-color .2s, transform .2s, box-shadow .2s; }
.ind-card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: var(--shadow-card); }
.ind-card h3 { font-family: var(--font-sans); font-size: 1.02rem; font-weight: 600; margin: 0 0 0.3rem; color: var(--ink); letter-spacing: -0.01em; }
.ind-card p { margin: 0; font-size: 0.88rem; color: var(--muted); line-height: 1.5; }
.ind-cat { font-family: var(--font-sans); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.18em; color: var(--muted-2); margin: 2.5rem 0 1.1rem; }
.feat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
.feat-card { padding: 1.6rem; border: 1px solid var(--line); border-radius: var(--r-lg); background: var(--surface); }
.feat-card h3 { font-family: var(--font-sans); font-size: 1rem; font-weight: 600; margin: 0 0 0.4rem; color: var(--ink); }
.feat-card p { margin: 0; font-size: 0.92rem; color: var(--ink-soft); line-height: 1.6; }
.answer-box { border-left: 3px solid var(--accent); background: var(--bg-soft); padding: 1.4rem 1.6rem; border-radius: 0 var(--r-md) var(--r-md) 0; margin: 2rem 0; }
.answer-box p { margin: 0; font-size: 1.02rem; line-height: 1.65; color: var(--ink-soft); }
.faq-item { border-top: 1px solid var(--line); padding: 1.5rem 0; }
.faq-item h3 { font-family: var(--font-sans); font-size: 1.02rem; font-weight: 600; margin: 0 0 0.5rem; color: var(--ink); }
.faq-item p { margin: 0; color: var(--ink-soft); line-height: 1.65; }
@media (max-width: 720px) { .ind-grid, .feat-grid { grid-template-columns: 1fr; } }
</style>
<!-- GSAP — async, non-render-blocking. main.js detects and gracefully degrades. -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/main.js?v=''' + VER + '''" defer></script>
<a href="/#contact" class="audit-cta">
  <span class="audit-cta-mark" aria-hidden="true"></span>
  Book a free 15-min audit
  <svg class="audit-cta-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
</a>
<script src="/assets/widgets.js?v=''' + VER + '''" defer></script>
</body>
</html>'''


def esc(s):
    return html.escape(s, quote=True)


def head(title, desc, canonical, jsonld_blocks, og_title=None):
    og_title = og_title or title
    blocks = "\n".join(
        '<script type="application/ld+json">\n' + b + '\n</script>' for b in jsonld_blocks
    )
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{canonical}" />
<meta name="robots" content="index,follow,max-image-preview:large" />

<meta property="og:type" content="website" />
<meta property="og:url" content="{canonical}" />
<meta property="og:title" content="{esc(og_title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://lofts.studio/assets/og.jpg?v=2" />
<meta name="twitter:card" content="summary_large_image" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="alternate icon" href="/favicon.svg" />
<link rel="icon" type="image/png" href="/apple-touch-icon.png" />
<link rel="apple-touch-icon" href="/favicon.svg" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={VER}" />

{blocks}
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1KT1MFDY8R"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-1KT1MFDY8R');
  </script>
  <script>(function(){{try{{var m=localStorage.getItem('lofts-theme')||'device';var d=m==='dark'||(m==='device'&&window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches);document.documentElement.setAttribute('data-theme',d?'dark':'light');}}catch(e){{}}}})();</script>
</head>
<body>
'''


def breadcrumb_jsonld(items):
    el = ", ".join(
        f'{{"@type": "ListItem", "position": {i+1}, "name": "{esc(n)}", "item": "{u}"}}'
        for i, (n, u) in enumerate(items)
    )
    return f'{{ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [ {el} ] }}'


def faq_jsonld(faqs):
    qa = ", ".join(
        '{"@type": "Question", "name": %s, "acceptedAnswer": {"@type": "Answer", "text": %s}}'
        % (json.dumps(q), json.dumps(a))
        for q, a in faqs
    )
    return '{ "@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [ %s ] }' % qa


def service_jsonld(name, kw, canonical):
    return ('{ "@context": "https://schema.org", "@type": "Service", '
            f'"name": "{esc(name)} Website Design & Development", '
            '"provider": { "@type": "Organization", "name": "Lofts Studio", "@id": "https://lofts.studio/#organization", "url": "https://lofts.studio/" }, '
            f'"serviceType": "{esc(kw)} design and development", '
            '"areaServed": ["United States", "United Kingdom", "Canada"], '
            f'"url": "{canonical}", '
            f'"description": "Fast, search-optimised websites for {esc(name.lower())} that get found on Google and turn visitors into booked customers." }}')


# ── Trade data. Each entry's problem / includes / local / faqs are unique to
#    the trade; shared studio scaffolding (proof, process, CTA) is templated. ──
def T(cat, slug, name, kw, desc, eyebrow, h1a, h1b, lead, answer, problem, includes, local, faqs):
    return dict(cat=cat, slug=slug, name=name, kw=kw, desc=desc, eyebrow=eyebrow,
                h1a=h1a, h1b=h1b, lead=lead, answer=answer, problem=problem,
                includes=includes, local=local, faqs=faqs)

TRADES = [
 # ───────────────────────── FOOD & HOSPITALITY ─────────────────────────
 T("Food & Hospitality","restaurants","Restaurants","restaurant website",
   "Restaurant website design that loads fast, shows your menu instantly, takes reservations, and gets you found on Google Maps. Built for independent restaurants and cafés.",
   "Restaurants &amp; Cafés","A restaurant site that","fills tables",
   "Most people decide where to eat on their phone in under a minute. Your website&rsquo;s only job is to make that decision easy — menu, hours, location, and a way to book, all before the page even finishes loading.",
   "A great restaurant website loads in under two seconds on mobile, puts the menu and hours one tap away, takes reservations directly, and feeds Google your location, photos, and opening times so you surface on Maps and &ldquo;restaurants near me&rdquo; searches.",
   "The two things that lose you covers are a menu trapped in a slow PDF and a site that doesn&rsquo;t show up when someone searches your area. Diners won&rsquo;t pinch-zoom a PDF, and they won&rsquo;t scroll to page two of Google to find you.",
   [("Instant, mobile-first menu","A real HTML menu — searchable, fast, easy to update yourself. No PDFs, no zooming."),
    ("Reservations &amp; waitlist","Direct booking (or your OpenTable/Resy embed) so tables fill without a phone call."),
    ("Google Maps &amp; hours","Structured location, hours, and holiday hours so Google shows you correctly in local results."),
    ("Photos that sell the room","Fast-loading galleries of the food and space — the single biggest driver of a first visit.")],
   "Diners search &ldquo;[food] near me&rdquo; and &ldquo;best restaurant in [town]&rdquo; on their phones, then judge you in seconds on Google. We make sure your hours, menu, and photos are correct everywhere Google looks, so you win that glance.",
   [("How much detail should go on a restaurant website?","Enough to make the decision easy: menu, hours, location, a few strong photos, and a way to book. Anything more usually gets in the way on a phone."),
    ("Do I still need a website if I have Instagram and a Google listing?","Yes. Instagram and Google get people interested, but you don&rsquo;t own them and they can&rsquo;t hold your full menu or take reservations cleanly. Your website is the one place you control."),
    ("Can I update the menu myself?","Yes. We build the menu so you can change services and dishes in minutes, with no developer and no waiting."),
    ("Will it work for takeout and delivery too?","Absolutely — we can add direct online ordering or link your existing delivery platforms, whichever adds overhead you less in margin leakage.")]),
 T("Food & Hospitality","cafes-bakeries","Cafés &amp; Bakeries","cafe website",
   "Café and bakery website design — fast menus, opening hours, online ordering and pre-orders, and local SEO so regulars and newcomers find you first.",
   "Cafés &amp; Bakeries","A café site that","brings the regulars in",
   "A café lives on its regulars and the steady trickle of newcomers who searched &ldquo;coffee near me.&rdquo; Your website should win both — clear hours, a tempting menu, and easy pre-orders for the morning rush.",
   "A strong café or bakery website shows accurate opening hours front and centre, loads a mouth-watering menu instantly, and offers pre-orders or click-and-collect so the morning queue moves faster and bigger orders come in ahead of time.",
   "Cafés lose business to one thing more than any other: wrong or hidden opening hours. If Google shows you as closed when you&rsquo;re open, that customer is already walking to the next place.",
   [("Always-accurate hours","Opening hours that sync with Google so nobody arrives to a locked door — or skips you thinking you&rsquo;re shut."),
    ("Pre-orders &amp; click-and-collect","Let customers order cakes, boxes, and morning coffees ahead — fewer queues, bigger tickets."),
    ("A menu that tempts","Fast, photo-led menu for seasonal specials and bakes, editable by you in minutes."),
    ("Local discovery","Structured data and reviews so you win &ldquo;coffee near me&rdquo; and &ldquo;bakery in [town].&rdquo;")],
   "Most café visits start with a phone search for coffee or a specific bake nearby. We make your hours, location, and best photos unmissable on Google so the casual searcher chooses you.",
   [("Can customers pre-order cakes or large orders online?","Yes — we build a simple pre-order flow so custom cakes, party boxes, and bulk orders come in with the details and deposit already sorted."),
    ("How do I stop Google showing the wrong opening hours?","We wire your hours into structured data and your Google Business Profile so they stay correct everywhere, including holidays."),
    ("Is a website worth it for a small café?","Yes — even a one-page site with hours, menu, and directions captures the &ldquo;near me&rdquo; searches that would otherwise go to a competitor."),
    ("Can I add online coffee-bean or merch sales later?","Easily. We can bolt a small shop onto your site whenever you&rsquo;re ready, without rebuilding.")]),
 T("Food & Hospitality","bars-pubs","Bars &amp; Pubs","bar website",
   "Bar and pub website design — events, what&rsquo;s-on listings, bookings for tables and functions, and local SEO that fills the room on quiet nights.",
   "Bars &amp; Pubs","A bar site that","fills the room",
   "A bar or pub sells an experience and a calendar — quiz nights, live music, the big game, Sunday roasts. Your website should make tonight&rsquo;s reason to come in obvious, and let people book a table or a function in a couple of taps.",
   "A good bar or pub website leads with what&rsquo;s on this week, makes table and function bookings effortless, shows accurate hours and kitchen times, and ranks for &ldquo;pubs near me&rdquo; and &ldquo;bars in [town]&rdquo; so footfall doesn&rsquo;t depend on luck.",
   "Pubs live and die on events and function bookings, yet most pub websites bury both. If finding your quiz night or booking a birthday means a phone call, you&rsquo;ve lost half the people.",
   [("What&rsquo;s-on &amp; events","A live calendar of quiz nights, live music, screenings, and specials — the reason people come in tonight."),
    ("Table &amp; function bookings","Direct bookings for tables and private functions, with the details captured up front."),
    ("Kitchen &amp; bar hours","Separate, accurate hours for food and drink so nobody turns up after the kitchen closes."),
    ("Local discovery","Reviews and structured data that win &ldquo;pub near me&rdquo; and &ldquo;Sunday roast in [town].&rdquo;")],
   "People search &ldquo;pubs near me,&rdquo; &ldquo;live music tonight,&rdquo; and &ldquo;function room [town]&rdquo; on the night or a few days ahead. We make your events and bookings the first thing Google and your visitors see.",
   [("Can I manage events myself?","Yes — add, edit, and remove events in minutes. The calendar and homepage update automatically."),
    ("Can people book function rooms online?","Yes. We build an enquiry-to-booking flow that captures date, headcount, and requirements so you reply with a enquiry, not twenty questions."),
    ("Do I need separate food and drink hours?","If your kitchen closes before the bar, yes — and we make both unmistakable so customers aren&rsquo;t disappointed."),
    ("Will it help on quiet weeknights?","That&rsquo;s exactly what the events calendar and local SEO are for — giving people a specific reason and making it easy to find.")]),
 T("Food & Hospitality","caterers","Caterers","catering website",
   "Catering website design that turns enquiries into booked events — clear packages, fast project requests, galleries, and SEO for &ldquo;catering near me.&rdquo;",
   "Caterers","A catering site that","books real events",
   "Catering is sold on trust and a fast, detailed enquiry. Your website should show the range of what you do, make the enquiry effortless, and get back the answers you need to scope — date, headcount, dietary, venue — in one go.",
   "A high-converting catering website presents clear service types and sample menus, shows a strong gallery of past events, and uses a structured enquiry form that captures date, guest count, and requirements so you can enquiry fast and win the booking.",
   "Most catering sites either show too little to build trust or make enquiring a vague &ldquo;contact us.&rdquo; Either way, the client moves on to the caterer who made it easy to picture the event and quick to ask.",
   [("Services &amp; sample menus","Weddings, corporate, private — clear packages and menus that set expectations before they call."),
    ("Smart enquiry form","Captures date, headcount, dietary needs, and venue so your first reply is a enquiry, not a questionnaire."),
    ("Event gallery","Real photos of plated food and set tables — the proof that turns interest into a booking."),
    ("Local &amp; occasion SEO","Ranks for &ldquo;wedding catering [town]&rdquo; and &ldquo;corporate catering near me&rdquo; when demand is highest.")],
   "Clients search by occasion and area — &ldquo;wedding catering near me,&rdquo; &ldquo;office lunch catering [town].&rdquo; We structure your pages around those searches so the right enquiries land in your inbox.",
   [("What makes a catering website actually win bookings?","A clear sense of what you do, proof you do it well, and an enquiry form that gathers enough to enquiry quickly. Speed of reply wins more catering jobs than anything else."),
    ("Should I show services?","Usually not defined scopes — catering is bespoke. We frame it around packages and a fast enquiry instead, which sets expectations without scaring anyone off."),
    ("Can the form capture dietary and venue details?","Yes — we tailor the enquiry fields to exactly what you need to scope a job, so there&rsquo;s less back-and-forth."),
    ("Can you separate weddings from corporate work?","Yes. Dedicated pages for each occasion rank better and speak to very different buyers.")]),
 T("Food & Hospitality","hotels-bnb","Hotels &amp; B&amp;Bs","hotel website",
   "Hotel and B&B website design that drives direct bookings — fast galleries, room details, a margin leakage-free booking path, and local SEO.",
   "Hotels &amp; B&amp;Bs","A hotel site that","wins direct bookings",
   "Every booking through an OTA adds overhead you 15&ndash;20% in margin leakage. A fast, trustworthy website that lets guests book direct is the highest-return marketing a small hotel or B&amp;B can own.",
   "A strong hotel or B&amp;B website loads beautiful, fast room galleries, shows availability and rates clearly, and offers a direct booking path that saves the OTA margin leakage — backed by local SEO and reviews that build trust before the guest commits.",
   "Small hotels hand a fifth of their revenue to booking platforms because their own site feels slower and less trustworthy than the OTA. Fix that, and every direct booking is money you keep.",
   [("Room galleries that sell","Fast, full-screen photography of rooms and common areas — the deciding factor for most bookings."),
    ("Direct, margin leakage-free booking","A clean booking path (or your booking engine, embedded) so guests book with you, not an OTA."),
    ("Availability &amp; rates","Clear room types, rates, and what&rsquo;s included, with no surprises at checkout."),
    ("Local &amp; trust SEO","Structured data, reviews, and area guides that win &ldquo;hotels in [town]&rdquo; and build confidence to book direct.")],
   "Guests compare you against OTAs and nearby stays on their phone. We make your direct site faster and more reassuring than the alternatives, and ensure Google shows your rooms, reviews, and location accurately.",
   [("How does a website get me more direct bookings?","By being faster and more trustworthy than the OTA listing, with a booking path that&rsquo;s just as easy — so guests have no reason to pay the middleman&rsquo;s markup."),
    ("Can it connect to my booking system?","Yes — we integrate your existing booking engine or channel manager so availability stays in sync."),
    ("Do reviews matter for a small B&B?","Hugely. We surface your best reviews and wire up structured data so they show in Google, which is often what tips a direct booking."),
    ("Can you add area guides and packages?","Yes — local guides and seasonal packages both rank well and give guests a reason to book longer stays.")]),
 # ───────────────────────── HEALTH & MEDICAL ─────────────────────────
 T("Health & Medical","dentists","Dentists","dentist website",
   "Dental website design that books new patients — online booking, new-patient intake, treatment pages, and local SEO that wins &ldquo;dentist near me.&rdquo;",
   "Dental Practices","A dental site that","books new patients",
   "A new patient is worth thousands over their lifetime, and they almost always start with a Google search and a quick look at your website. It has to load fast, look clean and trustworthy, and let them book without a phone call.",
   "A strong dental website ranks for &ldquo;dentist near me,&rdquo; loads fast on mobile, builds trust with clear treatment information and real reviews, and lets new patients book or request an appointment online instead of calling during work hours.",
   "Most dental sites lose new patients in two ways: they look dated enough to seem risky, and they force a phone call to book. Today&rsquo;s patients book hair appointments online — they expect the same from your practice.",
   [("Online booking &amp; intake","New patients book or request appointments and complete intake forms before they arrive — fewer calls, fuller diary."),
    ("Treatment pages that rank","Clear pages for implants, Invisalign, whitening, and check-ups that win specific high-intent searches."),
    ("Trust &amp; reviews","Real patient reviews, credentials, and a clean modern design that reassures nervous patients."),
    ("Local SEO","Structured data and a tuned Google Business Profile so you win &ldquo;dentist near me&rdquo; and &ldquo;emergency dentist [town].&rdquo;")],
   "Patients search &ldquo;dentist near me,&rdquo; &ldquo;Invisalign [town],&rdquo; and &ldquo;emergency dentist&rdquo; and pick from the first few results. We build the treatment pages and local signals that put you there, then make booking effortless.",
   [("How do dental websites attract new patients?","By ranking for local treatment searches, loading fast and looking trustworthy, and letting people book online the moment they decide — instead of losing them to a phone queue."),
    ("Is online booking secure and compliant?","Yes. We use compliant booking and intake tools and keep patient data handled correctly for your region."),
    ("Should each treatment have its own page?","Yes — dedicated pages for implants, Invisalign, whitening and so on rank far better than one &ldquo;services&rdquo; list and bring in higher-value patients."),
    ("Can you redesign without losing my Google ranking?","Yes. We preserve your URLs, content, and rankings during the rebuild — a migration done properly is invisible to Google.")]),
 T("Health & Medical","medical-clinics","Doctors &amp; Clinics","medical clinic website",
   "Medical clinic and private GP website design — clear services, online appointment requests, trust signals, and accessible, compliant, fast pages.",
   "Doctors &amp; Private Clinics","A clinic site that","earns patient trust",
   "Patients choosing a private clinic are weighing trust above all. Your website has to feel professional, load quickly, explain your services plainly, and let people request an appointment without friction.",
   "A good medical clinic website presents services and clinicians clearly, signals trust through credentials and reviews, meets accessibility standards, and offers a simple, compliant way to request or book an appointment online.",
   "Clinic websites often hide the basics — services, who the clinicians are, how to be seen — behind dense text or a single phone number. Anxious patients want clarity and an easy next step, fast.",
   [("Clear services &amp; clinicians","Plain-language service pages and clinician profiles that build confidence before the first visit."),
    ("Appointment requests","Compliant online booking or request forms so patients reach you outside phone hours."),
    ("Accessibility &amp; speed","Fast, WCAG-minded pages that work for every patient and rank well on Google."),
    ("Local &amp; condition SEO","Pages that win &ldquo;private GP [town]&rdquo; and specific condition or service searches.")],
   "Patients search for specific services and conditions in their area. We build clear, trustworthy pages around those terms so the right patients find you and feel confident getting in touch.",
   [("Can patients request appointments online?","Yes — we add compliant booking or request forms so patients can reach you any time, with the details you need to triage."),
    ("Will the site meet accessibility requirements?","We build to recognised accessibility standards so your site works for every patient and avoids compliance risk."),
    ("Should clinicians have individual profiles?","Yes — clinician profiles build trust and rank for name and specialty searches, both of which bring in patients."),
    ("How do you handle patient privacy?","We keep forms and data handling compliant for your region and never expose sensitive information in the page or analytics.")]),
 T("Health & Medical","physiotherapy","Physiotherapy &amp; Chiropractic","physiotherapy website",
   "Physiotherapy and chiropractic website design — online booking, condition pages, reviews, and local SEO that books more appointments.",
   "Physio &amp; Chiropractic","A clinic site that","keeps the diary full",
   "Physio and chiro clinics live on a full appointment book. Your website&rsquo;s job is to rank for the injuries and conditions you treat, build trust fast, and let people book the moment the pain makes them act.",
   "An effective physiotherapy or chiropractic website ranks for condition and injury searches, shows real reviews and clear scoping-free service info, and offers online booking so patients can grab a slot the instant they decide to seek help.",
   "People book physio on impulse, often in pain and often after hours. If your site doesn&rsquo;t rank for their problem or doesn&rsquo;t let them book right then, they call the next clinic.",
   [("Online booking","Let patients book or request appointments 24/7 — most physio bookings happen outside clinic hours."),
    ("Condition &amp; treatment pages","Pages for back pain, sports injuries, sciatica and more that win specific, high-intent searches."),
    ("Reviews &amp; results","Real patient outcomes and reviews that turn a searcher into a booking."),
    ("Local SEO","Structured data and Google Business tuning to win &ldquo;physio near me&rdquo; and &ldquo;chiropractor [town].&rdquo;")],
   "Patients search their exact problem plus their area — &ldquo;sports physio near me,&rdquo; &ldquo;back pain chiropractor [town].&rdquo; We build the condition pages and local signals that capture those searches and route them straight to your booking.",
   [("Why is online booking so important for physio?","Because most people decide to book in the evening or at the weekend, in pain. If they can book instantly, they book you; if they have to wait for office hours, they don&rsquo;t."),
    ("Should I have a page per condition?","Yes — condition-specific pages rank far better and bring in patients who are ready to book for that exact problem."),
    ("Can it integrate with my booking software?","Yes — we connect Cliniko, Jane, or your existing system so the diary stays accurate."),
    ("Will reviews really make a difference?","Strongly. For health decisions, real reviews and outcomes are often the deciding factor, so we put them front and centre.")]),
 T("Health & Medical","opticians","Opticians &amp; Eye Care","opticians website",
   "Opticians and optometry website design — eye-test booking, frames ranges, clinical trust, and local SEO that books appointments.",
   "Opticians &amp; Optometry","An opticians site that","books eye tests",
   "Opticians sell two things — clinical care and eyewear — and your website should make booking an eye test as easy as browsing frames. The practices that win make both effortless on a phone.",
   "A strong opticians website lets patients book an eye test online, showcases frame ranges and lens options, signals clinical credibility, and ranks locally for &ldquo;opticians near me&rdquo; and &ldquo;eye test [town].&rdquo;",
   "Most opticians&rsquo; sites treat the eye test as an afterthought behind a phone number, while the high-street chains let you book online in seconds. That gap is appointments walking out the door.",
   [("Eye-test booking","Online appointment booking for eye tests and contact-lens checks, day or night."),
    ("Frames &amp; lenses","Show your ranges, designer brands, and lens options so patients arrive knowing what they want."),
    ("Clinical trust","Optometrist profiles, equipment, and reviews that reassure patients you&rsquo;re more than retail."),
    ("Local SEO","Structured data and reviews to win &ldquo;opticians near me&rdquo; and &ldquo;emergency eye appointment [town].&rdquo;")],
   "Patients search &ldquo;opticians near me&rdquo; and &ldquo;book eye test [town]&rdquo; and expect to book on the spot. We make your booking and local presence match the chains, so independents keep the appointment.",
   [("Can patients book eye tests online?","Yes — we add online booking for tests and contact-lens checks so you capture appointments around the clock."),
    ("Should I show my frame ranges online?","Yes — showcasing brands and ranges draws people in and lets them arrive with a shortlist, which lifts dispensing."),
    ("How do I compete with the big chains online?","By matching them on booking convenience and beating them on local trust — real optometrist profiles, reviews, and community presence, all of which we surface."),
    ("Can it handle NHS and private clearly?","Yes — we lay out what&rsquo;s available clearly so patients understand their options before they arrive.")]),
 T("Health & Medical","veterinary","Veterinary Practices","veterinary website",
   "Veterinary website design — appointment booking, new-client registration, emergency info, and local SEO that wins anxious pet owners.",
   "Veterinary Practices","A vet site that","registers new clients",
   "Pet owners choose a vet with their heart and their phone. Your website needs to feel caring and competent, make registration and booking easy, and be crystal clear about emergencies — because that&rsquo;s when people search hardest.",
   "A good veterinary website makes booking and new-client registration easy, gives unmistakable emergency and out-of-hours information, builds trust with the team and services, and ranks for &ldquo;vet near me&rdquo; and &ldquo;emergency vet [town].&rdquo;",
   "When a pet is sick, owners panic-search and need answers in seconds — hours, location, emergency number. A slow or vague vet site at that moment sends a frightened owner straight to a competitor.",
   [("Booking &amp; registration","Online appointment booking and new-client registration so owners join without a phone call."),
    ("Emergency &amp; out-of-hours","Impossible-to-miss emergency info — the highest-stress, highest-search moment you must own."),
    ("Team &amp; services","Warm profiles and clear services that build the trust pet owners need."),
    ("Local SEO","Structured data and reviews to win &ldquo;vet near me&rdquo; and &ldquo;emergency vet [town]&rdquo; the instant they&rsquo;re searched.")],
   "Owners search &ldquo;vet near me,&rdquo; &ldquo;emergency vet [town],&rdquo; and specific worries about their pet. We make your hours, emergency info, and reassurance unmissable on Google for exactly those moments.",
   [("How important is emergency information?","Critical. The highest-intent searches a vet gets are emergencies, so we make your emergency and out-of-hours details the easiest thing to find on the whole site."),
    ("Can new clients register online?","Yes — online registration and booking let owners join and book without waiting for the phone lines, which captures more new clients."),
    ("Will it help with routine bookings too?","Yes — easy online booking lifts vaccination, check-up, and dental bookings, not just emergencies."),
    ("Can you show our team warmly but professionally?","That&rsquo;s the balance we aim for — caring and competent — because pet owners choose on both.")]),
 T("Health & Medical","therapists","Therapists &amp; Counsellors","therapist website",
   "Therapist and counsellor website design — calm, trustworthy, with easy enquiry, clear specialisms, and local SEO that fills your practice.",
   "Therapists &amp; Counsellors","A therapy site that","fills your practice",
   "Choosing a therapist is deeply personal. Your website should feel calm and safe, explain how you help and who you help, and make that first nervous step — getting in touch — as gentle and easy as possible.",
   "A good therapist website feels calm and trustworthy, clearly states your specialisms and approach, reassures on confidentiality, and offers a low-pressure way to enquire or book a first session — backed by local and specialism-based SEO.",
   "Clients often hesitate for weeks before reaching out. A cold, clinical, or confusing website adds friction at the exact moment they need reassurance — and they close the tab.",
   [("Gentle enquiry path","A warm, low-pressure contact or booking form that makes the first step feel safe."),
    ("Specialisms &amp; approach","Clear pages on what you help with — anxiety, couples, trauma — that rank and resonate."),
    ("Trust &amp; confidentiality","Credentials, memberships, and a calm tone that reassure before the first message."),
    ("Local &amp; remote SEO","Win &ldquo;therapist near me,&rdquo; specialism searches, and online-therapy searches across your region.")],
   "Clients search by need and area — &ldquo;anxiety therapist near me,&rdquo; &ldquo;couples counselling [town],&rdquo; &ldquo;online therapist.&rdquo; We build calm, clear pages around your specialisms so the right clients find you and feel safe reaching out.",
   [("What matters most on a therapist&rsquo;s website?","Feeling safe. A calm design, plain explanation of how you help, and a gentle way to make contact matter more than anything flashy."),
    ("Should I list my specialisms separately?","Yes — specialism pages rank for the exact searches clients make and help the right people feel you understand them."),
    ("Can I offer online and in-person clearly?","Yes — we make both options obvious and let clients choose, which widens your reach."),
    ("How do you handle confidentiality on the site?","We keep enquiry forms private and compliant, and never expose client information in analytics or the page.")]),
 # ───────────────────────── BEAUTY & WELLNESS ─────────────────────────
 T("Beauty & Wellness","hair-salons","Hair Salons","hair salon website",
   "Hair salon website design with online booking, stylist profiles, galleries, and local SEO that keeps every chair full.",
   "Hair Salons","A salon site that","keeps chairs full",
   "Salon clients book online, late at night, on their phones. If your site can&rsquo;t take that booking in three taps, you&rsquo;re handing the appointment to the salon down the road that can.",
   "A great hair salon website offers instant online booking, shows your stylists and their work, makes services and offers clear, and ranks locally so new clients find you and existing ones rebook without a phone call.",
   "The single biggest leak for salons is &ldquo;call to book.&rdquo; Most booking decisions happen after hours, so a phone-only salon loses exactly the clients who were ready to commit.",
   [("24/7 online booking","Direct booking or your Fresha/Booksy embed so clients book any time, by stylist and service."),
    ("Stylist profiles &amp; galleries","Show the team and their best work — clients pick a stylist as much as a salon."),
    ("Clear services","Services and what&rsquo;s included, laid out so clients book the right appointment length."),
    ("Local SEO","Structured data and reviews that win &ldquo;hair salon near me&rdquo; and &ldquo;balayage [town].&rdquo;")],
   "Clients search &ldquo;hair salon near me,&rdquo; &ldquo;balayage [town],&rdquo; and stylist styles, then book on the spot. We make your booking instant and your local presence strong so the appointment is yours.",
   [("Why is online booking essential for salons?","Because most clients book in the evening when you&rsquo;re closed. Instant online booking captures those decisions instead of losing them to voicemail."),
    ("Can clients book a specific stylist?","Yes — we set up booking by stylist and service so clients get exactly who and what they want."),
    ("Do galleries really bring in clients?","Yes — clients choose on results. Strong before-and-after galleries are one of the biggest drivers of new bookings."),
    ("Can it connect to Fresha or Booksy?","Yes — we embed your existing booking system or build a direct one, whichever you prefer.")]),
 T("Beauty & Wellness","barbershops","Barbershops","barbershop website",
   "Barbershop website design with online booking, barber profiles, galleries, and local SEO that keeps the queue moving and chairs full.",
   "Barbershops","A barber site that","keeps the queue full",
   "Barbershop clients are loyal but impatient. They want to book their barber, see the cuts you do, and know your hours — fast, on a phone, with no phone call.",
   "A good barbershop website offers quick online booking by barber, shows your best cuts, makes hours and walk-in policy clear, and ranks for &ldquo;barber near me&rdquo; so new clients find you and regulars rebook in seconds.",
   "Barbers lose new clients to two things: no online booking and no proof of the cuts they do. Both are easy fixes, and both are scoping chairs right now.",
   [("Book-your-barber","Fast online booking by barber and service, plus a clear walk-in policy."),
    ("Cuts gallery","Show the fades, beards, and styles you do best — clients book what they can see."),
    ("Barber profiles","Let clients pick their barber and rebook the same one, building loyalty."),
    ("Local SEO","Win &ldquo;barber near me&rdquo; and &ldquo;[style] barber [town]&rdquo; with structured data and reviews.")],
   "Clients search &ldquo;barber near me&rdquo; and specific styles, then want to book or walk in. We make your booking, hours, and best work unmissable on Google so the chair stays full.",
   [("Do barbershops really need a website?","Yes — even a simple site with booking, hours, and a cuts gallery captures the &ldquo;barber near me&rdquo; searches that otherwise go to a competitor."),
    ("Can clients book a specific barber?","Yes — booking by barber builds loyalty and keeps regulars coming back to the same chair."),
    ("What about walk-ins?","We make your walk-in policy and live wait info clear so walk-in clients aren&rsquo;t turned away confused."),
    ("Can I show services?","If you want — simple, clear scoping works well for barbers and reduces awkward questions at the chair.")]),
 T("Beauty & Wellness","spas","Spas &amp; Beauty","spa website",
   "Spa and beauty salon website design — treatment menus, online booking, gift vouchers, and local SEO that books treatments and sells gifts.",
   "Spas &amp; Beauty Salons","A spa site that","books treatments",
   "A spa sells calm and indulgence, and your website should feel like the first moment of it. Beautiful, fast, with treatments easy to browse, book, and gift.",
   "A strong spa or beauty website presents a clear treatment menu, offers online booking, sells gift vouchers, and ranks locally so new clients book treatments and existing ones buy gifts and rebook.",
   "Two missed revenue streams sink most spa sites: no online booking, and no online gift-voucher sales. Vouchers especially are pure margin you&rsquo;re leaving on the table every holiday season.",
   [("Treatment menu &amp; booking","A beautiful, browsable menu with instant online booking by treatment and therapist."),
    ("Gift vouchers online","Sell digital and physical vouchers around the clock — a major, often-missed revenue stream."),
    ("Atmosphere &amp; trust","Calm, fast design and real reviews that convey the experience and build confidence."),
    ("Local SEO","Win &ldquo;spa near me,&rdquo; &ldquo;facial [town],&rdquo; and &ldquo;massage near me&rdquo; with structured data and reviews.")],
   "Clients search treatments and occasions — &ldquo;spa day near me,&rdquo; &ldquo;facial [town],&rdquo; &ldquo;spa gift voucher.&rdquo; We build the booking and voucher paths so those searches convert instead of bouncing.",
   [("Can I sell gift vouchers online?","Yes — and you should. Online vouchers are one of the biggest easy wins for spas, especially around holidays, with almost no extra work for you."),
    ("Can clients book specific treatments and therapists?","Yes — we set up booking by treatment and therapist so the calendar fills correctly."),
    ("Should the site show services?","Treatment scoping usually helps here — clients want to know before booking a spa day — but we present it tastefully, never as the headline."),
    ("Can you make it feel as calm as the spa?","Yes — fast, serene design that previews the experience is exactly what lifts spa bookings.")]),
 T("Beauty & Wellness","nail-salons","Nail Salons","nail salon website",
   "Nail salon website design with online booking, design galleries, service menus, and local SEO that keeps appointments rolling in.",
   "Nail Salons","A nail site that","fills the book",
   "Nail clients choose with their eyes and book on their phones. A strong gallery and instant booking are the whole game — the salon that shows its best sets and lets clients book at midnight wins.",
   "A good nail salon website leads with a strong gallery of your designs, offers instant online booking by service, makes your menu clear, and ranks for &ldquo;nail salon near me&rdquo; so clients book the look they just saw.",
   "Nail salons live on visual proof and impulse booking, yet most have no gallery and no online booking — so the client who loved a look has nowhere to book it and moves on.",
   [("Designs gallery","Show your best sets — gel, acrylic, nail art — because clients book what they can see."),
    ("Instant booking","Online booking by service and technician, available the moment a client decides."),
    ("Clear service menu","Services and durations laid out so clients book the right slot."),
    ("Local SEO","Win &ldquo;nail salon near me&rdquo; and &ldquo;[design] nails [town]&rdquo; with structured data and reviews.")],
   "Clients search &ldquo;nail salon near me&rdquo; and specific designs, then book on impulse. We make your gallery and booking the first thing they find so the impulse becomes an appointment.",
   [("Do I need a website if I&rsquo;m on Instagram?","Yes — Instagram shows your work but can&rsquo;t take bookings cleanly or rank on Google. Your website turns that interest into booked appointments."),
    ("Can clients book by technician?","Yes — booking by technician and service keeps regulars loyal and the schedule accurate."),
    ("How important is the gallery?","It&rsquo;s the most important thing — nail clients book what they can see, so we make the gallery fast and front-and-centre."),
    ("Can it link to my existing booking app?","Yes — we embed your current system or build a direct one, whichever you prefer.")]),
 # ───────────────────────── FITNESS ─────────────────────────
 T("Fitness","gyms","Gyms &amp; Fitness Studios","gym website",
   "Gym and fitness studio website design — class schedules, online sign-up and trials, member info, and local SEO that drives memberships.",
   "Gyms &amp; Fitness Studios","A gym site that","signs up members",
   "People join a gym in a moment of motivation that fades fast. Your website has to catch that moment — clear classes, an easy trial or sign-up, and proof it&rsquo;s the right place — before the impulse cools.",
   "A strong gym website shows a live class schedule, makes joining or booking a free trial effortless, conveys the community and results, and ranks for &ldquo;gym near me&rdquo; so motivated searchers sign up before the feeling fades.",
   "Gyms lose joiners to friction. A buried schedule, a sign-up that demands a visit, or a site that doesn&rsquo;t rank locally all let that fleeting burst of motivation slip away.",
   [("Live class schedule","An always-current timetable, with class booking, so members and prospects can plan and commit."),
    ("Trials &amp; sign-up","Free-trial and join flows that capture motivated leads the instant they&rsquo;re ready."),
    ("Community &amp; results","Photos, member stories, and trainers that convey the experience and outcomes."),
    ("Local SEO","Win &ldquo;gym near me,&rdquo; &ldquo;[class] [town]&rdquo; and &ldquo;personal trainer near me&rdquo; with structured data and reviews.")],
   "People search &ldquo;gym near me,&rdquo; &ldquo;CrossFit [town],&rdquo; and class types in a burst of motivation. We make sign-up and trials instant and your local presence strong so that motivation converts.",
   [("How does a gym website increase memberships?","By catching motivated searchers at the right moment — clear classes, an easy trial or join, and strong local ranking — before the impulse to get fit fades."),
    ("Can members book classes online?","Yes — we add a live schedule with booking, or integrate your existing system like Glofox or Mindbody."),
    ("Should I offer a free trial through the site?","Almost always yes — a frictionless trial sign-up is one of the most effective ways to convert local searchers into members."),
    ("Can it handle multiple class types and trainers?","Yes — we structure classes, trainers, and timetables so everything stays clear and current.")]),
 T("Fitness","yoga-pilates","Yoga &amp; Pilates Studios","yoga studio website",
   "Yoga and Pilates studio website design — class booking, schedules, intro offers, and local SEO that fills classes and builds a community.",
   "Yoga &amp; Pilates","A studio site that","fills classes",
   "Yoga and Pilates students want calm, clarity, and an easy way to book the right class. Your website should feel like your studio — serene and welcoming — and let people reserve a mat in seconds.",
   "A good yoga or Pilates studio website shows a clear schedule, offers easy class booking and intro packages, conveys the studio&rsquo;s feel and teachers, and ranks for &ldquo;yoga near me&rdquo; so newcomers book their first class.",
   "Studios lose newcomers when the schedule is confusing, booking is clunky, or there&rsquo;s no clear intro offer. A nervous first-timer needs a gentle, obvious path in.",
   [("Schedule &amp; booking","A clear timetable with easy booking, by class type and teacher."),
    ("Intro offers","A welcoming intro package and first-class path that converts curious newcomers."),
    ("Teachers &amp; styles","Profiles and class-style explanations so students pick the right class with confidence."),
    ("Local SEO","Win &ldquo;yoga near me,&rdquo; &ldquo;Pilates [town],&rdquo; and beginner-class searches with structured data and reviews.")],
   "Newcomers search &ldquo;yoga near me,&rdquo; &ldquo;beginner Pilates [town],&rdquo; and class styles. We make your schedule, intro offer, and booking effortless so first-timers actually show up.",
   [("Can students book and pay for classes online?","Yes — we add class booking and packages, or integrate Momence, Mindbody, or your current platform."),
    ("How do I attract beginners?","With a clear intro offer, beginner-friendly class explanations, and local SEO for &ldquo;beginner yoga&rdquo; searches — all of which we build in."),
    ("Can I sell class passes and memberships?","Yes — passes, memberships, and intro packs can all be sold and managed through the site."),
    ("Will it feel calm, like the studio?","Yes — serene, fast, uncluttered design is exactly what suits a yoga or Pilates studio and what converts newcomers.")]),
 T("Fitness","personal-trainers","Personal Trainers","personal trainer website",
   "Personal trainer website design — credibility, transformations, easy enquiry and booking, and local SEO that lands new clients.",
   "Personal Trainers","A PT site that","lands new clients",
   "Personal training is sold on results and trust. Your website should prove you get people where they want to be, make booking a consult easy, and rank when someone in your area decides it&rsquo;s time.",
   "A strong personal trainer website shows real transformations and reviews, explains your approach and packages, makes booking a consultation effortless, and ranks for &ldquo;personal trainer near me&rdquo; so ready-to-start clients reach you.",
   "Most PT sites are thin — a logo and a contact form — so they don&rsquo;t prove results and don&rsquo;t rank. The trainer with real proof and a clear next step wins the client every time.",
   [("Transformations &amp; reviews","Real before-and-afters and client reviews — the proof that converts enquiries."),
    ("Approach &amp; packages","Clear explanation of how you work and what&rsquo;s on offer, without scaring people off on scope."),
    ("Easy consult booking","A simple path to book a free consult or first session the moment they decide."),
    ("Local &amp; online SEO","Win &ldquo;personal trainer near me&rdquo; and online-coaching searches with strong local signals.")],
   "Clients search &ldquo;personal trainer near me,&rdquo; &ldquo;online fitness coach,&rdquo; and specific goals. We build proof-led pages and an easy consult booking so motivated people choose and contact you.",
   [("What converts visitors into PT clients?","Proof and an easy next step — real transformations, honest reviews, and a simple way to book a consult the moment someone is ready to commit."),
    ("Should I show services?","Usually not as the headline — PT is sold on outcome and fit. We frame packages and a free consult instead, which converts better."),
    ("Can it support online coaching too?","Yes — we make in-person and online coaching both clear and bookable, widening your client base."),
    ("Do I need transformations to start?","They help most, but reviews, your approach, and credentials build trust too — we lead with whatever proof you have.")]),
 # ───────────────────────── HOME & TRADES ─────────────────────────
 T("Home & Trades","trades","Trades &amp; Contractors","tradesman website",
   "Tradesman and contractor website design — fast project requests, project galleries, trust signals, and local SEO that brings in leads.",
   "Trades &amp; Contractors","A trades site that","brings in leads",
   "Homeowners hire the trade they trust and can reach fast. Your website should prove your work, show your service area, and make requesting a enquiry a thirty-second job — because the first to reply usually wins.",
   "A great tradesman website shows real project photos, makes project requests effortless, signals trust with reviews and accreditations, and ranks for &ldquo;[trade] near me&rdquo; so local homeowners find and contact you first.",
   "Trades lose work to slow, hard-to-find websites. If a homeowner can&rsquo;t see your work, your area, and a quick way to get a enquiry, they call the next number on Google.",
   [("Fast project requests","A simple request-a-project request form with photo upload, so jobs land with enough detail to scope."),
    ("Project gallery","Real before-and-after photos that prove your standard and win trust instantly."),
    ("Trust &amp; accreditations","Reviews, guarantees, insurance, and trade memberships that reassure homeowners."),
    ("Local SEO","Win &ldquo;[trade] near me&rdquo; and &ldquo;[trade] [town]&rdquo; with structured data and service-area pages.")],
   "Homeowners search &ldquo;[trade] near me&rdquo; and specific jobs, then contact the first few that look trustworthy. We build your proof, service area, and enquiry path so you&rsquo;re the one they call.",
   [("What gets a trades website more leads?","Showing real work, clear service areas, and a fast way to request a enquiry — plus ranking locally so you appear the moment someone searches your trade."),
    ("Do I need photos of my work?","Yes — project photos are the single most persuasive thing on a trades site. We make them load fast and look great."),
    ("Can homeowners send photos with an enquiry?","Yes — photo upload on the project request form means you can scope jobs faster and with fewer site visits."),
    ("Can you cover multiple towns I serve?","Yes — we build service-area pages so you rank in each town you work in, not just where you&rsquo;re based.")]),
 T("Home & Trades","plumbers","Plumbers","plumber website",
   "Plumber website design — emergency call-outs, fast enquiries, service-area pages, and local SEO that wins &ldquo;plumber near me.&rdquo;",
   "Plumbers","A plumbing site that","rings the phone",
   "Half of plumbing searches are emergencies — a burst pipe, no hot water — and the homeowner calls the first plumber who looks reliable and local. Your website&rsquo;s job is to be that plumber.",
   "A strong plumber website makes your phone number and service area unmissable, ranks for emergency and routine searches, shows reviews and accreditations, and lets homeowners call or request a enquiry in one tap.",
   "Plumbing is won on speed and trust at the moment of panic. A slow site, a hidden phone number, or no local ranking means the emergency — and the customer — goes to a competitor.",
   [("Click-to-call &amp; emergency","A prominent click-to-call and clear emergency info for the burst-pipe moment that drives the most calls."),
    ("Service-area pages","Pages for every town you cover so you rank for &ldquo;plumber in [town]&rdquo; across your patch."),
    ("Reviews &amp; accreditations","Gas Safe, insurance, guarantees, and reviews that turn a panicked searcher into a call."),
    ("Fast enquiries","A quick project request form with photo upload for non-urgent jobs like bathrooms and boilers.")],
   "Homeowners search &ldquo;emergency plumber near me,&rdquo; &ldquo;boiler repair [town],&rdquo; and &ldquo;plumber [town]&rdquo; — usually in a hurry. We make you rank for those and make calling you instant.",
   [("How do plumbers get more calls from their website?","By ranking for local emergency and routine searches, loading fast, and making the phone number one tap away — so the panicking homeowner calls you first."),
    ("Should I have a page for each town?","Yes — service-area pages let you rank in every town you cover, not just your home base, which multiplies your leads."),
    ("Do reviews and Gas Safe matter online?","Hugely — they&rsquo;re what turn a nervous emergency searcher into a call. We surface them prominently."),
    ("Can people send an enquirys for bigger jobs?","Yes — a project request form with photo upload lets you scope bathrooms and boiler swaps without an immediate visit.")]),
 T("Home & Trades","electricians","Electricians","electrician website",
   "Electrician website design — emergency and routine call-outs, certifications, service-area pages, and local SEO that wins more jobs.",
   "Electricians","An electrician site that","wins more jobs",
   "Electrical work is hired on trust and certification. Homeowners want to know you&rsquo;re qualified, insured, local, and reachable now — and your website should answer all four before they even call.",
   "A good electrician website highlights your certifications and reviews, ranks for emergency and project searches, covers your service area, and makes calling or requesting a enquiry effortless for both urgent faults and planned work.",
   "Electrical customers are cautious — they&rsquo;re wary of cowboys. A site that doesn&rsquo;t prove your qualifications and reviews fast loses to one that does, even if you&rsquo;re the better sparky.",
   [("Certifications front and centre","NICEIC/Part P, insurance, and guarantees displayed where nervous homeowners look first."),
    ("Emergency &amp; routine","Clear paths for urgent faults and planned work like rewires, EV chargers, and fuse boards."),
    ("Service-area pages","Rank for &ldquo;electrician in [town]&rdquo; across every area you cover."),
    ("Reviews &amp; enquiries","Real reviews plus a fast project request form for larger jobs.")],
   "Homeowners search &ldquo;electrician near me,&rdquo; &ldquo;EV charger installer [town],&rdquo; and &ldquo;emergency electrician.&rdquo; We make your credentials and local presence win those searches and the call that follows.",
   [("What reassures homeowners hiring an electrician online?","Visible certifications, insurance, guarantees, and real reviews — proof you&rsquo;re qualified and safe. We put those exactly where cautious customers look."),
    ("Should I cover services like EV chargers separately?","Yes — dedicated pages for EV chargers, rewires, and fuse boards rank for those specific, growing searches."),
    ("Can I rank in several towns?","Yes — service-area pages get you found across your whole working area, not just your base."),
    ("Can people book or just call?","Both — we make urgent jobs one-tap callable and add a project request form for planned work.")]),
 T("Home & Trades","hvac","HVAC &amp; Heating","HVAC website",
   "HVAC and heating website design — emergency repairs, installs, maintenance plans, service-area pages, and local SEO that drives calls.",
   "HVAC &amp; Heating","An HVAC site that","drives service calls",
   "Heating and cooling is seasonal and urgent — when the system fails in a heatwave or cold snap, people search and call within minutes. Your website should capture both the emergency and the lucrative install and maintenance work.",
   "A strong HVAC website ranks for emergency repair and installation searches, promotes maintenance plans for recurring revenue, covers your service area, and makes calling or booking a service visit effortless year-round.",
   "HVAC firms chase emergency calls but miss the bigger prize: recurring maintenance plans and high-value installs. A site that only shouts &ldquo;repairs&rdquo; leaves that revenue on the table.",
   [("Emergency &amp; seasonal","Capture urgent no-heat / no-cool searches with click-to-call and clear availability."),
    ("Installs &amp; enquiries","Showcase install work (heat pumps, AC, boilers) with a enquiry path for high-value jobs."),
    ("Maintenance plans","Promote service plans that turn one-off jobs into recurring revenue."),
    ("Service-area &amp; SEO","Rank for &ldquo;HVAC near me&rdquo; and &ldquo;[system] repair [town]&rdquo; across your coverage.")],
   "People search &ldquo;AC repair near me,&rdquo; &ldquo;boiler installation [town],&rdquo; and &ldquo;heat pump enquiry&rdquo; depending on season and need. We build for all of it so your calendar stays full year-round.",
   [("How do I get more than just emergency calls?","By building pages and SEO for installs and maintenance plans, not only repairs. We promote the recurring and high-value work alongside the emergencies."),
    ("Are maintenance plans worth promoting online?","Very — they smooth out seasonal swings into recurring revenue. We give them a clear, sign-up-able home on your site."),
    ("Can I rank for both heating and cooling?","Yes — we structure pages around each system and season so you capture demand all year."),
    ("Can customers book a service visit online?","Yes — we add booking or fast request forms alongside one-tap calling for emergencies.")]),
 T("Home & Trades","builders","Builders &amp; Contractors","builder website",
   "Builder and construction website design — project portfolios, trust signals, enquiry forms, and local SEO that wins bigger projects.",
   "Builders &amp; Construction","A builder site that","wins bigger projects",
   "Building work is a big-ticket decision made on proof and trust. Homeowners and developers want to see projects like theirs, done well, by a firm that looks established and reachable.",
   "A great builder website showcases a strong project portfolio, signals trust with accreditations and reviews, makes detailed enquiries easy, and ranks for &ldquo;builders [town]&rdquo; and project-type searches so you win higher-value work.",
   "Builders lose premium jobs to a weak portfolio and a thin website. When someone&rsquo;s spending tens of thousands, a site that doesn&rsquo;t prove your standard makes you look like the risky choice.",
   [("Project portfolio","Rich galleries of extensions, renovations, and new-builds that prove your standard."),
    ("Trust &amp; accreditations","Memberships, insurance, guarantees, and reviews that reassure on big-scope decisions."),
    ("Detailed enquiries","An enquiry form that captures project type, scope, and timeline so you qualify leads fast."),
    ("Local &amp; project SEO","Rank for &ldquo;builders [town],&rdquo; &ldquo;house extension [town],&rdquo; and renovation searches.")],
   "Clients search &ldquo;builders near me,&rdquo; &ldquo;extension builder [town],&rdquo; and project types. We build the portfolio and project pages that prove your standard and bring serious enquiries.",
   [("What wins higher-value building work online?","A portfolio that proves your standard on projects like theirs, plus trust signals and an enquiry path that qualifies serious clients. We build both."),
    ("Should I have pages per project type?","Yes — pages for extensions, renovations, and new-builds rank for those searches and speak to different clients."),
    ("How do I look established online?","Through a strong portfolio, accreditations, reviews, and a professional, fast site — all of which we put front and centre."),
    ("Can the form qualify leads?","Yes — we capture project type, scope, and scope range so you spend time on the enquiries worth quoting.")]),
 T("Home & Trades","roofers","Roofers","roofing website",
   "Roofing website design — emergency repairs, installs, project galleries, service-area pages, and local SEO that brings in roofing leads.",
   "Roofing","A roofing site that","brings in leads",
   "Roofing splits into urgent leaks and planned replacements, and both start with a local Google search. Your website should capture the emergency and prove you&rsquo;re the trustworthy choice for the bigger job.",
   "A good roofing website ranks for emergency leak and roof-replacement searches, shows real project photos and reviews, covers your service area, and makes requesting a enquiry or call effortless.",
   "Roofers lose work when their site doesn&rsquo;t show real roofs they&rsquo;ve done or doesn&rsquo;t rank in nearby towns. Homeowners need proof and a fast way to reach you, especially with water coming in.",
   [("Emergency &amp; repairs","Capture urgent leak searches with click-to-call and clear, reassuring availability."),
    ("Project gallery","Real roofs — repairs, re-roofs, flat and pitched — that prove your work."),
    ("Service-area pages","Rank for &ldquo;roofer in [town]&rdquo; across every area you cover."),
    ("Reviews &amp; enquiries","Reviews, guarantees, and a fast project request form with photo upload.")],
   "Homeowners search &ldquo;roof repair near me,&rdquo; &ldquo;roofer [town],&rdquo; and &ldquo;flat roof replacement&rdquo; — often urgently. We make you rank and make getting a enquiry or call effortless.",
   [("How do roofers get more enquiries?","By ranking for local emergency and replacement searches and proving quality with real project photos and reviews — then making contact one tap away."),
    ("Should I show photos of past roofs?","Yes — proof of real, completed roofs is the most persuasive thing on a roofing site."),
    ("Can I cover several towns?","Yes — service-area pages get you found across your whole patch, not just your base."),
    ("Can customers send photos of the damage?","Yes — photo upload on the project request form helps you assess and scope without an immediate visit.")]),
 T("Home & Trades","landscaping","Landscaping &amp; Lawn Care","landscaping website",
   "Landscaping and lawn-care website design — project galleries, seasonal services, project requests, and local SEO that fills your schedule.",
   "Landscaping &amp; Lawn Care","A landscaping site that","fills the schedule",
   "Landscaping sells transformation, and nothing proves it like before-and-after photos. Your website should make people picture their own garden transformed, then make booking a enquiry effortless.",
   "A strong landscaping website leads with before-and-after galleries, lays out seasonal and one-off services, makes project requests easy, and ranks for &ldquo;landscaper near me&rdquo; and &ldquo;garden design [town].&rdquo;",
   "Landscapers with no gallery and no local ranking blend into every other &ldquo;contact us&rdquo; site. The visual nature of the work is your biggest advantage — most sites waste it.",
   [("Before-and-after galleries","Transformation photos that sell the outcome better than any words."),
    ("Seasonal &amp; one-off services","Clear pages for design, maintenance, paving, and seasonal work."),
    ("Easy project requests","A quick form with photo upload so you can scope and scope jobs fast."),
    ("Local SEO","Win &ldquo;landscaper near me,&rdquo; &ldquo;garden design [town],&rdquo; and &ldquo;lawn care [town].&rdquo;")],
   "People search &ldquo;landscaper near me,&rdquo; &ldquo;garden design [town],&rdquo; and specific jobs like paving or turfing. We build galleries and service pages that turn those searches into booked enquiries.",
   [("What sells landscaping work online?","Before-and-after photos — they let people picture their own garden transformed, which is what drives the enquiry. We make them the centrepiece."),
    ("Should I separate maintenance from design?","Yes — they&rsquo;re different buyers. Separate pages rank better and convert each more clearly."),
    ("Can people get a enquiry without a visit?","Often yes — a photo-upload project request form lets you scope many jobs remotely first."),
    ("Will it help with seasonal work?","Yes — we build seasonal service pages and SEO so you capture demand as it shifts through the year.")]),
 T("Home & Trades","painters","Painters &amp; Decorators","painter decorator website",
   "Painter and decorator website design — portfolios, clear services, easy enquiries, and local SEO that keeps the diary booked.",
   "Painters &amp; Decorators","A decorating site that","keeps you booked",
   "Decorating is judged on finish and reliability. Your website should show clean, crisp work, make requesting a enquiry simple, and prove you turn up and do it properly — the two things customers actually worry about.",
   "A good painter and decorator website shows a portfolio of clean finishes, lists interior and exterior services clearly, makes enquiries easy, and ranks for &ldquo;painter and decorator near me.&rdquo;",
   "Decorators lose jobs when their site shows no real work and makes getting a enquiry a hassle. Customers want to see the finish and reach you fast — most sites deliver neither.",
   [("Finish portfolio","Photos of crisp interior and exterior work that prove your standard."),
    ("Clear services","Interior, exterior, commercial — laid out so customers know you do their job."),
    ("Easy enquiries","A simple project request form with photo upload for fast, accurate scoping."),
    ("Local SEO","Win &ldquo;painter and decorator near me&rdquo; and &ldquo;[town] decorator.&rdquo;")],
   "Customers search &ldquo;painter and decorator near me&rdquo; and specific jobs. We prove your finish and make getting a enquiry effortless so the booking is yours.",
   [("What gets decorators more work online?","Proof of clean finishes and an easy enquiry path, plus ranking locally so customers find you first. We build all three."),
    ("Do I need photos of my work?","Yes — decorating is visual, and a portfolio of crisp finishes is the most persuasive thing on the site."),
    ("Can I show interior and exterior separately?","Yes — separate, clear services help customers self-select and improve ranking."),
    ("Can customers send photos for a enquiry?","Yes — photo upload lets you scope many jobs before visiting.")]),
 T("Home & Trades","cleaning","Cleaning Services","cleaning company website",
   "Cleaning company website design — instant enquiries and booking, service types, trust signals, and local SEO that books recurring clients.",
   "Cleaning Services","A cleaning site that","books recurring clients",
   "Cleaning is recurring revenue, and the easier you make booking, the faster that revenue compounds. Your website should let people get a scope and book a regular clean in minutes, not wait for a callback.",
   "A strong cleaning website offers instant enquiries and online booking, clearly separates domestic, commercial, and specialist services, builds trust with reviews and insurance, and ranks for &ldquo;cleaners near me.&rdquo;",
   "Cleaning companies lose easy, recurring bookings to slow &ldquo;request a callback&rdquo; forms. When someone wants a cleaner, the company that lets them book now wins the contract.",
   [("Instant enquiry &amp; booking","Let customers get a scope and book a one-off or recurring clean online, right away."),
    ("Service types","Domestic, commercial, end-of-tenancy, and deep cleans — each clear and bookable."),
    ("Trust &amp; insurance","Reviews, vetted-staff and insurance messaging that reassure people letting you into their home."),
    ("Local SEO","Win &ldquo;cleaners near me,&rdquo; &ldquo;office cleaning [town],&rdquo; and &ldquo;end of tenancy clean [town].&rdquo;")],
   "People search &ldquo;cleaners near me,&rdquo; &ldquo;end of tenancy cleaning [town],&rdquo; and &ldquo;office cleaning&rdquo; and want a fast scope. We make quoting and booking instant so they book you, not the slower competitor.",
   [("Can customers get a scope and book online?","Yes — instant online enquiries and booking are the biggest win for cleaning companies, turning interest into recurring contracts immediately."),
    ("Should domestic and commercial be separate?","Yes — they&rsquo;re different buyers with different searches, so separate pages rank and convert better."),
    ("How do I reassure people letting cleaners into their home?","With visible vetting, insurance, and reviews — we put that trust messaging where it matters."),
    ("Can it handle recurring bookings?","Yes — we set up one-off and recurring booking so regular clients are easy to win and keep.")]),
 T("Home & Trades","pest-control","Pest Control","pest control website",
   "Pest control website design — urgent call-outs, treatment pages, trust signals, and local SEO that wins &ldquo;pest control near me.&rdquo;",
   "Pest Control","A pest control site that","wins urgent jobs",
   "Pest problems are urgent and a bit embarrassing — people search privately on their phone and call the first discreet, professional, local option. Your website should be exactly that.",
   "A good pest control website ranks for urgent pest searches, makes calling fast and discreet, covers your service area and pest types, and builds trust with reviews and accreditations.",
   "Pest control is won in minutes. A homeowner with mice or wasps wants it gone today — a slow site or hidden number sends that ready-to-pay customer to a competitor.",
   [("Urgent click-to-call","One-tap calling for the &ldquo;deal with it today&rdquo; searches that drive most jobs."),
    ("Pest &amp; treatment pages","Pages per pest — rodents, wasps, bedbugs — that rank for exactly what people search."),
    ("Trust &amp; discretion","Accreditations, reviews, and a professional, discreet tone that reassures."),
    ("Service-area SEO","Win &ldquo;pest control near me&rdquo; and &ldquo;[pest] removal [town]&rdquo; across your patch.")],
   "People search &ldquo;[pest] control near me&rdquo; and &ldquo;[pest] removal [town]&rdquo; urgently. We build pest-specific pages and local signals so you&rsquo;re the first discreet, trustworthy call.",
   [("How does pest control get more calls online?","By ranking for urgent, pest-specific local searches and making the call one discreet tap away — so the ready-to-act homeowner calls you first."),
    ("Should each pest have its own page?","Yes — pages for rodents, wasps, bedbugs and so on rank for those exact searches and bring in ready customers."),
    ("Do accreditations matter online?","Yes — they reassure people they&rsquo;re hiring a professional, not a chancer. We display them prominently."),
    ("Can I cover commercial contracts too?","Yes — we add a clear commercial path for ongoing business contracts alongside domestic call-outs.")]),
 # ───────────────────────── PROFESSIONAL SERVICES ─────────────────────────
 T("Professional Services","law-firms","Law Firms &amp; Solicitors","law firm website",
   "Law firm and solicitor website design — practice-area pages, easy consultations, authority and trust, and local SEO that wins clients.",
   "Law Firms &amp; Solicitors","A law firm site that","wins better clients",
   "People choose a solicitor on trust and expertise, and they research on their phone first. Your website should project authority, explain your practice areas clearly, and make booking a consultation simple.",
   "A strong law firm website ranks for practice-area and local searches, projects authority and trust, makes booking a consultation effortless, and turns anxious searchers into qualified enquiries.",
   "Many law firm sites are dense, dated, and impersonal — the opposite of reassuring. Clients with a legal worry want clarity and a confident, easy next step, not legalese and a single phone number.",
   [("Practice-area pages","Clear pages for each area — family, conveyancing, employment — that rank and reassure."),
    ("Authority &amp; trust","Solicitor profiles, credentials, and reviews that establish expertise."),
    ("Easy consultations","Simple consultation booking or enquiry so worried clients take the next step."),
    ("Local &amp; practice SEO","Win &ldquo;[practice area] solicitor [town]&rdquo; and &ldquo;solicitor near me.&rdquo;")],
   "Clients search &ldquo;divorce solicitor [town],&rdquo; &ldquo;conveyancing enquiry,&rdquo; and &ldquo;employment lawyer near me.&rdquo; We build authoritative practice-area pages that rank and convert those anxious searches into enquiries.",
   [("What makes a law firm website win clients?","Authority, clarity, and an easy next step — practice-area pages that rank, solicitor profiles that build trust, and simple consultation booking for anxious clients."),
    ("Should each practice area have its own page?","Yes — dedicated practice-area pages rank for specific searches and speak directly to each client&rsquo;s worry, which a single &ldquo;services&rdquo; page can&rsquo;t."),
    ("Can clients book consultations online?","Yes — we add compliant consultation booking or enquiry forms so people act the moment they decide."),
    ("Can you handle compliance and confidentiality?","Yes — we build to your regulatory requirements and keep all enquiry data handled correctly.")]),
 T("Professional Services","accountants","Accountants &amp; Bookkeepers","accountant website",
   "Accountant and bookkeeper website design — clear services, trust, easy enquiries, and local SEO that brings in better clients.",
   "Accountants &amp; Bookkeepers","An accountancy site that","brings in better clients",
   "Businesses pick an accountant on trust and fit. Your website should make it obvious who you help, what you handle, and how to start — so the right clients reach out and the wrong-fit ones self-select away.",
   "A strong accountancy website clearly states who you serve and what you do, signals trust and qualifications, makes enquiries easy, and ranks for &ldquo;accountant for [niche]&rdquo; and &ldquo;accountant near me.&rdquo;",
   "Accountancy sites often read as generic and interchangeable. The firm that clearly states its niche and makes getting started easy wins better-fit, higher-value clients than the one that tries to be everything.",
   [("Clear services &amp; niches","Spell out who you help — contractors, ecommerce, startups — and what you handle."),
    ("Trust &amp; qualifications","Accreditations, reviews, and a professional tone that build confidence with money on the line."),
    ("Easy onboarding","A simple enquiry-to-call path so prospects start without friction."),
    ("Local &amp; niche SEO","Win &ldquo;accountant for [niche]&rdquo; and &ldquo;accountant near me&rdquo; with focused pages.")],
   "Businesses search &ldquo;accountant near me,&rdquo; &ldquo;accountant for limited company,&rdquo; and niche terms. We build focused, trustworthy pages that attract the clients you actually want.",
   [("How do accountants attract better clients online?","By being specific — clear niches, who you help, and proof of expertise — rather than generic. Specificity attracts higher-value, better-fit clients. We build for that."),
    ("Should I show a niche or stay general?","A clear niche almost always wins better clients and ranks more easily. We can present a primary niche while still serving general work."),
    ("Can prospects book a call online?","Yes — a simple enquiry-to-call path removes friction and gets the right prospects talking to you sooner."),
    ("Will it look trustworthy enough for finance?","Yes — clean, professional, fast design plus visible qualifications and reviews is exactly what reassures clients trusting you with their money.")]),
 T("Professional Services","real-estate","Real Estate Agents","real estate agent website",
   "Real estate and estate agent website design — fast listings, valuations, lead capture, and local SEO that wins instructions and buyers.",
   "Real Estate &amp; Estate Agents","An agent site that","wins instructions",
   "Estate agency is a two-sided game: attract sellers wanting a valuation and buyers wanting listings. Your website should do both — fast, beautiful listings and an irresistible, easy valuation request.",
   "A strong estate agent website shows fast, attractive property listings, captures seller valuations with an easy request, builds local authority, and ranks for &ldquo;estate agents [town]&rdquo; and &ldquo;home valuation [town].&rdquo;",
   "Agent sites often have slow, clunky listings and bury the valuation request — the single most valuable action a seller can take. That friction hands instructions to the competitor down the high street.",
   [("Fast property listings","Quick, beautiful listings with great photos that keep buyers browsing."),
    ("Valuation capture","A prominent, easy &ldquo;book a valuation&rdquo; path — the highest-value lead an agent can get."),
    ("Local authority","Area guides and market insight that establish you as the local expert."),
    ("Local SEO","Win &ldquo;estate agents [town],&rdquo; &ldquo;houses for sale [town],&rdquo; and &ldquo;home valuation near me.&rdquo;")],
   "Sellers search &ldquo;estate agents [town]&rdquo; and &ldquo;how much is my house worth,&rdquo; while buyers search listings. We build for both, making the valuation request impossible to miss.",
   [("What&rsquo;s the most valuable thing on an agent&rsquo;s website?","The valuation request — it&rsquo;s how you win instructions. We make it prominent and effortless so more sellers take that step with you."),
    ("Can it pull in my listings automatically?","Yes — we integrate your CRM or portal feed so listings stay current without manual work."),
    ("How do I become the local expert online?","Through area guides, market insight, and local SEO — content that ranks and positions you as the area authority. We build that out."),
    ("Does it work for lettings too?","Yes — we structure sales and lettings clearly so both landlords and tenants find what they need.")]),
 T("Professional Services","financial-advisors","Financial Advisors","financial advisor website",
   "Financial advisor and IFA website design — trust-led, compliant, with clear services, easy enquiries, and local SEO for better clients.",
   "Financial Advisors &amp; IFAs","An advisor site that","earns trust first",
   "Financial advice is sold entirely on trust. Your website should feel credible and calm, explain who you help and how, meet compliance, and make that first cautious enquiry easy.",
   "A strong financial advisor website builds trust through credentials, clarity, and a professional feel, explains your services and who you serve, stays compliant, and makes enquiring straightforward.",
   "Advisor sites often feel either cold and corporate or thin and untrustworthy. Clients handing over their financial future need to feel safe and clear before they&rsquo;ll pick up the phone.",
   [("Trust &amp; credentials","Qualifications, regulation, and reviews that reassure clients about their money."),
    ("Clear services &amp; clients","Who you help — retirement, pensions, protection — and how, in plain English."),
    ("Compliant enquiries","A straightforward, compliant enquiry path that respects financial-promotion rules."),
    ("Local &amp; niche SEO","Win &ldquo;financial advisor near me&rdquo; and &ldquo;[service] advice [town].&rdquo;")],
   "Clients search &ldquo;financial advisor near me,&rdquo; &ldquo;pension advice [town],&rdquo; and specific needs. We build trustworthy, compliant pages that attract the right clients and make getting in touch feel safe.",
   [("What matters most on a financial advisor&rsquo;s website?","Trust — credibility, clarity, and compliance. Clients need to feel safe before they enquire, so we lead with credentials, plain explanations, and a calm, professional feel."),
    ("Can you keep it compliant?","Yes — we build with financial-promotion and regulatory requirements in mind and keep enquiry data handled correctly."),
    ("Should I focus on a niche?","A clear focus — retirement, business owners, expats — attracts better-fit clients and ranks more easily. We can lead with a primary niche."),
    ("Will it generate quality enquiries?","Yes — trust-led pages plus local and niche SEO attract clients who are ready and a good fit, not tyre-kickers.")]),
 T("Professional Services","consultants","Consultants &amp; Coaches","consultant website",
   "Consultant and coach website design — authority positioning, clear offers, easy booking, and SEO that attracts high-value clients.",
   "Consultants &amp; Coaches","A consulting site that","attracts the right clients",
   "Consulting and coaching are sold on authority and clarity. Your website should make it instantly obvious who you help, the result you deliver, and how to start — so premium clients self-select in.",
   "A strong consultant or coach website positions your authority, states your offer and outcome clearly, makes booking a call easy, and ranks for your niche so the right high-value clients find and choose you.",
   "Most consultant sites are vague — full of buzzwords, light on who they help and what changes. Clarity and proof are what convert high-value clients; vagueness just attracts scope-shoppers.",
   [("Authority positioning","Clear positioning, results, and proof that establish you as the expert worth paying for."),
    ("Sharp offer &amp; outcome","Exactly who you help and the result you deliver — no jargon, no guessing."),
    ("Easy call booking","A frictionless path to book a discovery call the moment they&rsquo;re convinced."),
    ("Niche &amp; content SEO","Rank for your specific niche and the problems your ideal clients search.")],
   "Clients search for your specific problem and niche — not &ldquo;consultant.&rdquo; We build sharp, authority-led pages and content around those searches so the right clients find and trust you.",
   [("What converts visitors into consulting clients?","Clarity and authority — being unmistakably clear about who you help and the outcome you deliver, backed by proof, with an easy way to book a call."),
    ("Should I show services?","Usually not — high-value consulting is sold on outcome and fit via a call. We frame the offer and a discovery call instead, which converts far better."),
    ("How do I stand out from other consultants?","By being specific and proving results where others are vague. Specificity plus proof is what wins premium clients, and it&rsquo;s what we build around."),
    ("Can it support content and lead magnets?","Yes — we build in a blog and lead capture so your authority content compounds into a steady client pipeline.")]),
 T("Professional Services","recruitment","Recruitment Agencies","recruitment agency website",
   "Recruitment agency website design — job listings, two-sided lead capture, employer trust, and SEO that wins clients and candidates.",
   "Recruitment Agencies","A recruitment site that","wins both sides",
   "Recruitment is two markets at once — employers who need talent and candidates who need roles. Your website should serve both cleanly: fast job listings for candidates, and a confident pitch for employers.",
   "A strong recruitment website shows fast, searchable job listings for candidates, makes a clear case to employers, captures both sides as leads, and ranks for &ldquo;[sector] recruitment [town]&rdquo; and role searches.",
   "Recruitment sites often serve candidates and ignore employers — or vice versa. Winning agencies make both audiences feel the site is built for them, with a clear path to act.",
   [("Fast job listings","Searchable, current vacancies that keep candidates coming back and applying."),
    ("Employer pitch","A confident client-side section that wins the instructions that actually pay."),
    ("Two-sided capture","Clear paths for candidates to apply and employers to brief a role."),
    ("Sector &amp; local SEO","Rank for &ldquo;[sector] recruitment agency [town]&rdquo; and specific role searches.")],
   "Candidates search roles and &ldquo;[sector] jobs [town];&rdquo; employers search &ldquo;[sector] recruitment agency.&rdquo; We build for both so you grow candidate flow and client instructions at once.",
   [("Can it pull jobs from my CRM or ATS?","Yes — we integrate your applicant-tracking system so vacancies stay current automatically."),
    ("How do I win more employer clients?","With a confident, separate employer section that makes your case and an easy way to brief a role — not just a candidate-facing job board. We build both sides."),
    ("Should candidates and employers have separate journeys?","Yes — they want different things. Clear, separate paths convert each far better."),
    ("Can it rank for specific sectors?","Yes — sector and role-specific pages rank for the searches your candidates and clients actually make.")]),
 # ───────────────────────── AUTO ─────────────────────────
 T("Auto","auto-repair","Auto Repair &amp; Mechanics","mechanic website",
   "Auto repair and mechanic website design — booking, services, MOT reminders, trust, and local SEO that fills the workshop.",
   "Auto Repair &amp; Mechanics","A garage site that","fills the workshop",
   "Drivers pick a garage on trust and convenience, and they search when something&rsquo;s wrong or an MOT is due. Your website should make booking easy, prove you&rsquo;re honest and skilled, and rank when they search.",
   "A good mechanic website lets drivers book a service or MOT online, lists services clearly, builds trust with reviews and transparency, and ranks for &ldquo;garage near me&rdquo; and &ldquo;MOT [town].&rdquo;",
   "Garages lose bookings to phone-only sites and a reputation problem the web can fix. Drivers fear being ripped off — a transparent, well-reviewed, easy-to-book site wins their trust and their car.",
   [("Online booking","Let drivers book services, MOTs, and repairs online — fewer phone calls, fuller bays."),
    ("Clear services &amp; honesty","Services and a transparent, no-surprises tone that counters the &ldquo;dodgy garage&rdquo; fear."),
    ("Reviews &amp; trust","Real reviews and accreditations that turn a cautious driver into a booking."),
    ("Local SEO","Win &ldquo;garage near me,&rdquo; &ldquo;MOT [town],&rdquo; and &ldquo;[repair] near me.&rdquo;")],
   "Drivers search &ldquo;garage near me,&rdquo; &ldquo;MOT near me,&rdquo; and specific repairs. We make booking easy and your trust signals strong so they choose your workshop.",
   [("Can drivers book MOTs and services online?","Yes — online booking is a big win for garages, capturing bookings around the clock and cutting phone time."),
    ("How do I overcome the &lsquo;dodgy garage&rsquo; fear?","With transparency, real reviews, and accreditations front and centre — exactly the trust signals we build in to win cautious drivers."),
    ("Can I send MOT reminders?","Yes — we can set up reminder capture so you bring drivers back automatically each year."),
    ("Will it rank for my town?","Yes — local SEO and a tuned Google Business Profile get you found for &ldquo;garage near me&rdquo; and &ldquo;MOT [town].&rdquo;")]),
 T("Auto","car-dealers","Car Dealerships","car dealership website",
   "Car dealership website design — fast stock listings, finance enquiries, trust, and local SEO that drives forecourt and online leads.",
   "Car Dealerships","A dealership site that","drives forecourt leads",
   "Car buyers research online for weeks before they visit. Your website is the forecourt now — fast stock listings, clear finance, and easy enquiries decide whether they come to you or the dealer down the road.",
   "A strong dealership website shows fast, searchable stock with great photos, makes finance and part-exchange enquiries easy, builds trust, and ranks for &ldquo;used cars [town]&rdquo; and model searches.",
   "Dealership sites with slow, ugly stock pages lose buyers before they ever visit. The forecourt experience now starts online, and a poor one sends ready buyers elsewhere.",
   [("Fast stock listings","Quick, searchable inventory with strong photos and clear details that keep buyers browsing."),
    ("Finance &amp; part-ex","Easy finance and part-exchange enquiries that capture serious buyers."),
    ("Trust &amp; reviews","Reviews, warranties, and transparency that reassure on a big purchase."),
    ("Local &amp; model SEO","Win &ldquo;used cars [town]&rdquo; and specific make/model searches.")],
   "Buyers search &ldquo;used cars [town],&rdquo; specific models, and &ldquo;car finance.&rdquo; We make your stock fast and your enquiry paths easy so online research turns into forecourt visits.",
   [("Can it sync with my stock feed?","Yes — we integrate your inventory feed so listings stay current automatically as stock moves."),
    ("How do I capture finance leads?","With clear, easy finance and part-exchange enquiry paths on every vehicle — we build those in to capture serious buyers."),
    ("Do photos really matter that much?","Yes — strong vehicle photography is the biggest driver of enquiries. We make galleries fast and high-impact."),
    ("Will it bring people to the forecourt?","That&rsquo;s the goal — turning weeks of online research into a visit, with fast stock, trust signals, and easy enquiries.")]),
 # ───────────────────────── EVENTS & CREATIVE ─────────────────────────
 T("Events & Creative","photographers","Photographers","photographer website",
   "Photographer website design — fast portfolios, clear packages, easy enquiry, and SEO that books weddings, portraits, and commercial work.",
   "Photographers","A photography site that","books the work",
   "A photographer&rsquo;s website is the portfolio, and it has to load fast and look stunning. Show your best work, make packages and enquiry clear, and the right clients book themselves.",
   "A great photographer website shows a fast, beautiful portfolio, presents packages and process clearly, makes enquiry effortless, and ranks for &ldquo;[type] photographer [town]&rdquo; so ideal clients find and book you.",
   "Photographers often have gorgeous photos trapped in a slow, clunky site that buries the work and the enquiry. Speed and clarity matter as much as the images themselves.",
   [("Fast, stunning portfolio","Galleries that load fast and show your best work at its best — the whole pitch."),
    ("Clear packages &amp; process","What you offer and how it works, so clients arrive ready to book."),
    ("Easy enquiry","A simple enquiry form that captures date, type, and details up front."),
    ("Niche &amp; local SEO","Win &ldquo;wedding photographer [town],&rdquo; &ldquo;newborn photographer near me,&rdquo; and commercial searches.")],
   "Clients search &ldquo;[type] photographer [town]&rdquo; and judge instantly on the work. We make your portfolio fast and your enquiry easy so ideal clients book without hesitation.",
   [("How fast does my photography site need to be?","Very — heavy galleries that load slowly lose clients before the images even appear. We optimise so your work loads fast and looks flawless."),
    ("Should I niche my photography pages?","Yes — separate pages for weddings, newborns, or commercial rank better and speak to each client clearly."),
    ("Should I show services?","A starting point or packages usually helps filter enquiries — we present it tastefully so it qualifies without scaring people off."),
    ("Can clients view and pick galleries?","Yes — we can add client galleries and proofing so delivery is as polished as the booking.")]),
 T("Events & Creative","wedding-planners","Wedding &amp; Event Planners","wedding planner website",
   "Wedding and event planner website design — beautiful portfolios, clear services, easy enquiry, and SEO that books couples and events.",
   "Wedding &amp; Event Planners","A planner site that","books dream events",
   "Couples and clients hire a planner on style and trust. Your website should feel like your taste, prove you deliver beautiful events flawlessly, and make that first enquiry feel exciting and easy.",
   "A strong wedding or event planner website showcases a beautiful portfolio, explains your services and process, makes enquiry effortless, and ranks for &ldquo;wedding planner [town]&rdquo; so the right couples reach you.",
   "Planner sites that show too little or feel off-brand lose couples instantly — this is an emotional, taste-led decision. Your site has to feel like the events you create.",
   [("Beautiful portfolio","A stunning, fast gallery of past events that proves your style and standard."),
    ("Services &amp; process","Full-planning, partial, on-the-day — clear, so clients pick the right fit."),
    ("Easy, warm enquiry","An inviting enquiry form capturing date, type, and vision."),
    ("Local &amp; occasion SEO","Win &ldquo;wedding planner [town]&rdquo; and event-type searches.")],
   "Clients search &ldquo;wedding planner [town]&rdquo; and event types, judging on taste. We make your portfolio and brand shine and your enquiry effortless so the right clients book.",
   [("What matters most on a planner&rsquo;s website?","Taste and trust — a beautiful, on-brand portfolio that proves your style, with an easy, warm enquiry path. It&rsquo;s an emotional decision, and the site has to feel right."),
    ("Should I separate service levels?","Yes — full, partial, and on-the-day planning are different buyers, and clear pages help each choose and convert."),
    ("Do I need to show services?","Usually a starting point helps qualify enquiries; full scoping is bespoke. We frame it so the right couples feel comfortable reaching out."),
    ("Can it feel as unique as my brand?","Yes — we design to your taste so the site feels like the events you create, which is exactly what books clients.")]),
 T("Events & Creative","florists","Florists","florist website",
   "Florist website design — online ordering, occasion ranges, local delivery, and SEO that wins same-day and event flower orders.",
   "Florists","A florist site that","takes flower orders",
   "Flowers are bought on emotion and deadline — a birthday tomorrow, an apology today. Your website should let people order beautiful arrangements fast, choose delivery, and find you for every occasion.",
   "A good florist website offers easy online ordering with occasion ranges, clear local delivery and same-day cut-offs, and ranks for &ldquo;florist near me&rdquo; and &ldquo;flower delivery [town]&rdquo; so orders come in around the clock.",
   "Florists without online ordering lose impulse and last-minute orders to the chains and apps. Local florists win on quality and speed — but only if customers can order online.",
   [("Online ordering","Let customers order arrangements online, by occasion, with clear delivery options."),
    ("Occasion ranges","Birthdays, sympathy, weddings, anniversaries — ranges that match how people search and buy."),
    ("Local delivery &amp; cut-offs","Clear delivery areas and same-day cut-off times that capture urgent orders."),
    ("Local SEO","Win &ldquo;florist near me,&rdquo; &ldquo;flower delivery [town],&rdquo; and occasion searches.")],
   "People search &ldquo;florist near me,&rdquo; &ldquo;flower delivery [town],&rdquo; and occasions, often urgently. We make ordering and delivery effortless so the local florist beats the app.",
   [("Can customers order and pay online?","Yes — online ordering is essential for florists, capturing impulse and last-minute orders that phone-only shops miss."),
    ("How do I compete with the big flower apps?","On quality, locality, and same-day delivery — advantages we surface clearly, with ordering as easy as theirs."),
    ("Can I show same-day cut-off times?","Yes — clear delivery areas and cut-offs capture urgent orders and set the right expectations."),
    ("Can it handle weddings and events too?","Yes — we add an enquiry path for bespoke wedding and event work alongside everyday ordering.")]),
 # ───────────────────────── EDUCATION & CARE ─────────────────────────
 T("Education & Care","childcare","Childcare &amp; Nurseries","nursery website",
   "Nursery and childcare website design — warm trust-building, enquiries and waitlists, clear info, and local SEO that fills places.",
   "Nurseries &amp; Childcare","A nursery site that","fills places",
   "Parents choosing childcare are trusting you with what matters most. Your website should feel warm and safe, answer their questions plainly, and make booking a visit or joining the waitlist easy.",
   "A strong nursery website builds trust with warmth and transparency, shows your setting and team, makes booking a visit or joining the waitlist easy, and ranks for &ldquo;nursery near me&rdquo; and &ldquo;childcare [town].&rdquo;",
   "Nursery sites that feel cold or hide the basics — terms-free key info, ratios, the setting, how to visit — lose anxious parents to settings that feel open and reassuring.",
   [("Warm, reassuring feel","Photos of the setting and team, and a tone that reassures protective parents."),
    ("Visit booking &amp; waitlist","Easy paths to book a show-around or join the waitlist — the key conversion."),
    ("Clear key info","Hours, approach, ratios, and Ofsted/inspection info, plainly laid out."),
    ("Local SEO","Win &ldquo;nursery near me&rdquo; and &ldquo;childcare [town]&rdquo; for searching parents.")],
   "Parents search &ldquo;nursery near me&rdquo; and &ldquo;childcare [town],&rdquo; then judge on trust. We make your setting warm and your visit-booking easy so parents reach out and visit.",
   [("What do parents look for on a nursery website?","Reassurance — a warm feel, photos of the real setting and team, clear key info, and an easy way to book a visit. We build all of it to win trust."),
    ("Can parents book a visit or join a waitlist online?","Yes — these are the key actions, so we make both effortless to capture interested families."),
    ("Should I show inspection ratings?","Yes — Ofsted or equivalent ratings are powerful trust signals, and we surface them clearly."),
    ("How do I look established and safe?","Through warm, professional design, real photos, transparent info, and reviews from parents — exactly what we lead with.")]),
 T("Education & Care","tutoring","Tutors &amp; Education","tutoring website",
   "Tutor and tuition website design — clear subjects and levels, easy booking, trust and results, and SEO that fills your timetable.",
   "Tutors &amp; Tuition","A tutoring site that","fills your timetable",
   "Parents and students choose a tutor on results and trust. Your website should make your subjects, levels, and approach clear, prove you get results, and make booking a first session easy.",
   "A good tutoring website clearly lists subjects, levels, and approach, proves results with reviews, makes booking a session easy, and ranks for &ldquo;[subject] tutor [town]&rdquo; and online-tuition searches.",
   "Tutoring sites are often vague about exactly what&rsquo;s offered and to whom. Parents want specifics — subject, level, format, results — and an easy way to start.",
   [("Subjects &amp; levels","Clear pages for each subject and level — GCSE maths, 11+, A-level — that rank and resonate."),
    ("Results &amp; reviews","Grades improved and parent reviews that prove you deliver."),
    ("Easy booking","A simple path to book an assessment or first session."),
    ("Local &amp; online SEO","Win &ldquo;[subject] tutor [town],&rdquo; &ldquo;11+ tutor near me,&rdquo; and online-tuition searches.")],
   "Parents search &ldquo;[subject] tutor near me,&rdquo; &ldquo;GCSE maths tutor [town],&rdquo; and online tuition. We build subject- and level-specific pages that rank and convert into bookings.",
   [("Should I have a page per subject?","Yes — subject and level pages rank for the exact searches parents make and let the right families find you fast."),
    ("How do I prove results online?","With grade improvements, success stories, and parent reviews — the proof that converts. We make it prominent."),
    ("Can students book online?","Yes — easy assessment and session booking turns interested parents into committed clients."),
    ("Does it work for online tutoring?","Yes — we make in-person and online tuition both clear and bookable, widening your reach beyond your town.")]),
 T("Education & Care","driving-schools","Driving Schools &amp; Instructors","driving instructor website",
   "Driving school and instructor website design — easy booking, pass rates, packages, and local SEO that keeps your diary full.",
   "Driving Schools &amp; Instructors","A driving site that","keeps the diary full",
   "Learners pick an instructor on pass rates, availability, and ease of booking. Your website should prove you get people through their test and let them book lessons without a phone call.",
   "A strong driving instructor website shows pass rates and reviews, makes booking lessons or block deals easy, covers your area, and ranks for &ldquo;driving instructor near me&rdquo; and &ldquo;driving lessons [town].&rdquo;",
   "Most instructors rely on word of mouth and a phone number. The one with an easy-to-book, well-reviewed website captures the steady stream of learners searching online every week.",
   [("Easy lesson booking","Let learners book lessons or block packages online, with your availability clear."),
    ("Pass rates &amp; reviews","Proof you get learners through — the number one thing they care about."),
    ("Packages &amp; intensive","Clear options from single lessons to intensive courses."),
    ("Local SEO","Win &ldquo;driving instructor near me&rdquo; and &ldquo;driving lessons [town].&rdquo;")],
   "Learners search &ldquo;driving instructor near me&rdquo; and &ldquo;driving lessons [town].&rdquo; We make your pass rates and booking shine so learners choose and book you over the phone-only competition.",
   [("Can learners book lessons online?","Yes — easy online booking captures learners the moment they decide, instead of losing them to voicemail."),
    ("Do pass rates help?","Strongly — they&rsquo;re the main thing learners and parents care about, so we put them front and centre with reviews."),
    ("Can I offer intensive courses?","Yes — we lay out single lessons, block deals, and intensive courses clearly so learners pick what suits them."),
    ("Will it help me get found locally?","Yes — local SEO and a tuned Google profile get you found for &ldquo;driving instructor near me&rdquo; across your area.")]),
 T("Education & Care","funeral-homes","Funeral Homes &amp; Directors","funeral home website",
   "Funeral home and director website design — compassionate, clear, with easy contact, service info, and local SEO families can rely on.",
   "Funeral Homes &amp; Directors","A funeral site that","families can rely on",
   "Families finding a funeral director are in their hardest moment. Your website should be calm, clear, and compassionate — answering their immediate questions and making it effortless to reach you, day or night.",
   "A compassionate funeral home website provides clear, gentle information on services, makes 24-hour contact effortless, builds trust quietly, and ranks for &ldquo;funeral directors [town]&rdquo; so grieving families find you fast.",
   "Funeral websites that are cold, cluttered, or hard to contact add stress at the worst possible time. Families need calm, clarity, and an immediate, obvious way to reach a real person.",
   [("Compassionate, calm design","A gentle, dignified feel that reassures families in distress."),
    ("24-hour contact","Immediate, obvious contact — including out-of-hours — for the moment families need you."),
    ("Clear service information","Services, options, and what to do next, explained gently and plainly."),
    ("Local SEO","Win &ldquo;funeral directors [town]&rdquo; and &ldquo;funeral home near me&rdquo; for families searching in grief.")],
   "Families search &ldquo;funeral directors near me&rdquo; and &ldquo;funeral home [town],&rdquo; needing immediate help. We make your contact effortless and your tone reassuring so they reach you without added stress.",
   [("What matters most on a funeral home website?","Compassion and clarity — a calm, dignified feel, gentle information, and an immediate, obvious way to reach a real person, day or night."),
    ("Should contact be available 24 hours?","Yes — families often need help out of hours, so we make 24-hour contact unmistakable and easy."),
    ("How do you keep the tone right?","With restrained, dignified design and plain, gentle language — never salesy — so the site reassures rather than adds stress."),
    ("Can you include obituaries or tributes?","Yes — we can add tribute or obituary pages if you wish, handled with care and dignity.")]),
 # ───────────────────────── LOCAL RETAIL ─────────────────────────
 T("Local Retail","local-retail","Local Shops &amp; Retailers","retail shop website",
   "Local retail and shop website design — online ordering or click-and-collect, hours and location, and local SEO that drives footfall and sales.",
   "Local Shops &amp; Retailers","A shop site that","drives footfall &amp; sales",
   "A local shop competes with online giants on something they can&rsquo;t match: being right here. Your website should pull people through the door with hours, stock, and click-and-collect — and sell online where it makes sense.",
   "A strong local retail website shows your hours and location clearly, highlights stock and specialities, offers click-and-collect or online ordering, and ranks for &ldquo;[product] shop near me&rdquo; so locals choose you over the giants.",
   "Local shops often have no website at all, ceding every &ldquo;near me&rdquo; search to chains and Amazon. Even a simple site with hours, stock, and click-and-collect recaptures local customers who&rsquo;d rather buy nearby.",
   [("Hours, location &amp; stock","The essentials that turn a &ldquo;near me&rdquo; search into a visit through your door."),
    ("Click-and-collect or online sales","Sell or reserve online, collect in store — the local advantage the giants can&rsquo;t match."),
    ("Your speciality &amp; story","What makes your shop worth choosing over a faceless warehouse."),
    ("Local SEO","Win &ldquo;[product] shop near me&rdquo; and &ldquo;[product] [town]&rdquo; with structured data and reviews.")],
   "People search &ldquo;[product] near me&rdquo; and &ldquo;[product] shop [town],&rdquo; wanting it today. We make your hours, stock, and collect options unmissable so locals choose you over next-day delivery.",
   [("Do small local shops really need a website?","Yes — without one you cede every &ldquo;near me&rdquo; search to chains and Amazon. Even a simple site recaptures locals who&rsquo;d rather buy from you today."),
    ("Should I sell online or just show the shop?","Either works — click-and-collect or simple online ordering captures more, but even an informational site with hours and stock drives real footfall. We build to your goals."),
    ("How do I compete with Amazon?","On immediacy and locality — being here now, with click-and-collect and real service. We surface exactly those advantages."),
    ("Can I start small and grow it?","Yes — we can launch with the essentials and add online sales or more later, without a rebuild.")]),
]

CATS = ["Food & Hospitality", "Health & Medical", "Beauty & Wellness", "Fitness",
        "Home & Trades", "Professional Services", "Auto", "Events & Creative",
        "Education & Care", "Local Retail"]


# ── Shared, templated sections (studio offer is consistent; trade-specific
#    copy carries the uniqueness). ──
def proof_band():
    return '''
<section class="section" style="border-top: 1px solid var(--line); background: var(--bg-soft);">
  <div class="container">
    <div data-reveal style="max-width: 720px; margin: 0 auto; text-align: center;">
      <span class="eyebrow">Who builds it</span>
      <h2 class="h-1" style="margin-top: 1rem;">Senior engineers. <span class="italic-serif" style="color: var(--accent);">No agency markup.</span></h2>
      <p class="lead" style="margin-top: 1.5rem;">You work directly with the brothers who write the code &mdash; Adnan in Multan, Irfan in Dubai. Two Top Rated Upwork operators, a long delivery record across almost 15 years, and a 100% Job Success Score. Hire us directly, or run it documented and milestone-led through Upwork &mdash; your call.</p>
      <div class="hero-stats" style="margin-top: 2.5rem; justify-content: center;">
        <div class="hero-stat"><div class="bignum"><span data-count="1000">1000</span><span class="bignum-suffix">+</span></div><div class="hero-stat-lbl">Projects delivered</div></div>
        <div class="hero-stat"><div class="bignum">100<span class="bignum-suffix">%</span></div><div class="hero-stat-lbl">Upwork JSS</div></div>
        <div class="hero-stat"><div class="bignum">15<span class="bignum-suffix">&nbsp;yrs</span></div><div class="hero-stat-lbl">Delivery history</div></div>
        <div class="hero-stat"><div class="bignum">4<span class="bignum-suffix">&nbsp;hr</span></div><div class="hero-stat-lbl">Reply, Mon&ndash;Sat</div></div>
      </div>
    </div>
  </div>
</section>'''


def cta_band(name):
    return f'''
<section class="section-sm" style="background: var(--ink); color: var(--bg);">
  <div class="container-narrow" data-reveal style="text-align: center; padding: 4rem 0;">
    <h2 class="h-1" style="color: var(--bg); margin: 0 0 1.5rem;">Want a {name.lower()} website that earns its keep?</h2>
    <p style="font-family: var(--font-serif); font-size: 1.15rem; line-height: 1.65; color: rgba(244,240,234,.78); max-width: 56ch; margin: 0 auto 2.5rem;">Tell us about your business and what you want the site to do. We&rsquo;ll reply within four hours with honest, specific next steps &mdash; whether you hire us or not.</p>
    <a href="/#contact" class="btn" style="background: var(--bg); color: var(--ink); padding: 1rem 2rem;">
      Start a conversation
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
    </a>
  </div>
</section>'''


def siblings_band(trade):
    sibs = [t for t in TRADES if t["cat"] == trade["cat"] and t["slug"] != trade["slug"]][:3]
    if len(sibs) < 3:
        sibs += [t for t in TRADES if t["slug"] != trade["slug"] and t not in sibs][:3 - len(sibs)]
    cards = "\n".join(
        f'        <a href="/websites/{s["slug"]}/" class="ind-card"><h3>{s["name"]}</h3><p>{s["kw"].capitalize()} design that gets found and books customers.</p></a>'
        for s in sibs
    )
    return f'''
<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 720px; margin-bottom: 2.5rem;">
      <span class="eyebrow">More industries</span>
      <h2 class="h-2" style="margin-top: 1rem;">We build for these too.</h2>
    </div>
    <div class="ind-grid" data-reveal>
{cards}
    </div>
    <p style="margin-top: 2rem;"><a href="/websites/" class="btn-link">See every industry we build for
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg></a></p>
  </div>
</section>'''


def render_trade(trade):
    slug = trade["slug"]; name = trade["name"]; kw = trade["kw"]
    canonical = f"{SITE}/websites/{slug}/"
    title = f'{name.replace("&amp;", "&")} Website Design &amp; Development | Lofts Studio'
    title_plain = re.sub("<[^>]+>", "", title).replace("&amp;", "&")
    jsonld = [
        service_jsonld(re.sub("&amp;", "&", name), kw, canonical),
        faq_jsonld([(re.sub("&[a-z]+;", lambda m: {"&amp;":"&","&rsquo;":"’","&ldquo;":"“","&rdquo;":"”","&lsquo;":"‘"}.get(m.group(0), m.group(0)), q),
                     re.sub("&[a-z]+;", lambda m: {"&amp;":"&","&rsquo;":"’","&ldquo;":"“","&rdquo;":"”","&lsquo;":"‘"}.get(m.group(0), m.group(0)), a))
                    for q, a in trade["faqs"]]),
        breadcrumb_jsonld([("Home", SITE + "/"), ("Websites", SITE + "/websites/"), (re.sub("&amp;", "&", name), canonical)]),
    ]
    includes = "\n".join(
        f'        <div class="feat-card" data-reveal><h3>{t}</h3><p>{d}</p></div>'
        for t, d in trade["includes"]
    )
    faqs = "\n".join(
        f'      <div class="faq-item" data-reveal><h3>{q}</h3><p>{a}</p></div>'
        for q, a in trade["faqs"]
    )
    body = f'''{NAV}

<section class="paper" style="padding: 5.5rem 0 3.5rem;">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);" data-reveal>
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <a href="/websites/" style="color: var(--muted);">Websites</a> <span style="margin: 0 8px;">/</span>
      <span style="color: var(--ink);">{name}</span>
    </nav>
    <div data-reveal style="max-width: 920px;">
      <span class="eyebrow">{trade["eyebrow"]}</span>
      <h1 class="h-display" style="margin-top: 1.25rem;">
        {trade["h1a"]} <span class="italic-serif" style="color: var(--accent);">{trade["h1b"]}</span>.
      </h1>
      <p class="lead" style="margin-top: 1.75rem; max-width: 680px;">{trade["lead"]}</p>
      <div style="margin-top: 2.25rem; display: flex; flex-wrap: wrap; gap: 0.75rem;">
        <a href="/#contact" class="btn btn-primary">Start a conversation
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </a>
        <a href="/portfolio/" class="btn btn-ghost">See our work</a>
      </div>
      <p style="margin-top: 1.5rem; font-size: 0.85rem; color: var(--muted);"><strong style="color: var(--ink);">Top Rated on Upwork</strong> · 100% Job Success · US, UK &amp; Canada hours · Direct hire or a documented workspace</p>
    </div>
    <div class="answer-box" data-reveal style="max-width: 820px;">
      <p><strong style="color: var(--ink);">The short version:</strong> {trade["answer"]}</p>
    </div>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 720px;">
      <span class="eyebrow">The gap</span>
      <h2 class="h-1" style="margin-top: 1rem;">Where most {name.lower()} sites lose the customer.</h2>
      <p class="lead" style="margin-top: 1.5rem;">{trade["problem"]}</p>
    </div>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 720px; margin-bottom: 3rem;">
      <span class="eyebrow">What a great {name.lower()} website includes</span>
      <h2 class="h-1" style="margin-top: 1rem;">Built around how your <span class="italic-serif" style="color: var(--accent);">customers actually decide</span>.</h2>
    </div>
    <div class="feat-grid">
{includes}
    </div>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 760px;">
      <span class="eyebrow">Getting found locally</span>
      <h2 class="h-1" style="margin-top: 1rem;">Show up the moment they search.</h2>
      <p class="lead" style="margin-top: 1.5rem;">{trade["local"]}</p>
      <div class="feat-grid" style="margin-top: 2.5rem;">
        <div class="feat-card" data-reveal><h3>Google Business Profile</h3><p>Properly set up and wired to your site so your hours, location, photos, and reviews are correct everywhere Google shows you.</p></div>
        <div class="feat-card" data-reveal><h3>Reviews that rank</h3><p>Structured review data so your star ratings can show in search &mdash; often the deciding factor between you and the next result.</p></div>
        <div class="feat-card" data-reveal><h3>Fast on mobile</h3><p>Sub-two-second loads on a phone, because a slow site is a closed door &mdash; and speed is a Google ranking factor too.</p></div>
        <div class="feat-card" data-reveal><h3>Built to be found</h3><p>Clean structure, the right local keywords, and technical SEO done properly &mdash; so you climb for &ldquo;{kw} near me&rdquo; and hold the position.</p></div>
      </div>
    </div>
  </div>
</section>
{proof_band()}

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container" style="max-width: 760px;">
    <div data-reveal style="margin-bottom: 1rem;">
      <span class="eyebrow">Questions</span>
      <h2 class="h-1" style="margin-top: 1rem;">{name}, <span class="italic-serif" style="color: var(--accent);">answered</span>.</h2>
    </div>
{faqs}
  </div>
</section>
{siblings_band(trade)}
{cta_band(re.sub("&amp;", "and", name))}

{FOOTER}'''
    return head(title_plain, trade["desc"], canonical, jsonld, og_title=title_plain) + body


def render_hub():
    canonical = f"{SITE}/websites/"
    title = "Websites for Local Businesses | Lofts Studio"
    desc = "Fast, search-optimised websites for local businesses — restaurants, dentists, trades, law firms, salons, gyms and more. Get found on Google and turn visitors into booked customers."
    items = ", ".join(
        f'{{"@type": "ListItem", "position": {i+1}, "name": "{re.sub("&amp;","&",t["name"])} Website Design", "url": "{SITE}/websites/{t["slug"]}/"}}'
        for i, t in enumerate(TRADES)
    )
    hub_faqs = [
        ("Do I need a website if I already have a Google Business Profile and social media?",
         "Yes. Google Business Profile and social media help people discover you, but you don’t own them and they can’t hold your full information, take bookings cleanly, or rank for everything customers search. Your website is the one place you control, and it makes every other channel work harder."),
        ("How does a local business website help me get found on Google?",
         "Through local SEO: a properly set-up Google Business Profile, structured data for reviews and hours, fast mobile pages, and content built around what your customers actually search. Done right, you appear for “[your service] near me” and hold the position."),
        ("Can you build a website for my type of business?",
         "Almost certainly. We build for restaurants, clinics, trades, professional services, salons, gyms, retailers and many more — and the same senior team handles anything not listed. If you serve local customers, we can build the site that brings them in."),
        ("Do I work with an agency or directly with the developer?",
         "Directly with the brothers who write the code — Adnan and Irfan, both Top Rated on Upwork. No account managers, no junior handoffs. You can hire us directly or run the project documented and milestone-led through Upwork."),
    ]
    jsonld = [
        f'{{ "@context": "https://schema.org", "@type": "CollectionPage", "name": "Websites for Local Businesses", "url": "{canonical}", "description": "{desc}", "isPartOf": {{ "@type": "WebSite", "url": "{SITE}/" }} }}',
        f'{{ "@context": "https://schema.org", "@type": "ItemList", "name": "Local business website types", "itemListElement": [ {items} ] }}',
        faq_jsonld(hub_faqs),
        breadcrumb_jsonld([("Home", SITE + "/"), ("Websites", canonical)]),
    ]
    groups = ""
    for cat in CATS:
        cards = "\n".join(
            f'      <a href="/websites/{t["slug"]}/" class="ind-card"><h3>{t["name"]}</h3><p>{t["kw"].capitalize()} design that gets you found and books customers.</p></a>'
            for t in TRADES if t["cat"] == cat
        )
        groups += f'\n    <p class="ind-cat">{cat}</p>\n    <div class="ind-grid">\n{cards}\n    </div>\n'
    faqs_html = "\n".join(
        f'      <div class="faq-item" data-reveal><h3>{q}</h3><p>{a}</p></div>' for q, a in hub_faqs
    )
    body = f'''{NAV}

<section class="paper" style="padding: 5.5rem 0 3.5rem;">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);" data-reveal>
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <span style="color: var(--ink);">Websites</span>
    </nav>
    <div data-reveal style="max-width: 920px;">
      <span class="eyebrow">Websites for local business</span>
      <h1 class="h-display" style="margin-top: 1.25rem;">
        A website that gets you <span class="italic-serif" style="color: var(--accent);">found and booked</span>.
      </h1>
      <p class="lead" style="margin-top: 1.75rem; max-width: 720px;">Most of your future customers will search for you on a phone, decide in seconds, and never call if the site is slow, dated, or missing. We build fast, trustworthy websites for local businesses across the US, UK and Canada &mdash; built around exactly how your customers choose.</p>
      <div style="margin-top: 2.25rem; display: flex; flex-wrap: wrap; gap: 0.75rem;">
        <a href="/#contact" class="btn btn-primary">Start a conversation
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </a>
        <a href="/free-audit/" class="btn btn-ghost">Free 15-min audit</a>
      </div>
      <p style="margin-top: 1.5rem; font-size: 0.85rem; color: var(--muted);"><strong style="color: var(--ink);">Top Rated on Upwork</strong> · 100% Job Success · high-volume delivery · Direct hire or a documented workspace</p>
    </div>
    <div class="answer-box" data-reveal style="max-width: 820px;">
      <p><strong style="color: var(--ink);">The short version:</strong> A local-business website has one job &mdash; get found on Google and turn that visit into a call, booking, or visit. That means fast mobile pages, a clear next step, real local SEO, and content built around how your specific customers decide. Pick your industry below.</p>
    </div>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 720px; margin-bottom: 1rem;">
      <span class="eyebrow">Choose your industry</span>
      <h2 class="h-1" style="margin-top: 1rem;">Built for <span class="italic-serif" style="color: var(--accent);">your kind of business</span>.</h2>
      <p class="lead" style="margin-top: 1.25rem;">Every page below is built around how that specific customer searches and decides &mdash; not a template with the name swapped. Don&rsquo;t see yours? <a href="/#contact">Just ask</a> &mdash; we build for it too.</p>
    </div>
{groups}
  </div>
</section>
{proof_band()}

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container" style="max-width: 760px;">
    <div data-reveal style="margin-bottom: 1rem;">
      <span class="eyebrow">Questions</span>
      <h2 class="h-1" style="margin-top: 1rem;">Local business websites, <span class="italic-serif" style="color: var(--accent);">answered</span>.</h2>
    </div>
{faqs_html}
  </div>
</section>
{cta_band("your business")}

{FOOTER}'''
    return head(title, desc, canonical, jsonld) + body


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def update_sitemap():
    sm = ROOT / "sitemap.xml"
    xml = sm.read_text()
    urls = [f"{SITE}/websites/"] + [f"{SITE}/websites/{t['slug']}/" for t in TRADES]
    block = "\n".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-14</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>"
        for u in urls
    )
    wrapped = f"  <!-- INDUSTRY:START -->\n{block}\n  <!-- INDUSTRY:END -->"
    if "<!-- INDUSTRY:START -->" in xml:
        xml = re.sub(r"  <!-- INDUSTRY:START -->.*?  <!-- INDUSTRY:END -->", wrapped, xml, flags=re.S)
    else:
        xml = xml.replace("</urlset>", wrapped + "\n</urlset>")
    sm.write_text(xml)


def update_llms():
    p = ROOT / "llms.txt"
    txt = p.read_text()
    # Remove any scoping line (no scoping anywhere on the site)
    txt = re.sub(r"- Typical [^\n]*\n", "- Scoping is shared on a short strategy call; every project is fixed-scope, fixed-date, and includes 30 days of post-launch support.\n", txt)
    lines = "\n".join(f"- {re.sub('&amp;','&',t['name'])}: {SITE}/websites/{t['slug']}/" for t in TRADES)
    section = (f"<!-- INDUSTRY:START -->\n## Websites by industry (local businesses)\n"
               f"Lofts Studio builds search-optimised websites for local businesses across the US, UK, and Canada. "
               f"Hub: {SITE}/websites/\n{lines}\n<!-- INDUSTRY:END -->")
    if "<!-- INDUSTRY:START -->" in txt:
        txt = re.sub(r"<!-- INDUSTRY:START -->.*?<!-- INDUSTRY:END -->", section, txt, flags=re.S)
    else:
        txt = txt.rstrip() + "\n\n" + section + "\n"
    p.write_text(txt)


def main():
    write(ROOT / "websites" / "index.html", render_hub())
    for t in TRADES:
        write(ROOT / "websites" / t["slug"] / "index.html", render_trade(t))
    update_sitemap()
    update_llms()
    print(f"Generated /websites/ hub + {len(TRADES)} industry pages.")
    print("Updated sitemap.xml and llms.txt.")


if __name__ == "__main__":
    main()
