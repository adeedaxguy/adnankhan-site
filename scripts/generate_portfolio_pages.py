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
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_DIR = ROOT / "portfolio"
DATA_FILE = PORTFOLIO_DIR / "portfolio.json"
INDEX_FILE = ROOT / "index.html"
CACHE_VER = "20260731b"
SITE_URL = "https://lofts.studio"
GTM_HEAD = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-PM4CX9JG');</script>
<!-- End Google Tag Manager -->"""
GTM_BODY = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-PM4CX9JG"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

# ── Service routing ───────────────────────────────────────────────────────────
SERVICE_MAP = {
    "shopify plus": ("/services/shopify-plus-migration.html", "Shopify Plus Migration"),
    "shopify":      ("/services/shopify-development.html",    "Shopify Development"),
    "woocommerce":  ("/services/woocommerce-development.html","WooCommerce Development"),
    "webflow":      ("/services/webflow-development.html",    "Webflow Development"),
    "wordpress":    ("/services/wordpress-development.html",  "WordPress Development"),
    "elementor":    ("/services/wordpress-development.html",  "WordPress + Elementor"),
    "custom platform": ("/services/custom-app-development.html","Custom App Development"),
    "custom":       ("/services/custom-app-development.html", "Custom Website Development"),
    "saas":         ("/services/saas-website-design.html",    "SaaS Website Design"),
    "app":          ("/services/custom-app-development.html", "Custom App Development"),
    "ai":           ("/services/ai-calling-agents.html",      "AI Automation"),
    "lms":          ("/services/custom-app-development.html","Custom App Development"),
}

# Keywords per platform for SEO density on case-study pages
PLATFORM_KEYWORDS = {
    "shopify": [
        "Shopify development portfolio", "Shopify website design",
        "custom Shopify theme development", "Shopify expert",
        "Shopify store setup and customization",
    ],
    "woocommerce": [
        "WooCommerce development portfolio", "WooCommerce website design",
        "WooCommerce store setup", "WooCommerce expert",
        "custom WooCommerce development",
    ],
    "wordpress": [
        "WordPress development portfolio", "custom WordPress development",
        "WordPress website design", "WordPress expert",
        "Elementor developer",
    ],
    "shopify plus": [
        "Shopify Plus migration", "Shopify Plus developer",
        "migrate to Shopify Plus", "Shopify Plus expert",
    ],
    "webflow": [
        "Webflow development portfolio", "Webflow website design",
        "Webflow developer", "custom Webflow development",
    ],
    "custom": [
        "custom website development portfolio", "custom web development",
        "website design portfolio", "senior web engineering",
    ],
}


INDUSTRY_KEYWORDS = {
    "b2b": ["B2B website design", "B2B web development", "lead generation website"],
    "marketplace": ["marketplace website development", "marketplace web design"],
    "finance": ["finance website design", "trust-led website design"],
    "insurance": ["insurance website design", "regulated business website"],
    "ecommerce": ["ecommerce website design", "conversion-focused ecommerce site"],
    "dtc": ["DTC ecommerce website", "direct-to-consumer web design"],
    "saas": ["SaaS website design", "product website design"],
    "app": ["web app design", "product-led website"],
    "ai": ["AI website design", "AI automation website"],
    "pet": ["pet services website design"],
    "construction": ["construction website design"],
    "architecture": ["architecture portfolio website"],
    "food": ["food marketplace website"],
    "travel": ["travel website development"],
    "automotive": ["automotive ecommerce website"],
    "membership": ["membership website development"],
    "community": ["community website development"],
    "agency": ["agency website design"],
    "brand": ["brand website design"],
}


def keywords_for(item) -> list:
    if isinstance(item, str):
        platform = item
        category = ""
        stack = ""
        name = ""
    else:
        platform = item.get("platform", "")
        category = item.get("category", "")
        stack = " ".join(item.get("stack") or [])
        name = item.get("name", "")
    p = platform.lower()
    combined = f"{platform} {category} {stack}".lower()
    kws = []
    for key, kws in PLATFORM_KEYWORDS.items():
        if key in p:
            kws = list(kws)
            break
    if not kws:
        kws = list(PLATFORM_KEYWORDS["custom"])
    for key, industry_kws in INDUSTRY_KEYWORDS.items():
        if key in combined:
            kws.extend(industry_kws)
    if name:
        kws.extend([f"{name} case study", f"{name} website"])
    # Preserve order while removing duplicates.
    return list(dict.fromkeys([kw for kw in kws if kw]))


def service_for(platform: str):
    p = (platform or "").lower()
    for key, val in SERVICE_MAP.items():
        if key in p:
            return val
    return ("/websites/", "Website Design & Development")


def title_for(item: dict) -> str:
    """SEO title: [Client] [Service] case study | Lofts Studio."""
    _, svc = service_for(item.get("platform", ""))
    name = item["name"]
    category = (item.get("category") or "").split("·")[0].strip()
    base = f"{name} {svc} Case Study"
    if category and len(f"{base} for {category} | Lofts Studio") <= 65:
        base = f"{base} for {category}"
    suffix = " | Lofts Studio"
    if len(base) + len(suffix) <= 65:
        return base + suffix
    return f"{name} Case Study | Lofts Studio"


def meta_desc_for(item: dict) -> str:
    """SEO meta description — unique per project, under 155 chars."""
    name = item["name"]
    tagline = item.get("tagline", "")
    platform = item.get("platform", "")
    category = item.get("category", "")
    _, svc = service_for(platform)
    base = f"See {name}, a Lofts Studio {svc} case study for {category}: {tagline}. Built for clarity, trust, performance, and conversion."
    return base[:155].rstrip(" ,.;:-") + ("." if len(base) > 155 else "")


def abs_url(path: str) -> str:
    if not path:
        return f"{SITE_URL}/assets/og.jpg?v=2"
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{SITE_URL}{path if path.startswith('/') else '/' + path}"


def initials_for(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", name or "")
    if not words:
        return "LS"
    if len(words) == 1:
        return words[0][:2].upper()
    return "".join(word[0] for word in words[:2]).upper()


def app_schema_type(item: dict) -> str:
    text = " ".join([
        item.get("platform", ""),
        item.get("category", ""),
        " ".join(item.get("stack") or []),
    ]).lower()
    if any(k in text for k in ["app", "saas", "crm", "ai", "lms", "platform", "automation"]):
        return "WebApplication"
    return "WebSite"


def schema_graph_for(item: dict, page_desc: str, og_image: str, kw_list: list) -> str:
    slug = item["slug"]
    name = item["name"]
    url = item.get("url") or f"{SITE_URL}/portfolio/{slug}.html"
    app_type = app_schema_type(item)
    app_node_id = f"{SITE_URL}/portfolio/{slug}.html#project"
    service_url, service_label = service_for(item.get("platform", ""))
    category = item.get("category", "")
    platform = item.get("platform", "")
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{SITE_URL}/#organization",
                "name": "Lofts Studio",
                "url": f"{SITE_URL}/",
                "logo": f"{SITE_URL}/assets/brand/logo-mark.svg",
                "sameAs": [
                    "https://www.upwork.com/freelancers/wordpressandshopifydeveloper",
                    "https://www.upwork.com/freelancers/irfankhan",
                ],
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE_URL}/#website",
                "name": "Lofts Studio",
                "url": f"{SITE_URL}/",
                "publisher": {"@id": f"{SITE_URL}/#organization"},
                "inLanguage": "en",
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{SITE_URL}/portfolio/{slug}.html#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Portfolio", "item": f"{SITE_URL}/portfolio/"},
                    {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE_URL}/portfolio/{slug}.html"},
                ],
            },
            {
                "@type": app_type,
                "@id": app_node_id,
                "name": name,
                "url": url,
                "description": f"{item.get('tagline', '')}. {item.get('summary', '')}".strip(),
            },
            {
                "@type": "Service",
                "@id": f"{SITE_URL}/portfolio/{slug}.html#service",
                "name": service_label,
                "serviceType": service_label,
                "provider": {"@id": f"{SITE_URL}/#organization"},
                "url": f"{SITE_URL}{service_url}",
                "areaServed": [
                    {"@type": "Country", "name": "United States"},
                    {"@type": "Country", "name": "United Kingdom"},
                    {"@type": "Country", "name": "Australia"},
                    {"@type": "Country", "name": "United Arab Emirates"}
                ],
                "audience": {
                    "@type": "BusinessAudience",
                    "audienceType": category or "Business websites"
                }
            },
            {
                "@type": "CreativeWork",
                "@id": f"{SITE_URL}/portfolio/{slug}.html#case-study",
                "name": f"{name} case study",
                "headline": f"{name} Case Study",
                "description": page_desc,
                "url": f"{SITE_URL}/portfolio/{slug}.html",
                "image": abs_url(og_image),
                "dateCreated": str(item.get("year", "")),
                "creator": {"@id": f"{SITE_URL}/#organization"},
                "about": {"@id": app_node_id},
                "workExample": {"@id": app_node_id},
                "provider": {"@id": f"{SITE_URL}/#organization"},
                "keywords": kw_list + [name, item.get("platform", ""), item.get("category", "")],
            },
            {
                "@type": "FAQPage",
                "@id": f"{SITE_URL}/portfolio/{slug}.html#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"What type of project was {name}?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"{name} was a {platform} project for {category}. The work focused on making the offer clearer, easier to maintain, and stronger as a public proof point."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": f"Can Lofts Studio build something similar to {name}?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Yes. Lofts Studio handles {service_label} work for serious businesses that need clearer structure, stronger conversion paths, mobile usability, and a maintainable build."
                        }
                    }
                ]
            },
            {
                "@type": "WebPage",
                "@id": f"{SITE_URL}/portfolio/{slug}.html#webpage",
                "url": f"{SITE_URL}/portfolio/{slug}.html",
                "name": title_for(item),
                "description": page_desc,
                "isPartOf": {"@id": f"{SITE_URL}/#website"},
                "publisher": {"@id": f"{SITE_URL}/#organization"},
                "breadcrumb": {"@id": f"{SITE_URL}/portfolio/{slug}.html#breadcrumb"},
                "mainEntity": {"@id": f"{SITE_URL}/portfolio/{slug}.html#case-study"},
                "hasPart": [
                    {"@id": f"{SITE_URL}/portfolio/{slug}.html#faq"},
                    {"@id": f"{SITE_URL}/portfolio/{slug}.html#service"}
                ],
                "primaryImageOfPage": abs_url(og_image),
                "significantLink": [
                    f"{SITE_URL}/portfolio/",
                    f"{SITE_URL}{service_for(item.get('platform', ''))[0]}",
                    f"{SITE_URL}/free-audit/",
                    f"{SITE_URL}/#contact",
                ],
                "inLanguage": "en",
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False, indent=2)


def case_context_for(item: dict) -> dict:
    """Return cautious, non-invented narrative details for a case study."""
    platform = (item.get("platform") or "").lower()
    category = (item.get("category") or "").lower()
    stack = " ".join(item.get("stack") or []).lower()
    text = f"{platform} {category} {stack}"

    if any(k in text for k in ["finance", "insurance", "investment", "reinsurance"]):
        return {
            "market": "regulated, trust-heavy buying journey",
            "buyer": "visitors need clarity, credibility, and a reason to keep moving before they enquire",
            "priorities": [
                "Make the first screen explain the offer without forcing the visitor to decode industry language.",
                "Keep proof, team credibility, and next-step paths close to the moments where doubt appears.",
                "Build pages so future compliance, copy, and market updates can be made without redesigning the site.",
            ],
            "seo": "For finance and insurance projects, search visibility depends on clean crawl paths, careful metadata, entity clarity, and pages that answer the real questions a cautious buyer asks before making contact.",
        }
    if any(k in text for k in ["b2b", "wholesale", "enterprise", "supplier"]):
        return {
            "market": "B2B buying journey with longer consideration and multiple stakeholders",
            "buyer": "buyers need to understand the offer, qualify themselves, and trust the operation before they start a conversation",
            "priorities": [
                "Separate casual browsing from serious buyer intent with clear navigation and purposeful calls to action.",
                "Give product, service, or capability pages enough context to support internal stakeholder sharing.",
                "Keep the platform maintainable so the sales team can adjust messaging as the market changes.",
            ],
            "seo": "For B2B projects, the SEO opportunity is usually not one generic keyword; it is a cluster of service, category, industry, and problem-aware searches that need clear internal linking.",
        }
    if any(k in text for k in ["shopify", "woocommerce", "ecommerce", "dtc", "store", "retail"]):
        return {
            "market": "commerce journey where speed, trust, merchandising, and checkout confidence all matter",
            "buyer": "customers need to understand the product quickly, believe the store is reliable, and reach purchase paths without friction",
            "priorities": [
                "Keep product discovery, trust signals, and buying actions visible without making the page feel crowded.",
                "Protect performance by keeping images, scripts, and app dependencies under control.",
                "Structure templates so new products, campaigns, and landing pages can be added without weakening the system.",
            ],
            "seo": "For ecommerce projects, organic growth depends on collection architecture, product metadata, internal links, structured data, image performance, and pages that match the way customers compare before buying.",
        }
    if any(k in text for k in ["app", "saas", "ai", "lms", "platform", "membership", "portal"]):
        return {
            "market": "product-led or platform journey where the interface has to explain value fast",
            "buyer": "users need to see what the product does, why it is trustworthy, and what step to take next",
            "priorities": [
                "Turn the product story into a page structure that makes the use case obvious within seconds.",
                "Balance marketing pages with product-like clarity, screenshots, flows, and clear next actions.",
                "Keep the technical foundation flexible enough for new features, onboarding changes, and analytics.",
            ],
            "seo": "For SaaS and app projects, the strongest search pages usually combine use-case language, comparison intent, integration terms, and clear product proof rather than broad feature claims.",
        }
    if any(k in text for k in ["agency", "brand", "marketing", "editorial", "portfolio"]):
        return {
            "market": "brand-led journey where taste, proof, and clarity have to work together",
            "buyer": "visitors need to understand the positioning, see proof of standard, and feel an obvious next step",
            "priorities": [
                "Make the visual system feel distinctive without hiding the practical offer.",
                "Use hierarchy, typography, and project proof to make the page easier to scan.",
                "Keep content blocks flexible so new campaigns, services, and proof can be added cleanly.",
            ],
            "seo": "For brand-led projects, search performance improves when the site names the offer clearly, supports it with project proof, and gives search engines structured context around services and expertise.",
        }
    return {
        "market": "service journey where the site has to make the offer credible quickly",
        "buyer": "visitors need to understand what is being offered, why it is reliable, and how to take the next step",
        "priorities": [
            "Clarify the first screen so the visitor understands the offer before they scroll.",
            "Support the page with proof, structure, and a path to enquire without unnecessary friction.",
            "Keep the site maintainable so future edits do not require a full rebuild.",
        ],
        "seo": "For service projects, the strongest organic pages connect the service, audience, proof, location or category context, and next step in a way both people and search engines can understand.",
    }


def render_case_depth(item: dict, service_url: str, service_label: str, kw_str: str) -> str:
    ctx = case_context_for(item)
    name = item["name"]
    platform = item.get("platform", "")
    category = item.get("category", "")
    priority_items = "\n".join(
        f'<li style="margin-bottom:0.75rem;">{point}</li>' for point in ctx["priorities"]
    )
    return f'''<section class="section-sm" style="padding:5rem 0;border-top:1px solid var(--line);">
  <div class="container">
    <div data-reveal class="case-depth-grid">
      <div>
        <span class="eyebrow">Project notes</span>
        <h2 class="h-2" style="margin:1rem 0 0;">What had to work for {name}</h2>
      </div>
      <div>
        <p style="font-family:var(--font-serif);font-size:1.12rem;line-height:1.75;color:var(--ink);margin:0 0 1.5rem;">
          {name} sits in a {ctx["market"]}. The page experience had to help {ctx["buyer"]}. That meant treating the build as more than a visual refresh: the structure, copy hierarchy, technical setup, and handoff all had to support the same commercial job.
        </p>
        <div class="case-depth-cards">
          <div class="card" style="padding:1.25rem;">
            <p style="font-family:var(--font-sans);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--muted);margin:0 0 0.8rem;">Build priorities</p>
            <ul style="font-family:var(--font-serif);color:var(--ink-soft);line-height:1.65;margin:0;padding-left:1.1rem;">{priority_items}</ul>
          </div>
          <div class="card" style="padding:1.25rem;">
            <p style="font-family:var(--font-sans);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--muted);margin:0 0 0.8rem;">SEO &amp; conversion notes</p>
            <p style="font-family:var(--font-serif);color:var(--ink-soft);line-height:1.7;margin:0;">{ctx["seo"]}</p>
            <p style="font-family:var(--font-serif);color:var(--ink-soft);line-height:1.7;margin:1rem 0 0;">Relevant search context includes {kw_str}. The goal is not keyword stuffing; it is making the project, platform, audience, and outcome legible.</p>
          </div>
        </div>
        <p style="font-family:var(--font-serif);font-size:1.04rem;line-height:1.75;color:var(--ink-soft);margin:0;">
          If you are planning a similar {platform} project in {category}, the useful starting point is a clear page map, a proof-led first screen, fast mobile performance, and a maintainable CMS or theme setup. The related service page for this type of work is <a href="{service_url}" style="color:var(--ink);text-decoration:underline;text-underline-offset:4px;">{service_label}</a>.
        </p>
      </div>
    </div>
  </div>
</section>

<section class="section-sm" style="padding:4rem 0;background:var(--bg-soft);border-top:1px solid var(--line);">
  <div class="container-narrow" data-reveal>
    <span class="eyebrow">Case study FAQ</span>
    <div style="margin-top:1.5rem;display:grid;gap:0.8rem;">
      <details class="faq"><summary>What type of project was {name}? <span class="plus">+</span></summary><div class="faq-body">{name} was a {platform} project for {category}. The work focused on making the offer clearer, easier to maintain, and stronger as a public proof point.</div></details>
      <details class="faq"><summary>What mattered most in the build? <span class="plus">+</span></summary><div class="faq-body">The important parts were clarity, mobile usability, performance discipline, and a structure the client could keep improving after launch.</div></details>
      <details class="faq"><summary>Can Lofts Studio build something similar? <span class="plus">+</span></summary><div class="faq-body">Yes. Start with the related {service_label} page or send the current URL through the homepage form so the first reply can include practical next steps.</div></details>
    </div>
  </div>
</section>'''


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
    kws        = keywords_for(item)
    kw_str     = ", ".join(kws)

    # ── Screenshot / wordmark block ───────────────────────────────────────────
    if image and not item.get("hideScreenshot"):
        url_display = url.replace("https://", "").replace("http://", "")
        image_html = f'''<section class="section-sm" style="padding:1rem 0 5rem;">
  <div class="container" data-reveal>
    <div style="border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--bg-soft);">
      <a href="{url}" target="_blank" rel="noopener" aria-label="Visit {name} live site">
        <img src="{image}" alt="{name} homepage screenshot — {platform} project by Lofts Studio" loading="lazy" decoding="async" style="display:block;width:100%;height:auto;" />
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

    og_image = image if image else "/assets/og.jpg?v=2"

    schema_graph = schema_graph_for(item, page_desc, og_image, kws)
    case_depth = render_case_depth(item, service_url, service_label, kw_str)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{GTM_HEAD}
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{page_title}</title>
<meta name="description" content="{page_desc}" />
<link rel="canonical" href="{SITE_URL}/portfolio/{slug}.html" />
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1" />

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
<link rel="alternate icon" href="/favicon.svg" />
<link rel="icon" type="image/png" href="/apple-touch-icon.png" />
<link rel="apple-touch-icon" href="/favicon.svg" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />
<link rel="stylesheet" href="/assets/experience.css?v=20260731c" data-lofts-experience />

<script type="application/ld+json">
{schema_graph}
</script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1KT1MFDY8R"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-1KT1MFDY8R');</script>
  <script>(function(){{try{{var m=localStorage.getItem('lofts-theme')||'device';var d=m==='dark'||(m==='device'&&window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches);document.documentElement.setAttribute('data-theme',d?'dark':'light');}}catch(e){{}}}})();</script>
</head>
<body>
{GTM_BODY}

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
      <div style="margin-top:1.4rem;border:1px solid var(--line);border-radius:var(--r-md);padding:1rem 1.15rem;max-width:720px;background:var(--surface);">
        <p style="font-family:var(--font-sans);font-size:0.72rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--muted);margin:0 0 0.45rem;">Quick answer</p>
        <p style="font-family:var(--font-serif);font-size:1.02rem;line-height:1.6;color:var(--ink-soft);margin:0;">Lofts Studio used {platform} web development for {name} to support a {category} experience with clearer structure, maintainable templates, and a direct path from visitor attention to enquiry or purchase.</p>
      </div>
      <div style="margin-top:2rem;display:flex;gap:0.75rem;flex-wrap:wrap;">
        {f'<a href="{url}" target="_blank" rel="noopener" class="btn btn-primary">Visit live site &nbsp;&rarr;</a>' if url else ''}
        <a href="/free-audit/" class="btn btn-ghost">Audit a similar site</a>
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

{case_depth}

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
        <span style="font-family:var(--font-sans);font-size:0.68rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.2em;font-weight:600;">Get in touch</span>
        <h3 class="h-2" style="margin:0;">Want something like {name} for your store?</h3>
        <p style="font-family:var(--font-serif);color:var(--ink-soft);margin:0;line-height:1.6;">Send a URL and what you&rsquo;d change. Four-hour reply with three specific suggestions, whether you hire me or not.</p>
        <span class="btn-editorial" style="align-self:flex-start;margin-top:0.5rem;">Open the form &nbsp;&rarr;</span>
      </a>
      <a href="{service_url}" class="card" style="text-decoration:none;display:flex;flex-direction:column;gap:0.85rem;">
        <span style="font-family:var(--font-sans);font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.2em;font-weight:600;">Related service</span>
        <h3 class="h-2" style="margin:0;">Read about {service_label}</h3>
        <p style="font-family:var(--font-serif);color:var(--ink-soft);margin:0;line-height:1.6;">How a {service_label} engagement actually moves through this studio — scope, timeline, deliverables, handoff.</p>
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
  .case-depth-grid {{ display:grid;grid-template-columns:0.72fr 1.8fr;gap:4rem;max-width:1080px;margin:0 auto; }}
  .case-depth-cards {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.25rem;margin:2rem 0; }}
  @media (max-width:880px) {{
    .case-brief {{ grid-template-columns:1fr;gap:1.5rem; }}
    .case-depth-grid {{ grid-template-columns:1fr;gap:1.75rem; }}
    .case-depth-cards {{ grid-template-columns:1fr; }}
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
            category_parts = [part.strip() for part in item.get("category", "").split("·") if part.strip()]
            place = " / ".join(category_parts[:2]) or item.get("platform", "") or "Live engagement"
            tone = "studio"
            combined = f'{item.get("category", "")} {item.get("tagline", "")} {item.get("platform", "")}'.lower()
            if any(k in combined for k in ["insurance", "finance", "investment", "research"]):
                tone = "finance"
            elif any(k in combined for k in ["shopify", "woocommerce", "dtc", "store", "ecommerce"]):
                tone = "commerce"
            elif any(k in combined for k in ["health", "clinic", "directory", "auto"]):
                tone = "care"
            elif any(k in combined for k in ["contractor", "industrial", "architecture", "construction"]):
                tone = "field"
            elif any(k in combined for k in ["agency", "brand", "marketing"]):
                tone = "brand"
            initials = initials_for(item["name"])
            designed_name = escape(item["name"])
            designed_place = escape(place)
            designed_meta = escape(f'{item.get("platform", "")} / {item.get("year", "")}')
            img_html = f'''<div class="work-card-designed" data-tone="{tone}" data-initials="{initials}">
              <span class="work-card-designed-kicker">Portfolio preview</span>
              <span class="work-card-designed-name">{designed_name}</span>
              <span class="work-card-designed-place">{designed_place}</span>
              <span class="work-card-designed-meta">{designed_meta}</span>
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
{GTM_HEAD}
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Portfolio — Web, Shopify & App Case Studies | Lofts Studio</title>
<meta name="description" content="A curated public archive from Lofts Studio: selected shipped work across Shopify, WooCommerce, WordPress, custom apps, B2B platforms, marketplaces, and performance rebuilds." />
<link rel="canonical" href="{SITE_URL}/portfolio/" />
<meta name="robots" content="index,follow" />
<meta property="og:type" content="website" />
<meta property="og:title" content="Portfolio — Web, Shopify & App Case Studies | Lofts Studio" />
<meta property="og:description" content="A curated public archive from Lofts Studio: selected shipped work across Shopify, WooCommerce, WordPress, custom apps, B2B platforms, marketplaces, and performance rebuilds." />
<meta property="og:url" content="{SITE_URL}/portfolio/" />
<meta property="og:image" content="{SITE_URL}/assets/og.jpg?v=2" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="alternate icon" href="/favicon.svg" />
<link rel="icon" type="image/png" href="/apple-touch-icon.png" />
<link rel="apple-touch-icon" href="/favicon.svg" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />
<link rel="stylesheet" href="/assets/experience.css?v=20260731c" data-lofts-experience />

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Lofts Studio Portfolio",
  "description": "A collection of Lofts Studio case studies across Shopify, WooCommerce, WordPress, custom apps, B2B platforms, marketplaces, and performance rebuilds.",
  "url": "{SITE_URL}/portfolio/",
  "mainEntity": {{
    "@type": "ItemList",
    "itemListElement": [
{schema_str}
    ]
  }}
}}
</script>
</head>
<body class="portfolio-page">
{GTM_BODY}

{nav}

<section class="paper" style="padding:7rem 0 4rem;">
  <div class="container">
    <div data-reveal style="max-width:940px;">
      <span class="eyebrow">Selected work &nbsp;&middot;&nbsp; 2011&ndash;present</span>
      <h1 class="h-display" data-split="words" style="margin-top:1.5rem;">
        A curated public archive. <span class="italic-serif">Every project here launched.</span>
      </h1>
      <p class="lead" style="margin-top:2rem;">
        This is the work I can show publicly, not the full body of work. Across 1,500+ projects handled for a much larger client base, the pattern is simple: clear scope, senior execution, shipped sites that survive real traffic.
      </p>
      <div class="hero-stats">
        <div class="hero-stat"><div class="bignum">1,500<span class="bignum-suffix">+</span></div><div class="hero-stat-lbl">Projects handled</div></div>
        <div class="hero-stat"><div class="bignum">15<span class="bignum-suffix">&nbsp;yrs</span></div><div class="hero-stat-lbl">Client work</div></div>
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

      <span style="margin-left:auto;font-family:var(--font-sans);font-size:0.72rem;color:var(--muted);" id="filterCount"></span>
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
        <p>Every one of these projects had a faster path: pick a off-the-shelf theme, hire whoever&rsquo;s cheapest, ship in a fortnight. These founders didn&rsquo;t take it. They wanted the build to survive a year of changes, an investor due-diligence read, a Black Friday spike, and the day someone else has to come in and edit the codebase.</p>
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
    countEl.textContent = '';

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
  /* Mobile: compact, even-height 2-up portfolio cards */
  @media (max-width: 640px) {{
    /* Filter bar was sticky and covered the page on scroll — let it scroll away */
    .pf-filter-bar {{ position: static !important; }}
    .pf-filter-bar .container {{ padding-top: 0.6rem !important; padding-bottom: 0.6rem !important; }}
    .filter-btn {{ padding: 0.32rem 0.7rem; font-size: 0.64rem; letter-spacing: 0.08em; }}

    /* Two-up grid — cards size to their content so short cards don't stretch into voids */
    #workGrid.work-grid {{ grid-template-columns: repeat(2, 1fr); gap: 1rem 0.7rem; align-items: start; }}
    .work-card-body {{ padding: 0.8rem 0.8rem 0.95rem; }}
    .work-card-meta {{ font-size: 0.58rem; letter-spacing: 0.05em; line-height: 1.35; }}
    .work-card-name {{ font-size: 0.98rem !important; margin-top: 0.15rem; }}
    .work-card-tag {{
      font-size: 0.8rem !important; line-height: 1.4 !important; margin-top: 0.3rem;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
    }}
    /* Show only the Case study link on mobile — the raw URL truncated awkwardly */
    .work-card-live {{ display: none; }}
    .work-card-actions {{ margin-top: 0.7rem; padding-top: 0.65rem; flex-direction: row; align-items: center; gap: 0.5rem; }}
    .work-card-cs {{ font-size: 0.78rem; }}
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
