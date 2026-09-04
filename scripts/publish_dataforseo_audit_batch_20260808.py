#!/usr/bin/env python3
"""
Publish the 2026-08-08 Lofts Studio DataForSEO audit-report batch.

Research basis:
- DataForSEO trial-safe report, 2026-08-07, seed: site audit report.
- Search intent: site audit report, SEO site audit report, on-site audit report,
  site audit report format, free site audit report, content audit, audit checklist.
- Competitor pattern: audit tools and free report generators win the SERP, so
  Lofts Studio should answer the query and route visitors into a human review,
  free-audit flow, technical SEO audit service, and conversion-focused rebuild path.
"""

import html
import importlib.util
import json
import re
import textwrap
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog"
ASSET_DIR = ROOT / "assets" / "blog"
POSTS_JSON = BLOG_DIR / "posts.json"
SITE = "https://lofts.studio"
DATE = "2026-08-08"
CACHE_VER = "20260808-audit"


POSTS = [
    {
        "slug": "seo-site-audit-report-for-lead-generation",
        "title": "SEO Site Audit Report for Lead Generation Websites",
        "primary": "SEO site audit report",
        "secondary": "site audit report for leads",
        "intent": "service business owners who need search traffic to turn into qualified inquiries",
        "angle": "Tie every technical finding to a page, a search intent, and a lead route before adding more content.",
    },
    {
        "slug": "site-audit-report-format-service-business",
        "title": "Site Audit Report Format for Service Businesses",
        "primary": "site audit report format",
        "secondary": "service website audit report",
        "intent": "teams comparing report formats before choosing who should fix the website",
        "angle": "Use a compact format that separates crawl issues, content gaps, UX friction, and next actions.",
    },
    {
        "slug": "on-site-audit-report-business-websites",
        "title": "On-Site Audit Report for Business Websites",
        "primary": "on site audit report",
        "secondary": "business website audit",
        "intent": "owners who suspect the website itself is blocking visibility or leads",
        "angle": "Review the live page experience, not only crawler output, so the report can lead to implementation.",
    },
    {
        "slug": "site-seo-audit-report-before-redesign",
        "title": "Site SEO Audit Report Before a Website Redesign",
        "primary": "site SEO audit report",
        "secondary": "website redesign SEO audit",
        "intent": "founders planning a redesign and worried about losing rankings or leads",
        "angle": "Audit the old site before rebuild work starts so redirects, canonicals, content value, and lead pages are protected.",
    },
    {
        "slug": "free-site-audit-report-vs-human-review",
        "title": "Free Site Audit Report vs Human Review",
        "primary": "free site audit report",
        "secondary": "human website audit review",
        "intent": "visitors using free audit tools but unsure which findings matter",
        "angle": "A free report finds symptoms; a human review decides which issues affect search, trust, and leads first.",
    },
    {
        "slug": "content-audit-for-service-business-websites",
        "title": "Content Audit for Service Business Websites",
        "primary": "content audit",
        "secondary": "service website content audit",
        "intent": "businesses with many pages but weak rankings, unclear messaging, or poor lead quality",
        "angle": "Map each page to intent, proof, internal links, schema, and a conversion path before writing more.",
    },
    {
        "slug": "audit-checklist-for-website-redesign",
        "title": "Audit Checklist Before a Website Redesign",
        "primary": "audit checklist",
        "secondary": "website redesign checklist",
        "intent": "teams that need a practical pre-redesign checklist",
        "angle": "Protect what already works, repair indexability, and define the lead path before changing layouts.",
    },
    {
        "slug": "technical-audit-report-for-service-pages",
        "title": "Technical Audit Report for Service Pages",
        "primary": "technical audit report",
        "secondary": "service page technical SEO audit",
        "intent": "operators checking whether service pages are crawlable, indexable, and schema-safe",
        "angle": "Service-page audits should combine technical status with answer clarity and trust signals.",
    },
    {
        "slug": "landing-page-audit-report-for-leads",
        "title": "Landing Page Audit Report for Better Leads",
        "primary": "landing page audit report",
        "secondary": "lead generation landing page audit",
        "intent": "marketers trying to understand why landing pages receive visits but few qualified inquiries",
        "angle": "Audit query fit, first-screen clarity, proof, CTA friction, and follow-up path as one funnel.",
    },
    {
        "slug": "gsc-indexing-audit-report",
        "title": "GSC Indexing Audit Report for Service Websites",
        "primary": "GSC indexing audit report",
        "secondary": "Google Search Console indexing issues",
        "intent": "site owners seeing redirect, duplicate canonical, or discovered-not-indexed warnings",
        "angle": "Classify each GSC issue as fix, expected, or monitor before asking Google to validate anything.",
    },
    {
        "slug": "canonical-redirect-audit-report",
        "title": "Canonical and Redirect Audit Report",
        "primary": "canonical redirect audit",
        "secondary": "page with redirect duplicate canonical",
        "intent": "teams trying to clean up duplicate URLs, redirect paths, and canonical confusion",
        "angle": "Keep only intentional redirects and canonicals; repair any valuable page that Google cannot index.",
    },
    {
        "slug": "service-website-schema-audit-report",
        "title": "Service Website Schema Audit Report",
        "primary": "schema audit report",
        "secondary": "service website schema",
        "intent": "businesses trying to earn rich-result eligibility without fake schema claims",
        "angle": "Schema should mirror visible content, support breadcrumbs and FAQs, and never invent ratings or locations.",
    },
    {
        "slug": "website-audit-report-executive-summary",
        "title": "Website Audit Report Executive Summary",
        "primary": "website audit report executive summary",
        "secondary": "audit report summary",
        "intent": "decision makers who need a short useful summary before approving implementation work",
        "angle": "Summarize the few fixes that protect traffic, improve search appearance, and create more inquiries.",
    },
    {
        "slug": "website-audit-priority-scorecard",
        "title": "Website Audit Priority Scorecard",
        "primary": "website audit scorecard",
        "secondary": "audit priority scorecard",
        "intent": "teams that need to choose which website fixes matter first",
        "angle": "Score by indexability, traffic potential, business value, implementation effort, and conversion impact.",
    },
    {
        "slug": "website-audit-report-action-plan",
        "title": "Website Audit Report Action Plan",
        "primary": "website audit action plan",
        "secondary": "site audit next steps",
        "intent": "owners who have an audit but need a sequence for repairs and publishing",
        "angle": "A report is only useful when it becomes a dated implementation plan with owners, QA, and live checks.",
    },
    {
        "slug": "site-audit-report-for-ai-search",
        "title": "Site Audit Report for AI Search Visibility",
        "primary": "site audit report for AI search",
        "secondary": "AEO GEO website audit",
        "intent": "businesses that want their service pages to be clearer for AI answers and Google AI Overviews",
        "angle": "Audit direct answers, entity co-occurrence, visible proof, schema, and internal links together.",
    },
    {
        "slug": "local-service-website-audit-report",
        "title": "Local Service Website Audit Report",
        "primary": "local service website audit",
        "secondary": "local business website audit report",
        "intent": "local service businesses that need cleaner pages before investing in local SEO content",
        "angle": "Validate service-area architecture, unique local value, contact path, and indexability without fake locations.",
    },
    {
        "slug": "ecommerce-service-page-audit-report",
        "title": "Ecommerce Service Page Audit Report",
        "primary": "ecommerce service page audit",
        "secondary": "Shopify service page audit",
        "intent": "ecommerce teams evaluating developer, optimization, or migration service pages",
        "angle": "Audit speed, proof, migration safety, collection/product paths, and service conversion together.",
    },
    {
        "slug": "portfolio-page-audit-for-web-design-leads",
        "title": "Portfolio Page Audit for Web Design Leads",
        "primary": "portfolio page audit",
        "secondary": "web design portfolio conversion audit",
        "intent": "studios and agencies using portfolio pages to win web design leads",
        "angle": "Portfolio pages need context, outcomes, proof, next steps, and internal links into the right service path.",
    },
    {
        "slug": "website-audit-report-qa-before-launch",
        "title": "Website Audit Report QA Before Launch",
        "primary": "website audit report QA",
        "secondary": "pre-launch website QA checklist",
        "intent": "teams preparing to publish new pages, posts, or redesign work",
        "angle": "Run live QA for mobile layout, canonical, schema, sitemap inclusion, forms, and lead routes before requesting indexing.",
    },
]


VISUALS = [
    ("/assets/blog/lofts-aeo-answer-map.svg", "Direct answer, evidence, schema, and lead CTA map for a service website"),
    ("/assets/blog/lofts-gsc-to-lead-funnel.svg", "Flow from Search Console clicks into audits, consultations, and inquiries"),
    ("/assets/blog/lofts-internal-link-graph.svg", "Internal link graph connecting blog guides to service and audit pages"),
    ("/assets/blog/lofts-authority-loop.svg", "Authority loop connecting useful assets, citations, and service trust")
]


def esc(value):
    return html.escape(str(value), quote=True)


def load_nav_and_footer():
    source = (ROOT / "index.html").read_text()
    nav = re.search(r'<header class="nav-bar">.*?</header>', source, re.DOTALL).group(0)
    footer = re.search(r'<footer class="site-footer.*?</footer>', source, re.DOTALL).group(0)
    return nav, footer


def post_url(post):
    return f"{SITE}/blog/{post['slug']}.html"


def faq_schema(post):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"What should a {post['primary']} include?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "It should include indexability, search intent, page structure, content gaps, internal links, schema, mobile UX, proof, and the next lead action for each important page."
                }
            },
            {
                "@type": "Question",
                "name": "How does Lofts Studio turn an audit into more leads?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Lofts Studio connects the audit findings to landing pages, service pages, technical fixes, calls to action, and live QA so search attention can become qualified inquiries."
                }
            },
            {
                "@type": "Question",
                "name": "Should every audit finding be fixed immediately?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "No. Fixes should be prioritized by indexability risk, traffic opportunity, conversion impact, implementation effort, and whether the page supports a real business outcome."
                }
            }
        ]
    }


def render_post(post, nav, footer):
    title = post["title"]
    description = f"{title}: a practical Lofts Studio guide for turning audit findings into search visibility, better landing pages, and qualified lead paths."
    visuals = "\n".join(
        f'''          <figure>
            <img src="{src}" alt="{esc(alt)}" width="1200" height="675" loading="lazy" />
            <figcaption>{esc(alt)}</figcaption>
          </figure>'''
        for src, alt in VISUALS
    )
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "image": f"{SITE}/assets/blog/{post['slug']}.png",
        "datePublished": f"{DATE}T09:00:00Z",
        "dateModified": f"{DATE}T09:00:00Z",
        "author": {"@type": "Person", "name": "Adnan K.", "url": f"{SITE}/about.html"},
        "publisher": {"@type": "Organization", "name": "Lofts Studio", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.svg"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": post_url(post)},
        "keywords": f"{post['primary']}, {post['secondary']}, site audit report, service business SEO"
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": post_url(post)}
        ]
    }
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<script data-lofts-theme-init>(function(){{var m="light";try{{m=localStorage.getItem("lofts-theme")==="dark"?"dark":"light"}}catch(e){{}}document.documentElement.dataset.theme=m;document.documentElement.style.colorScheme=m}}())</script>
<title>{esc(title)} | Lofts Studio</title>
<meta name="description" content="{esc(description)}" />
<link rel="canonical" href="{post_url(post)}" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="author" content="Adnan K." />
<meta property="og:type" content="article" />
<meta property="og:url" content="{post_url(post)}" />
<meta property="og:title" content="{esc(title)} | Lofts Studio" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:image" content="{SITE}/assets/blog/{post['slug']}.png" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="stylesheet" href="/assets/styles.css?v=20260801j" />
<link rel="stylesheet" href="/assets/experience.css?v=20260801g" data-lofts-experience />
<link rel="stylesheet" href="/assets/typography.css" />
<script type="application/ld+json">{json.dumps(article_schema, separators=(",", ":"))}</script>
<script type="application/ld+json">{json.dumps(breadcrumb_schema, separators=(",", ":"))}</script>
<script type="application/ld+json">{json.dumps(faq_schema(post), separators=(",", ":"))}</script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1KT1MFDY8R"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-1KT1MFDY8R');
  </script>
<style>
  .audit-post {{ background: var(--bg); color: var(--ink); }}
  .audit-shell {{ max-width: 1120px; margin: 0 auto; padding: clamp(3.5rem, 7vw, 6rem) 1.25rem; }}
  .audit-hero {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, 420px); gap: clamp(1.5rem, 5vw, 4rem); align-items: end; padding-bottom: 2rem; border-bottom: 1px solid var(--line); }}
  .audit-kicker {{ margin: 0 0 1rem; color: var(--muted); font: 700 .74rem/1.4 var(--font-mono); letter-spacing: .14em; text-transform: uppercase; }}
  .audit-hero h1 {{ max-width: 14ch; margin: 0; font-family: var(--font-display); font-size: clamp(2.6rem, 6vw, 5.2rem); font-weight: 500; line-height: .98; letter-spacing: 0; text-wrap: balance; }}
  .audit-lead {{ margin: 1.35rem 0 0; color: var(--ink-soft); font-size: clamp(1.06rem, 2vw, 1.28rem); line-height: 1.68; }}
  .audit-answer {{ padding: 1.25rem; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); box-shadow: var(--shadow-card); }}
  .audit-answer h2 {{ margin: 0 0 .7rem; font: 500 clamp(1.3rem, 2.3vw, 1.8rem)/1.12 var(--font-display); }}
  .audit-answer p {{ margin: 0; color: var(--ink-soft); line-height: 1.65; }}
  .audit-cta-row {{ display: flex; flex-wrap: wrap; gap: .75rem; margin-top: 1rem; }}
  .audit-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: clamp(1.25rem, 4vw, 2rem); margin-top: 3rem; }}
  .audit-card {{ padding: clamp(1.1rem, 3vw, 1.5rem); border: 1px solid var(--line); border-radius: 6px; background: color-mix(in srgb, var(--surface) 84%, transparent); }}
  .audit-card h2, .audit-card h3 {{ margin: 0 0 .8rem; font: 500 clamp(1.35rem, 2.5vw, 2rem)/1.15 var(--font-display); }}
  .audit-card p, .audit-card li {{ color: var(--ink-soft); line-height: 1.72; }}
  .audit-card ul, .audit-card ol {{ margin: 0; padding-left: 1.2rem; }}
  .audit-visuals {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 3rem; }}
  .audit-visuals figure {{ margin: 0; }}
  .audit-visuals img {{ width: 100%; height: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }}
  .audit-visuals figcaption {{ margin-top: .55rem; color: var(--muted); font: 700 .72rem/1.35 var(--font-mono); letter-spacing: .08em; text-transform: uppercase; }}
  .audit-table {{ width: 100%; border-collapse: collapse; font-size: .96rem; }}
  .audit-table th, .audit-table td {{ padding: .85rem; border-bottom: 1px solid var(--line); color: var(--ink-soft); text-align: left; vertical-align: top; }}
  .audit-table th {{ color: var(--ink); background: var(--bg-soft); }}
  .audit-final {{ margin-top: 3rem; padding: clamp(1.25rem, 3vw, 2rem); border-radius: 6px; background: var(--ink); color: var(--bg); }}
  .audit-final h2, .audit-final p {{ color: inherit; }}
  @media (max-width: 860px) {{
    .audit-hero, .audit-grid, .audit-visuals {{ grid-template-columns: 1fr; }}
    .audit-hero h1 {{ max-width: 13ch; font-size: clamp(2.35rem, 13vw, 3.9rem); }}
  }}
</style>
</head>
<body class="audit-post">
<a class="skip-link" href="#main-content">Skip to main content</a>
{nav}
<main id="main-content" tabindex="-1">
  <article class="audit-shell">
    <section class="audit-hero">
      <div>
        <p class="audit-kicker">DataForSEO audit report cluster</p>
        <h1>{esc(title)}</h1>
        <p class="audit-lead">{esc(post['intent'].capitalize())}. This guide explains how Lofts Studio turns that search intent into a practical audit, implementation order, and lead-focused page path.</p>
      </div>
      <aside class="audit-answer">
        <h2>Quick answer</h2>
        <p>{esc(post['angle'])} A useful {esc(post['primary'])} should tell the owner what is broken, why it matters, what to fix first, and which page should produce the next inquiry.</p>
        <div class="audit-cta-row">
          <a class="btn btn-primary" href="/free-audit">Start audit</a>
          <a class="btn btn-secondary" href="/services/technical-seo-audit.html">Technical SEO audit</a>
        </div>
      </aside>
    </section>

    <section class="audit-grid">
      <div class="audit-card">
        <h2>What the report should decide</h2>
        <p>The audit should decide whether the page needs a technical fix, a content rewrite, a stronger first screen, a better proof section, an internal-link upgrade, or a new landing path. Tool output is useful, but the decision has to be tied to business value.</p>
        <ul>
          <li>Can Google crawl and index the intended URL?</li>
          <li>Does the page answer the query directly near the top?</li>
          <li>Is the next action clear on mobile?</li>
          <li>Does schema match visible content?</li>
          <li>Are related service, portfolio, and audit pages linked?</li>
        </ul>
      </div>
      <div class="audit-card">
        <h2>Competitor gap</h2>
        <p>DataForSEO showed audit tools, checklist pages, and free report generators dominating the query family. Lofts Studio can compete by explaining what automated tools miss: prioritization, redesign risk, conversion friction, service-page depth, and implementation QA.</p>
        <p>The page should not chase volume alone. It should help a serious visitor understand the audit, trust the process, and start with the free audit or technical SEO service path.</p>
      </div>
    </section>

    <section class="audit-visuals" aria-label="Audit visuals">
{visuals}
    </section>

    <section class="audit-grid">
      <div class="audit-card">
        <h2>Audit table</h2>
        <table class="audit-table">
          <thead><tr><th>Area</th><th>Question</th><th>Lead-focused action</th></tr></thead>
          <tbody>
            <tr><td>Indexing</td><td>Is the intended URL indexable?</td><td>Repair noindex, canonical, redirect, or sitemap issues.</td></tr>
            <tr><td>Answer clarity</td><td>Can the visitor understand the offer quickly?</td><td>Add a short answer, examples, and stronger headings.</td></tr>
            <tr><td>Trust</td><td>Does the page prove Lofts can do the work?</td><td>Link portfolio, process, founder context, and relevant services.</td></tr>
            <tr><td>Conversion</td><td>Is the next step obvious?</td><td>Route to the audit, contact form, WhatsApp, or service page.</td></tr>
          </tbody>
        </table>
      </div>
      <div class="audit-card">
        <h2>Implementation order</h2>
        <ol>
          <li>Check GSC indexing, redirects, canonicals, sitemap, and top pages.</li>
          <li>Match each query family to an existing page or a new support page.</li>
          <li>Add AI-friendly direct answers, FAQs, and truthful schema.</li>
          <li>Improve the landing page CTA and internal links.</li>
          <li>Deploy, live-check, record the URL, then request indexing when available.</li>
        </ol>
      </div>
    </section>

    <section class="audit-grid">
      <div class="audit-card">
        <h2>Related Lofts paths</h2>
        <ul>
          <li><a href="/free-audit">Free website audit report</a></li>
          <li><a href="/services/technical-seo-audit.html">Technical SEO audit service</a></li>
          <li><a href="/services/conversion-rate-optimization.html">Conversion rate optimization</a></li>
          <li><a href="/blog/service-website-serp-appearance-checklist.html">SERP appearance checklist</a></li>
          <li><a href="/tools/seo-aeo-checker.html">SEO/AEO checker</a></li>
        </ul>
      </div>
      <div class="audit-card">
        <h2>FAQ</h2>
        <h3>What should a {esc(post['primary'])} include?</h3>
        <p>It should include indexability, intent fit, technical blockers, schema, content gaps, internal links, mobile UX, proof, and the next lead action.</p>
        <h3>How should fixes be prioritized?</h3>
        <p>Prioritize by search impact, lead impact, implementation effort, and production risk. Fix crawl and conversion blockers before writing unrelated content.</p>
      </div>
    </section>

    <section class="audit-final">
      <h2>Want this applied to your website?</h2>
      <p>Lofts Studio can turn the audit into a practical implementation sprint: technical fixes, service-page updates, search appearance cleanup, and conversion paths designed to create qualified inquiries.</p>
      <a class="btn btn-primary" href="/free-audit">Start with a free audit</a>
    </section>
  </article>
</main>
{footer}
<script src="/assets/main.js?v=20260801j" defer></script>
<script src="/assets/widgets.js?v=20260801j" defer></script>
</body>
</html>
'''


def update_posts_json():
    data = json.loads(POSTS_JSON.read_text())
    existing = {post["slug"]: post for post in data.get("posts", [])}
    for post in POSTS:
        existing[post["slug"]] = {
            "slug": post["slug"],
            "title": post["title"],
            "excerpt": f"Use {post['primary']} to prioritize website fixes that improve indexability, search appearance, and qualified lead paths.",
            "category": "SEO",
            "date": DATE,
            "readingTime": "7 min",
            "primaryKeyword": post["primary"],
            "secondaryKeyword": post["secondary"],
            "funnelTo": "/free-audit",
            "featured": False,
            "published": True,
        }
    data["lastUpdated"] = DATE
    data["posts"] = sorted(existing.values(), key=lambda item: item.get("date", ""), reverse=True)
    POSTS_JSON.write_text(json.dumps(data, indent=2))


def draw_covers():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        print(f"  ! cover generation skipped: {exc}")
        return

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    font_candidates = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ]
    mono_candidates = [
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    title_font = ImageFont.truetype(next((f for f in font_candidates if Path(f).exists()), font_candidates[-1]), 62)
    mono_font = ImageFont.truetype(next((f for f in mono_candidates if Path(f).exists()), mono_candidates[-1]), 24)
    small_font = ImageFont.truetype(next((f for f in mono_candidates if Path(f).exists()), mono_candidates[-1]), 18)

    for post in POSTS:
        image = Image.new("RGB", (1200, 675), (244, 240, 234))
        draw = ImageDraw.Draw(image)
        draw.rectangle([760, 0, 1200, 675], fill=(30, 26, 22))
        draw.line([78, 116, 360, 116], fill=(139, 58, 31), width=7)
        draw.text((78, 70), "LOFTS STUDIO / SEO AUDIT", font=mono_font, fill=(108, 98, 88))
        y = 170
        for line in textwrap.wrap(post["title"], width=24):
            draw.text((78, y), line, font=title_font, fill=(26, 22, 18))
            y += 72
        draw.text((78, 575), post["primary"], font=small_font, fill=(108, 98, 88))
        for idx, radius in enumerate((96, 150, 210)):
            color = (216, 123, 85) if idx == 1 else (74, 62, 52)
            draw.ellipse([880-radius, 330-radius, 880+radius, 330+radius], outline=color, width=5)
        draw.rounded_rectangle([840, 280, 1120, 390], radius=18, outline=(216, 123, 85), width=6)
        draw.line([870, 320, 1090, 320], fill=(250, 247, 241), width=4)
        draw.line([870, 350, 1020, 350], fill=(250, 247, 241), width=4)
        draw.text((865, 438), "Audit -> Fix -> Leads", font=mono_font, fill=(250, 247, 241))
        image.save(ASSET_DIR / f"{post['slug']}.png")


def refresh_indexes():
    spec = importlib.util.spec_from_file_location("seo_engine", ROOT / "scripts" / "seo_engine.py")
    seo_engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seo_engine)
    seo_engine.refresh_blog_index()
    seo_engine.gen_sitemap()


def main():
    nav, footer = load_nav_and_footer()
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    for post in POSTS:
        (BLOG_DIR / f"{post['slug']}.html").write_text(render_post(post, nav, footer))
        print(f"  ✓ blog/{post['slug']}.html")
    update_posts_json()
    draw_covers()
    refresh_indexes()
    print(json.dumps({"date": DATE, "posts": len(POSTS), "urls": [post_url(p) for p in POSTS]}, indent=2))


if __name__ == "__main__":
    main()
