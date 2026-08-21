#!/usr/bin/env python3
"""Lofts Studio SEO production run for 2026-08-11.

Generates the vertical pages and support posts selected from DataForSEO,
GSC Insights, GA4, and live SERP evidence.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lofts.studio"
TODAY = "2026-08-11"
ASSET_VERSION = "20260811a"


def read(path: str) -> str:
    return (ROOT / path).read_text()


def write(path: str, body: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)


def extract_chrome() -> tuple[str, str]:
    home = read("index.html")
    nav = re.search(r'<header class="nav-bar">.*?</header>', home, re.S).group(0)
    footer = re.search(r'<footer class="site-footer.*?</footer>', home, re.S).group(0)
    return nav, footer


NAV, FOOTER = extract_chrome()


COMMON_STYLE = """
<style>
.seo-page { background: var(--bg); }
.seo-hero { padding: 5.5rem 0 3.4rem; border-bottom: 1px solid var(--line); background: var(--surface); }
.seo-kicker { font: 700 0.72rem/1.2 var(--font-mono); letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent); }
.seo-title { max-width: 920px; margin: 1rem 0 0; font-family: var(--font-display); font-weight: 600; font-size: clamp(2.5rem, 7vw, 5.8rem); line-height: 0.93; letter-spacing: -0.055em; color: var(--ink); }
.seo-lead { max-width: 760px; margin: 1.5rem 0 0; color: var(--ink-soft); font-size: clamp(1.05rem, 2vw, 1.32rem); line-height: 1.65; }
.seo-actions { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 2rem; }
.ai-answer { max-width: 860px; margin-top: 2rem; padding: 1.35rem 1.55rem; border-left: 3px solid var(--accent); border-radius: 0 var(--r-md) var(--r-md) 0; background: var(--bg-soft); color: var(--ink-soft); line-height: 1.65; }
.seo-section { padding: 4.5rem 0; border-bottom: 1px solid var(--line); }
.seo-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 1.8rem; }
.seo-card { border: 1px solid var(--line); border-radius: var(--r-lg); padding: 1.35rem; background: var(--surface); }
.seo-card h3 { margin: 0 0 0.5rem; font-size: 1rem; color: var(--ink); }
.seo-card p { margin: 0; color: var(--ink-soft); line-height: 1.6; }
.seo-table { width: 100%; border-collapse: collapse; margin-top: 1.5rem; border: 1px solid var(--line); background: var(--surface); }
.seo-table th, .seo-table td { padding: 0.95rem 1rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; color: var(--ink-soft); }
.seo-table th { color: var(--ink); background: var(--bg-soft); font-weight: 700; }
.seo-table tr:last-child td { border-bottom: 0; }
.post-visual { margin: 2rem 0; padding: 1rem; border: 1px solid var(--line); border-radius: var(--r-lg); background: var(--surface); }
.post-visual svg { display: block; width: 100%; height: auto; border-radius: var(--r-md); background: var(--bg-soft); }
.post-visual figcaption { margin-top: 0.75rem; color: var(--muted); font-size: 0.9rem; line-height: 1.5; }
.post-prose { max-width: 780px; margin: 0 auto; }
.post-prose h2 { margin: 3rem 0 1rem; font-family: var(--font-display); font-size: clamp(1.55rem, 3vw, 2rem); letter-spacing: -0.035em; }
.post-prose p, .post-prose li { color: var(--ink-soft); font-size: 1.05rem; line-height: 1.75; }
.post-prose a { color: var(--accent); }
@media (max-width: 720px) { .seo-grid { grid-template-columns: 1fr; } .seo-table { display: block; overflow-x: auto; } }
</style>
"""


def jsonld(data: dict) -> str:
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + "\n</script>"


def page_shell(title: str, description: str, canonical: str, body: str, schema: list[dict], og_type: str = "website") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<script data-lofts-theme-init>(function(){{var m="light";try{{m=localStorage.getItem("lofts-theme")==="dark"?"dark":"light"}}catch(e){{}}document.documentElement.dataset.theme=m;document.documentElement.style.colorScheme=m}}())</script>
<title>{title}</title>
<meta name="description" content="{description}" />
<link rel="canonical" href="{canonical}" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta property="og:type" content="{og_type}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="{SITE}/assets/og.jpg?v=2" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="icon" type="image/png" href="/apple-touch-icon.png" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="stylesheet" href="/assets/styles.css?v=20260808k" />
<link rel="stylesheet" href="/assets/experience.css?v=20260810b" data-lofts-experience />
<link rel="stylesheet" href="/assets/typography.css" />
<link rel="stylesheet" href="/assets/design-system.css?v=20260810b" />
{''.join(jsonld(s) for s in schema)}
{COMMON_STYLE}
</head>
<body class="seo-page">
<a class="skip-link" href="#main-content">Skip to main content</a>
{NAV}
<main id="main-content" tabindex="-1">
{body}
</main>
{FOOTER}
<script src="/assets/main.js?v={ASSET_VERSION}" defer></script>
<script src="/assets/widgets.js?v={ASSET_VERSION}" defer></script>
</body>
</html>
"""


def service_schema(name: str, description: str, url: str, service_type: str) -> list[dict]:
    return [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": name,
            "provider": {"@type": "Organization", "name": "Lofts Studio", "@id": f"{SITE}/#organization", "url": f"{SITE}/"},
            "serviceType": service_type,
            "areaServed": ["United States", "United Kingdom", "Canada"],
            "url": url,
            "description": description,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Websites", "item": f"{SITE}/websites"},
                {"@type": "ListItem", "position": 3, "name": name, "item": url},
            ],
        },
    ]


def service_page(slug: str, name: str, title: str, description: str, lead: str, short: str, primary_keyword: str, cards: list[tuple[str, str]], table_rows: list[tuple[str, str, str]], links: list[tuple[str, str]]) -> None:
    canonical = f"{SITE}/websites/{slug}"
    body = f"""
<section class="seo-hero">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);"><a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span><a href="/websites" style="color: var(--muted);">Websites</a> <span style="margin: 0 8px;">/</span><span>{name}</span></nav>
    <span class="seo-kicker">{primary_keyword}</span>
    <h1 class="seo-title">{title}</h1>
    <p class="seo-lead">{lead}</p>
    <div class="seo-actions"><a class="btn btn-primary" href="/free-audit">Run a free audit</a><a class="btn btn-ghost" href="/#contact">Talk to Lofts Studio</a></div>
    <div class="ai-answer"><strong>The short version:</strong> {short}</div>
  </div>
</section>
<section class="seo-section">
  <div class="container">
    <span class="seo-kicker">What the page must do</span>
    <h2 class="h-1" style="margin-top: 1rem;">Build around the buyer action, not just the design.</h2>
    <div class="seo-grid">
      {''.join(f'<div class="seo-card"><h3>{h}</h3><p>{p}</p></div>' for h, p in cards)}
    </div>
  </div>
</section>
<section class="seo-section">
  <div class="container">
    <span class="seo-kicker">Outranking angle</span>
    <h2 class="h-1" style="margin-top: 1rem;">Where Lofts Studio can beat generic agency pages.</h2>
    <table class="seo-table">
      <thead><tr><th>Searcher need</th><th>Weak competitor pattern</th><th>Lofts Studio upgrade</th></tr></thead>
      <tbody>{''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in table_rows)}</tbody>
    </table>
  </div>
</section>
<section class="seo-section">
  <div class="container">
    <span class="seo-kicker">Next path</span>
    <h2 class="h-1" style="margin-top: 1rem;">Support pages and services connected to this intent.</h2>
    <div class="seo-grid">
      {''.join(f'<a class="seo-card" href="{href}"><h3>{label}</h3><p>Use this next if you want the planning, proof, audit, or conversion path behind the page.</p></a>' for label, href in links)}
    </div>
  </div>
</section>
"""
    schema = service_schema(name, description, canonical, primary_keyword)
    write(f"websites/{slug}/index.html", page_shell(f"{name} | Lofts Studio", description, canonical, body, schema))


def visual(title: str, a: str, b: str, c: str, d: str) -> str:
    return f"""
<figure class="post-visual">
  <svg viewBox="0 0 920 320" role="img" aria-label="{title}">
    <rect x="24" y="24" width="872" height="272" rx="18" fill="#fbf7f0" stroke="#ddd0c3"/>
    <text x="52" y="72" font-family="Arial" font-size="28" font-weight="700" fill="#1d1712">{title}</text>
    <g font-family="Arial" font-size="18" fill="#4d4038">
      <rect x="52" y="112" width="180" height="118" rx="12" fill="#ffffff" stroke="#ddd0c3"/><text x="76" y="156">{a}</text>
      <path d="M246 171h70" stroke="#964a2b" stroke-width="4"/><path d="m304 157 16 14-16 14" fill="none" stroke="#964a2b" stroke-width="4"/>
      <rect x="332" y="112" width="180" height="118" rx="12" fill="#ffffff" stroke="#ddd0c3"/><text x="356" y="156">{b}</text>
      <path d="M526 171h70" stroke="#964a2b" stroke-width="4"/><path d="m584 157 16 14-16 14" fill="none" stroke="#964a2b" stroke-width="4"/>
      <rect x="612" y="112" width="232" height="118" rx="12" fill="#ffffff" stroke="#ddd0c3"/><text x="636" y="150">{c}</text><text x="636" y="180">{d}</text>
    </g>
  </svg>
  <figcaption>{title}: a simple workflow diagram for the article section.</figcaption>
</figure>
"""


def article_page(slug: str, title: str, description: str, keyword: str, intro: str, sections: list[tuple[str, str]], links: list[tuple[str, str]]) -> None:
    canonical = f"{SITE}/blog/{slug}.html"
    visuals = [
        visual("Search intent to lead path", "Search", "Trust", "Audit", "Inquiry"),
        visual("Page structure map", "Hero", "Proof", "CTA", "Follow-up"),
        visual("Local SEO content loop", "Service", "Location", "FAQ", "Reviews"),
        visual("Measurement loop", "GSC", "GA4", "Fix", "Retest"),
    ]
    prose = f"""
<section class="seo-hero">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);"><a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span><a href="/blog" style="color: var(--muted);">Blog</a> <span style="margin: 0 8px;">/</span><span>{title}</span></nav>
    <span class="seo-kicker">{keyword}</span>
    <h1 class="seo-title">{title}</h1>
    <p class="seo-lead">{intro}</p>
    <div class="seo-actions"><a class="btn btn-primary" href="/free-audit">Check your website</a><a class="btn btn-ghost" href="/websites">View industry pages</a></div>
    <div class="ai-answer"><strong>Direct answer:</strong> {description}</div>
  </div>
</section>
<section class="seo-section">
  <div class="container post-prose">
    {visuals[0]}
    {''.join(f'<h2>{h}</h2><p>{p}</p>{visuals[(i % 3) + 1] if i < 3 else ""}' for i, (h, p) in enumerate(sections))}
    <h2>Connected Lofts Studio pages</h2>
    <ul>{''.join(f'<li><a href="{href}">{label}</a></li>' for label, href in links)}</ul>
  </div>
</section>
"""
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "datePublished": f"{TODAY}T09:00:00Z",
            "dateModified": f"{TODAY}T09:00:00Z",
            "author": {"@type": "Person", "name": "Adnan K.", "url": f"{SITE}/about.html"},
            "publisher": {"@type": "Organization", "name": "Lofts Studio", "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.svg"}},
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "keywords": keyword,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
            ],
        },
    ]
    write(f"blog/{slug}.html", page_shell(title, description, canonical, prose, schema, "article"))


def add_support_section(path: str, marker: str, html: str) -> None:
    content = read(path)
    if marker in content:
        return
    anchor = "</section>\n\n<section class=\"section\" style=\"border-top: 1px solid var(--line);\""
    content = content.replace(anchor, "</section>\n\n" + html + "\n\n<section class=\"section\" style=\"border-top: 1px solid var(--line);\"", 1)
    write(path, content)


def update_posts_json() -> None:
    path = ROOT / "blog/posts.json"
    data = json.loads(path.read_text())
    additions = [
        ("veterinary-website-features-appointment-growth", "Veterinary Website Features That Grow Appointments", "Veterinary website features that connect local SEO, emergency clarity, appointment booking, and new-client registration.", "veterinarian website design"),
        ("insurance-agency-quote-request-funnel", "Insurance Agency Quote Request Funnel: Website Structure That Converts", "A practical insurance agency website funnel for quote requests, product pages, local trust, and lead routing.", "insurance agency website design"),
        ("optometrist-website-design-appointment-booking", "Optometrist Website Design for Appointment Booking", "How optometry and ophthalmology websites can turn eye-care searches into booked appointments.", "optometrist website design"),
    ]
    existing = {post["slug"] for post in data["posts"]}
    new_posts = []
    for slug, title, excerpt, primary in additions:
        if slug not in existing:
            new_posts.append({
                "slug": slug,
                "title": title,
                "excerpt": excerpt,
                "category": "SEO",
                "date": TODAY,
                "readingTime": "6 min",
                "primaryKeyword": primary,
                "secondaryKeyword": "industry website design",
                "funnelTo": "/free-audit/",
                "featured": False,
                "published": True,
            })
    data["lastUpdated"] = TODAY
    data["posts"] = new_posts + data["posts"]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def update_websites_index() -> None:
    path = ROOT / "websites/index.html"
    content = path.read_text()
    if "/websites/insurance-agencies" not in content:
        content = content.replace(
            '<a href="/websites/opticians" class="ind-card"><h3>Optometry &amp; ophthalmology</h3>',
            '<a href="/websites/insurance-agencies" class="ind-card"><h3>Insurance agencies</h3><p>Insurance agency website design, quote-request funnels, carrier pages, local trust, and SEO-ready structure.</p></a>\n      <a href="/websites/orthodontists" class="ind-card"><h3>Orthodontists</h3><p>Orthodontist website design, treatment pages, consultation booking, local SEO, and parent/adult patient paths.</p></a>\n      <a href="/websites/opticians" class="ind-card"><h3>Optometry &amp; ophthalmology</h3>',
            1,
        )
    path.write_text(content)


def update_llms() -> None:
    path = ROOT / "llms.txt"
    content = path.read_text()
    links = [
        "- [Insurance Agency Website Design and SEO](https://lofts.studio/websites/insurance-agencies)",
        "- [Orthodontist Website Design and SEO](https://lofts.studio/websites/orthodontists)",
        "- [Veterinary Website Features That Grow Appointments](https://lofts.studio/blog/veterinary-website-features-appointment-growth.html)",
        "- [Insurance Agency Quote Request Funnel](https://lofts.studio/blog/insurance-agency-quote-request-funnel.html)",
        "- [Optometrist Website Design for Appointment Booking](https://lofts.studio/blog/optometrist-website-design-appointment-booking.html)",
    ]
    for link in links:
        if link not in content:
            content += "\n" + link
    path.write_text(content + ("\n" if not content.endswith("\n") else ""))


def main() -> None:
    service_page(
        "insurance-agencies",
        "Insurance Agency Website Design and SEO",
        "Insurance agency websites built for quote requests.",
        "Insurance agency website design and SEO for agencies that need quote-request funnels, carrier pages, local trust, and measurable lead paths.",
        "Insurance agencies need more than a brochure site. The page has to explain coverage, build trust, route quote requests, and make local prospects comfortable enough to start the conversation.",
        "A strong insurance agency website combines product pages, quote-request flow, local agency trust, compliance-aware copy, reviews, call tracking, and SEO-ready structure so prospects can find the right coverage path and request help.",
        "insurance agency website design",
        [
            ("Quote request path", "Create a low-friction route from coverage need to quote request, including conditional questions when useful."),
            ("Carrier and product pages", "Explain auto, home, life, business, and specialty coverage without hiding the next step."),
            ("Local agency trust", "Use team, reviews, service areas, and practical FAQ content to compete with platforms and directories."),
            ("Measurement", "Track calls, form starts, quote requests, and organic landing-page quality in GA4."),
        ],
        [
            ("Coverage clarity", "Templates and platform pages often stay generic.", "Build product pages that answer the buyer question and lead into quote flow."),
            ("Local trust", "Many competitors rely on stock language.", "Show agency team, service-area fit, reviews, and process before asking for details."),
            ("Search structure", "Quote pages are often isolated.", "Connect product, location, FAQ, quote, and audit paths with descriptive internal links."),
        ],
        [("Insurance quote funnel guide", "/blog/insurance-agency-quote-request-funnel.html"), ("Free website audit", "/free-audit"), ("Technical SEO audit", "/services/technical-seo-audit.html")],
    )
    service_page(
        "orthodontists",
        "Orthodontist Website Design and SEO",
        "Orthodontist websites built for consultation bookings.",
        "Orthodontist website design and SEO for practices that need treatment pages, consultation booking, local search visibility, and parent/adult patient paths.",
        "Orthodontic buyers compare trust, treatment options, financing language, convenience, and before-after proof carefully. The website has to guide both parents and adult patients into a consultation path.",
        "A strong orthodontist website combines treatment pages, consultation booking, parent and adult patient paths, doctor trust, local SEO, schema, and clear next steps without making unsupported treatment claims.",
        "orthodontist website design",
        [
            ("Consultation booking", "Make the first consultation path obvious from mobile, service pages, and local landing pages."),
            ("Treatment structure", "Separate braces, clear aligners, adult orthodontics, and pediatric paths when the practice offers them."),
            ("Trust without risky claims", "Use process, doctor profiles, FAQs, and visible proof instead of exaggerated outcomes."),
            ("Local SEO", "Support near-me and city/service-area queries through clean architecture and schema."),
        ],
        [
            ("Parent and adult intent", "Generic dental pages blur the audience.", "Split decision paths for parents, teens, and adults."),
            ("Consultation friction", "Many pages bury booking.", "Place the consultation action near the answer block and repeat it naturally."),
            ("Schema and FAQs", "Competitors often underuse visible Q&A.", "Mirror real FAQs with truthful FAQPage and BreadcrumbList schema."),
        ],
        [("Dentist and clinic website design", "/websites/dentists"), ("Free website audit", "/free-audit"), ("Conversion optimization", "/services/conversion-rate-optimization.html")],
    )
    article_page(
        "veterinary-website-features-appointment-growth",
        "Veterinary Website Features That Grow Appointments",
        "The best veterinary website features support emergency clarity, appointment booking, new-client registration, local SEO, service pages, and trust.",
        "veterinarian website design",
        "Veterinary websites win when anxious pet owners can find care, trust the clinic, and book or register without friction.",
        [
            ("Start with emergency and booking clarity", "Pet owners often search in a hurry. Emergency details, opening hours, booking, and new-client registration should be visible before the owner has to dig through the menu."),
            ("Build service pages around real owner questions", "Vaccinations, dental care, surgery, urgent care, wellness plans, and new-patient pages should answer the practical questions owners ask before they call."),
            ("Use trust signals that feel real", "Doctor and team profiles, clinic photos, reviews, care philosophy, accessibility, and location details help local owners choose confidently."),
            ("Measure the appointment path", "GSC can show which veterinary queries are earning impressions, while GA4 should show whether visitors move from service pages into booking, calls, registration, or contact."),
        ],
        [("Veterinary website design", "/websites/veterinary"), ("Free website audit", "/free-audit"), ("SEO/AEO checker", "/tools/seo-aeo-checker.html")],
    )
    article_page(
        "insurance-agency-quote-request-funnel",
        "Insurance Agency Quote Request Funnel: Website Structure That Converts",
        "An insurance agency quote-request funnel connects coverage pages, local trust, clear questions, consent language, and lead routing.",
        "insurance agency website design",
        "Insurance buyers need clarity before they share details. A good agency website turns coverage intent into a quote request without feeling like a generic form dump.",
        [
            ("Make the coverage path specific", "Auto, home, business, life, and specialty insurance buyers arrive with different concerns. Route them into the right page before the quote request."),
            ("Use the form as a guided decision path", "A quote form should ask only useful questions, explain why details are needed, and make the next step clear after submission."),
            ("Add local and team trust", "Insurance is trust-heavy. Team context, service area, carrier/product clarity, reviews, and practical FAQs help prospects choose a local agency over a platform."),
            ("Track quality, not just submissions", "Measure organic landing pages, form starts, quote requests, call clicks, and qualified follow-up so SEO is tied to real agency opportunities."),
        ],
        [("Insurance agency website design", "/websites/insurance-agencies"), ("Insurance and finance work", "/work/insurance-finance"), ("Free website audit", "/free-audit")],
    )
    article_page(
        "optometrist-website-design-appointment-booking",
        "Optometrist Website Design for Appointment Booking",
        "Optometrist website design should connect eye-test searches, doctor/location pages, insurance information, and booking actions.",
        "optometrist website design",
        "Eye-care websites convert when patients can understand services, choose the right location or doctor, and book an eye test or consultation quickly on mobile.",
        [
            ("Put booking close to the query answer", "A patient searching for an eye test, contact-lens check, emergency eye appointment, or ophthalmology consultation should see the booking path immediately."),
            ("Create doctor, location, and service clarity", "The site should explain doctors, services, insurance information, and locations without forcing patients to call for basic answers."),
            ("Use frame and treatment pages carefully", "Retail-style frame pages and clinical treatment pages are different intents. Keep them clear, useful, and internally linked."),
            ("Watch GSC Insights and GA4 behavior", "If eye-care pages start earning impressions or visits but no bookings, refresh the first screen, proof, FAQ, and internal links before publishing unrelated content."),
        ],
        [("Optometry website design", "/websites/opticians"), ("Free website audit", "/free-audit"), ("Conversion optimization", "/services/conversion-rate-optimization.html")],
    )
    add_support_section(
        "websites/veterinary/index.html",
        "data-20260811-serp-gap",
        """<section class="section" style="border-top: 1px solid var(--line);" data-20260811-serp-gap>
  <div class="container">
    <span class="eyebrow">2026 SERP gap</span>
    <h2 class="h-1" style="margin-top: 1rem;">Compete against specialist vet sites with clearer action.</h2>
    <div class="answer-box"><p><strong style="color: var(--ink);">DataForSEO showed high-CPC demand around best veterinarian website design.</strong> The pages currently ranking lean on portfolios, templates, or broad agency promises. Lofts Studio can outwork them by pairing veterinary SEO, emergency clarity, booking, registration, service pages, and an audit-first lead path.</p></div>
    <div class="feat-grid">
      <div class="feat-card"><h3>Emergency-first mobile UX</h3><p>Make urgent care, opening hours, location, and contact paths impossible to miss.</p></div>
      <div class="feat-card"><h3>Appointment growth guide</h3><p>Support this page with <a href="/blog/veterinary-website-features-appointment-growth.html">veterinary website features that grow appointments</a>.</p></div>
    </div>
  </div>
</section>""",
    )
    add_support_section(
        "websites/opticians/index.html",
        "data-20260811-serp-gap",
        """<section class="section" style="border-top: 1px solid var(--line);" data-20260811-serp-gap>
  <div class="container">
    <span class="eyebrow">Appointment path</span>
    <h2 class="h-1" style="margin-top: 1rem;">Turn optometrist searches into booked eye-care visits.</h2>
    <div class="answer-box"><p><strong style="color: var(--ink);">GSC and GA4 show Lofts visitors already interact with audit and industry pages.</strong> This eye-care page now connects optometrist website design, ophthalmology website design, insurance clarity, doctor/location pages, and a support guide focused on booking.</p></div>
    <div class="feat-grid">
      <div class="feat-card"><h3>Doctor and location pages</h3><p>Useful pages for providers, locations, treatments, frames, insurance, and emergency eye appointments.</p></div>
      <div class="feat-card"><h3>Booking support guide</h3><p>Read <a href="/blog/optometrist-website-design-appointment-booking.html">optometrist website design for appointment booking</a>.</p></div>
    </div>
  </div>
</section>""",
    )
    add_support_section(
        "websites/landscaping/index.html",
        "data-20260811-serp-gap",
        """<section class="section" style="border-top: 1px solid var(--line);" data-20260811-serp-gap>
  <div class="container">
    <span class="eyebrow">Project-gallery SEO</span>
    <h2 class="h-1" style="margin-top: 1rem;">Pool builders and landscapers need proof before prose.</h2>
    <div class="answer-box"><p><strong style="color: var(--ink);">Live SERPs show visual proof and lead management are major pool-builder angles.</strong> This page now leans harder into galleries, service-area pages, seasonal content, and estimate requests so the searcher sees the outcome and can act.</p></div>
    <div class="feat-grid">
      <div class="feat-card"><h3>Gallery as the centerpiece</h3><p>Before-after photos, service filters, and project context should sit close to the first conversion action.</p></div>
      <div class="feat-card"><h3>Estimate-ready pages</h3><p>Service-area and seasonal pages should push homeowners into a structured estimate request.</p></div>
    </div>
  </div>
</section>""",
    )
    update_posts_json()
    update_websites_index()
    update_llms()
    print("Lofts Studio SEO run assets generated.")


if __name__ == "__main__":
    main()
