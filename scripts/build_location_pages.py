from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://lofts.studio"
CACHE_VER = "20260618c"
TODAY = "2026-06-18"


INDUSTRIES = {
    "dentists": ("Dentists", "/websites/dentists/", "trust-heavy dental sites that turn anxious searches into booked appointments"),
    "medical": ("Medical clinics", "/websites/medical-clinics/", "clinic websites with clear services, credentials, intake paths, and local SEO"),
    "hvac": ("HVAC", "/websites/hvac/", "emergency and installation pages for heating, cooling, and seasonal demand"),
    "law": ("Law firms", "/websites/law-firms/", "authority-led practice pages, attorney proof, and intake flows"),
    "restaurants": ("Restaurants", "/websites/restaurants/", "menus, local discovery, direct booking, and mobile-first ordering paths"),
    "real_estate": ("Real estate", "/websites/real-estate/", "valuation requests, listings, neighborhood pages, and lead routing"),
    "spas": ("Spas and beauty", "/websites/spas/", "premium local service pages for med spas, salons, and beauty clinics"),
    "trades": ("Trades", "/websites/trades/", "proof-led contractor websites with galleries, service areas, and fast enquiries"),
    "plumbers": ("Plumbers", "/websites/plumbers/", "urgent-service pages and photo-upload project request flows"),
    "electricians": ("Electricians", "/websites/electricians/", "certification-forward electrical websites for emergency and planned work"),
    "photographers": ("Photographers", "/websites/photographers/", "portfolio-led sites that make style, availability, and enquiry paths obvious"),
    "hospitality": ("Hotels and B&Bs", "/websites/hotels-bnb/", "direct-booking pages, local trust, and mobile guest journeys"),
    "financial": ("Financial advisors", "/websites/financial-advisors/", "credibility-first pages for advisory, planning, and local trust"),
    "auto": ("Auto repair", "/websites/auto-repair/", "repair, diagnostics, service-area, and booking-focused auto websites"),
    "retail": ("Local retail", "/websites/local-retail/", "local shop websites built for discovery, inventory clarity, and repeat visits"),
}


STATES = [
    {
        "name": "California",
        "slug": "california",
        "abbr": "CA",
        "angle": "California search is split between high-intent local service searches, polished brand expectations, and fast mobile comparison. A California page has to feel credible quickly, then move a visitor toward a call, booking, or project request without making them work.",
        "industries": ["medical", "spas", "real_estate", "restaurants", "retail"],
        "cities": [
            {
                "name": "Los Angeles",
                "slug": "los-angeles-web-design",
                "market": "Los Angeles buyers compare polished options fast: clinics, wellness brands, professional services, restaurants, production teams, and local retailers all need proof above the fold.",
                "search": "Most searches are mobile, visual, and impatient. The site has to show credibility, location relevance, and a next step before the visitor opens the next tab.",
                "ai": "AI calling agents are useful for LA teams that miss enquiries while staff are with clients, on shoots, in treatment rooms, or covering multiple locations.",
                "industries": ["spas", "medical", "restaurants", "real_estate", "photographers"],
            },
            {
                "name": "San Diego",
                "slug": "san-diego-web-design",
                "market": "San Diego has a strong mix of wellness, clinics, tourism, home services, and ecommerce brands. The best sites feel calm, fast, and specific to the buyer's intent.",
                "search": "People often search by neighborhood, specialty, and urgency. Pages need clean service architecture, fast mobile speed, and review-ready trust signals.",
                "ai": "AI phone agents fit practices and service teams that need to capture after-hours questions, route appointment requests, and collect useful intake details.",
                "industries": ["medical", "spas", "trades", "hospitality", "restaurants"],
            },
            {
                "name": "San Francisco",
                "slug": "san-francisco-web-design",
                "market": "San Francisco buyers are fluent in software and allergic to vague agency language. They expect a site to explain the offer, prove technical competence, and load cleanly.",
                "search": "B2B, SaaS, fintech, healthcare, and professional-service searches often include comparison language and high trust requirements.",
                "ai": "AI calling agents can qualify inbound leads, summarize conversations, and hand serious enquiries to a founder or operator with context attached.",
                "industries": ["financial", "medical", "law", "real_estate", "retail"],
            },
            {
                "name": "San Jose",
                "slug": "san-jose-web-design",
                "market": "San Jose businesses often sit between local service demand and technical buyer expectations. A generic brochure site will not carry enough proof.",
                "search": "The site needs direct service pages, technical clarity, fast performance, and structured paths for both local and B2B enquiries.",
                "ai": "AI calling agents work well for teams that need intake routing, appointment capture, and clear summaries without hiring more front-desk coverage.",
                "industries": ["medical", "law", "electricians", "real_estate", "financial"],
            },
            {
                "name": "Irvine",
                "slug": "irvine-web-design",
                "market": "Irvine searches skew professional, healthcare, real estate, education, and high-trust services. Visitors expect polished design without noise.",
                "search": "Strong pages answer who you serve, why you are credible, what happens next, and how fast someone can speak to the right person.",
                "ai": "AI calling agents help offices qualify appointment requests, capture after-hours enquiries, and route higher-value conversations to the right team member.",
                "industries": ["medical", "law", "real_estate", "financial", "spas"],
            },
        ],
    },
    {
        "name": "Texas",
        "slug": "texas",
        "abbr": "TX",
        "angle": "Texas pages need to work across fast-growth cities, competitive home services, healthcare, restaurants, and B2B firms. The goal is not decoration. The goal is to show up for the right search, prove the business is real, and make the next step obvious.",
        "industries": ["hvac", "trades", "medical", "law", "restaurants"],
        "cities": [
            {
                "name": "Austin",
                "slug": "austin-web-design",
                "market": "Austin businesses compete with polished startups and strong local operators at the same time. A site needs personality, technical confidence, and a clear conversion path.",
                "search": "Searches split between local service intent and founder-led B2B evaluation. Pages should be sharp enough for both.",
                "ai": "AI calling agents fit Austin teams that move fast, test offers, and need every qualified enquiry captured even when the team is in delivery mode.",
                "industries": ["restaurants", "medical", "hvac", "spas", "financial"],
            },
            {
                "name": "Dallas",
                "slug": "dallas-web-design",
                "market": "Dallas search results are crowded across healthcare, legal, B2B, home services, and local retail. The strongest sites lead with proof and remove friction.",
                "search": "Buyers compare credentials, reviews, service areas, and response paths. Pages need to be structured for scanning, not reading every word.",
                "ai": "AI calling agents can separate urgent calls from general enquiries, capture intake details, and keep the pipeline warm outside office hours.",
                "industries": ["law", "medical", "hvac", "real_estate", "financial"],
            },
            {
                "name": "Houston",
                "slug": "houston-web-design",
                "market": "Houston has heavy demand across medical, contractors, logistics, energy-adjacent services, restaurants, and legal work. Trust and clarity matter.",
                "search": "People search by urgency, neighborhood, specialty, and service type. The site needs deep service pages and strong mobile performance.",
                "ai": "AI calling agents are useful for Houston teams handling high call volume, appointment requests, emergency routing, and multilingual intake handoff.",
                "industries": ["medical", "hvac", "trades", "law", "restaurants"],
            },
            {
                "name": "San Antonio",
                "slug": "san-antonio-web-design",
                "market": "San Antonio local businesses win when the site feels trustworthy, human, and easy to act on. Over-designed pages often lose to clarity.",
                "search": "The best pages answer service fit, service area, proof, and next steps quickly for families, homeowners, tourists, and local buyers.",
                "ai": "AI calling agents help clinics, trades, and hospitality teams catch routine questions and appointment intent without slowing staff down.",
                "industries": ["medical", "trades", "restaurants", "hospitality", "auto"],
            },
            {
                "name": "Fort Worth",
                "slug": "fort-worth-web-design",
                "market": "Fort Worth search demand rewards practical proof: real work, clear services, quick contact paths, and pages that feel dependable.",
                "search": "Home services, legal, healthcare, and local retail searches need specific pages rather than one generic homepage trying to do everything.",
                "ai": "AI calling agents can triage service requests, gather photos or appointment details, and hand the team a clean summary before they respond.",
                "industries": ["trades", "law", "medical", "auto", "retail"],
            },
        ],
    },
    {
        "name": "Florida",
        "slug": "florida",
        "abbr": "FL",
        "angle": "Florida local search blends tourism, healthcare, legal, real estate, home services, and hospitality. The pages need to feel local enough to match search intent while staying honest about remote senior delivery.",
        "industries": ["hospitality", "spas", "real_estate", "law", "hvac"],
        "cities": [
            {
                "name": "Miami",
                "slug": "miami-web-design",
                "market": "Miami businesses need visual polish, bilingual-ready structure, fast mobile pages, and trust signals that work for both locals and visitors.",
                "search": "Hospitality, med spa, real estate, legal, restaurant, and clinic searches are competitive. The site must be clean, fast, and decisive.",
                "ai": "AI calling agents help Miami teams capture after-hours enquiries, route appointment requests, and handle repeat questions while staff serve customers.",
                "industries": ["spas", "real_estate", "hospitality", "law", "restaurants"],
            },
            {
                "name": "Tampa",
                "slug": "tampa-web-design",
                "market": "Tampa search demand is strong across home services, healthcare, finance, restaurants, and local professional services.",
                "search": "The winning pages are practical: fast loading, service-area clarity, reviews, FAQs, and strong calls to action.",
                "ai": "AI calling agents work well for Tampa service teams that want every call answered, sorted, and summarized before a human follows up.",
                "industries": ["hvac", "medical", "financial", "restaurants", "trades"],
            },
            {
                "name": "Orlando",
                "slug": "orlando-web-design",
                "market": "Orlando businesses often serve both residents and visitors. A site has to separate local service intent from tourism-driven browsing.",
                "search": "Clear pages for services, location, booking, trust, and mobile speed matter because visitors often decide on the move.",
                "ai": "AI calling agents can answer routine questions, sort booking requests, and capture intent when staff are busy with customers.",
                "industries": ["hospitality", "restaurants", "medical", "trades", "retail"],
            },
            {
                "name": "Jacksonville",
                "slug": "jacksonville-web-design",
                "market": "Jacksonville rewards steady, practical websites for home services, logistics, law, healthcare, and local operators.",
                "search": "Search pages need service area clarity, strong proof, and simple paths for calls, appointments, or project requests.",
                "ai": "AI calling agents can help Jacksonville teams triage service requests, gather context, and avoid missed opportunities during busy days.",
                "industries": ["trades", "hvac", "law", "medical", "auto"],
            },
            {
                "name": "Fort Lauderdale",
                "slug": "fort-lauderdale-web-design",
                "market": "Fort Lauderdale demand includes marine, real estate, medical, hospitality, law, and premium local services.",
                "search": "A strong page needs high-trust visuals, clear service positioning, mobile-first speed, and a direct next step.",
                "ai": "AI calling agents help premium service businesses answer after-hours questions and route serious enquiries without burying staff in admin.",
                "industries": ["real_estate", "hospitality", "medical", "law", "spas"],
            },
        ],
    },
    {
        "name": "New York",
        "slug": "new-york",
        "abbr": "NY",
        "angle": "New York search is competitive and skeptical. Pages have to get specific quickly: who the service is for, what proof exists, what happens next, and why the visitor should trust a remote senior team.",
        "industries": ["law", "medical", "restaurants", "real_estate", "financial"],
        "cities": [
            {
                "name": "New York City",
                "slug": "new-york-city-web-design",
                "market": "New York City businesses compete in dense search results where vague design language disappears. The page needs authority, proof, and a fast route to action.",
                "search": "Professional services, clinics, restaurants, DTC brands, and real estate searches all demand credibility before creativity.",
                "ai": "AI calling agents are useful for NYC teams that receive high-volume enquiries and need intake, routing, and follow-up summaries without slowing down.",
                "industries": ["law", "medical", "restaurants", "real_estate", "financial"],
            },
            {
                "name": "Brooklyn",
                "slug": "brooklyn-web-design",
                "market": "Brooklyn pages need taste and utility together. Restaurants, wellness studios, creative services, local retail, and clinics all need a site that feels alive but works hard.",
                "search": "Local searches often include neighborhood, style, specialty, and urgency. The website architecture has to support all of that.",
                "ai": "AI calling agents help Brooklyn teams answer routine questions, route bookings, and protect staff time when the floor is busy.",
                "industries": ["restaurants", "spas", "photographers", "retail", "medical"],
            },
            {
                "name": "Long Island",
                "slug": "long-island-web-design",
                "market": "Long Island businesses win with strong local trust: dentists, law firms, home services, real estate, and healthcare need proof that feels close to home.",
                "search": "Service-area pages, town-level clarity, reviews, and clean enquiry flows matter more than flashy homepage design.",
                "ai": "AI calling agents can route homeowners, patients, and clients to the right next step while collecting useful context for staff.",
                "industries": ["dentists", "law", "trades", "real_estate", "medical"],
            },
            {
                "name": "Buffalo",
                "slug": "buffalo-web-design",
                "market": "Buffalo search rewards practical websites for healthcare, trades, education, restaurants, and local professional services.",
                "search": "Pages should show service fit, location relevance, trust proof, and fast next steps without trying to sound bigger than the business.",
                "ai": "AI calling agents help Buffalo teams keep routine enquiries moving and avoid missed calls during job sites, appointments, or service hours.",
                "industries": ["medical", "trades", "restaurants", "law", "retail"],
            },
            {
                "name": "Rochester",
                "slug": "rochester-web-design",
                "market": "Rochester has strong healthcare, education, B2B, and home service demand. A strong site makes expertise easy to verify.",
                "search": "The goal is clear content architecture: service pages, proof, FAQs, contact paths, and tracking for every lead source.",
                "ai": "AI calling agents can support practices and service teams by handling first-pass intake and summarizing what the human team needs to know.",
                "industries": ["medical", "financial", "trades", "law", "retail"],
            },
        ],
    },
    {
        "name": "Georgia",
        "slug": "georgia",
        "abbr": "GA",
        "angle": "Georgia pages should balance Atlanta growth-market energy with practical local-service demand across suburbs and coastal cities. The best pages are direct, fast, and grounded in the way buyers actually choose.",
        "industries": ["medical", "hvac", "law", "restaurants", "financial"],
        "cities": [
            {
                "name": "Atlanta",
                "slug": "atlanta-web-design",
                "market": "Atlanta businesses need a site that can speak to fast-growth startups, healthcare, home services, restaurants, and professional firms without sounding generic.",
                "search": "Searchers compare credibility, availability, local proof, and response paths. The page has to remove uncertainty quickly.",
                "ai": "AI calling agents fit Atlanta teams that need to handle busy inbound periods, after-hours enquiries, and appointment routing cleanly.",
                "industries": ["medical", "hvac", "law", "restaurants", "financial"],
            },
            {
                "name": "Savannah",
                "slug": "savannah-web-design",
                "market": "Savannah businesses often blend hospitality, tourism, restaurants, local services, and creative work. The site needs charm, but the conversion path still has to be obvious.",
                "search": "Visitors and locals search differently. A strong page separates booking, service, location, and trust content so each searcher finds their path.",
                "ai": "AI calling agents help hospitality and service teams answer routine questions and route booking intent without pulling staff out of the work.",
                "industries": ["hospitality", "restaurants", "photographers", "trades", "retail"],
            },
            {
                "name": "Alpharetta",
                "slug": "alpharetta-web-design",
                "market": "Alpharetta buyers expect polished professional service websites, especially across SaaS, healthcare, finance, real estate, and consulting.",
                "search": "The page needs to feel senior: clear positioning, proof, strong service pages, and a path for qualified enquiries.",
                "ai": "AI calling agents can qualify inbound requests, route them by service line, and give the team clean summaries before follow-up.",
                "industries": ["financial", "medical", "real_estate", "law", "retail"],
            },
            {
                "name": "Marietta",
                "slug": "marietta-web-design",
                "market": "Marietta local search is practical: home services, medical practices, law firms, retail, and restaurants need clarity over flash.",
                "search": "Pages should emphasize service-area coverage, reviews, proof, and easy contact paths that work on mobile.",
                "ai": "AI calling agents help teams collect appointment details, route service requests, and keep the first response consistent.",
                "industries": ["trades", "medical", "law", "retail", "restaurants"],
            },
            {
                "name": "Sandy Springs",
                "slug": "sandy-springs-web-design",
                "market": "Sandy Springs demand is strong across healthcare, legal, real estate, finance, wellness, and premium local services.",
                "search": "The site should feel polished and reassuring, with quick answers for service fit, location relevance, and next steps.",
                "ai": "AI calling agents can support high-trust offices by collecting context, routing enquiries, and preserving staff focus during appointments.",
                "industries": ["medical", "law", "real_estate", "financial", "spas"],
            },
        ],
    },
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n")


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def indefinite_article(name: str) -> str:
    return "an" if name[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def header(title: str, description: str, canonical: str, schema: list[dict]) -> str:
    schema_tags = "\n".join(f'<script type="application/ld+json">\n{json_ld(item)}\n</script>' for item in schema)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}" />
<link rel="canonical" href="{esc(canonical)}" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{esc(canonical)}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:image" content="{SITE}/assets/og.jpg?v=2" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:type" content="image/jpeg" />
<meta property="og:image:alt" content="Lofts Studio — Senior Web Engineering" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="/favicon.ico" sizes="any" /><link rel="icon" href="/favicon.svg" type="image/svg+xml" /><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" /><link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="icon" type="image/png" href="/apple-touch-icon.png" />
<link rel="apple-touch-icon" href="/favicon.svg" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />
{schema_tags}
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1KT1MFDY8R"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-1KT1MFDY8R');
  </script>
  <script>(function(){{try{{var m=localStorage.getItem('lofts-theme');document.documentElement.setAttribute('data-theme',m==='dark'?'dark':'light');}}catch(e){{}}}})();</script>
</head>
<body>"""


def nav() -> str:
    return """<header class="nav-bar">
  <div class="nav-inner">
    <a href="/" class="nav-logo">Lofts<span class="dot">studio</span></a>
    <nav class="nav-links" aria-label="Primary">
      <a href="/websites/" class="nav-link">Web Design</a>
      <a href="/locations/usa/" class="nav-link">Locations</a>
      <a href="/services/ai-calling-agents.html" class="nav-link">AI Calling</a>
      <a href="/portfolio/" class="nav-link">Portfolio</a>
      <a href="/process/" class="nav-link">Process</a>
      <a href="/blog/" class="nav-link">Blog</a>
      <a href="/about.html" class="nav-link">About</a>
    </nav>
    <a href="/#contact" class="btn btn-primary">Start a conversation
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
    </a>
    <button id="menuBtn" class="menu-btn" aria-label="Open menu" aria-expanded="false">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="21" y1="12" y2="12"/><line x1="3" x2="21" y1="18" y2="18"/></svg>
    </button>
  </div>
</header>
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
      <a href="/locations/usa/" class="mnav-link" data-num="02">Locations</a>
      <a href="/services/ai-calling-agents.html" class="mnav-link" data-num="03">AI Calling</a>
      <a href="/portfolio/" class="mnav-link" data-num="04">Portfolio</a>
      <a href="/services/" class="mnav-link" data-num="05">Services</a>
      <a href="/blog/" class="mnav-link" data-num="06">Blog</a>
    </nav>
    <div class="mnav-services">
      <p class="mnav-label">Services</p>
      <div class="mnav-grid">
        <a href="/services/ai-calling-agents.html">AI Calling</a>
        <a href="/websites/">Local websites</a>
        <a href="/services/shopify-development.html">Shopify</a>
        <a href="/services/woocommerce-development.html">WooCommerce</a>
        <a href="/services/webflow-development.html">Webflow</a>
        <a href="/services/custom-app-development.html">Custom Apps</a>
        <a href="/services/technical-seo-audit.html">Technical SEO</a>
        <a href="/free-audit/">Free Audit</a>
      </div>
    </div>
    <a href="/free-audit/" class="mnav-audit-link">Free 15-min Audit</a>
    <div class="mnav-foot">
      <a href="/#contact" class="mnav-cta">Start a conversation
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
      </a>
      <p class="mnav-meta">US, UK &amp; GCC hours covered</p>
    </div>
  </div>
</div>"""


def footer() -> str:
    return f"""<footer class="site-footer footer-rich">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="footer-logo">
          <span class="footer-logo-italic">Lofts<span class="footer-logo-dot">.</span></span>
          <span class="footer-logo-caps">STUDIO</span>
        </div>
        <p class="footer-tag">Senior web engineering led by brothers Adnan Khan and Irfan Khan. Websites, local SEO structure, and AI agents built for businesses that need qualified enquiries, booked calls, and clean handoff.</p>
      </div>
      <div class="footer-newsletter">
        <p class="footer-newsletter-eyebrow">Next step</p>
        <h3 class="footer-newsletter-title">Bring the website, search, and phone flow into one system.</h3>
        <a href="/#contact" class="btn btn-primary">Start a conversation</a>
      </div>
    </div>
    <div class="footer-grid">
      <div>
        <h5>Growth pages</h5>
        <ul>
          <li><a href="/locations/usa/">USA locations</a></li>
          <li><a href="/websites/">Websites by industry</a></li>
          <li><a href="/services/ai-calling-agents.html">AI calling agents</a></li>
          <li><a href="/free-audit/">Free audit</a></li>
        </ul>
      </div>
      <div>
        <h5>Core services</h5>
        <ul>
          <li><a href="/services/shopify-development.html">Shopify</a></li>
          <li><a href="/services/woocommerce-development.html">WooCommerce</a></li>
          <li><a href="/services/webflow-development.html">Webflow</a></li>
          <li><a href="/services/technical-seo-audit.html">Technical SEO</a></li>
        </ul>
      </div>
      <div>
        <h5>Studio</h5>
        <ul>
          <li><a href="/portfolio/">Portfolio</a></li>
          <li><a href="/about.html">About</a></li>
          <li><a href="/process/">Process</a></li>
          <li><a href="/blog/">Blog</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="meta">&copy; <span data-year>2026</span> Lofts Studio &middot; Multan, Pakistan &middot; Dubai, UAE</p>
      <p class="meta">CAN-SPAM &amp; UK GDPR compliant &nbsp;·&nbsp; Async, documented delivery</p>
    </div>
  </div>
</footer>
<script src="/assets/main.js?v={CACHE_VER}" defer></script>
<script src="/assets/widgets.js?v={CACHE_VER}" defer></script>
</body>
</html>"""


def breadcrumb(items: list[tuple[str, str | None]]) -> str:
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span>/</span>')
        if href:
            parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            parts.append(f'<span>{esc(label)}</span>')
    return f'<nav class="loc-breadcrumb" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def industry_cards(keys: list[str]) -> str:
    return "\n".join(
        f"""<a class="loc-card loc-card-link" href="{INDUSTRIES[key][1]}">
          <span class="loc-card-kicker">Industry page</span>
          <h3>{esc(INDUSTRIES[key][0])}</h3>
          <p>{esc(INDUSTRIES[key][2])}.</p>
        </a>"""
        for key in keys
    )


def state_url(state: dict) -> str:
    return f"/locations/{state['slug']}/"


def city_url(state: dict, city: dict) -> str:
    return f"/locations/{state['slug']}/{city['slug']}/"


def breadcrumbs_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label, "item": f"{SITE}{path}"}
            for i, (label, path) in enumerate(items)
        ],
    }


def faq_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
            for question, answer in items
        ],
    }


def build_usa() -> None:
    path = "/locations/usa/"
    title = "USA Website Design, Local SEO & AI Calling Agents | Lofts Studio"
    description = "Senior remote website design, local SEO structure, and AI calling agents for US service businesses. Start with priority state and city pages built for qualified enquiries."
    schema = [
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": f"{SITE}{path}", "description": description, "isPartOf": {"@type": "WebSite", "url": SITE}},
        {"@context": "https://schema.org", "@type": "Service", "name": "USA website design and AI calling agents", "provider": {"@type": "Organization", "name": "Lofts Studio", "url": SITE}, "areaServed": [{"@type": "Country", "name": "United States"}], "serviceType": ["Website design", "Local SEO", "AI calling agents"]},
        breadcrumbs_schema([("Home", "/"), ("USA locations", path)]),
    ]
    state_links = "\n".join(
        f"""<a class="loc-card loc-card-link" href="{state_url(state)}">
          <span class="loc-card-kicker">{esc(state["abbr"])}</span>
          <h3>{esc(state["name"])}</h3>
          <p>{esc(state["angle"])}</p>
        </a>"""
        for state in STATES
    )
    content = f"""{header(title, description, f"{SITE}{path}", schema)}
{nav()}
<main>
  <section class="loc-hero">
    <div class="container">
      {breadcrumb([("Home", "/"), ("USA locations", None)])}
      <div class="loc-hero-copy" data-reveal>
        <span class="eyebrow">USA service-area SEO</span>
        <h1 class="h-display">Website design, local SEO, and AI calling agents for US businesses.</h1>
        <p class="lead">This is the first layer of a controlled location system: state hubs, priority city pages, industry pages, and AI phone workflows connected into one lead path. No fake local offices. No thin city swaps. Each page has a real search intent and a real next step.</p>
        <div class="loc-actions">
          <a href="/#contact" class="btn btn-primary">Plan my lead flow</a>
          <a href="/services/ai-calling-agents.html" class="btn btn-ghost">See AI calling agents</a>
        </div>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">First rollout</span>
        <h2 class="h-1">Start with the states where search intent is broad enough to learn fast.</h2>
        <p>These pages are built to collect impressions, expose city-level intent in Search Console, and route qualified visitors into service, industry, and AI calling pages.</p>
      </div>
      <div class="loc-grid loc-grid-3" data-reveal>
        {state_links}
      </div>
    </div>
  </section>
  <section class="loc-band">
    <div class="container loc-split">
      <div data-reveal>
        <span class="eyebrow">The lead path</span>
        <h2 class="h-1">Search page to booked conversation, not search page to dead form.</h2>
      </div>
      <div class="loc-flow" data-reveal>
        <div><strong>1. Find</strong><span>Rank city and industry pages for clear service intent.</span></div>
        <div><strong>2. Trust</strong><span>Show proof, process, FAQs, and relevant internal links.</span></div>
        <div><strong>3. Capture</strong><span>Offer audit, project request, or AI phone intake.</span></div>
        <div><strong>4. Route</strong><span>Send the visitor to the right service path with context.</span></div>
      </div>
    </div>
  </section>
</main>
{footer()}"""
    write(ROOT / "locations/usa/index.html", content)


def build_state(state: dict) -> None:
    path = state_url(state)
    title = f"Website Design in {state['name']} | Local SEO & AI Calling Agents"
    description = f"Senior website design, local SEO structure, and AI calling agents for {state['name']} businesses. Priority city pages built for qualified enquiries and clean handoff."
    schema = [
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": f"{SITE}{path}", "description": description, "isPartOf": {"@type": "WebSite", "url": SITE}},
        {"@context": "https://schema.org", "@type": "Service", "name": f"Website design in {state['name']}", "provider": {"@type": "Organization", "name": "Lofts Studio", "url": SITE}, "areaServed": [{"@type": "State", "name": state["name"]}], "serviceType": ["Website design", "Local SEO", "AI calling agents"]},
        breadcrumbs_schema([("Home", "/"), ("USA locations", "/locations/usa/"), (state["name"], path)]),
    ]
    city_links = "\n".join(
        f"""<a class="loc-card loc-card-link" href="{city_url(state, city)}">
          <span class="loc-card-kicker">City page</span>
          <h3>{esc(city["name"])} web design</h3>
          <p>{esc(city["market"])}</p>
        </a>"""
        for city in state["cities"]
    )
    other_states = "\n".join(
        f'<a href="{state_url(other)}">{esc(other["name"])}</a>'
        for other in STATES
        if other["slug"] != state["slug"]
    )
    content = f"""{header(title, description, f"{SITE}{path}", schema)}
{nav()}
<main>
  <section class="loc-hero">
    <div class="container">
      {breadcrumb([("Home", "/"), ("USA locations", "/locations/usa/"), (state["name"], None)])}
      <div class="loc-hero-copy" data-reveal>
        <span class="eyebrow">{esc(state["name"])} web design</span>
        <h1 class="h-display">Website design in {esc(state["name"])} for businesses that need search visibility and booked conversations.</h1>
        <p class="lead">{esc(state["angle"])}</p>
        <div class="loc-actions">
          <a href="/#contact" class="btn btn-primary">Map my {esc(state["abbr"])} lead path</a>
          <a href="/websites/" class="btn btn-ghost">Browse industry pages</a>
        </div>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">Priority cities</span>
        <h2 class="h-1">The first {esc(state["name"])} city pages are built around real search intent.</h2>
        <p>Each city links into the industries most likely to convert, then into AI calling agents where phone capture is part of the lead problem.</p>
      </div>
      <div class="loc-grid loc-grid-3" data-reveal>
        {city_links}
      </div>
    </div>
  </section>
  <section class="loc-band">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">Best-fit industries</span>
        <h2 class="h-1">Start with the verticals where a better website changes the first conversation.</h2>
      </div>
      <div class="loc-grid loc-grid-3" data-reveal>
        {industry_cards(state["industries"])}
      </div>
      <div class="loc-inline-links" data-reveal>
        <span>Other state hubs:</span>{other_states}
      </div>
    </div>
  </section>
</main>
{footer()}"""
    write(ROOT / f"locations/{state['slug']}/index.html", content)


def build_city(state: dict, city: dict) -> None:
    path = city_url(state, city)
    title = f"{city['name']} Web Design & AI Calling Agents | Lofts Studio"
    description = f"Senior web design, local SEO structure, and AI calling agents for {city['name']} businesses that need qualified enquiries, booked calls, and clean handoff."
    article = indefinite_article(city["name"])
    faq_items = [
        (f"Do you have to be physically based in {city['name']} to build for {city['name']} businesses?", f"No. Lofts Studio works remotely with US businesses and does not claim a fake {city['name']} office. The page is built for service-area intent: senior website design, local SEO structure, and AI calling workflows for businesses serving {city['name']} customers."),
        (f"What should {article} {city['name']} web design page include?", "It should explain the offer clearly, load quickly on mobile, show proof, include service and industry pages, answer the questions buyers actually ask, and make the next step simple."),
        (f"Can AI calling agents help {article} {city['name']} local business?", f"Yes, when calls are being missed, staff are busy, or enquiries need better routing. The agent can answer routine questions, collect intake details, summarize the call, and hand serious conversations to the right person."),
    ]
    schema = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": f"{SITE}{path}", "description": description, "isPartOf": {"@type": "WebSite", "url": SITE}},
        {"@context": "https://schema.org", "@type": "Service", "name": f"Web design in {city['name']}", "provider": {"@type": "Organization", "name": "Lofts Studio", "url": SITE}, "areaServed": [{"@type": "City", "name": city["name"]}, {"@type": "State", "name": state["name"]}], "serviceType": ["Website design", "Local SEO", "AI calling agents"]},
        breadcrumbs_schema([("Home", "/"), ("USA locations", "/locations/usa/"), (state["name"], state_url(state)), (city["name"], path)]),
        faq_schema(faq_items),
    ]
    nearby = "\n".join(
        f'<a href="{city_url(state, other)}">{esc(other["name"])}</a>'
        for other in state["cities"]
        if other["slug"] != city["slug"]
    )
    content = f"""{header(title, description, f"{SITE}{path}", schema)}
{nav()}
<main>
  <section class="loc-hero">
    <div class="container">
      {breadcrumb([("Home", "/"), ("USA locations", "/locations/usa/"), (state["name"], state_url(state)), (city["name"], None)])}
      <div class="loc-hero-copy" data-reveal>
        <span class="eyebrow">{esc(city["name"])} web design</span>
        <h1 class="h-display">Website design for {esc(city["name"])} businesses that need search visibility, qualified enquiries, and booked calls.</h1>
        <p class="lead">{esc(city["market"])}</p>
        <div class="loc-actions">
          <a href="/#contact" class="btn btn-primary">Start with a website audit</a>
          <a href="/services/ai-calling-agents.html" class="btn btn-ghost">Add AI calling agents</a>
        </div>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container loc-split">
      <div data-reveal>
        <span class="eyebrow">Local search intent</span>
        <h2 class="h-1">The job is not to look local. The job is to be useful for the searcher.</h2>
      </div>
      <div class="prose" data-reveal>
        <p>{esc(city["search"])}</p>
        <p>A strong {esc(city["name"])} web design page should connect the searcher to the exact service, show enough proof to reduce doubt, and make the next step obvious. That means city relevance, industry links, technical SEO, fast mobile performance, and a contact path that does not bury the visitor in a generic form.</p>
      </div>
    </div>
  </section>
  <section class="loc-band">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">What gets built</span>
        <h2 class="h-1">A web and phone system designed around how {esc(city["name"])} buyers choose.</h2>
      </div>
      <div class="loc-grid loc-grid-4" data-reveal>
        <article class="loc-card"><span class="loc-card-kicker">01</span><h3>Search-ready structure</h3><p>Service pages, location relevance, metadata, schema, and internal links built so Google can understand what you do and who you serve.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">02</span><h3>Conversion-first pages</h3><p>Above-the-fold proof, fast mobile loading, clear calls to action, and content that answers the questions buyers ask before they reach out.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">03</span><h3>AI calling agents</h3><p>{esc(city["ai"])}</p></article>
        <article class="loc-card"><span class="loc-card-kicker">04</span><h3>Tracking and handoff</h3><p>Analytics, event tracking, call summaries, and clean routing so enquiries become visible instead of disappearing into inbox noise.</p></article>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">Best-fit industries</span>
        <h2 class="h-1">Start with the {esc(city["name"])} verticals where search intent is already active.</h2>
      </div>
      <div class="loc-grid loc-grid-3" data-reveal>
        {industry_cards(city["industries"])}
      </div>
      <div class="loc-inline-links" data-reveal>
        <span>Nearby {esc(state["name"])} pages:</span>{nearby}
      </div>
    </div>
  </section>
  <section class="loc-band">
    <div class="container loc-split">
      <div data-reveal>
        <span class="eyebrow">AI phone layer</span>
        <h2 class="h-1">The website should not be the end of the lead path.</h2>
      </div>
      <div class="prose" data-reveal>
        <p>For many local businesses, the highest-intent visitor still wants to call. The problem is that calls arrive during appointments, job sites, service windows, lunch rushes, or after hours. An AI calling agent gives the website a second conversion path: answer, qualify, summarize, and route.</p>
        <p>The agent should never pretend to be a human. It should be clear, useful, and bounded: answer routine questions, collect the right details, escalate sensitive conversations, and send the team a clean handoff.</p>
        <p><a class="btn-editorial" href="/services/ai-calling-agents.html">See the AI calling agent service &nbsp;&rarr;</a></p>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container loc-faq">
      <div data-reveal>
        <span class="eyebrow">Questions</span>
        <h2 class="h-1">{esc(city["name"])} web design, answered.</h2>
      </div>
      <div data-reveal>
        {"".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in faq_items)}
      </div>
    </div>
  </section>
</main>
{footer()}"""
    write(ROOT / f"locations/{state['slug']}/{city['slug']}/index.html", content)


def build_ai_calling() -> None:
    path = "/services/ai-calling-agents.html"
    title = "AI Calling Agents for Service Businesses | Lofts Studio"
    description = "AI phone agents that answer missed calls, qualify leads, route appointments, and summarize conversations for service businesses."
    faq_items = [
        ("What does an AI calling agent do?", "It answers inbound calls, asks the right intake questions, routes urgent conversations, summarizes the call, and sends the team a clean handoff. It is designed to support staff, not hide that automation is involved."),
        ("Which businesses are a good fit?", "Dentists, clinics, HVAC teams, law firms, real estate teams, med spas, restaurants, and home service companies are strong fits when calls are being missed or staff spend too much time repeating the same first questions."),
        ("Can it connect to my website and forms?", "Yes. The calling agent can connect to website forms, CRM fields, email notifications, Slack, calendars, and internal notes so the phone flow becomes part of the same lead system."),
        ("Do you build the scripts and guardrails?", "Yes. The build includes call flow mapping, script design, escalation rules, transcript summaries, and review loops so the agent stays useful and bounded."),
    ]
    schema = [
        {"@context": "https://schema.org", "@type": "Service", "name": "AI Calling Agents", "provider": {"@type": "Organization", "name": "Lofts Studio", "url": SITE}, "areaServed": ["United States", "United Kingdom", "Canada"], "serviceType": "AI phone answering and lead qualification agents", "description": description},
        breadcrumbs_schema([("Home", "/"), ("Services", "/services/"), ("AI Calling Agents", path)]),
        faq_schema(faq_items),
    ]
    content = f"""{header(title, description, f"{SITE}{path}", schema)}
{nav()}
<main>
  <section class="loc-hero ai-hero">
    <div class="container">
      {breadcrumb([("Home", "/"), ("Services", "/services/"), ("AI Calling Agents", None)])}
      <div class="loc-hero-copy" data-reveal>
        <span class="eyebrow">AI calling agents</span>
        <h1 class="h-display">Answer missed calls, qualify leads, and hand your team the context.</h1>
        <p class="lead">Most local websites lose the lead after the visitor decides to call. Staff are with customers, on jobs, in appointments, or offline. I build AI calling agents that answer clearly, collect the right details, and route serious conversations without turning your business into a chatbot gimmick.</p>
        <div class="loc-actions">
          <a href="/#contact" class="btn btn-primary">Map my call flow</a>
          <a href="/locations/usa/" class="btn btn-ghost">See location strategy</a>
        </div>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container loc-split">
      <div data-reveal>
        <span class="eyebrow">The problem</span>
        <h2 class="h-1">Your highest-intent lead often arrives when nobody can answer well.</h2>
      </div>
      <div class="prose" data-reveal>
        <p>A website can rank, persuade, and load quickly, then still lose the person at the phone layer. They call during a service window, after office hours, while the front desk is helping someone else, or while the owner is on the road.</p>
        <p>The right AI calling agent does not replace the business. It catches the first conversation, asks useful questions, separates urgent from routine, and gives the human team a clean handoff.</p>
      </div>
    </div>
  </section>
  <section class="loc-band">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">What it handles</span>
        <h2 class="h-1">A practical phone layer for service businesses.</h2>
      </div>
      <div class="loc-grid loc-grid-3" data-reveal>
        <article class="loc-card"><span class="loc-card-kicker">Capture</span><h3>Missed-call answering</h3><p>Answer after-hours and overflow calls with a clear, bounded script that explains what the agent can help with.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">Qualify</span><h3>Lead intake</h3><p>Collect service type, location, urgency, availability, contact details, and notes before the team follows up.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">Route</span><h3>Human handoff</h3><p>Send summaries to email, Slack, CRM, or calendar paths with urgency tags and the next recommended action.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">Protect</span><h3>Escalation rules</h3><p>Define what the agent should not answer, when it should escalate, and how sensitive conversations should be handled.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">Measure</span><h3>Transcript review</h3><p>Keep call transcripts and summaries visible so scripts can improve and the team can audit what happened.</p></article>
        <article class="loc-card"><span class="loc-card-kicker">Connect</span><h3>Website integration</h3><p>Connect calls, forms, location pages, and industry pages into one lead flow instead of separate tools.</p></article>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container">
      <div class="loc-section-head" data-reveal>
        <span class="eyebrow">Best fit</span>
        <h2 class="h-1">Industries where the phone still decides the sale.</h2>
      </div>
      <div class="loc-grid loc-grid-3" data-reveal>
        {industry_cards(["dentists", "medical", "hvac", "law", "spas", "real_estate"])}
      </div>
    </div>
  </section>
  <section class="loc-band">
    <div class="container loc-split">
      <div data-reveal>
        <span class="eyebrow">Build flow</span>
        <h2 class="h-1">Scripted, bounded, integrated, reviewed.</h2>
      </div>
      <div class="loc-flow" data-reveal>
        <div><strong>1. Map calls</strong><span>List caller types, questions, urgency levels, and handoff rules.</span></div>
        <div><strong>2. Write guardrails</strong><span>Define what the agent can say, collect, route, and escalate.</span></div>
        <div><strong>3. Connect systems</strong><span>Attach forms, CRM, inboxes, calendars, and team notifications.</span></div>
        <div><strong>4. Review calls</strong><span>Use transcripts and summaries to improve the flow after launch.</span></div>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="container loc-faq">
      <div data-reveal>
        <span class="eyebrow">Questions</span>
        <h2 class="h-1">AI calling agents, answered.</h2>
      </div>
      <div data-reveal>
        {"".join(f'<div class="faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in faq_items)}
      </div>
    </div>
  </section>
</main>
{footer()}"""
    write(ROOT / "services/ai-calling-agents.html", content)


def sitemap_urls() -> list[tuple[str, str, str]]:
    urls = [("/services/ai-calling-agents.html", "weekly", "0.9"), ("/locations/usa/", "weekly", "0.9")]
    for state in STATES:
        urls.append((state_url(state), "weekly", "0.85"))
        for city in state["cities"]:
            urls.append((city_url(state, city), "weekly", "0.8"))
    return urls


def update_sitemap() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text()
    start = "  <!-- LOCATIONS:START -->"
    end = "  <!-- LOCATIONS:END -->"
    block = [start]
    for url, freq, priority in sitemap_urls():
        block.append(f"""  <url>
    <loc>{SITE}{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")
    block.append(end)
    new_block = "\n".join(block)
    if start in text and end in text:
        before = text[: text.index(start)]
        after = text[text.index(end) + len(end) :]
        text = before + new_block + after
    else:
        text = text.replace("</urlset>", new_block + "\n</urlset>")
    sitemap.write_text(text)


def main() -> None:
    build_usa()
    for state in STATES:
        build_state(state)
        for city in state["cities"]:
            build_city(state, city)
    build_ai_calling()
    update_sitemap()


if __name__ == "__main__":
    main()
