#!/usr/bin/env python3
"""
Generate portfolio inner pages from portfolio.json.

Run: python3 scripts/generate_portfolio_pages.py
Outputs:
  /portfolio/<slug>.html  — individual case-study pages (SEO-optimised)
  /portfolio/index.html   — listing page with client-side filter + pagination
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_DIR = ROOT / "portfolio"
DATA_FILE = PORTFOLIO_DIR / "portfolio.json"
INDEX_FILE = ROOT / "index.html"
CACHE_VER = "20260611z"
SITE_URL = "https://lofts.studio"

# ── Service routing ───────────────────────────────────────────────────────────
SERVICE_MAP = {
    "shopify plus": ("/services/shopify-plus-migration.html", "Shopify Plus Migration"),
    "shopify":      ("/services/shopify-development.html",    "Shopify Development"),
    "woocommerce":  ("/services/woocommerce-development.html","WooCommerce Development"),
    "webflow":      ("/services/webflow-development.html",    "Webflow Development"),
    "wordpress":    ("/services/woocommerce-development.html","WordPress Development"),
    "elementor":    ("/services/woocommerce-development.html","WordPress + Elementor"),
    "custom platform": ("/services/custom-app-development.html","Custom App Development"),
    "lms":          ("/services/custom-app-development.html","Custom App Development"),
}

# Keywords per platform for SEO density on case-study pages
PLATFORM_KEYWORDS = {
    "shopify": [
        "hire Shopify developer", "Shopify development services",
        "custom Shopify theme development", "Shopify expert",
        "Shopify store setup and customization",
    ],
    "woocommerce": [
        "WooCommerce development services", "hire WooCommerce developer",
        "WooCommerce store setup", "WooCommerce expert",
        "custom WooCommerce plugin development",
    ],
    "wordpress": [
        "WordPress developer for hire", "custom WordPress development",
        "WordPress website development services", "WordPress expert",
        "Elementor developer",
    ],
    "shopify plus": [
        "Shopify Plus migration", "Shopify Plus developer",
        "migrate to Shopify Plus", "Shopify Plus expert",
    ],
}


def keywords_for(platform: str) -> list:
    p = platform.lower()
    for key, kws in PLATFORM_KEYWORDS.items():
        if key in p:
            return kws
    return PLATFORM_KEYWORDS["shopify"]


def service_for(platform: str):
    p = (platform or "").lower()
    for key, val in SERVICE_MAP.items():
        if key in p:
            return val
    return ("/services/shopify-development.html", "Shopify Development")


def title_for(item: dict) -> str:
    """SEO title: [Service] Case Study: [Client] — [Outcome] | Adnan K."""
    _, svc = service_for(item.get("platform", ""))
    name = item["name"]
    tagline = item.get("tagline", "")
    # Keep under ~60 chars: truncate tagline portion if needed
    base = f"{svc} Case Study: {name}"
    suffix = " | Adnan K."
    if len(base) + len(suffix) <= 60:
        return base + suffix
    return f"{name} — {svc} Case Study | Adnan K."


def meta_desc_for(item: dict) -> str:
    """SEO meta description — unique per project, under 155 chars."""
    _, svc = service_for(item.get("platform", ""))
    name = item["name"]
    tagline = item.get("tagline", "")
    year = item.get("year", "")
    # Template: "How Adnan K. delivered [tagline] for [name] ({year}). [svc] expert, 307 stores shipped."
    base = f"How Adnan K. built {name} — {tagline} ({year}). Shopify & WordPress expert, 307+ stores shipped, 100% JSS."
    return base[:155]


def get_next_item(items, current_slug):
    published = [i for i in items if i.get("published")]
    published.sort(key=lambda x: x.get("displayOrder", 999))
    for idx, item in enumerate(published):
        if item["slug"] == current_slug:
            return published[(idx + 1) % len(published)]
    return published[0] if published else None


def load_nav_and_footer():
    with open(INDEX_FILE) as f:
        index_html = f.read()
    nav_match = re.search(r'<header class="nav-bar">.*?</header>', index_html, re.DOTALL)
    footer_match = re.search(r'<footer class="site-footer.*?</footer>', index_html, re.DOTALL)
    if not nav_match or not footer_match:
        raise SystemExit("Cannot extract nav/footer from index.html")
    return nav_match.group(0), footer_match.group(0)


def render(item: dict, items: list, nav: str, footer: str) -> str:
    slug     = item["slug"]
    name     = item["name"]
    tagline  = item.get("tagline", "")
    summary  = item.get("summary", "")
    url      = item.get("url", "")
    image    = item.get("image", "")
    platform = item.get("platform", "")
    category = item.get("category", "")
    stack    = item.get("stack") or []
    metric   = item.get("metric") or {"value": "", "label": ""}
    year     = item.get("year", "")
    role     = item.get("role", "")

    service_url, service_label = service_for(platform)
    nxt = get_next_item(items, slug)
    page_title = title_for(item)
    page_desc  = meta_desc_for(item)
    kws        = keywords_for(platform)
    kw_str     = ", ".join(kws)

    # ── Screenshot / wordmark block ───────────────────────────────────────────
    if image and not item.get("hideScreenshot"):
        url_display = url.replace("https://", "").replace("http://", "")
        image_html = f'''<section class="section-sm" style="padding:1rem 0 5rem;">
  <div class="container" data-reveal>
    <div style="border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--bg-soft);">
      <a href="{url}" target="_blank" rel="noopener" aria-label="Visit {name} live site">
        <img src="{image}" alt="{name} homepage screenshot — {platform} project by Adnan K." loading="lazy" decoding="async" style="display:block;width:100%;height:auto;" />
      </a>
    </div>
    <p style="text-align:center;font-family:var(--font-sans);font-size:0.78rem;color:var(--muted);margin:1.25rem 0 0;letter-spacing:0.01em;">
      Live at <a href="{url}" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline;text-underline-offset:3px;">{url_display}</a> &nbsp;&middot;&nbsp; click to visit
    </p>
  </div>
</section>'''
    else:
        url_display = url.replace("https://", "").replace("http://", "")
        cat = item.get("category", "").split("·")[0].strip()
        visit_link = f'<a href="{url}" target="_blank" rel="noopener" style="display:inline-flex;margin-top:2.5rem;font-family:var(--font-sans);font-size:0.86rem;color:var(--ink);border-bottom:1px solid var(--ink);padding-bottom:2px;align-items:center;gap:8px;">Visit {url_display} &nbsp;&rarr;</a>' if url else ""
        image_html = f'''<section class="section-sm" style="padding:1rem 0 5rem;">
  <div class="container-narrow" data-reveal>
    <div style="position:relative;border-radius:var(--r-lg);padding:6rem 3rem 5rem;text-align:center;background:linear-gradient(155deg,var(--bg) 0%,var(--bg-soft) 60%,var(--surface) 100%);border:1px solid var(--line);">
      <div style="position:absolute;top:2rem;left:50%;transform:translateX(-50%);width:6px;height:6px;border-radius:50%;background:var(--accent);opacity:0.85;"></div>
      <p style="font-family:var(--font-serif);font-style:italic;font-weight:400;font-size:clamp(2.8rem,6vw,4.4rem);line-height:1.02;letter-spacing:-0.035em;color:var(--ink);margin:0;max-width:16ch;margin-left:auto;margin-right:auto;">{name}</p>
      <p style="margin-top:1.25rem;font-family:var(--font-sans);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.24em;color:var(--muted);">{cat}</p>
      {visit_link}
    </div>
  </div>
</section>'''

    stack_pills = " ".join([f'<span class="tag-pill">{s}</span>' for s in stack])

    # ── Next case study ───────────────────────────────────────────────────────
    next_section = ""
    if nxt:
        next_section = f'''<section class="section-sm" style="background:var(--bg-soft);border-top:1px solid var(--line);">
  <div class="container" data-reveal>
    <div style="display:flex;align-items:center;justify-content:space-between;gap:2rem;flex-wrap:wrap;padding:2.5rem 0;">
      <div>
        <p style="font-family:var(--font-sans);font-size:0.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.22em;margin:0 0 0.5rem;">Next case study</p>
        <h3 class="h-2" style="margin:0;"><a href="/portfolio/{nxt['slug']}.html" style="color:var(--ink);">{nxt['name']}</a></h3>
        <p style="font-family:var(--font-serif);color:var(--ink-soft);margin:0.4rem 0 0;font-style:italic;">{nxt.get('tagline','')}</p>
      </div>
      <a href="/portfolio/{nxt['slug']}.html" class="btn btn-primary">Read {nxt['name']} &nbsp;&rarr;</a>
    </div>
  </div>
</section>'''

    og_image = image if image else "/assets/og.jpg"

    # ── BreadcrumbList schema ─────────────────────────────────────────────────
    breadcrumb_schema = f'''{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE_URL}/"}},
    {{"@type":"ListItem","position":2,"name":"Portfolio","item":"{SITE_URL}/portfolio/"}},
    {{"@type":"ListItem","position":3,"name":"{name}","item":"{SITE_URL}/portfolio/{slug}.html"}}
  ]
}}'''

    # ── CreativeWork schema ───────────────────────────────────────────────────
    cw_schema = f'''{{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{name}",
  "description": "{tagline}. {summary[:200]}",
  "url": "{SITE_URL}/portfolio/{slug}.html",
  "image": "{SITE_URL}{og_image}",
  "dateCreated": "{year}",
  "keywords": "{kw_str}",
  "creator": {{
    "@type": "Person",
    "name": "Adnan K.",
    "url": "{SITE_URL}",
    "jobTitle": "Shopify & WordPress Developer",
    "knowsAbout": ["Shopify Development","WooCommerce Development","WordPress Development","Elementor","CRO","Speed Optimization"]
  }},
  "about": {{
    "@type": "WebSite",
    "name": "{name}",
    "url": "{url if url else SITE_URL}"
  }}
}}'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{page_title}</title>
<meta name="description" content="{page_desc}" />
<meta name="keywords" content="{kw_str}, {name}, {platform}, {category}" />
<link rel="canonical" href="{SITE_URL}/portfolio/{slug}.html" />
<meta name="robots" content="index,follow,max-image-preview:large" />

<!-- Open Graph -->
<meta property="og:type" content="article" />
<meta property="og:title" content="{page_title}" />
<meta property="og:description" content="{page_desc}" />
<meta property="og:url" content="{SITE_URL}/portfolio/{slug}.html" />
<meta property="og:image" content="{SITE_URL}{og_image}" />
<meta property="og:site_name" content="Lofts Studio" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{page_title}" />
<meta name="twitter:description" content="{page_desc}" />
<meta name="twitter:image" content="{SITE_URL}{og_image}" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />

<script type="application/ld+json">{breadcrumb_schema}</script>
<script type="application/ld+json">{cw_schema}</script>
</head>
<body>

{nav}

<section class="paper" style="padding:6rem 0 3rem;">
  <div class="container">
    <nav aria-label="Breadcrumb" data-reveal style="margin-bottom:1.5rem;font-family:var(--font-sans);font-size:0.78rem;color:var(--muted);letter-spacing:0.01em;">
      <a href="/" style="color:var(--muted);">Home</a> &nbsp;/&nbsp;
      <a href="/portfolio/" style="color:var(--muted);">Portfolio</a> &nbsp;/&nbsp;
      <span style="color:var(--ink);">{name}</span>
    </nav>
    <div data-reveal style="max-width:920px;">
      <span class="eyebrow">{category}</span>
      <h1 class="h-display" data-split="words" style="margin-top:1.25rem;">{name}.</h1>
      <p class="lead" style="margin-top:1.5rem;">{tagline}.</p>
      <div style="margin-top:2rem;display:flex;gap:0.75rem;flex-wrap:wrap;">
        {f'<a href="{url}" target="_blank" rel="noopener" class="btn btn-primary">Visit live site &nbsp;&rarr;</a>' if url else ''}
        <a href="/portfolio/" class="btn btn-ghost">&larr; All case studies</a>
      </div>
    </div>
  </div>
</section>

{image_html}

<section class="section-sm" style="border-top:1px solid var(--line);padding:4rem 0;">
  <div class="container">
    <div data-reveal class="case-brief">
      <div><span class="eyebrow">The brief</span></div>
      <div>
        <p style="font-family:var(--font-serif);font-size:1.15rem;line-height:1.7;color:var(--ink);margin:0 0 2rem;max-width:62ch;">{summary}</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:2rem;padding-top:2rem;border-top:1px solid var(--line);">
          <div>
            <p style="font-family:var(--font-sans);font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.2em;margin:0 0 0.5rem;">Year</p>
            <p style="font-family:var(--font-serif);font-size:1.05rem;color:var(--ink);margin:0;">{year}</p>
          </div>
          <div>
            <p style="font-family:var(--font-sans);font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.2em;margin:0 0 0.5rem;">Platform</p>
            <p style="font-family:var(--font-serif);font-size:1.05rem;color:var(--ink);margin:0;">{platform}</p>
          </div>
          <div>
            <p style="font-family:var(--font-sans);font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.2em;margin:0 0 0.5rem;">Role</p>
            <p style="font-family:var(--font-serif);font-size:1.05rem;color:var(--ink);margin:0;">{role}</p>
          </div>
        </div>
        <div style="margin-top:2rem;display:flex;gap:0.5rem;flex-wrap:wrap;">{stack_pills}</div>
      </div>
    </div>
  </div>
</section>

<section class="section-sm" style="background:var(--bg-soft);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:5rem 0;">
  <div class="container-narrow" data-reveal style="text-align:center;">
    <p style="font-family:var(--font-sans);font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.22em;margin:0 0 1.5rem;">The outcome</p>
    <p style="font-family:var(--font-display);font-weight:500;font-size:clamp(3rem,7vw,5.4rem);line-height:1;letter-spacing:-0.045em;color:var(--ink);margin:0;">{metric.get('value','')}</p>
    <p style="font-family:var(--font-serif);font-style:italic;font-size:1.2rem;color:var(--ink-soft);margin:1.25rem auto 0;max-width:38ch;line-height:1.45;">{metric.get('label','')}</p>
  </div>
</section>

<section class="section-sm" style="padding:5rem 0;">
  <div class="container">
    <div data-reveal class="case-cta-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;max-width:920px;margin:0 auto;">
      <a href="/#contact" class="card" style="text-decoration:none;display:flex;flex-direction:column;gap:0.85rem;">
        <span style="font-family:var(--font-sans);font-size:0.68rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.2em;font-weight:600;">Start a conversation</span>
        <h3 class="h-2" style="margin:0;">Want something like {name} for your store?</h3>
        <p style="font-family:var(--font-serif);color:var(--ink-soft);margin:0;line-height:1.6;">Send a URL and what you&rsquo;d change. Four-hour reply with three specific suggestions, whether you hire me or not.</p>
        <span class="btn-editorial" style="align-self:flex-start;margin-top:0.5rem;">Open the form &nbsp;&rarr;</span>
      </a>
      <a href="{service_url}" class="card" style="text-decoration:none;display:flex;flex-direction:column;gap:0.85rem;">
        <span style="font-family:var(--font-sans);font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.2em;font-weight:600;">Related service</span>
        <h3 class="h-2" style="margin:0;">Read about {service_label}</h3>
        <p style="font-family:var(--font-serif);color:var(--ink-soft);margin:0;line-height:1.6;">How a {service_label} engagement actually moves through this studio — scope, timeline, deliverables, fixed price.</p>
        <span class="btn-editorial" style="align-self:flex-start;margin-top:0.5rem;">See the service &nbsp;&rarr;</span>
      </a>
    </div>
  </div>
</section>

{next_section}

{footer}

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/main.js?v={CACHE_VER}" defer></script>
<script src="/assets/widgets.js?v={CACHE_VER}" defer></script>

<style>
  .case-brief {{ display:grid;grid-template-columns:0.6fr 2fr;gap:4rem;max-width:1080px;margin:0 auto; }}
  @media (max-width:880px) {{
    .case-brief {{ grid-template-columns:1fr;gap:1.5rem; }}
    .case-cta-grid {{ grid-template-columns:1fr !important; }}
  }}
</style>
</body>
</html>
'''


# ─────────────────────────────────────────────────────────────────────────────
#  Listing page — with filter + pagination
# ─────────────────────────────────────────────────────────────────────────────

def render_listing(items: list, nav: str, footer: str) -> str:
    published = [i for i in items if i.get("published")]
    published.sort(key=lambda x: x.get("displayOrder", 999))

    # Build unique filter options from the data
    platforms = sorted(set(i.get("platform", "").split("+")[0].split("/")[0].strip() for i in published if i.get("platform")))
    # Normalise platform buckets
    plat_buckets = {"Shopify": [], "WooCommerce": [], "WordPress": [], "Custom": []}
    for p in platforms:
        pl = p.lower()
        if "shopify" in pl:
            plat_buckets["Shopify"].append(p)
        elif "woocommerce" in pl:
            plat_buckets["WooCommerce"].append(p)
        elif "wordpress" in pl or "elementor" in pl:
            plat_buckets["WordPress"].append(p)
        else:
            plat_buckets["Custom"].append(p)

    # Category top-level buckets
    cat_buckets = {
        "Ecommerce": ["shopify", "woocommerce", "ecommerce", "dtc", "marketplace", "store"],
        "WordPress": ["wordpress", "elementor"],
        "B2B": ["b2b", "wholesale", "enterprise"],
        "Finance": ["finance", "insurance", "reinsurance", "fintech"],
        "SaaS / App": ["saas", "app", "ai", "edtech", "membership"],
        "Agency / Brand": ["agency", "brand", "branding", "marketing"],
    }

    def card_filter_attrs(item):
        """Return data-* attrs used by the JS filter."""
        p = item.get("platform", "").lower()
        c = item.get("category", "").lower()
        stack_str = " ".join(item.get("stack") or []).lower()
        # platform bucket
        if "shopify" in p:
            pb = "shopify"
        elif "woocommerce" in p:
            pb = "woocommerce"
        elif "wordpress" in p or "elementor" in p:
            pb = "wordpress"
        else:
            pb = "custom"
        # category bucket — check category AND stack AND platform for broadest matching
        combined = c + " " + stack_str + " " + p
        cb = "other"
        # Explicit priority order
        if any(k in combined for k in ["b2b", "wholesale", "enterprise", "regulated"]):
            cb = "b2b"
        elif any(k in combined for k in ["saas", "app", "ai", "edtech", "membership", "lms", "discord", "community", "phonics", "coaching"]):
            cb = "saas-app"
        elif any(k in combined for k in ["finance", "insurance", "reinsurance", "fintech", "investment", "research"]):
            cb = "finance"
        elif any(k in combined for k in ["agency", "brand", "branding", "marketing", "personal brand", "public figure"]):
            cb = "agency-brand"
        elif any(k in combined for k in ["ecommerce", "shopify", "woocommerce", "dtc", "marketplace", "store", "shop"]):
            cb = "ecommerce"
        elif any(k in combined for k in ["wordpress", "elementor"]):
            cb = "other"
        return f'data-platform="{pb}" data-cat="{cb}" data-featured="{str(item.get("featured", False)).lower()}"'

    # Build card HTML — now includes filter attrs + data-index for pagination
    card_blocks = []
    for idx, item in enumerate(published):
        img  = item.get("image", "")
        url_display = item.get("url", "").replace("https://", "").replace("http://", "")
        featured_badge = '<span class="work-card-badge">Featured</span>' if item.get("featured") else ""
        filter_attrs = card_filter_attrs(item)

        if img and not item.get("hideScreenshot"):
            img_html = f'<img src="{img}" alt="{item["name"]} — {item.get("platform","")} project" loading="lazy" />'
        else:
            cat = item.get("category", "").split("·")[0].strip()
            img_html = f'''<div class="work-card-placeholder">
              <span class="work-card-placeholder-name">{item["name"]}</span>
              <span class="work-card-placeholder-label">{cat or "Live engagement"}</span>
            </div>'''

        live_link = f'<a href="{item.get("url","#")}" target="_blank" rel="noopener" class="work-card-live" aria-label="Visit {item["name"]} live">&#8599;&nbsp;{url_display}</a>' if item.get("url") else ""

        card_blocks.append(f'''
      <article class="work-card{' work-card-featured' if item.get('featured') else ''}" {filter_attrs} data-index="{idx}">
        <a href="/portfolio/{item['slug']}.html" class="work-card-img-link" aria-label="View {item['name']} case study">
          <div class="work-card-img">{img_html}</div>
          {featured_badge}
        </a>
        <div class="work-card-body">
          <div class="work-card-meta">{item.get('platform','')} &nbsp;&middot;&nbsp; {item.get('year','')}</div>
          <h3 class="work-card-name">{item['name']}</h3>
          <p class="work-card-tag">{item.get('tagline','')}</p>
          <div class="work-card-actions">
            <a href="/portfolio/{item['slug']}.html" class="work-card-cs">Case study &nbsp;&rarr;</a>
            {live_link}
          </div>
        </div>
      </article>''')

    # Schema ItemList
    schema_items = []
    for idx, item in enumerate(published, start=1):
        schema_items.append(f'      {{"@type":"ListItem","position":{idx},"url":"{SITE_URL}/portfolio/{item["slug"]}.html","name":"{item["name"]}"}}')
    schema_str = ",\n".join(schema_items)
    total = len(published)

    cards_html = "\n".join(card_blocks)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Shopify & WordPress Portfolio — {total} Case Studies | Adnan K.</title>
<meta name="description" content="Browse {total} live client projects by Adnan K. — Shopify, WooCommerce & WordPress developer with 9 years experience, 307 stores shipped. Filter by platform, category, or stack." />
<meta name="keywords" content="Shopify developer portfolio, WooCommerce case studies, WordPress developer work, hire Shopify developer, ecommerce developer portfolio, Adnan K." />
<link rel="canonical" href="{SITE_URL}/portfolio/" />
<meta name="robots" content="index,follow" />
<meta property="og:type" content="website" />
<meta property="og:title" content="Portfolio — {total} Case Studies | Adnan K." />
<meta property="og:description" content="{total} live projects — Shopify, WooCommerce & WordPress. 307 stores shipped in 9 years." />
<meta property="og:url" content="{SITE_URL}/portfolio/" />
<meta property="og:image" content="{SITE_URL}/assets/og.jpg" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Portfolio — Adnan K.",
  "description": "Every live client project from nine years of Shopify and WooCommerce work.",
  "url": "{SITE_URL}/portfolio/",
  "mainEntity": {{
    "@type": "ItemList",
    "numberOfItems": {total},
    "itemListElement": [
{schema_str}
    ]
  }}
}}
</script>
</head>
<body>

{nav}

<section class="paper" style="padding:7rem 0 4rem;">
  <div class="container">
    <div data-reveal style="max-width:940px;">
      <span class="eyebrow">Selected work &nbsp;&middot;&nbsp; 2017&ndash;present</span>
      <h1 class="h-display" data-split="words" style="margin-top:1.5rem;">
        {total} live projects. <span class="italic-serif">Every one shipped.</span>
      </h1>
      <p class="lead" style="margin-top:2rem;">
        Nine years. Three hundred and seven builds. Below are the {total} I can show publicly — DTC, B2B, marketplaces, subscription, insurance, editorial. All have full case studies with live URLs you can open right now.
      </p>
      <div class="hero-stats">
        <div class="hero-stat"><div class="bignum"><span data-count="307">307</span></div><div class="hero-stat-lbl">Stores shipped</div></div>
        <div class="hero-stat"><div class="bignum">{total}</div><div class="hero-stat-lbl">Public case studies</div></div>
        <div class="hero-stat"><div class="bignum">9<span class="bignum-suffix">&nbsp;yrs</span></div><div class="hero-stat-lbl">Single-operator</div></div>
        <div class="hero-stat"><div class="bignum">100<span class="bignum-suffix">%</span></div><div class="hero-stat-lbl">Upwork JSS</div></div>
      </div>
    </div>
  </div>
</section>

<!-- ── Filter bar ─────────────────────────────────────────────────────────── -->
<div class="pf-filter-bar" id="filterBar" style="position:sticky;top:64px;z-index:50;background:rgba(244,240,234,.95);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--line);">
  <div class="container" style="padding-top:0.85rem;padding-bottom:0.85rem;">
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;">
      <span style="font-family:var(--font-sans);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--muted);margin-right:0.5rem;">Filter:</span>

      <!-- Platform -->
      <div class="filter-group" style="display:flex;gap:0.35rem;flex-wrap:wrap;">
        <button class="filter-btn active" data-filter="platform" data-value="all">All</button>
        <button class="filter-btn" data-filter="platform" data-value="shopify">Shopify</button>
        <button class="filter-btn" data-filter="platform" data-value="woocommerce">WooCommerce</button>
        <button class="filter-btn" data-filter="platform" data-value="wordpress">WordPress</button>
        <button class="filter-btn" data-filter="platform" data-value="custom">Custom</button>
      </div>

      <span style="width:1px;height:20px;background:var(--line);margin:0 0.25rem;"></span>

      <!-- Category -->
      <div class="filter-group" style="display:flex;gap:0.35rem;flex-wrap:wrap;">
        <button class="filter-btn" data-filter="cat" data-value="ecommerce">Ecommerce</button>
        <button class="filter-btn" data-filter="cat" data-value="b2b">B2B</button>
        <button class="filter-btn" data-filter="cat" data-value="finance">Finance</button>
        <button class="filter-btn" data-filter="cat" data-value="saas-app">SaaS / App</button>
        <button class="filter-btn" data-filter="cat" data-value="agency-brand">Agency / Brand</button>
      </div>

      <span style="margin-left:auto;font-family:var(--font-sans);font-size:0.72rem;color:var(--muted);" id="filterCount">{total} projects</span>
    </div>
  </div>
</div>

<!-- ── Work grid ──────────────────────────────────────────────────────────── -->
<section class="section" id="all-work" style="border-top:0;padding:4rem 0 6rem;">
  <div class="container">
    <div class="work-grid" id="workGrid">
{cards_html}
    </div>

    <!-- Empty state -->
    <div id="emptyState" style="display:none;text-align:center;padding:5rem 0;">
      <p style="font-family:var(--font-serif);font-size:1.2rem;color:var(--ink-soft);font-style:italic;">No projects match that filter — try clearing one.</p>
      <button class="filter-btn active" style="margin-top:1.5rem;" onclick="resetFilters()">Clear filters</button>
    </div>

    <!-- ── Pagination ──────────────────────────────────────────────────────── -->
    <nav aria-label="Portfolio pages" id="pagination" style="display:flex;justify-content:center;gap:0.5rem;margin-top:4rem;flex-wrap:wrap;"></nav>
  </div>
</section>

<!-- Closing essay -->
<section class="section">
  <div class="container">
    <div data-reveal class="essay-grid" style="display:grid;grid-template-columns:1fr 2fr;gap:5rem;max-width:1100px;margin:0 auto;">
      <div><span class="eyebrow">The thread</span></div>
      <div class="prose">
        <h2 class="h-1" style="margin:0 0 1.5rem;">There is a pattern in the projects above — <span class="italic-serif">and it&rsquo;s not Shopify.</span></h2>
        <p>DTC and B2B, fashion and food, military and medical, marketplaces and editorial. Five different platforms. Twenty-nine different audiences. What they share isn&rsquo;t a stack — it&rsquo;s founders who chose to wait a little longer for work that lasts.</p>
        <p>Every one of these projects had a faster path: pick a $300 theme, hire whoever&rsquo;s cheapest, ship in a fortnight. These founders didn&rsquo;t take it. They wanted the build to survive a year of changes, an investor due-diligence read, a Black Friday spike, and the day someone else has to come in and edit the codebase.</p>
        <p>That&rsquo;s the only audience I&rsquo;m built for. If that&rsquo;s you, the form on <a href="/#contact" style="color:var(--ink);text-decoration:underline;text-underline-offset:4px;">the homepage</a> takes ninety seconds.</p>
      </div>
    </div>
  </div>
</section>

<section class="section-sm" style="background:var(--ink);color:var(--bg);">
  <div class="container-narrow" data-reveal style="text-align:center;padding:4rem 0;">
    <h2 class="h-1" style="color:var(--bg);margin:0 0 1.5rem;">Want one of these stories to be yours next?</h2>
    <p style="font-family:var(--font-serif);font-size:1.15rem;line-height:1.65;color:rgba(244,240,234,.78);max-width:56ch;margin:0 auto 2.5rem;">Send your URL and the one thing you&rsquo;d change. I&rsquo;ll reply within four hours with three suggestions &mdash; whether you hire me or not.</p>
    <a href="/#contact" class="btn" style="background:var(--bg);color:var(--ink);padding:1rem 2rem;">
      Send a note
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
    </a>
  </div>
</section>

{footer}

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/main.js?v={CACHE_VER}" defer></script>
<script src="/assets/widgets.js?v={CACHE_VER}" defer></script>

<script>
(function() {{
  const PER_PAGE = 12;
  let activePlatform = 'all';
  let activeCat = 'all';
  let currentPage = 1;

  const grid = document.getElementById('workGrid');
  const pagination = document.getElementById('pagination');
  const countEl = document.getElementById('filterCount');
  const emptyState = document.getElementById('emptyState');
  const allCards = Array.from(grid.querySelectorAll('.work-card'));

  function getVisible() {{
    return allCards.filter(card => {{
      const pm = activePlatform === 'all' || card.dataset.platform === activePlatform;
      const cm = activeCat === 'all' || card.dataset.cat === activeCat;
      // When both filters are active simultaneously, use OR (union) so you always see results
      if (activePlatform !== 'all' && activeCat !== 'all') return pm || cm;
      return pm && cm;
    }});
  }}

  function render() {{
    const visible = getVisible();
    const totalPages = Math.ceil(visible.length / PER_PAGE);
    if (currentPage > totalPages) currentPage = 1;
    const start = (currentPage - 1) * PER_PAGE;
    const end = start + PER_PAGE;

    // Show/hide cards
    allCards.forEach(c => c.style.display = 'none');
    visible.slice(start, end).forEach(c => c.style.display = '');

    // Empty state
    emptyState.style.display = visible.length === 0 ? 'block' : 'none';

    // Count label
    countEl.textContent = visible.length + ' project' + (visible.length === 1 ? '' : 's');

    // Pagination
    pagination.innerHTML = '';
    if (totalPages <= 1) return;
    for (let p = 1; p <= totalPages; p++) {{
      const btn = document.createElement('button');
      btn.className = 'filter-btn' + (p === currentPage ? ' active' : '');
      btn.textContent = p;
      btn.setAttribute('aria-label', 'Page ' + p);
      btn.addEventListener('click', () => {{ currentPage = p; render(); window.scrollTo({{top: document.getElementById('all-work').offsetTop - 120, behavior:'smooth'}}); }});
      pagination.appendChild(btn);
    }}
  }}

  // Filter button clicks
  document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const f = btn.dataset.filter;
      const v = btn.dataset.value;
      // Deactivate siblings
      document.querySelectorAll('.filter-btn[data-filter="' + f + '"]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (f === 'platform') activePlatform = v;
      if (f === 'cat') {{ activeCat = (activeCat === v) ? 'all' : v; document.querySelectorAll('.filter-btn[data-filter="cat"]').forEach(b => b.classList.toggle('active', b.dataset.value === activeCat)); }}
      currentPage = 1;
      render();
    }});
  }});

  window.resetFilters = function() {{
    activePlatform = 'all'; activeCat = 'all'; currentPage = 1;
    document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.toggle('active', b.dataset.value === 'all'));
    render();
  }};

  render();
}})();
</script>

<style>
  .filter-btn {{
    font-family: var(--font-sans); font-size: 0.72rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.12em;
    padding: 0.4rem 0.9rem; border-radius: 100px;
    border: 1px solid var(--line); background: transparent; color: var(--ink-soft);
    cursor: pointer; transition: all 0.18s ease; white-space: nowrap;
  }}
  .filter-btn:hover {{ background: var(--surface); color: var(--ink); }}
  .filter-btn.active {{ background: var(--ink); color: var(--bg); border-color: var(--ink); }}
  .essay-grid {{ @media (max-width:880px) {{ grid-template-columns: 1fr; gap: 2rem; }} }}
  /* Mobile: keep the filter bar from covering the page, show 2 cards per row */
  @media (max-width: 640px) {{
    /* Was sticky — on phones it followed the scroll and hid the work. Let it scroll away. */
    .pf-filter-bar {{ position: static !important; }}
    .pf-filter-bar .container {{ padding-top: 0.6rem !important; padding-bottom: 0.6rem !important; }}
    .filter-btn {{ padding: 0.32rem 0.7rem; font-size: 0.64rem; letter-spacing: 0.08em; }}

    /* Two-up portfolio grid */
    #workGrid.work-grid {{ grid-template-columns: repeat(2, 1fr); gap: 0.85rem; }}
    .work-card-body {{ padding: 0.85rem 0.85rem 1rem; }}
    .work-card-meta {{ font-size: 0.6rem; letter-spacing: 0.06em; }}
    .work-card-name {{ font-size: 1rem !important; }}
    .work-card-tag {{ font-size: 0.82rem !important; line-height: 1.45 !important; }}
    .work-card-actions {{ flex-direction: column; align-items: flex-start; gap: 0.45rem; }}
    .work-card-badge {{ font-size: 0.55rem; padding: 0.25rem 0.55rem; }}
  }}
</style>
</body>
</html>
'''


def main():
    with open(DATA_FILE) as f:
        data = json.load(f)
    items = data.get("items", [])
    published = [i for i in items if i.get("published")]
    nav, footer = load_nav_and_footer()

    for item in published:
        slug = item["slug"]
        out = PORTFOLIO_DIR / f"{slug}.html"
        out.write_text(render(item, items, nav, footer))
        print(f"  ✓ portfolio/{slug}.html")

    listing_path = PORTFOLIO_DIR / "index.html"
    listing_path.write_text(render_listing(items, nav, footer))
    print(f"  ✓ portfolio/index.html (with {len(published)} items)")
    print(f"\nGenerated {len(published)} inner pages + listing.")


if __name__ == "__main__":
    main()
