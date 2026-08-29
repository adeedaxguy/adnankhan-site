#!/usr/bin/env python3
"""
SEO Engine — Lofts Studio
─────────────────────────────────────────────────────────────────────────────
Single source-of-truth content engine. Consolidates:
  • Blog post generation from structured Python specs (see POSTS dict below)
  • Country/service location pages (see LOCATIONS + LOCATION_SERVICES)
  • Sitemap.xml auto-regeneration from filesystem
  • blog/index.html refresh from posts.json
  • robots.txt validation

Run modes:
  python3 scripts/seo_engine.py blog        # regen blog posts + index + posts.json
  python3 scripts/seo_engine.py locations   # regen all location service pages
  python3 scripts/seo_engine.py sitemap     # crawl filesystem → sitemap.xml
  python3 scripts/seo_engine.py all         # everything

Design goals:
  - Zero deps (stdlib only)
  - Idempotent: rerun is safe
  - Posts and pages are data, not magic
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://lofts.studio"
CACHE_VER = "20260801i"
BRAND_NAME = "Lofts Studio"
BRAND_TAGLINE = "Senior web engineering for founders."
FOUNDERS = "Adnan & Irfan Khan"

EXCLUDED_PUBLIC_BLOG_SLUGS = {
    "landing-page-design-cost",
    "pricing-page-design",
    "shopify-developer-freelance-rates",
    "small-business-website-cost-2026",
}

BLOG_DIR = ROOT / "blog"
SERVICES_DIR = ROOT / "services"
POSTS_JSON = BLOG_DIR / "posts.json"
INDEX_HTML = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"


# ─────────────────────────────────────────────────────────────────────────────
#  Nav + footer extraction (shared)
# ─────────────────────────────────────────────────────────────────────────────

def load_nav_and_footer():
    html = INDEX_HTML.read_text()
    nav = re.search(r'<header class="nav-bar">.*?</header>', html, re.DOTALL).group(0)
    footer = re.search(r'<footer class="site-footer.*?</footer>', html, re.DOTALL).group(0)
    return nav, footer


# ─────────────────────────────────────────────────────────────────────────────
#  BLOG POSTS — structured specs. Add a new dict here and rerun.
# ─────────────────────────────────────────────────────────────────────────────

def make_service_business_post(
    *,
    slug,
    title,
    excerpt,
    meta,
    category,
    primary,
    secondary,
    funnel_to,
    funnel_label,
    market_signal,
    searcher_problem,
    page_angle,
    checks,
    related_links,
):
    check_rows = "\n".join(
        f"        <tr><td><strong>{area}</strong></td><td>{need}</td><td>{reason}</td></tr>"
        for area, need, reason in checks
    )
    link_items = "\n".join(
        f'        <li><a href="{href}">{label}</a> - {why}</li>'
        for label, href, why in related_links
    )

    return {
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "meta": meta,
        "category": category,
        "date": "2026-08-30",
        "readingTime": "9 min",
        "primaryKeyword": primary,
        "secondaryKeyword": secondary,
        "funnelTo": funnel_to,
        "funnelLabel": funnel_label,
        "featured": False,
        "intentCardHtml": f"""<aside class="post-intent-card" aria-labelledby="{slug}-audit">
      <h2 id="{slug}-audit">Want this mapped for your own website?</h2>
      <form class="post-audit-launcher" action="/free-audit/" method="get">
        <label for="{slug}-audit-url">Website URL to audit</label>
        <div class="post-audit-row">
          <input id="{slug}-audit-url" name="url" type="url" inputmode="url" placeholder="https://example.com" autocomplete="url" required />
          <button class="btn btn-primary" type="submit">Start report <span aria-hidden="true">&rarr;</span></button>
        </div>
      </form>
      <p>Lofts Studio turns the search intent, page structure, trust proof, speed, schema, and lead path into a practical website improvement plan.</p>
      <div class="post-intent-actions">
        <a href="{funnel_to}" class="btn btn-ghost">{funnel_label}</a>
        <a href="/tools/seo-aeo-checker.html" class="btn btn-ghost">Run SEO/AEO check</a>
      </div>
      <div class="post-intent-note" aria-label="Sprint includes">
        <span>Search intent</span>
        <span>Technical SEO</span>
        <span>Lead path</span>
      </div>
    </aside>""",
        "hook": f"{primary} is not only a keyword. It is a buying situation. The page has to explain the problem, show what a better website needs, prove the work can be trusted, and move the visitor toward a clear audit or consultation step.",
        "faqs": [
            {
                "question": f"What should a page targeting {primary} include?",
                "answer": "It should include a direct answer, service fit, examples of what the buyer should check, visible trust proof, useful internal links, FAQ coverage, and a next step that matches the visitor's intent."
            },
            {
                "question": "Should this be a blog post or a service page?",
                "answer": "If the visitor is ready to hire, the main target should be a service or industry page. A blog post should support that page by answering the questions people ask before they contact a provider."
            },
            {
                "question": "How should Lofts Studio measure this SEO work?",
                "answer": "Measure non-brand impressions, clicks, CTR, average position, internal-link coverage, audit starts, contact clicks, and whether the page earns new related queries in Search Console."
            }
        ],
        "body": [
            ("p", market_signal),
            ("callout", "The ranking play is to satisfy the exact buyer intent, then connect that answer to a useful audit, service page, case study, or consultation path."),
            ("h2", "The search intent to satisfy"),
            ("p", searcher_problem),
            ("h2", "The Lofts Studio page angle"),
            ("p", page_angle),
            ("h2", "Page structure that can rank and convert"),
            ("html", f"""<div class="post-table-wrap"><table>
      <thead><tr><th>Page area</th><th>What to include</th><th>Why it matters</th></tr></thead>
      <tbody>
{check_rows}
      </tbody>
    </table></div>"""),
            ("h2", "Internal links to build around it"),
            ("html", f"""<ul>
{link_items}
    </ul>"""),
            ("h2", "What to avoid"),
            ("ul", [
                "Do not make a generic design-inspiration page when the query has service intent.",
                "Do not promise rankings, traffic, bookings, or lead volume that the current site cannot prove.",
                "Do not copy competitor wording. Use the SERP to understand missing buyer questions, then answer them in Lofts Studio's own voice.",
                "Do not create several near-identical URLs for the same intent. One canonical page should carry the main query family."
            ]),
            ("h2", "Daily measurement plan"),
            ("ol", [
                "Check Search Console for the target query family and the target URL.",
                "Watch whether impressions expand before judging clicks.",
                "Add internal links from the website hub, niche page, audit tool, and relevant articles.",
                "Refresh the title, opening answer, FAQ, and CTA if CTR or engagement is weak.",
                "Keep the page source-safe: clean canonicals, indexable robots, fast mobile layout, and no unsupported claims."
            ]),
        ],
    }


POSTS = [
    make_service_business_post(
        slug="seo-friendly-website-design-services",
        title="SEO-Friendly Website Design Services for Service Businesses",
        excerpt="How to structure SEO-friendly website design services around crawlability, answer clarity, internal links, speed, and qualified leads.",
        meta="SEO-friendly website design services for service businesses: page structure, technical SEO, AEO, internal links, speed, and lead paths.",
        category="SEO",
        primary="SEO-friendly website design services",
        secondary="SEO friendly website design",
        funnel_to="/websites",
        funnel_label="Website Design Hub",
        market_signal="DataForSEO showed a smaller but highly relevant SEO-friendly website design cluster, while live SERPs show competitors often split design, SEO, and conversion into separate ideas. That is the opening for Lofts Studio: one page architecture that covers crawlability, answer clarity, proof, speed, and enquiry flow together.",
        searcher_problem="A service-business owner searching this phrase is usually not looking for decoration. They want a website that can be crawled, understood, trusted, and turned into enquiries. The page should explain what makes a design SEO-friendly before the buyer asks for a redesign.",
        page_angle="Lofts Studio should position this as senior website engineering: sitemap, URL structure, schema, Core Web Vitals, internal links, service-page hierarchy, proof sections, and a conversion path planned before visual polish.",
        checks=[
            ("Opening answer", "Define SEO-friendly design in plain language.", "It helps Google and answer engines extract the core promise quickly."),
            ("Technical base", "Show crawlability, canonicals, sitemap, robots, speed, and schema.", "These are the common reasons a pretty site still fails in search."),
            ("Service hierarchy", "Explain parent, child, and support pages.", "This prevents thin pages and builds topical authority."),
            ("Trust proof", "Add process, portfolio, founder context, and measured QA.", "Service buyers need confidence before they contact a developer."),
            ("Lead path", "Link to free audit, website hub, and contact.", "Traffic only matters when the next step is obvious."),
        ],
        related_links=[
            ("Website design by industry", "/websites", "parent commercial page for service-business website work"),
            ("Free website audit", "/free-audit/", "low-friction entry point for owners unsure what to fix"),
            ("Technical SEO audit", "/services/technical-seo-audit.html", "implementation-led technical support"),
            ("SEO/AEO checker", "/tools/seo-aeo-checker.html", "quick self-check for answer clarity and indexability"),
        ],
    ),
    make_service_business_post(
        slug="website-development-for-service-businesses",
        title="Website Development for Service Businesses: Build for Search and Leads",
        excerpt="A practical website development plan for service businesses that need better search visibility, trust, speed, and enquiries.",
        meta="Website development for service businesses focused on search intent, technical SEO, mobile trust, service pages, and qualified lead flow.",
        category="Design",
        primary="website development for service businesses",
        secondary="business website development",
        funnel_to="/websites",
        funnel_label="Website Design Hub",
        market_signal="DataForSEO showed very large demand around website development and development website, but the live SERP is dominated by broad educational and builder results. Lofts should not chase that broad head term alone. It should use service-business modifiers and conversion-led examples to narrow the intent.",
        searcher_problem="A business owner may know the website is outdated, but not know whether they need a redesign, new service pages, technical SEO, better booking, or a stronger lead funnel. The content should help them diagnose the actual need.",
        page_angle="Lofts Studio should frame development as a business system: structure, copy, UI, technical SEO, analytics, integrations, and QA working together so the site can be found and chosen.",
        checks=[
            ("Discovery", "Map services, locations, buyer questions, and current traffic.", "Good development starts with the customer path, not a blank template."),
            ("Information architecture", "Create clear hubs for services, industries, proof, blog, tools, and contact.", "Search engines and buyers need predictable routes."),
            ("Mobile first", "Make phone, audit, booking, and contact actions easy to tap.", "Most service searches begin on mobile."),
            ("Analytics", "Track forms, audit starts, clicks, calls, and useful events.", "Without measurement, SEO work becomes guesswork."),
            ("Maintenance", "Plan redirects, sitemap updates, and content refreshes.", "Service websites need ongoing improvement after launch."),
        ],
        related_links=[
            ("Website design by industry", "/websites", "the commercial hub for service-business pages"),
            ("Process", "/process", "how Lofts plans and ships builds"),
            ("Portfolio", "/portfolio", "proof for the development range"),
            ("Website conversion path audit", "/blog/website-conversion-path-audit.html", "supporting guide for traffic-to-lead flow"),
        ],
    ),
    make_service_business_post(
        slug="veterinary-clinic-website-design-checklist",
        title="Veterinary Clinic Website Design Checklist for Booking and Local SEO",
        excerpt="A veterinary clinic website design checklist for emergency clarity, online booking, new-client registration, local SEO, and trust.",
        meta="Veterinary clinic website design checklist covering emergency info, appointment booking, new-client registration, local SEO, schema, and mobile trust.",
        category="Design",
        primary="website design for veterinary clinics",
        secondary="veterinary clinic website design",
        funnel_to="/websites/veterinary",
        funnel_label="Veterinary Website Design",
        market_signal="DataForSEO found a smaller but clean veterinary website design opportunity, and live SERPs show specialist competitors leading with mobile, SEO, booking, and client acquisition. Lofts can compete by making the page more operational: emergency routes, registration, service pages, local proof, speed, and measurement.",
        searcher_problem="A veterinary practice owner wants more booked appointments and more confident pet owners, not just a nicer homepage. The page has to address urgent searches, routine bookings, client registration, trust, and local visibility.",
        page_angle="Lofts Studio should make the veterinary offer specific: emergency info above the fold, appointment paths, service pages, pet-owner reassurance, Google Business Profile alignment, and local SEO that supports real booking intent.",
        checks=[
            ("Emergency path", "Emergency and out-of-hours details must be instantly visible.", "These are high-intent, high-stress searches."),
            ("Booking path", "Online booking, phone, and new-client registration should be clear.", "The site should reduce friction before the receptionist is involved."),
            ("Service pages", "Separate vaccinations, dentistry, surgery, diagnostics, wellness, and urgent care.", "Specific pages match specific pet-owner queries."),
            ("Trust", "Use team bios, clinic photos, reviews, and care process.", "Pet owners choose on reassurance as much as convenience."),
            ("Local SEO", "Use location, hours, schema, nearby service areas, and GBP consistency.", "Local relevance is the core channel for clinics."),
        ],
        related_links=[
            ("Veterinary website design", "/websites/veterinary", "main commercial page for the niche"),
            ("Medical clinic websites", "/websites/medical-clinics", "adjacent clinic architecture"),
            ("Free website audit", "/free-audit/", "starting point for clinic owners"),
            ("Mobile lead flow audit", "/blog/mobile-lead-flow-audit.html", "supporting mobile conversion guide"),
        ],
    ),
    make_service_business_post(
        slug="veterinary-emergency-page-website-seo",
        title="Veterinary Emergency Page SEO: What Pet Owners Need First",
        excerpt="How a veterinary emergency page should answer urgent searches, show out-of-hours details, and route pet owners without confusion.",
        meta="Veterinary emergency page SEO guide for urgent pet-owner searches, out-of-hours information, mobile calls, schema, and local trust.",
        category="SEO",
        primary="veterinary emergency page SEO",
        secondary="emergency vet website page",
        funnel_to="/websites/veterinary",
        funnel_label="Veterinary Website Design",
        market_signal="The veterinary SERP pattern rewards useful, fast, local pages that answer immediate questions. Emergency intent is sharper than generic clinic design intent, so Lofts should support the main veterinary page with this urgent-search guide.",
        searcher_problem="Someone searching emergency vet terms wants to know whether the clinic can help now, whether it is open, where to go, and what to do next. If the page hides that information, the visitor leaves.",
        page_angle="Lofts Studio should show clinic owners how to build an emergency page that is human-first and search-ready: phone action, location, hours, triage notes, out-of-hours partner, and schema that reflects visible content.",
        checks=[
            ("Immediate action", "Put phone, address, hours, and emergency instructions first.", "Urgent visitors do not read a long brand story first."),
            ("Mobile tap targets", "Make call and map actions large and persistent enough.", "Emergency searches are often on mobile."),
            ("Scope", "Explain what the clinic can and cannot handle after hours.", "Clear scope prevents dangerous confusion."),
            ("Local proof", "Connect location, nearby areas, and service context naturally.", "Emergency vet searches are strongly local."),
            ("Schema", "Use accurate LocalBusiness or VeterinaryCare markup where applicable.", "Structured data should match visible facts, not invent claims."),
        ],
        related_links=[
            ("Veterinary website design", "/websites/veterinary", "parent niche page"),
            ("Technical SEO audit", "/services/technical-seo-audit.html", "schema and crawl support"),
            ("Core Web Vitals checklist", "/blog/core-web-vitals-redesign-checklist.html", "speed support for urgent searches"),
            ("Contact Lofts Studio", "/#contact", "consultation path for clinic rebuilds"),
        ],
    ),
    make_service_business_post(
        slug="insurance-agency-local-seo-website-plan",
        title="Insurance Agency Local SEO Website Plan for Quote Requests",
        excerpt="A local SEO website plan for insurance agencies that need quote intent, product pages, trust proof, and cleaner follow-up paths.",
        meta="Insurance agency local SEO website plan for quote requests, product pages, location pages, trust proof, schema, and lead tracking.",
        category="SEO",
        primary="insurance agency local SEO website",
        secondary="insurance agency website design",
        funnel_to="/work/insurance-finance",
        funnel_label="Insurance and Finance Work",
        market_signal="Lofts already has finance and insurance proof, and the niche research ranked insurance agencies as a strong target because the searches have business value while many pages still look generic. The page should connect quote flow, product depth, local trust, and compliance-aware copy.",
        searcher_problem="An insurance agency wants more quote requests, but prospects often need product clarity, carrier context, local trust, and a fast way to ask for help. A generic brochure website does not cover that decision path.",
        page_angle="Lofts Studio should position insurance websites as quote systems: product pages, local pages, lead forms, call tracking, proof, disclaimers, speed, analytics, and a clean path from search to advisor conversation.",
        checks=[
            ("Product pages", "Separate auto, home, commercial, life, and specialty insurance where relevant.", "Different policies create different query families."),
            ("Quote flow", "Make quote requests short and route details to the right team.", "Conversion friction directly reduces leads."),
            ("Trust", "Show licensing context, carriers, reviews, team, and local proof where true.", "Financial-services buyers need credibility."),
            ("Location relevance", "Use city/service-area pages only when the agency truly serves them.", "Fake location scale creates trust and indexing risk."),
            ("Measurement", "Track form starts, submissions, calls, and source pages.", "Lead quality matters more than traffic volume."),
        ],
        related_links=[
            ("Insurance and finance work", "/work/insurance-finance", "proof-led commercial page"),
            ("Conversion path audit", "/blog/website-conversion-path-audit.html", "how quote traffic becomes leads"),
            ("Technical SEO audit", "/services/technical-seo-audit.html", "crawl and schema support"),
            ("Free website audit", "/free-audit/", "first step for an underperforming agency site"),
        ],
    ),
    make_service_business_post(
        slug="optometrist-website-seo-service-page",
        title="Optometrist Website SEO: Appointments, Insurance, Local Trust",
        excerpt="How an optometrist website service page should cover exams, frames, insurance, doctor trust, local search, and booking flow.",
        meta="Optometrist website SEO service page guide for eye exams, appointment booking, insurance clarity, local SEO, doctor trust, and conversion flow.",
        category="SEO",
        primary="optometrist website SEO",
        secondary="optometrist website design",
        funnel_to="/websites/opticians",
        funnel_label="Opticians Website Design",
        market_signal="The Lofts niche plan treats optometry and ophthalmology as a strong healthcare target because appointment intent, insurance questions, and local trust are clear. Competitors often talk about design but under-explain the page architecture needed for exams, locations, doctors, and insurance.",
        searcher_problem="An eye-care practice needs patients to understand available exams, accepted insurance, frame or lens options, doctors, and how to book. If the website blends everything into one page, it loses both search relevance and confidence.",
        page_angle="Lofts Studio should expand opticians into an eye-care SEO system: exam pages, doctor/location pages, insurance information, appointment CTAs, FAQ coverage, and local schema aligned with real practice details.",
        checks=[
            ("Appointment path", "Put online booking and phone options near every service section.", "Eye-care searches often turn into appointment actions."),
            ("Insurance clarity", "Explain accepted insurance or how to verify benefits where true.", "Insurance uncertainty blocks bookings."),
            ("Doctor trust", "Show doctors, credentials, specialties, and care style.", "Medical buyers need human reassurance."),
            ("Service depth", "Separate eye exams, contacts, glasses, pediatric care, and urgent eye care if offered.", "Each service has its own query family."),
            ("Local consistency", "Match website, GBP, hours, phone, address, and schema.", "Local mismatches weaken confidence and search clarity."),
        ],
        related_links=[
            ("Opticians and eye care websites", "/websites/opticians", "main niche page"),
            ("Medical clinic websites", "/websites/medical-clinics", "adjacent healthcare structure"),
            ("SEO/AEO checker", "/tools/seo-aeo-checker.html", "quick page clarity check"),
            ("Free website audit", "/free-audit/", "entry point for practice owners"),
        ],
    ),
    make_service_business_post(
        slug="orthodontist-website-consultation-funnel",
        title="Orthodontist Website Consultation Funnel for Local SEO",
        excerpt="A practical orthodontist website funnel for treatment pages, parent and adult patient trust, local SEO, and consultation booking.",
        meta="Orthodontist website consultation funnel covering braces, Invisalign-style intent, local SEO, parent trust, adult patients, and booking flow.",
        category="CRO",
        primary="orthodontist website consultation funnel",
        secondary="orthodontist website design",
        funnel_to="/websites/dentists",
        funnel_label="Dental Website Design",
        market_signal="Orthodontist terms are a strong second-wave healthcare opportunity for Lofts because consultation value is high and the service-page path is specific. The current dental page can support the cluster while a dedicated orthodontist service page is validated.",
        searcher_problem="Orthodontic visitors compare treatment options, financing questions, before-and-after proof, parent concerns, adult confidence, and consultation availability. A generic dental page cannot carry that full journey.",
        page_angle="Lofts Studio should build orthodontic website content around consultation conversion: treatment pages, trust sections, review proof, doctor profile, local answers, FAQs, and analytics that identify which pages create appointments.",
        checks=[
            ("Treatment pages", "Give braces, clear aligners, retainers, child, teen, and adult pages where relevant.", "Specific treatment intent needs specific content."),
            ("Consultation CTA", "Make the consultation action visible but not aggressive.", "The buyer is comparing trust before committing."),
            ("Proof", "Use real case photos, reviews, and doctor context where allowed.", "Visual and human proof matter in orthodontics."),
            ("Parent/adult paths", "Answer both parent and adult patient concerns.", "The decision maker changes by treatment type."),
            ("Local SEO", "Tie pages to true locations, hours, and service areas.", "Orthodontic competition is local and reputation-led."),
        ],
        related_links=[
            ("Dentist website design", "/websites/dentists", "current parent healthcare page"),
            ("Medical clinic websites", "/websites/medical-clinics", "clinic architecture reference"),
            ("Website conversion path audit", "/blog/website-conversion-path-audit.html", "consultation flow support"),
            ("Free website audit", "/free-audit/", "first diagnostic step"),
        ],
    ),
    make_service_business_post(
        slug="pool-builder-website-project-gallery-template",
        title="Pool Builder Website Project Gallery Template for Better Leads",
        excerpt="How pool builders can turn project photos into SEO pages, trust proof, estimate intent, and stronger local enquiries.",
        meta="Pool builder website project gallery template for SEO, project proof, estimate requests, service-area relevance, and lead quality.",
        category="Design",
        primary="pool builder website project gallery",
        secondary="pool builder website design",
        funnel_to="/websites/landscaping",
        funnel_label="Landscaping Website Design",
        market_signal="Pool builder and landscaping searches share visual proof, project geography, estimate intent, and local-service competition. The opportunity is not another gallery page; it is turning completed work into crawlable proof and quote paths.",
        searcher_problem="A homeowner wants to see whether a builder can deliver a project like theirs, in a similar location, with a clear path to ask for an estimate. A gallery without context wastes the strongest proof on the site.",
        page_angle="Lofts Studio should show pool builders how to structure project galleries as SEO assets: project type, location, materials, constraints, outcome, photos, FAQs, and estimate CTA.",
        checks=[
            ("Project taxonomy", "Tag projects by pool type, material, yard shape, feature, and location.", "This turns visual proof into searchable structure."),
            ("Gallery copy", "Add concise context to every project, not just images.", "Google and buyers need details."),
            ("Estimate CTA", "Place estimate requests after proof and near relevant gallery filters.", "Lead intent rises after the visitor sees similar work."),
            ("Image SEO", "Use compressed images, descriptive alt text, and dimensions.", "Visual pages must stay fast."),
            ("Local proof", "Connect real service areas and project examples.", "Pool builder searches are location-sensitive."),
        ],
        related_links=[
            ("Landscaping website design", "/websites/landscaping", "adjacent local-service page"),
            ("Portfolio", "/portfolio", "Lofts proof architecture"),
            ("Core Web Vitals checklist", "/blog/core-web-vitals-redesign-checklist.html", "image-speed support"),
            ("Free website audit", "/free-audit/", "lead path for visual-service businesses"),
        ],
    ),
    make_service_business_post(
        slug="landscaping-company-website-lead-plan",
        title="Landscaping Company Website Lead Plan for Local Search",
        excerpt="A landscaping company website plan for service pages, seasonal demand, estimate requests, reviews, project photos, and local SEO.",
        meta="Landscaping company website lead plan for local SEO, estimate requests, service pages, project photos, seasonal content, and trust proof.",
        category="SEO",
        primary="landscaping company website leads",
        secondary="landscaper website design",
        funnel_to="/websites/landscaping",
        funnel_label="Landscaping Website Design",
        market_signal="Landscaping remains a strong local-service niche because the buyer intent is visual, seasonal, and location-based. A Lofts page should focus on estimate flow and service-area structure instead of generic web design copy.",
        searcher_problem="A landscaping company needs visitors to understand services, see proof, trust the crew, and request an estimate. If the site hides services behind one gallery or one contact form, the owner loses high-intent searchers.",
        page_angle="Lofts Studio should connect landscaping pages to seasonal content, service pages, project proof, reviews, local schema, and a simple estimate request path.",
        checks=[
            ("Service pages", "Separate lawn care, hardscaping, maintenance, design, and seasonal services where offered.", "Each service earns different searches."),
            ("Estimate path", "Ask only for details needed to qualify the request.", "Long forms reduce lead volume."),
            ("Project proof", "Add before-and-after images with context.", "Visual trust is the sales engine."),
            ("Seasonal pages", "Plan spring cleanup, summer maintenance, fall prep, and winter content.", "Seasonality creates recurring SEO windows."),
            ("Local SEO", "Use true service areas, reviews, and GBP alignment.", "Local relevance decides many landscaping searches."),
        ],
        related_links=[
            ("Landscaping website design", "/websites/landscaping", "main niche page"),
            ("Websites by industry", "/websites", "parent industry hub"),
            ("Website lead funnel audit", "/blog/website-lead-funnel-audit.html", "conversion support"),
            ("Free website audit", "/free-audit/", "first step for local service owners"),
        ],
    ),
    make_service_business_post(
        slug="business-website-development-audit-checklist",
        title="Business Website Development Audit Checklist Before You Rebuild",
        excerpt="A business website development audit checklist for indexability, page structure, lead paths, speed, trust, schema, and analytics.",
        meta="Business website development audit checklist for service companies planning a rebuild, redesign, technical SEO fix, or lead-generation upgrade.",
        category="SEO",
        primary="business website development audit",
        secondary="company website development checklist",
        funnel_to="/free-audit/",
        funnel_label="Free Website Audit Report",
        market_signal="Broad website development demand is huge but vague. The practical opportunity for Lofts is to intercept owners before a rebuild with an audit checklist that turns broad demand into a qualified website-improvement conversation.",
        searcher_problem="The owner knows the website is not working, but may not know whether the problem is indexation, content, trust, speed, design, tracking, or offer clarity. The checklist should help identify the first constraint.",
        page_angle="Lofts Studio should use this as a diagnostic bridge from broad searches to the free audit, technical SEO audit, website hub, and contact path.",
        checks=[
            ("Indexing", "Check robots, canonical, sitemap, redirects, and noindex.", "A rebuilt page has no value if Google cannot serve it."),
            ("Structure", "Map services, support posts, proof, tools, and contact routes.", "Good structure helps both search and navigation."),
            ("Content depth", "Answer buyer questions and objections on the page.", "Thin service pages rarely satisfy serious buyers."),
            ("Speed", "Keep images, scripts, fonts, and layout stable.", "Slow sites leak trust and leads."),
            ("Tracking", "Measure audit starts, contact clicks, form submits, and phone clicks.", "SEO should be judged by business actions."),
        ],
        related_links=[
            ("Free website audit", "/free-audit/", "diagnostic entry point"),
            ("Technical SEO audit", "/services/technical-seo-audit.html", "crawl/indexing implementation"),
            ("Website design by industry", "/websites", "commercial service hub"),
            ("Website structure audit report", "/blog/website-structure-audit-report.html", "supporting structure guide"),
        ],
    ),
    make_service_business_post(
        slug="market-my-website-local-lead-system",
        title="Market My Website: Local Lead System for Service Businesses",
        excerpt="A practical answer for owners searching market my website: fix search intent, service pages, proof, local SEO, and conversion paths.",
        meta="Market my website guide for service businesses that need local SEO, better service pages, proof, technical fixes, and a clearer lead path.",
        category="SEO",
        primary="market my website",
        secondary="market my website local leads",
        funnel_to="/free-audit/",
        funnel_label="Free Website Audit Report",
        market_signal="Market my website is broad and buyer-led. The useful Lofts angle is to help owners understand that marketing a weak website starts with fixing the destination: page intent, trust, speed, internal links, and conversion measurement.",
        searcher_problem="A business owner searching this phrase wants more visibility, but paid traffic, SEO, social posts, and outreach all fail if the website does not answer the visitor's need. The page should explain the order of operations.",
        page_angle="Lofts Studio should own the practical answer: audit the current site, fix the highest-leverage pages, strengthen local/niche search coverage, then use content and promotion only after the lead path works.",
        checks=[
            ("Current traffic", "Check GSC queries and GA4 landing pages first.", "Existing impressions reveal where Google is already testing the site."),
            ("Offer clarity", "Make the service, audience, proof, and next step obvious.", "Marketing cannot fix a confusing offer."),
            ("Local/niche pages", "Build pages around real services, industries, and locations.", "Specific pages can satisfy specific searchers."),
            ("Content support", "Publish articles that support commercial pages, not random topics.", "Topical architecture compounds."),
            ("Conversion path", "Route visitors to audit, quote, booking, or contact.", "Traffic without action is only a vanity metric."),
        ],
        related_links=[
            ("Free website audit", "/free-audit/", "starting point for owners asking how to market the site"),
            ("Website design by industry", "/websites", "commercial service hub"),
            ("SEO Insights to Leads Workflow", "/blog/seo-insights-to-leads-workflow.html", "GSC-to-action workflow"),
            ("Contact Lofts Studio", "/#contact", "direct consultation path"),
        ],
    ),
    {
        "slug": "seo-audit-report-template-for-leads",
        "title": "SEO Audit Report Template for Better Service Website Leads",
        "excerpt": "Use an SEO audit report template to turn technical findings, content gaps, and conversion friction into a lead-focused fix plan.",
        "meta": "A practical SEO audit report template for service websites that need more qualified leads from Google, AI search, and better landing pages.",
        "category": "SEO",
        "date": "2026-07-30",
        "readingTime": "8 min",
        "primaryKeyword": "SEO audit report template for leads",
        "secondaryKeyword": "service website SEO audit report",
        "funnelTo": "/free-audit/",
        "funnelLabel": "Free Website Audit Report",
        "featured": False,
        "intentCardHtml": """<aside class="post-intent-card" aria-labelledby="run-lead-audit-now">
      <h2 id="run-lead-audit-now">Want the audit report for your own site?</h2>
      <form class="post-audit-launcher" action="/free-audit" method="get">
        <label for="lead-audit-url">Website URL to audit</label>
        <div class="post-audit-row">
          <input id="lead-audit-url" name="url" type="url" inputmode="url" placeholder="https://example.com" autocomplete="url" required />
          <button class="btn btn-primary" type="submit">Start report <span aria-hidden="true">&rarr;</span></button>
        </div>
      </form>
      <p>Lofts Studio checks crawlability, page structure, answer clarity, trust signals, and the path from search visitor to qualified inquiry.</p>
      <div class="post-intent-actions">
        <a href="/free-audit" class="btn btn-ghost">Open audit tool</a>
        <a href="/tools/seo-aeo-checker.html" class="btn btn-ghost">Check SEO/AEO</a>
      </div>
      <div class="post-intent-note" aria-label="Audit report includes">
        <span>SEO + AEO</span>
        <span>Lead path</span>
        <span>Fix priority</span>
      </div>
    </aside>""",
        "hook": "An SEO audit report template is useful only if it helps the business decide what to fix first. For a service website, that means connecting crawl health, page quality, internal links, search intent, and lead flow into one clear action plan.",
        "faqs": [
            {
                "question": "What should an SEO audit report template include for a service website?",
                "answer": "It should include indexability, canonical and redirect checks, sitemap status, page intent, content gaps, internal links, schema, mobile UX, trust signals, and the next conversion step for each important page."
            },
            {
                "question": "Should an SEO audit focus only on technical issues?",
                "answer": "No. Technical issues matter, but a service website audit also needs to show how pages convert search visitors into audit requests, calls, messages, or qualified inquiries."
            },
            {
                "question": "How does this help AI search visibility?",
                "answer": "The report should check whether important pages include direct answers, clear entity context, visible proof, FAQs, and structured data that match the content users can see."
            }
        ],
        "body": [
            ("p", "A weak audit report lists issues. A useful report explains the business impact. If a page has a redirect problem, the report should say whether that URL is intentionally retired or whether a valuable page is being hidden from search. If a service page has traffic but no leads, the report should show whether the next step is visible, trusted, and easy to complete."),
            ("callout", "The goal is not to create a longer checklist. The goal is to create a fix order that improves indexability, useful content, and lead quality."),
            ("h2", "The lead-focused audit structure"),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Audit area</th><th>Question to answer</th><th>Lead-focused fix</th></tr></thead>
      <tbody>
        <tr><td><strong>Indexability</strong></td><td>Can Google crawl and index the intended URL?</td><td>Fix status code, canonical, robots, sitemap, or redirect path.</td></tr>
        <tr><td><strong>Intent match</strong></td><td>Does the page answer the query the visitor used?</td><td>Add a direct answer, comparison, checklist, or FAQ section.</td></tr>
        <tr><td><strong>Trust</strong></td><td>Does the page prove the business can do the work?</td><td>Add examples, process, outcomes, proof, or owner context.</td></tr>
        <tr><td><strong>Internal links</strong></td><td>Can visitors and crawlers move to the next useful page?</td><td>Link articles, service pages, tools, audit flow, and contact pages.</td></tr>
        <tr><td><strong>Conversion</strong></td><td>Is the next action obvious on mobile and desktop?</td><td>Add audit, consultation, WhatsApp, form, or download path.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Use Search Console before writing new pages"),
            ("p", "Search Console often shows which pages Google is already testing. Pages with impressions, low CTR, indexing issues, or rising queries should be reviewed before the team writes new content. Sometimes the fastest win is a better title, answer box, schema, or internal link on a page that already has data."),
            ("h2", "Add the AEO and GEO layer"),
            ("p", "For answer engines, the report should check whether the page states the business, service, audience, location or market, and useful next step clearly. A direct answer near the top helps, but it should be supported by proof, examples, FAQs, and schema that match visible content."),
            ("h2", "Where Lofts Studio fits"),
            ("p", "Lofts Studio uses this audit style when planning service pages, blog clusters, technical fixes, and landing pages. The work is not just to get noticed. It is to help the right visitor understand the offer, trust the page, and start a conversation."),
            ("h2", "Daily fix order"),
            ("ol", [
                "Check GSC indexing, sitemap, redirects, canonical signals, and top pages.",
                "Check Ahrefs or SEMrush for competitor pages and content gaps.",
                "Refresh pages that already have attention before building thin new pages.",
                "Add a direct answer, proof section, internal links, schema, and lead path.",
                "Deploy, live-check, and record the URL for follow-up measurement."
            ]),
        ],
    },
    {
        "slug": "website-conversion-path-audit",
        "title": "Website Conversion Path Audit: Turn SEO Traffic Into Better Leads",
        "excerpt": "A website conversion path audit checks whether visitors can move from search query to trust, proof, offer, and inquiry without getting lost.",
        "meta": "Run a website conversion path audit to turn SEO and AI-search traffic into qualified leads through better pages, CTAs, proof, and follow-up paths.",
        "category": "CRO",
        "date": "2026-07-30",
        "readingTime": "8 min",
        "primaryKeyword": "website conversion path audit",
        "secondaryKeyword": "turn SEO traffic into leads",
        "funnelTo": "/free-audit/",
        "funnelLabel": "Free Website Audit Report",
        "featured": False,
        "intentCardHtml": """<aside class="post-intent-card" aria-labelledby="run-conversion-audit-now">
      <h2 id="run-conversion-audit-now">Check your own conversion path</h2>
      <form class="post-audit-launcher" action="/free-audit" method="get">
        <label for="conversion-audit-url">Website URL to audit</label>
        <div class="post-audit-row">
          <input id="conversion-audit-url" name="url" type="url" inputmode="url" placeholder="https://example.com" autocomplete="url" required />
          <button class="btn btn-primary" type="submit">Start audit <span aria-hidden="true">&rarr;</span></button>
        </div>
      </form>
      <p>The audit looks for first-screen clarity, proof, internal links, form friction, mobile UX, and whether the page gives search visitors a reason to take the next step.</p>
      <div class="post-intent-actions">
        <a href="/free-audit" class="btn btn-ghost">Open audit tool</a>
        <a href="/#contact" class="btn btn-ghost">Discuss a rebuild</a>
      </div>
      <div class="post-intent-note" aria-label="Conversion audit includes">
        <span>First screen</span>
        <span>Proof path</span>
        <span>Lead action</span>
      </div>
    </aside>""",
        "hook": "SEO traffic does not become a lead by accident. The page has to answer the query, prove the business can help, remove doubt, and make the next action easy. A conversion path audit checks that full journey.",
        "faqs": [
            {
                "question": "What is a website conversion path audit?",
                "answer": "It is a review of how a visitor moves from landing page to trust, offer, proof, call to action, form, message, or booking. It checks whether the page turns search traffic into a qualified business action."
            },
            {
                "question": "Is this different from a normal CRO audit?",
                "answer": "Yes. A conversion path audit for SEO starts with the search intent and landing page, then follows the visitor through internal links, proof, forms, and follow-up actions."
            },
            {
                "question": "Which pages should be audited first?",
                "answer": "Start with pages that get impressions, clicks, paid traffic, backlinks, service intent, or existing leads. Those pages have more evidence and faster upside."
            }
        ],
        "body": [
            ("p", "A service website can rank and still lose the buyer. The first screen might be vague, the proof might be hidden, the form might ask too much, or the next useful page might not be linked. Search visibility is only the first half of the job."),
            ("callout", "The conversion path starts before the click. The search query tells you what the visitor expects, and the landing page has to confirm that expectation quickly."),
            ("h2", "The conversion path to audit"),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Stage</th><th>What the visitor needs</th><th>What to improve</th></tr></thead>
      <tbody>
        <tr><td><strong>Query</strong></td><td>A page that matches the problem they searched.</td><td>Align title, H1, intro answer, and page type.</td></tr>
        <tr><td><strong>First screen</strong></td><td>Clarity on who the page helps and what happens next.</td><td>Add a direct answer, service fit, and primary action.</td></tr>
        <tr><td><strong>Proof</strong></td><td>Reasons to trust the business.</td><td>Add process, screenshots, examples, testimonials, or case evidence.</td></tr>
        <tr><td><strong>Decision</strong></td><td>A clear way to compare options or scope.</td><td>Add checklist, FAQ, risk notes, and internal links.</td></tr>
        <tr><td><strong>Action</strong></td><td>A low-friction next step.</td><td>Audit tool, contact form, WhatsApp, calendar, or scoped request.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Use analytics to find friction"),
            ("p", "GA4 can show landing pages, engagement, scroll behavior, events, and paths. Search Console can show the queries and pages earning attention. Together, they tell you where the visitor arrived, what they expected, and whether the page encouraged a meaningful action."),
            ("h2", "Improve the page before adding more content"),
            ("p", "If a page already earns impressions but produces weak engagement, refresh the page first. Add a clearer answer, stronger proof, a more useful CTA, better internal links, and schema. New posts should support the page, not distract from the funnel."),
            ("h2", "Make the next step feel natural"),
            ("p", "For Lofts Studio, the next step may be a free audit report, a contact form, a WhatsApp conversation, or a service page. The right CTA depends on the visitor's intent. Someone reading an audit template is closer to the audit tool; someone reading a rebuild guide may need the contact path."),
            ("h2", "Daily conversion audit checklist"),
            ("ul", [
                "Match the page to one search intent and one business goal.",
                "Put a direct answer and primary action near the top.",
                "Add proof before asking for commitment.",
                "Use internal links to connect article, service, audit, and contact paths.",
                "Live-check mobile layout after deployment."
            ]),
        ],
    },
    {
        "slug": "website-structure-audit-report",
        "title": "Website Structure Audit Report + Free Tool",
        "excerpt": "A plain-English website structure audit report guide for checking crawl paths, page hierarchy, internal links, content depth, schema, UX, and conversion before rebuilding anything.",
        "meta": "Use the free website structure audit report tool, then read the checklist for crawl paths, hierarchy, internal links, UX, schema, and leads.",
        "category": "SEO",
        "date": "2026-07-08",
        "modifiedDate": "2026-07-17",
        "readingTime": "12 min",
        "primaryKeyword": "website structure audit report",
        "secondaryKeyword": "website audit report for free",
        "funnelTo": "/free-audit/",
        "funnelLabel": "Free Website Audit Report",
        "featured": False,
        "intentCardHtml": """<aside class="post-intent-card" aria-labelledby="run-structure-audit-now">
      <h2 id="run-structure-audit-now">Need the report, not just the article?</h2>
      <form class="post-audit-launcher" action="/free-audit" method="get">
        <label for="structure-audit-url">Website URL to audit</label>
        <div class="post-audit-row">
          <input id="structure-audit-url" name="url" type="url" inputmode="url" placeholder="https://example.com" autocomplete="url" required />
          <button class="btn btn-primary" type="submit">Start report <span aria-hidden="true">&rarr;</span></button>
        </div>
      </form>
      <p>Open the Lofts Studio audit tool from here. It checks structure, SEO/AEO, trust, broken links, design friction, and the next fixes worth discussing.</p>
      <div class="post-intent-actions">
        <a href="/free-audit" class="btn btn-ghost">Open audit tool</a>
        <a href="/tools/seo-aeo-checker.html" class="btn btn-ghost">Check SEO/AEO compatibility</a>
      </div>
      <div class="post-intent-note" aria-label="Audit report includes">
        <span>PDF report</span>
        <span>Structure + SEO checks</span>
        <span>Fix order</span>
      </div>
    </aside>""",
        "hook": "A website structure audit report should tell you whether the site is built in a way that search engines, answer engines, and real buyers can follow. It is not only a technical checklist. It is a map of where trust, content, navigation, crawlability, and conversion are helping the business or quietly blocking it.",
        "faqs": [
            {
                "question": "What is a website structure audit report?",
                "answer": "A website structure audit report reviews how a site is organized, crawled, linked, understood, and used. It checks page hierarchy, navigation, internal links, indexability, schema, content depth, mobile UX, and conversion paths so the business knows what to fix before redesigning or adding more content."
            },
            {
                "question": "Is a website structure audit different from a technical SEO audit?",
                "answer": "Yes. A technical SEO audit focuses heavily on crawlability, indexability, speed, redirects, canonical tags, schema, and search health. A website structure audit includes those foundations, but also reviews how pages are grouped, how users move through the site, whether the content supports buyer decisions, and whether the next step is clear."
            },
            {
                "question": "What should a website structure audit report include?",
                "answer": "It should include crawl and index checks, sitemap and navigation review, page hierarchy, internal links, heading structure, content gaps, duplicate or thin pages, schema, mobile first-screen review, conversion paths, trust signals, and a prioritized fix plan."
            },
            {
                "question": "Should I audit structure before redesigning a website?",
                "answer": "Yes. A structure audit before a redesign protects the pages, rankings, links, proof, and conversion paths that already work. It also reveals whether the redesign should be a visual refresh, a content rebuild, a technical cleanup, or a full architecture change."
            }
        ],
        "body": [
            ("p", "Most website audits stop too early. They check whether the page loads, whether the title tag exists, whether an image is missing alt text, and whether a few SEO basics are present. That is useful, but it does not answer the bigger question: is the website organized in a way that helps people and search systems understand what the business does?"),
            ("p", "That is the job of a website structure audit report. It looks at the site as a system. Homepage, service pages, blog posts, tools, case studies, location pages, footer links, navigation, forms, schema, and internal links all have to work together. If they do not, the site can have good individual pages and still feel confusing."),
            ("p", "For Lofts Studio, this matters because Search Console is already testing the site around audit-report and compatibility queries. GA4 also shows people are using the audit tool and downloading reports. That is a useful early signal: visitors do not only want generic web design advice. They want to know what is wrong with a site and what should be fixed first."),
            ("callout", "The practical goal: a website structure audit report should turn a vague feeling that the site is underperforming into a prioritized map of what to fix, what to keep, what to rewrite, and what to measure next."),
            ("h2", "What a website structure audit report actually reviews"),
            ("p", "A good structure audit does not treat every issue as equal. A missing meta description is not the same as a broken conversion path. A weak H2 is not the same as a service page that cannot be found from the navigation. The report should separate foundations, page architecture, content clarity, trust, and next actions."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Audit area</th><th>What it checks</th><th>Why it matters</th></tr></thead>
      <tbody>
        <tr><td><strong>Crawl and index</strong></td><td>Status codes, HTTPS, robots, noindex, canonical tags, sitemap, and redirects.</td><td>Pages cannot earn search visibility if Google cannot reliably crawl or index them.</td></tr>
        <tr><td><strong>Page hierarchy</strong></td><td>Homepage, service hubs, service pages, tools, blog posts, case studies, and location paths.</td><td>The site should explain what matters most through structure, not only through copy.</td></tr>
        <tr><td><strong>Internal links</strong></td><td>Navigation, footer, in-content links, related posts, breadcrumbs, and CTA paths.</td><td>Links show users and crawlers which pages belong together and what to do next.</td></tr>
        <tr><td><strong>Content depth</strong></td><td>Direct answers, buyer questions, proof, examples, FAQs, and page uniqueness.</td><td>Thin pages struggle in traditional search and are weaker for answer-led discovery.</td></tr>
        <tr><td><strong>Trust and conversion</strong></td><td>Proof, case studies, forms, report downloads, contact paths, mobile UX, and first-screen clarity.</td><td>Traffic only matters if the page helps the visitor trust the business and take action.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Start with the crawlable map"),
            ("p", "The first layer is simple: can search engines access the important pages, and is the site telling a consistent story about which URLs matter? This includes the XML sitemap, robots.txt, canonical tags, status codes, redirects, and indexability rules."),
            ("p", "This is where many redesigns go wrong. A team starts with visuals, then later discovers old service pages were removed, useful blog posts were orphaned, redirects were missed, or canonical tags point at the wrong place. The damage is usually avoidable if structure is audited before the rebuild."),
            ("ul", [
                "Check that the sitemap includes the pages you actually want discovered.",
                "Confirm important pages return 200 status codes and are not blocked by robots.txt or noindex.",
                "Review canonical tags so each page points to its preferred public URL.",
                "Map old URLs before removing or renaming pages.",
                "Check whether redirects lead directly to the best replacement page.",
                "Look for important pages that exist but are not linked from the site."
            ]),
            ("p", "This is also why the <a href='/free-audit'>free website audit report</a> starts with reachability and technical signals before it talks about design. If the page cannot be reliably accessed, the rest of the advice sits on weak ground."),
            ("h2", "Review the page hierarchy like a buyer would"),
            ("p", "Page hierarchy is the skeleton of the site. A good hierarchy tells a visitor what the business does, who it helps, how the services relate, where proof lives, and what the next step should be. A weak hierarchy makes every page feel like a separate island."),
            ("p", "For a service business, the structure usually needs a clear homepage, service hub or service pages, proof or portfolio pages, educational guides, tools, about page, contact path, and sometimes location or industry pages. The exact shape depends on the business, but the rule is consistent: the most valuable offers should not be buried."),
            ("p", "A structure audit should ask whether the site has a clear path from broad interest to commercial action. For example, someone may land on an article about an audit checklist, then move to a free audit tool, then read a technical SEO service page, then submit a form. If those pages are not linked together, the site loses momentum."),
            ("h2", "Find orphaned and under-linked pages"),
            ("p", "An orphaned page is a page that exists but is not meaningfully linked from other pages. Search engines may still discover it through a sitemap, but users rarely will. More importantly, the site is not sending authority or context to that page through internal links."),
            ("p", "This is especially common on sites that publish many blog posts, campaign landing pages, or location pages. The page goes live, gets added to the sitemap, and then slowly disappears from the real user journey. A website structure audit should identify those pages and decide whether to strengthen, merge, redirect, or remove them."),
            ("ul", [
                "Important commercial pages should be linked from navigation, footer, related blog posts, and relevant case studies.",
                "Support articles should link back to the service or tool they support.",
                "Case studies should link to the service category they prove.",
                "Location pages should link to parent state or country pages and related service pages.",
                "Old posts with similar intent should be consolidated or linked into a clearer cluster."
            ]),
            ("h2", "Check whether the content architecture matches search intent"),
            ("p", "A structure audit is not only about menus and URLs. It also reviews whether each important page matches the reason someone would search for it. A page targeting an audit-report query should show what the report checks, how to interpret it, what to fix first, and what happens after the audit. A page targeting a technical SEO service should explain diagnosis, implementation, validation, and measurement."),
            ("p", "If the content does not match intent, more internal links will not save it. The page may need a clearer answer near the top, a better section order, a stronger table or checklist, proof near the claim, and a CTA that fits the visitor's stage."),
            ("p", "This is where SEO and AEO overlap. The page has to be useful to a searcher, but it also has to be easy for answer engines to summarize. That means direct answers, descriptive headings, clean schema, and enough original detail to be worth citing."),
            ("h2", "Use the first screen as a structural test"),
            ("p", "The first screen tells you whether the page knows what job it is doing. A strong first screen answers three questions quickly: what is this page about, who is it for, and what should I do next? A weak first screen may look polished but still leave the visitor unsure."),
            ("p", "For a website audit or SEO page, the first screen should not hide behind vague lines like <em>we build digital experiences</em>. It should say what kind of audit or service it offers, what the visitor will learn, and why the next step is worth taking."),
            ("p", "A structure audit should review first-screen clarity on the homepage, core service pages, tool pages, and high-traffic posts. If a page earns impressions but has poor CTR or weak engagement, the first screen is one of the first places to look."),
            ("h2", "Check headings and answer blocks"),
            ("p", "Headings are not decoration. They are the outline of the page. Search engines, answer engines, screen readers, and impatient humans all use headings to understand what comes next. If the headings are vague, repeated, or purely creative, the page becomes harder to scan."),
            ("p", "A good audit report should identify whether each key page has one clear H1, descriptive H2s, and short answer blocks under the sections where buyers expect them. The goal is not keyword stuffing. The goal is making the page easy to understand without reading every sentence."),
            ("ul", [
                "Use one H1 that names the page topic.",
                "Use H2s for the questions or decisions the page answers.",
                "Add short answer paragraphs before deeper explanations.",
                "Use tables when the visitor is comparing options.",
                "Use ordered lists when the visitor needs steps.",
                "Use FAQs for genuine buyer questions, not filler."
            ]),
            ("p", "If the page is meant to support AI search or answer-led discovery, run it through the <a href='/tools/seo-aeo-checker.html'>SEO/AEO compatibility checker</a> after the structure pass. That gives a second view on whether the page can be crawled, understood, trusted, and chosen."),
            ("h2", "Look for thin, duplicate, or overlapping pages"),
            ("p", "Thin pages are not always short. A long page can still be thin if it repeats broad claims without helping the reader make a decision. Duplicate pages are not always copied word-for-word. Two pages can compete with each other if they target the same intent with slightly different phrasing."),
            ("p", "A structure audit should identify cannibalization before the site adds more content. If two posts are trying to rank for the same audit term, decide which one should be the main guide and which one should link into it, be merged, or be redirected. If service pages and blog posts overlap, clarify the job of each page."),
            ("p", "This is one reason I prefer fewer excellent pages over a large library of thin posts. A site with a clean cluster around audit reports, technical SEO, AEO, AI visibility, and conversion can outperform a larger site that publishes disconnected articles."),
            ("h2", "Audit trust signals in the page flow"),
            ("p", "Trust signals should not live only in a footer or a portfolio grid. They should appear where the visitor needs reassurance. If a page says the audit finds conversion friction, show what kind of friction the audit checks. If it says the report is client-ready, explain what is included and how a non-technical owner should read it."),
            ("p", "For service pages, proof might be case studies, process detail, screenshots, before-and-after explanations, or real examples of the checks being performed. For audit tools, proof comes from the clarity of the report itself: useful findings, readable categories, PDF download, broken-link scan, design analysis, technical snapshot, and a plain-English fix order."),
            ("p", "GA4 already shows audit runs, completions, and downloads. That means the report experience is not just an SEO asset. It is part of the conversion path. The structure audit should treat it as a key page, not a side tool."),
            ("h2", "Review schema after visible content is fixed"),
            ("p", "Schema should confirm what the page visibly says. It should not invent a richer version of the business than the visitor can see. A website structure audit should check whether schema types match the page: Organization, WebSite, WebPage, BreadcrumbList, Article, FAQPage, Service, Product, or LocalBusiness where appropriate."),
            ("p", "The most common schema issue is not the absence of markup. It is mismatch. FAQ schema for hidden questions, service schema for vague pages, review markup without visible review context, or duplicate organization data can create confusion. Clean schema is better than heavy schema."),
            ("p", "For audit-report content, visible FAQs and matching FAQPage schema make sense. For a tool page, WebApplication schema can make sense. For a technical SEO service page, Service schema can make sense. The markup should follow the visible structure."),
            ("h2", "Turn the audit into a fix order"),
            ("p", "A report is only useful if it tells the business what to do next. The final section should prioritize issues by impact, not by how easy they were to find. A title tag warning may matter, but it should not outrank an indexability problem, a broken navigation path, or a mobile CTA that visitors cannot use."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Priority</th><th>Fix first when...</th><th>Examples</th></tr></thead>
      <tbody>
        <tr><td><strong>Critical</strong></td><td>The page cannot be accessed, indexed, trusted, or used.</td><td>Server errors, noindex, broken canonical, blocked page, broken form, broken mobile layout.</td></tr>
        <tr><td><strong>High</strong></td><td>The page is visible but unclear or weak for conversion.</td><td>Vague H1, thin service page, no proof, poor first-screen CTA, missing internal links.</td></tr>
        <tr><td><strong>Medium</strong></td><td>The page can work but is harder to understand or choose.</td><td>Weak meta description, incomplete FAQ, shallow comparison, missing schema, under-linked guide.</td></tr>
        <tr><td><strong>Low</strong></td><td>The fix improves polish, sharing, or long-term maintenance.</td><td>Open Graph gaps, small alt text misses, footer cleanup, minor copy consistency.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "A simple structure audit checklist"),
            ("ol", [
                "Export or crawl the full URL list and compare it with the live sitemap.",
                "Mark which pages are commercial, educational, proof, tool, location, legal, or support pages.",
                "Check whether every important commercial page is linked from navigation, footer, and related content.",
                "Find orphaned pages and decide whether to strengthen, merge, redirect, or remove them.",
                "Review the first screen on homepage, service pages, tools, and top posts.",
                "Check H1, H2, answer blocks, FAQs, and content depth for each priority page.",
                "Map internal links between tools, services, guides, case studies, and contact paths.",
                "Validate schema only after the visible content and page role are clear.",
                "Review mobile layout and CTA visibility for the pages that should generate enquiries.",
                "Turn the findings into a fix order with critical, high, medium, and low priorities."
            ]),
            ("h2", "How this should guide a redesign"),
            ("p", "A redesign should not wipe the slate clean without understanding what already works. The structure audit tells you which URLs to preserve, which pages need stronger content, which links need to stay, which templates are weak, which CTAs are hidden, and which pages already have search demand."),
            ("p", "That is how you avoid a redesign that looks better but performs worse. The design system, navigation, content plan, templates, schema, redirects, and measurement plan should all be shaped by the audit. Otherwise the redesign becomes a visual project instead of a business improvement."),
            ("p", "If you want the fast version, use the <a href='/free-audit'>free website audit report</a>. If the site needs deeper implementation, the next step is a <a href='/services/technical-seo-audit.html'>technical SEO audit</a> that turns findings into fixes."),
            ("h2", "Frequently asked"),
            ("h3", "What is the difference between a website audit and a website structure audit?"),
            ("p", "A website audit can review many things: design, SEO, performance, trust, broken links, accessibility, and conversion. A website structure audit focuses specifically on how pages, links, hierarchy, content, schema, and conversion paths work together as a system."),
            ("h3", "How often should a site structure be audited?"),
            ("p", "Audit structure before any redesign, migration, major content expansion, or location-page rollout. For a growing business, a lighter quarterly review is useful because old posts, campaign pages, and service changes can create drift quickly."),
            ("h3", "Can a structure audit improve AI search visibility?"),
            ("p", "Yes, indirectly and often directly. AI search benefits from clear page roles, answer blocks, internal links, schema that matches visible content, and proof that supports claims. Those are all part of a strong structure audit."),
        ],
    },
    {
        "slug": "shopify-theme-customization-modify-or-rebuild",
        "title": "Shopify Theme Customization: Modify or Rebuild?",
        "excerpt": "A senior Shopify decision guide for knowing when to customize the existing theme, when to clean the architecture, and when a rebuild protects the store better.",
        "meta": "Shopify theme customization guide: know when to modify sections, clean Liquid, rebuild templates, and protect speed, SEO, and UX.",
        "category": "Shopify",
        "date": "2026-07-05",
        "readingTime": "12 min",
        "primaryKeyword": "Shopify theme customization",
        "secondaryKeyword": "custom Shopify theme development",
        "funnelTo": "/services/shopify-development.html",
        "funnelLabel": "Shopify Development",
        "featured": False,
        "hook": "Shopify theme customization is not just changing colors, adding sections, or moving a button. The real decision is whether the existing theme can safely support the next stage of the business. Sometimes the right answer is a focused modification. Sometimes the safer answer is a cleaner rebuild. The difference shows up in speed, SEO, app behavior, editing control, and how confidently the team can launch changes later.",
        "faqs": [
            {
                "question": "When should a Shopify theme be customized instead of rebuilt?",
                "answer": "Customize the existing Shopify theme when the architecture is healthy, the templates are easy to edit, the app stack is stable, speed is acceptable, and the requested change is limited to sections, layout, styling, metafields, or content structure."
            },
            {
                "question": "When does a Shopify theme need a rebuild?",
                "answer": "A rebuild is usually better when the theme has repeated quick fixes, fragile Liquid, duplicate templates, poor mobile UX, slow first-screen performance, app conflicts, weak SEO structure, or a design direction the current theme cannot support cleanly."
            },
            {
                "question": "Can a Shopify theme rebuild keep the same brand design?",
                "answer": "Yes. A rebuild does not always mean a new brand direction. It can preserve the visual identity while rebuilding the underlying theme structure, sections, templates, product logic, and performance foundation."
            },
        ],
        "body": [
            ("p", "The most common Shopify request sounds simple: can we customize the theme? A founder wants a better homepage, a cleaner product page, a new landing page, a custom bundle section, a different header, stronger trust blocks, improved collection filtering, or a more premium mobile experience. On the surface, that feels like a design task. Under the hood, it is an architecture decision."),
            ("p", "A good Shopify theme can be modified for years. A fragile theme gets worse every time someone touches it. The hard part is knowing which one you have before you add the next feature. That is why Shopify theme customization should start with diagnosis, not a list of visual changes."),
            ("p", "This guide is written for store owners, operators, marketers, and founders who are trying to decide whether to keep improving the current theme or move into a cleaner custom build. It is also useful if you are hiring a Shopify developer and want to understand whether their recommendation is based on engineering reality or just preference."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Decision</th><th>Best when</th><th>Risk if ignored</th></tr></thead>
      <tbody>
        <tr><td><strong>Customize</strong></td><td>The theme is stable, fast enough, easy to edit, and the change is limited in scope.</td><td>A rebuild would slow momentum and add unnecessary complexity.</td></tr>
        <tr><td><strong>Refactor first</strong></td><td>The theme works, but repeated patches, app remnants, and messy sections are starting to slow updates.</td><td>New features keep landing on weak foundations and become harder to maintain.</td></tr>
        <tr><td><strong>Rebuild</strong></td><td>The current theme blocks the UX, mobile layout, SEO structure, performance, or merchandising system the business needs.</td><td>More customization creates a prettier version of the same technical problem.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "What Shopify theme customization really includes"),
            ("p", "Theme customization can mean a lot of different things. It may be a small styling change. It may be a new section. It may be a custom product template, a metafield-powered buying guide, a landing page system, a subscription layout, a wholesale experience, or an app-aware product page that needs custom Liquid and JavaScript."),
            ("p", "On Shopify, the theme controls the storefront experience. It defines templates, sections, blocks, snippets, assets, Liquid logic, app blocks, product media, navigation, collection pages, blog templates, and the editing controls your team sees inside the theme editor. Shopify's theme architecture is built around those parts, so good customization respects the architecture instead of fighting it."),
            ("p", "A clean customization should make the storefront better and the admin experience clearer. If the change makes the store look better for customers but harder for the team to operate, it is only half a win."),
            ("h2", "The first question: what is the theme blocking?"),
            ("p", "Before choosing customize or rebuild, name the actual constraint. Is the current theme blocking conversion, content editing, product merchandising, SEO, speed, mobile usability, app integration, or brand presentation? Each problem points to a different path."),
            ("p", "If the issue is a missing homepage section, a custom product badge, or a better comparison block, customization is usually enough. If the issue is that every template is hardcoded, the product page breaks when an app updates, the first screen is slow, and the team is afraid to publish theme changes, the problem is not a section. The problem is the foundation."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Symptom</th><th>Likely meaning</th><th>Best next step</th></tr></thead>
      <tbody>
        <tr><td>One page needs a stronger layout</td><td>The theme can probably support the change.</td><td>Customize the template or add a reusable section.</td></tr>
        <tr><td>The same issue appears across many templates</td><td>The section system may be weak or inconsistent.</td><td>Refactor shared snippets and templates before adding more features.</td></tr>
        <tr><td>Marketing cannot edit key content</td><td>The theme is not exposing the right settings, blocks, or metafields.</td><td>Build editor-friendly sections and structured fields.</td></tr>
        <tr><td>Mobile layout feels patched together</td><td>The design system may not have been built mobile-first.</td><td>Audit core templates and rebuild the mobile pattern if needed.</td></tr>
        <tr><td>Speed drops after every app or section change</td><td>The theme has weak performance governance.</td><td>Clean scripts, images, section loading, and app placement.</td></tr>
        <tr><td>Developers avoid touching old files</td><td>The theme has become fragile.</td><td>Plan a controlled rebuild or staged refactor.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "When a focused customization is the right move"),
            ("p", "A focused customization is right when the current theme is structurally healthy. The templates are understandable. The theme editor works. The product page is not overloaded with conflicting apps. The navigation and collection pages are usable. Mobile is not fighting the desktop design. Performance is not already failing before the work begins."),
            ("p", "In that situation, the best move is usually to add the smallest clean abstraction that solves the problem. That might be a custom section, a new product template, a reusable snippet, a metafield group, a landing page template, or a better block system inside an existing page."),
            ("ul", [
                "Use customization for a specific product page improvement, such as trust blocks, buying guidance, ingredient/spec tables, delivery messaging, or product comparison.",
                "Use customization for a better homepage section when the current theme already has good spacing, image handling, and mobile behavior.",
                "Use customization for content editing improvements, such as exposing settings, blocks, and metafields to the theme editor.",
                "Use customization for campaign landing pages when the base theme already supports reusable sections.",
                "Use customization when the brand direction is stable and the storefront only needs sharper execution."
            ]),
            ("p", "The key word is focused. A focused customization has a clear job, clear acceptance criteria, and a clean place inside the theme architecture. It does not scatter one-off code across ten files just to ship a visual request faster."),
            ("h2", "When a rebuild becomes the cleaner decision"),
            ("p", "A rebuild becomes the cleaner decision when the existing theme is no longer a reliable platform for change. This does not always mean the store looks bad. Some fragile Shopify themes look polished from the outside. The issue is what happens when the business tries to evolve."),
            ("p", "If every new request requires undoing an old workaround, the theme is asking for a reset. If the mobile product page is carrying desktop assumptions, the first screen is overloaded, app blocks conflict, headings are inconsistent, schema is messy, and nobody knows which snippets are still used, customization becomes risky."),
            ("p", "A rebuild can keep the brand direction while replacing the structure underneath. That matters. Many store owners hear rebuild and imagine starting the whole business identity again. In reality, a senior rebuild can preserve the visual language, improve the editing system, clean the Liquid architecture, simplify app behavior, and make the store easier to run."),
            ("h2", "The middle path: refactor before rebuilding"),
            ("p", "There is a useful middle path between quick customization and full rebuild: refactoring. A refactor keeps the current storefront direction but cleans the parts that are causing friction. This is often the best option for stores that are working well enough to keep live but are becoming harder to maintain."),
            ("p", "A refactor might consolidate duplicate sections, remove unused snippets, clean product media logic, replace hardcoded content with metafields, simplify JavaScript, fix heading structure, or standardize spacing and image behavior. It is not as visible as a redesign, but it can unlock cleaner future customization."),
            ("p", "The right question is not whether a refactor is glamorous. It is whether it reduces future risk. If a one-week cleanup makes the next six months of changes safer, it is often the most responsible move."),
            ("h2", "How Shopify Online Store 2.0 changed the decision"),
            ("p", "Shopify's Online Store 2.0 architecture made theme customization more flexible by using JSON templates, sections, blocks, app blocks, and metafields more deeply. That flexibility is powerful, but it can also hide complexity. A theme can expose many editing controls and still have poor structure behind them."),
            ("p", "JSON templates are useful because they let merchants compose pages with sections. But if every page becomes a unique pile of custom sections, the store slowly loses consistency. A good theme system balances flexibility with guardrails: reusable sections, predictable settings, clean blocks, clear image rules, and templates that make sense to the team editing them."),
            ("p", "The goal is not to create infinite options. The goal is to create the right options. A founder should not need to understand Liquid to update a value proposition, swap a testimonial, adjust a buying guide, or launch a seasonal landing page."),
            ("h2", "The product page is usually the truth test"),
            ("p", "If you want to know whether a Shopify theme is healthy, inspect the product page. It is where design, content, apps, checkout intent, reviews, variant logic, media, subscriptions, bundles, upsells, shipping messaging, and trust all collide."),
            ("p", "A strong product page is not just pretty. It answers buying questions quickly. It handles variants clearly. It keeps the main call to action visible without making the page feel trapped. It gives mobile shoppers enough context before asking for action. It loads the first product media quickly. It uses reviews and social proof without making the page feel crowded."),
            ("p", "If the product page can be improved by adding a few thoughtful sections, customize. If the product page needs five separate apps, duplicate mobile markup, hidden blocks, and fragile JavaScript just to feel normal, consider rebuilding the product template system."),
            ("h2", "Theme customization and SEO are connected"),
            ("p", "A theme decision is also an SEO decision. The theme controls heading structure, internal links, collection content, blog templates, product schema output, image behavior, pagination, canonical patterns, and how much useful content can live on important pages."),
            ("p", "A weak theme can make SEO work harder than it should. Collection pages may have no room for buying guidance. Product pages may hide important details in tabs that render poorly. Blog templates may lack author context or internal links. App scripts may slow the first screen. Schema may be incomplete or contradicted by visible page content."),
            ("p", "This is why Shopify theme customization should be reviewed alongside technical SEO. A visual change that damages crawlability, heading order, internal links, or performance is not an upgrade. It is a trade you may regret later."),
            ("h2", "Theme customization and speed are connected too"),
            ("p", "Every new section, image, app embed, script, animation, and font decision affects performance. The biggest performance issue is rarely one dramatic mistake. It is usually the accumulation of many reasonable-looking choices."),
            ("p", "A homepage slider here, a review widget there, a custom font stack, a hero image loaded too late, a product gallery requesting oversized images, a sticky bar, a tracking script, and a subscription app can work together to delay the first meaningful screen. That is why the best Shopify customization work includes performance rules from the beginning."),
            ("p", "Before adding a new visual component, ask what it loads, when it loads, whether it is needed above the fold, and how it behaves on mobile. If speed is already a problem, read the related guide on <a href='/blog/fix-shopify-lcp-dawn-theme.html'>fixing Shopify LCP on Dawn</a> before adding more first-screen weight."),
            ("h2", "A practical audit before you decide"),
            ("p", "Before approving any major Shopify theme customization, run a short audit. This does not need to be complicated. It needs to answer whether the existing theme can safely absorb the work."),
            ("ol", [
                "Open the theme editor and check whether key homepage, product, collection, and landing page content is editable without code.",
                "Review the product page on mobile and desktop. Look for cramped content, duplicated elements, app conflicts, weak buying guidance, and delayed product media.",
                "Inspect the main templates. Check whether they are structured with reusable sections or scattered one-off code.",
                "Check app embeds and app blocks. Identify what runs on every page and what only needs to run on specific templates.",
                "Run PageSpeed Insights on the homepage, a product page, and a collection page.",
                "Check headings, title tags, collection copy, product schema, and internal links.",
                "Search the theme for unused snippets, old page-builder code, duplicate sections, and hardcoded content.",
                "Ask the marketing team which updates they avoid because the theme feels risky.",
                "Decide whether the next change should be a customization, a refactor, or a rebuild."
            ]),
            ("h2", "What a good Shopify customization brief should include"),
            ("p", "A serious brief does not just say make it look better. It explains what the change must help the customer do and what the team must be able to edit later. That is the difference between design decoration and operational improvement."),
            ("ul", [
                "The target template or flow: homepage, product page, collection page, landing page, cart, blog, or account area.",
                "The buyer problem being solved: trust, comparison, product fit, navigation, mobile clarity, buying confidence, or lead capture.",
                "The editable fields the team needs inside the theme editor.",
                "The app blocks, metafields, tags, collections, or product data the section depends on.",
                "The mobile behavior and first-screen priority.",
                "The SEO requirements: headings, internal links, schema, crawlable content, image alt text, and indexability.",
                "The QA requirements: browser checks, device checks, speed checks, and rollback notes."
            ]),
            ("p", "If a developer cannot turn the request into a clear theme-level brief, the work will probably become a pile of patches. If the brief is clear, even a small customization can feel premium because it fits the system."),
            ("h2", "How to avoid over-customizing the theme"),
            ("p", "Over-customization happens when every new idea becomes a new one-off component. At first, it feels flexible. Later, it becomes slow to edit and hard to trust. The store grows, but the system does not."),
            ("p", "The antidote is reusable thinking. Build sections that can support multiple campaigns. Use metafields when content belongs to products or collections. Use snippets for shared logic. Keep app placement intentional. Avoid hardcoding content that the team will need to change. Keep mobile behavior designed, not patched."),
            ("p", "A premium Shopify build is not the one with the most custom code. It is the one where the custom code has a reason to exist."),
            ("h2", "A simple decision framework"),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Question</th><th>If yes</th><th>If no</th></tr></thead>
      <tbody>
        <tr><td>Can the team edit the important content safely?</td><td>Customize with reusable sections.</td><td>Refactor templates and settings first.</td></tr>
        <tr><td>Is mobile already clean and fast enough?</td><td>Add the new feature carefully.</td><td>Fix the mobile foundation before adding more.</td></tr>
        <tr><td>Are apps placed only where they are needed?</td><td>Keep app behavior scoped.</td><td>Clean app embeds and template loading.</td></tr>
        <tr><td>Does the current design system support the new direction?</td><td>Modify within the system.</td><td>Rebuild the relevant templates or theme layer.</td></tr>
        <tr><td>Will the next six months of changes be easier after this work?</td><td>Proceed.</td><td>Change the plan before adding more code.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Where Lofts Studio fits"),
            ("p", "The work I care about is not simply making Shopify look custom. It is making the store easier to trust, easier to buy from, easier to edit, and easier to improve later. That might mean a tight customization. It might mean a theme refactor. It might mean a custom rebuild when the current theme has run out of road."),
            ("p", "If you are unsure which path fits your store, start with the <a href='/free-audit'>free audit</a>. For implementation, the relevant service is <a href='/services/shopify-development.html'>Shopify development</a>. If performance is the main blocker, pair the theme review with <a href='/services/speed-optimization.html'>speed optimization</a>. If the issue is app logic rather than theme logic, compare it with <a href='/blog/shopify-custom-app-vs-public-app.html'>custom Shopify app vs public app</a>."),
            ("h2", "Sources worth reading"),
            ("ul", [
                "<a href='https://shopify.dev/docs/storefronts/themes/architecture' rel='nofollow noopener'>Shopify developer docs: theme architecture</a>",
                "<a href='https://shopify.dev/docs/storefronts/themes/architecture/templates/json-templates' rel='nofollow noopener'>Shopify developer docs: JSON templates</a>",
                "<a href='https://shopify.dev/docs/storefronts/themes/tools/theme-check' rel='nofollow noopener'>Shopify developer docs: Theme Check</a>",
                "<a href='https://shopify.dev/docs/storefronts/themes/best-practices/performance' rel='nofollow noopener'>Shopify developer docs: theme performance best practices</a>"
            ]),
            ("h2", "Frequently asked"),
            ("h3", "When should I customize my Shopify theme instead of rebuilding it?"),
            ("p", "Customize when the theme is stable, easy to edit, mobile-friendly, and the requested change has a clear place in the existing architecture. Good examples include new sections, better product information blocks, landing page templates, metafield-powered content, or layout improvements."),
            ("h3", "When is a Shopify theme rebuild the better option?"),
            ("p", "A rebuild is better when the current theme slows every change, breaks around apps, performs poorly on mobile, has confusing templates, duplicates code, or cannot support the experience the business now needs. Rebuilding can preserve the brand while cleaning the system underneath."),
            ("h3", "Can a Shopify theme be improved without changing the whole design?"),
            ("p", "Yes. Many stores need architecture cleanup more than a new look. A theme refactor can improve editing controls, Liquid structure, product templates, app placement, and performance while keeping the visual direction familiar."),
        ],
    },
    {
        "slug": "fix-shopify-lcp-dawn-theme",
        "title": "How to Fix Shopify LCP on Dawn Without Breaking Sections",
        "excerpt": "A practical Shopify LCP guide for fixing the real hero, image, Liquid, app, and section problems that slow Dawn-based stores without redesigning the whole theme.",
        "meta": "Fix Shopify LCP on Dawn with hero image priority, responsive media, Liquid cleanup, app script control, font tuning, and Core Web Vitals QA.",
        "category": "Speed",
        "date": "2026-07-03",
        "readingTime": "12 min",
        "primaryKeyword": "fix Shopify LCP",
        "secondaryKeyword": "Shopify Dawn LCP optimization",
        "funnelTo": "/services/speed-optimization.html",
        "funnelLabel": "Speed Optimization",
        "featured": True,
        "hook": "Most Shopify LCP fixes fail because the team optimizes the theme in general, not the exact element Google is measuring. On Dawn and Dawn-based themes, the Largest Contentful Paint element is usually a hero image, banner, product media block, collection image, or large text area above the fold. Fix that element first, then clean the supporting theme, app, font, and section work around it.",
        "faqs": [
            {
                "question": "What is a good LCP score for Shopify?",
                "answer": "A good Shopify LCP score is 2.5 seconds or faster at the 75th percentile of real user visits. PageSpeed Insights and Search Console are useful for field data, while Lighthouse and DevTools are better for diagnosing what to fix."
            },
            {
                "question": "What usually causes poor LCP on Shopify Dawn?",
                "answer": "The most common causes are lazy-loaded hero images, oversized media, missing image dimensions, slow app scripts, render-blocking CSS or JavaScript, too many font files, and above-the-fold sections that ask the browser to do too much before the first useful screen."
            },
            {
                "question": "Can Shopify LCP be fixed without redesigning the store?",
                "answer": "Yes. Many Shopify LCP issues can be fixed inside the existing Dawn-based theme by prioritizing the LCP element, reducing app and section weight, cleaning Liquid output, improving images, and testing templates separately."
            },
        ],
        "body": [
            ("p", "If a Shopify store is slow on mobile, the first instinct is usually to compress images, delete apps, or run a generic speed plugin. Sometimes that helps. Often it does not touch the real problem. Largest Contentful Paint, or LCP, is not a general feeling of speed. It is a specific Core Web Vitals metric that measures when the largest visible content element in the viewport finishes rendering. That means the browser is judging one dominant above-the-fold element, not the whole page equally."),
            ("p", "For many Dawn-based stores, that element is obvious once you look: the homepage image banner, the first collection banner, the product gallery image, a full-width promotion, or a large heading. The work is not to make every asset tiny at once. The work is to make the right element arrive earlier, render cleaner, and stop competing with scripts, fonts, CSS, and sections that do not deserve priority on the first screen."),
            ("p", "This is the exact order I use when a Shopify founder asks why PageSpeed Insights says their store is failing LCP even though the theme looks modern. It is practical, theme-safe, and built for stores that need to keep selling while the performance work happens."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Priority</th><th>What to fix first</th><th>Why it matters</th></tr></thead>
      <tbody>
        <tr><td><strong>1</strong></td><td>Identify the real LCP element on each template.</td><td>You cannot fix LCP reliably until you know whether Google is measuring the hero, product image, banner text, or another above-fold element.</td></tr>
        <tr><td><strong>2</strong></td><td>Give the LCP media the right loading priority.</td><td>The main visual should not be lazy-loaded or forced to wait behind lower-value images and scripts.</td></tr>
        <tr><td><strong>3</strong></td><td>Reduce above-fold section weight.</td><td>Dawn is flexible, but too many sections, app blocks, videos, sliders, and animations above the fold delay the first useful render.</td></tr>
        <tr><td><strong>4</strong></td><td>Control app, font, and script pressure.</td><td>Third-party code often competes with the LCP element before the visitor can even see the product or offer.</td></tr>
        <tr><td><strong>5</strong></td><td>QA home, product, collection, and landing pages separately.</td><td>A homepage fix does not automatically repair product detail pages or collection pages.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "What LCP is actually measuring"),
            ("p", "Google defines LCP as the render time of the largest image or text block visible within the viewport, measured from when the page first starts loading. In plain English: when the first screen finally looks meaningful, the timer stops. The target most teams use is 2.5 seconds or faster for the 75th percentile of real user visits."),
            ("p", "That distinction matters. A Lighthouse lab score can reveal what is wrong, but Search Console and PageSpeed Insights field data show what real users experienced. A store can feel acceptable on a fast office connection and still fail on mobile because real shoppers are loading it on weaker devices, slower networks, and app-heavy product pages."),
            ("p", "On Shopify, the LCP element varies by template. The homepage may be judged on the image banner. A product page may be judged on the first product media image. A collection page may be judged on the collection hero. A blog post may be judged on the title block or featured image. If you only test the homepage, you can miss the pages that actually drive revenue."),
            ("h2", "The Dawn-specific mistake: fixing everything except the measured element"),
            ("p", "Dawn is a strong baseline theme because it is section-based, modern, and designed around Shopify's Online Store 2.0 patterns. The problem is that stores rarely stay close to baseline. They add homepage sections, subscription widgets, review widgets, personalization scripts, sticky bars, tracking tags, popups, page builder remnants, custom font stacks, video embeds, and oversized campaign imagery."),
            ("p", "The theme may still look clean, but the browser's queue is crowded. If the LCP image is lazy-loaded, requested late, too large, or hidden behind render-blocking work, the score gets punished. If the hero section waits for app JavaScript or a custom animation before settling, the user sees a blank or incomplete screen longer than they should."),
            ("p", "That is why the first fix is diagnostic. Do not start with a random list of speed hacks. Start by finding the exact LCP element and the delay attached to it."),
            ("h2", "Step 1: identify the LCP element before editing anything"),
            ("p", "Open PageSpeed Insights for the exact URL you care about and check the LCP element screenshot or diagnostics. Then verify in Chrome DevTools Performance panel if needed. You are looking for a specific node: an image, heading, banner, product media element, or section wrapper that becomes the largest visible piece of content."),
            ("p", "Document this for the homepage, at least one product page, one collection page, and any paid-traffic landing page. Shopify stores often have different problems across templates. The homepage might fail because of a cinematic hero. The product page might fail because the first product image is too large. The collection page might fail because the theme loads filters, collection images, and product cards before the main visible content settles."),
            ("ul", [
                "Record the tested URL, device type, and test date.",
                "Write down the LCP element that PageSpeed Insights identifies.",
                "Check whether the LCP element is an image, video poster, text block, or product media component.",
                "Note whether the element loads late, renders late, shifts, or waits behind scripts.",
                "Repeat after every fix so you know whether the measured element changed."
            ]),
            ("h2", "Step 2: stop lazy-loading the hero or first product image"),
            ("p", "Lazy loading is useful for images below the fold. It is usually wrong for the main above-the-fold image. If the LCP element is a hero image or first product image, it should be loaded eagerly and given stronger priority. In a Dawn-based theme, this often means adjusting the image tag in the relevant section or snippet so the first visible image is not treated like a lower-priority asset."),
            ("p", "The exact file depends on the theme, but common places include image banner sections, slideshow sections, main product media snippets, collection banner sections, and custom landing page sections. The principle is stable: below-fold images can be lazy, but the LCP image should be available as early as possible."),
            ("pre", """<!-- Example principle only. Apply inside the actual Dawn section/snippet. -->
{{ image | image_url: width: 1800 | image_tag:
  loading: 'eager',
  fetchpriority: 'high',
  widths: '750, 1100, 1500, 1800',
  sizes: '100vw',
  alt: image.alt
}}"""),
            ("p", "Do not apply high priority to every image. That just creates a new priority problem. Use it for the image that is actually above the fold and actually being measured as LCP."),
            ("h2", "Step 3: use responsive image sizes that match the layout"),
            ("p", "An LCP image can have the right loading priority and still be too heavy. Many Shopify stores upload hero assets designed for print-level quality, then crop them inside CSS. The browser still has to download more than it needs. The fix is not simply compression; it is sending an appropriate image width for the visitor's viewport and layout."),
            ("p", "For full-width banners, define sensible widths and sizes. For product media, avoid requesting a giant desktop image for a mobile viewport. For split hero layouts, do not use 100vw if the image only takes half the screen on desktop. Use Shopify's image filters and responsive image output so the browser can choose the right candidate."),
            ("callout", "The goal is not to make images ugly. The goal is to stop making mobile users download image data they cannot see."),
            ("h2", "Step 4: reserve dimensions so the first screen does not jump"),
            ("p", "Poor LCP and layout shift often travel together. If the hero image, announcement bar, sticky header, app block, or product media area changes height after load, the browser may delay the final stable paint. Set width, height, aspect ratio, and predictable section spacing so the first screen has a stable shape before assets finish loading."),
            ("p", "This is especially important when a homepage hero uses different desktop and mobile crops. If the mobile crop is taller, define that behavior clearly in CSS. If the desktop version is a split image and text layout, make sure the mobile stack does not wait on desktop-only assets."),
            ("h2", "Step 5: simplify the first screen before touching the whole theme"),
            ("p", "On many stores, the first screen tries to do too much. It contains a top bar, sticky header, mega menu, announcement carousel, image slider, discount popup, review widget, personalization script, chat launcher, animated text, and hero media. Every piece may feel small in isolation. Together they create a traffic jam before the main offer appears."),
            ("p", "The first screen should do three things: show the offer, support trust, and make the next action obvious. Anything that does not help those jobs should move lower, load later, or become lighter."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>LCP culprit</th><th>How it shows up</th><th>Fix</th></tr></thead>
      <tbody>
        <tr><td>Lazy hero image</td><td>PageSpeed identifies the hero as LCP and it starts loading late.</td><td>Load the first hero image eagerly and use high fetch priority only for that element.</td></tr>
        <tr><td>Oversized hero</td><td>The image is visually cropped but the downloaded file is much larger than the viewport needs.</td><td>Use responsive widths, proper sizes, and a mobile-specific crop when needed.</td></tr>
        <tr><td>Slideshow above the fold</td><td>The store waits on multiple slides, animations, or JavaScript before the first meaningful hero appears.</td><td>Prefer one strong static hero. If a slider must stay, prioritize the first slide and delay the rest.</td></tr>
        <tr><td>App block near the top</td><td>Reviews, subscriptions, chat, tracking, or personalization scripts compete before the main content renders.</td><td>Move non-essential app blocks lower and defer scripts that do not affect the first decision.</td></tr>
        <tr><td>Font delay</td><td>The hero text appears late, swaps awkwardly, or waits for multiple font files.</td><td>Limit font weights, preload the critical face, and use font-display behavior that protects readability.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Step 6: control Shopify app scripts with a first-screen rule"),
            ("p", "Apps are not automatically bad. Uncontrolled app loading is bad. Reviews, bundles, subscriptions, loyalty, chat, heatmaps, analytics, upsells, inventory tools, and consent banners can all be legitimate. The question is whether they need to run before the visitor sees the first screen."),
            ("p", "Create a simple rule: if the app does not affect the first above-the-fold decision, it should not compete with the LCP element. A review snippet below the product title may be important on a product page. A loyalty launcher or heatmap script does not need to block the hero. A chat widget can wait until after the main content becomes visible."),
            ("p", "This is where Shopify speed work becomes business work. You cannot remove every app blindly. You have to decide which scripts create immediate value and which can be delayed without hurting conversion."),
            ("h2", "Step 7: reduce font pressure without losing the brand"),
            ("p", "Typography is part of brand quality, but font loading can damage LCP when a page uses too many families, weights, styles, and remote requests. A clean Shopify theme can become slow because it loads a full editorial font system for a homepage that only needs a few critical weights."),
            ("p", "For performance, keep the critical font set narrow. Use fewer weights above the fold. Preload only the font file that is truly needed early. Avoid loading decorative faces before the primary content. If the brand depends on a premium display face, use it with discipline and let body copy rely on a lighter, faster stack."),
            ("h2", "Step 8: clean Liquid output on the templates that matter"),
            ("p", "Dawn gives you a clean starting point, but custom sections can introduce expensive loops, duplicated snippets, hidden desktop/mobile markup, oversized metafield output, and repeated app embed containers. Liquid work matters because the browser cannot render what the server has not delivered."),
            ("p", "Look for sections that output both desktop and mobile versions of the same hero, hidden carousels that still load images, product cards that request too much media, and snippets that repeat app or icon markup many times. The fix is to simplify the markup path for the first screen and load secondary details when the visitor reaches them."),
            ("h2", "Step 9: test mobile and desktop separately"),
            ("p", "A common mistake is fixing desktop screenshots while mobile field data keeps failing. Shopify shoppers are heavily mobile, and mobile LCP is less forgiving. A desktop hero may be fine as a wide image, while the mobile version needs a different crop, smaller art direction, tighter section height, and less JavaScript pressure."),
            ("p", "For each important template, test mobile and desktop. Do not assume the same LCP element is measured on both. On desktop, the largest element might be the hero image. On mobile, it might be the heading because the image is lower or cropped differently. Fix what is measured in the actual viewport."),
            ("h2", "A Shopify LCP repair checklist"),
            ("ol", [
                "Test the exact URL in PageSpeed Insights and record the mobile LCP element.",
                "Repeat for homepage, product page, collection page, and any landing page used in campaigns.",
                "Remove lazy loading from the measured above-the-fold image.",
                "Add fetch priority carefully to the one image that deserves it.",
                "Generate responsive image widths that match the layout instead of sending one oversized asset.",
                "Reserve width, height, and aspect ratio for the LCP media and surrounding section.",
                "Move sliders, videos, popups, and app blocks lower if they are not essential to the first decision.",
                "Delay or defer third-party scripts that do not affect the first screen.",
                "Reduce above-fold font files and weights.",
                "Clean duplicate Liquid markup and hidden sections that still load assets.",
                "Re-test in lab tools, then monitor Search Console Core Web Vitals after real users see the change.",
            ]),
            ("h2", "How to know the fix worked"),
            ("p", "A successful LCP fix should show up in two places. First, the lab test should identify the LCP element earlier and with fewer blocking issues. Second, field data should improve after enough real traffic has visited the updated pages. Do not panic if Search Console takes time to reflect changes. Core Web Vitals field data is not instant."),
            ("p", "Use the lab test for immediate debugging and field data for business confidence. If the lab score improves but real-user data does not, the store may have traffic patterns, device issues, apps, or templates that the lab test did not represent. That is why template-level QA matters."),
            ("h2", "Where this fits inside a full Shopify speed audit"),
            ("p", "LCP is one important metric, not the whole performance story. Interaction to Next Paint, Cumulative Layout Shift, JavaScript execution, app governance, collection filtering, product media, checkout-adjacent scripts, and theme maintainability all matter. But LCP is often the most visible failure because it controls when the page first feels useful."),
            ("p", "If your store has strong products but the first screen feels slow, start here. Find the LCP element, prioritize it, reduce the noise around it, and then move through the rest of the performance stack with discipline."),
            ("p", "For a broader review, use the <a href=\"/free-audit/\">free audit</a>, compare the related <a href=\"/blog/passing-core-web-vitals-on-shopify.html\">Core Web Vitals guide for Shopify</a>, or review the <a href=\"/blog/shopify-technical-seo-audit-checklist.html\">Shopify technical SEO audit checklist</a>. If the store needs implementation, the relevant service page is <a href=\"/services/speed-optimization.html\">Shopify speed optimization</a>."),
            ("h2", "Sources worth reading"),
            ("ul", [
                "<a href=\"https://web.dev/articles/lcp\" rel=\"nofollow noopener\">web.dev: Largest Contentful Paint</a>",
                "<a href=\"https://web.dev/articles/optimize-lcp\" rel=\"nofollow noopener\">web.dev: Optimize Largest Contentful Paint</a>",
                "<a href=\"https://shopify.dev/docs/storefronts/themes/best-practices/performance\" rel=\"nofollow noopener\">Shopify developer docs: theme performance best practices</a>",
                "<a href=\"https://pagespeed.web.dev/\" rel=\"nofollow noopener\">PageSpeed Insights</a>"
            ]),
            ("h2", "Frequently asked"),
            ("h3", "What is a good LCP score for Shopify?"),
            ("p", "Aim for 2.5 seconds or faster at the 75th percentile of real user visits. A single Lighthouse run is useful for diagnosis, but Search Console and PageSpeed Insights field data are better for deciding whether the store is passing for real shoppers."),
            ("h3", "What usually causes poor LCP on Shopify Dawn?"),
            ("p", "The usual causes are lazy-loaded hero images, oversized media, missing image dimensions, app scripts that run too early, render-blocking CSS or JavaScript, heavy font loading, and above-the-fold sections that try to do too much."),
            ("h3", "Can Shopify LCP be fixed without redesigning the store?"),
            ("p", "Yes. If the brand direction is already working, many LCP problems can be fixed inside the existing Dawn-based theme by prioritizing the measured element, cleaning media output, reducing first-screen app pressure, and testing the important templates one by one."),
        ],
    },
    {
        "slug": "ecommerce-geo-product-pages-ai-search",
        "title": "Ecommerce GEO: How Product Pages Get Found in AI Search",
        "excerpt": "AI search and answer engines do not read ecommerce sites like shoppers do. This guide shows how product pages, feeds, schema, and proof work together.",
        "meta": "Ecommerce GEO guide for product pages: AI search, product schema, feeds, category pages, reviews, and conversion paths for Shopify and WooCommerce.",
        "category": "SEO",
        "date": "2026-07-01",
        "readingTime": "12 min",
        "primaryKeyword": "ecommerce GEO",
        "secondaryKeyword": "AI product discovery SEO",
        "funnelTo": "/services/technical-seo-audit.html",
        "funnelLabel": "Technical SEO Audit",
        "featured": False,
        "hook": "Ecommerce GEO is the work of making your products easy for AI search systems, answer engines, shopping agents, and normal buyers to understand. It is not a new trick. It is the tighter version of ecommerce SEO: cleaner product data, clearer product pages, stronger proof, valid schema, crawlable category pages, and a purchase path that does not collapse after the answer.",
        "faqs": [
            {
                "question": "What is ecommerce GEO?",
                "answer": "Ecommerce GEO, or generative engine optimization for ecommerce, is the process of making product pages, category pages, product feeds, schema, reviews, and brand information clear enough for AI search systems and answer engines to understand, cite, and recommend."
            },
            {
                "question": "Is ecommerce GEO different from ecommerce SEO?",
                "answer": "The foundations overlap. Ecommerce SEO focuses on search visibility, crawlability, content, internal links, schema, speed, and conversion. Ecommerce GEO adds stricter emphasis on extractable answers, entity clarity, product data quality, feed consistency, and proof that can support AI-generated recommendations."
            },
            {
                "question": "What should ecommerce brands fix first for AI product discovery?",
                "answer": "Start with the data AI systems need to trust: product titles, product type, variants, availability, product identifiers, shipping and return clarity, Product schema, review signals, category page copy, and internal links from buying guides to product and collection pages."
            },
        ],
        "body": [
            ("p", "Search is moving from a list of links toward answers, comparisons, and recommendations. That does not remove the need for good ecommerce SEO. It raises the standard. A page that only looks good to a human may not be specific enough for a system that is trying to answer questions like <em>which waterproof leather boot is best for wide feet and ships quickly?</em> or <em>which silk scarf looks premium but is easy to gift?</em>"),
            ("p", "The buyer still needs the storefront. The AI layer needs the facts behind the storefront. If those two disagree, the brand becomes harder to recommend. If they line up, the same work improves organic search, rich results, AI answers, product feeds, category pages, and conversion."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Key takeaway</th><th>What it means for an ecommerce site</th></tr></thead>
      <tbody>
        <tr><td><strong>AI search rewards clarity</strong></td><td>Product pages should answer material, fit, compatibility, use case, delivery, returns, and comparison questions without forcing the buyer to hunt.</td></tr>
        <tr><td><strong>Feeds and pages must agree</strong></td><td>Titles, prices, variants, availability, identifiers, product type, and schema should not contradict each other.</td></tr>
        <tr><td><strong>Category pages matter again</strong></td><td>Collections should explain choice, not just list products. They are the bridge between broad intent and product detail.</td></tr>
        <tr><td><strong>Proof is a ranking and conversion asset</strong></td><td>Reviews, FAQs, returns, shipping, brand story, and real photography help both humans and answer systems reduce doubt.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "What ecommerce GEO really means"),
            ("p", "GEO stands for generative engine optimization. In ecommerce, it means structuring the store so AI-generated answers can understand what you sell, who each product is for, when it is the right choice, and whether the claim is trustworthy. It includes traditional SEO work, but it is more demanding because product discovery is no longer only a keyword-to-page match."),
            ("p", "Google's guidance for <a href='https://developers.google.com/search/docs/appearance/ai-features' rel='noopener'>AI features and your website</a> is clear on the broad direction: make pages accessible to Google, create useful people-first content, and keep technical SEO fundamentals strong. For ecommerce, that translates into a very practical system: crawlable product pages, accurate product structured data, complete product feeds, helpful category content, and original information that a competitor cannot copy in one afternoon."),
            ("callout", "The simple rule: if a product fact matters to a buyer, it should be visible on the page, present in the feed when relevant, and confirmed in structured data where the format supports it."),
            ("h2", "Why product pages are vulnerable in AI search"),
            ("p", "Most product pages were built for a familiar journey: a shopper lands on a page, sees images, skims bullets, checks size or variant, and adds to cart. AI search changes the first half of that journey. The recommendation may happen before the shopper ever sees the page. The system may summarize options, compare products, or send the user directly to a short list."),
            ("p", "That makes vague product pages risky. A beautiful PDP with a poetic title, weak attributes, thin description, missing schema, and unclear availability can look premium but remain hard to extract. A less polished page with better structured information may be easier to understand and recommend."),
            ("p", "This is why ecommerce GEO sits between SEO, merchandising, UX, and operations. The page designer, developer, catalog manager, and marketer all touch the signals that decide whether the product is eligible for the right query."),
            ("h2", "The AI product discovery stack"),
            ("p", "A strong ecommerce GEO system has six layers. If one layer is weak, the store may still rank in classic search, but it becomes less dependable in answer-first discovery."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Layer</th><th>What to check</th><th>Why it matters</th></tr></thead>
      <tbody>
        <tr><td>Indexing</td><td>Product and category URLs are crawlable, canonical, and not blocked by robots or noindex rules.</td><td>AI search cannot use pages that search engines cannot reliably access.</td></tr>
        <tr><td>Product data</td><td>Titles, descriptions, variants, product type, brand, identifiers, images, availability, and shipping are complete.</td><td>Specific data helps match long, attribute-heavy buyer prompts.</td></tr>
        <tr><td>Structured data</td><td>Product, Offer, AggregateRating, Review, BreadcrumbList, and FAQ markup match visible content.</td><td>Schema reduces ambiguity and supports eligibility for product-rich search experiences.</td></tr>
        <tr><td>Category context</td><td>Collection pages explain who the products are for, how to choose, and what differentiates them.</td><td>Category pages help answer broad comparison and selection questions.</td></tr>
        <tr><td>Trust proof</td><td>Reviews, policies, delivery promises, product media, materials, guarantees, and support paths are visible.</td><td>Recommendations need confidence, not just relevance.</td></tr>
        <tr><td>Conversion path</td><td>The add-to-cart, checkout, payment, and support paths work cleanly on mobile.</td><td>Visibility without checkout confidence becomes expensive curiosity.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Start with product data quality"),
            ("p", "Product data is the unglamorous part of ecommerce GEO, which is exactly why it becomes an advantage. Many stores spend months polishing homepage sections while letting product titles, attributes, variant names, and availability drift. AI product discovery punishes that drift because it works by matching specific facts."),
            ("p", "A useful product title should identify the item clearly before it tries to be clever. A useful description should include what the product is, who it is for, what problem it solves, what it is made of, how it fits or functions, what is included, and what would make someone choose it over a nearby alternative. This does not mean every description should become a wall of text. It means the facts should exist in a predictable place."),
            ("ul", [
                "Replace internal shorthand with customer-readable product titles.",
                "Use attributes for material, size, color, fit, compatibility, use case, finish, bundle contents, and care instructions where relevant.",
                "Keep variant names human. <em>Walnut / 42 / Wide</em> is easier to understand than an internal code.",
                "Use product type and taxonomy consistently across the catalog.",
                "Make delivery, return, and support information easy to find near the buying decision.",
            ]),
            ("p", "For Shopify stores, this often means cleaning product fields, metafields, collection rules, search engine listings, and theme output. For WooCommerce stores, it usually means cleaning product attributes, taxonomy, variation data, schema output from the theme or SEO plugin, and any feed plugin that sends data to Google Merchant Center or another shopping channel."),
            ("h2", "Use Product schema as a confirmation layer"),
            ("p", "Google's <a href='https://developers.google.com/search/docs/appearance/structured-data/product' rel='noopener'>Product structured data documentation</a> is still one of the best references for ecommerce implementation because it forces the right question: what product facts can search systems verify on this page? Schema should confirm what users can already see. It should not invent ratings, prices, availability, or offers that are not visible and accurate."),
            ("p", "The same discipline applies to <a href='https://schema.org/Product' rel='noopener'>schema.org Product</a>, Offer, Review, AggregateRating, and BreadcrumbList markup. The markup is not a shortcut to authority. It is a machine-readable version of the page's real information."),
            ("html", """<div class="post-table-wrap"><table>
      <thead><tr><th>Field</th><th>Page visibility</th><th>GEO value</th></tr></thead>
      <tbody>
        <tr><td>Product name</td><td>Visible H1 or clear title</td><td>Helps match product identity and query wording.</td></tr>
        <tr><td>Brand</td><td>Shown on PDP or brand area</td><td>Connects the product to a recognizable entity.</td></tr>
        <tr><td>Offers</td><td>Visible price, availability, currency, and condition where relevant</td><td>Supports product-rich results and reduces recommendation risk.</td></tr>
        <tr><td>Aggregate rating</td><td>Visible reviews and rating summary</td><td>Provides proof when it is legitimate and review content is accessible.</td></tr>
        <tr><td>Images</td><td>High-quality product media with useful alt text</td><td>Supports visual trust and richer discovery surfaces.</td></tr>
        <tr><td>Breadcrumbs</td><td>Clear category path</td><td>Helps search systems understand product hierarchy and site structure.</td></tr>
      </tbody>
    </table></div>"""),
            ("h2", "Do not ignore product feeds"),
            ("p", "The page is not the only source AI and shopping systems may use. Product feeds often decide whether a product is eligible for shopping surfaces, product listings, merchant experiences, and future agentic commerce workflows. Google's <a href='https://support.google.com/merchants/answer/7052112' rel='noopener'>Merchant Center product data specification</a> shows the level of detail shopping systems expect: identifiers, titles, descriptions, links, images, availability, condition, price, brand, GTIN or MPN where applicable, shipping, tax, and more."),
            ("p", "The practical lesson is not to memorize every field. It is to stop treating the feed as a background export. The feed is a sales channel. It should be audited like a page. If the PDP says one thing, the feed says another, and schema says a third, the store creates distrust at machine speed."),
            ("ul", [
                "Check that feed titles are not truncated into nonsense.",
                "Confirm out-of-stock and discontinued products are not still promoted as available.",
                "Map variants clearly, especially size, color, material, and bundle differences.",
                "Add product identifiers where the product has them.",
                "Keep shipping and return data consistent with what the shopper sees on site.",
                "Audit feed errors monthly, not only during launch.",
            ]),
            ("h2", "Category pages need real buying guidance"),
            ("p", "Collection and category pages are often the weak middle of ecommerce SEO. They list products but do not help the buyer choose. That is a missed GEO opportunity because AI search often starts from category-level questions: best gifts for new homeowners, sustainable office chairs, premium silk scarves, waterproof boots for travel, or B2B coffee supplies for an office."),
            ("p", "A useful category page should answer the decision behind the category. Who is this range for? How should someone choose? What materials, sizes, features, styles, or constraints matter? Which products are best for different scenarios? What should a buyer know before ordering?"),
            ("p", "This is not doorway-page copy. It is merchandising turned into useful content. A strong category page can link to guides, compare product types, explain care or compatibility, and send shoppers to the right filters or hero products. It also gives AI systems a better summary of the product set than a bare grid can provide."),
            ("h2", "Build PDPs that answer before they sell"),
            ("p", "The strongest product pages answer the buyer's uncertainty before pushing the cart. For AI product discovery, that means the page should support direct answers to common pre-purchase questions. A human might read the FAQ. An answer engine might extract the same information. Both need accuracy."),
            ("ul", [
                "<strong>What is it?</strong> Use a clear product title and first paragraph.",
                "<strong>Who is it for?</strong> Name the use case, audience, or scenario.",
                "<strong>Why this one?</strong> Explain differentiators without vague premium language.",
                "<strong>What are the constraints?</strong> Fit, compatibility, care, sizing, lead time, warranty, or installation requirements.",
                "<strong>Can I trust it?</strong> Reviews, real photography, policies, brand proof, and support visibility.",
                "<strong>What happens next?</strong> Clear add-to-cart, shipping estimate, payment options, and support route.",
            ]),
            ("p", "This is where UX and SEO finally stop pretending to be separate. The same section that helps a visitor choose can help a search system summarize. The same policy block that reduces checkout anxiety can reduce recommendation risk. The same product FAQ can support FAQ schema when the questions are visible and useful."),
            ("h2", "Shopify and WooCommerce implementation notes"),
            ("p", "Shopify and WooCommerce can both support ecommerce GEO, but the implementation risks are different. Shopify usually gives a cleaner hosted foundation, but themes and apps can still output weak schema, duplicate headings, bloated scripts, and inconsistent product data. Shopify's own <a href='https://help.shopify.com/en/manual/promoting-marketing/seo' rel='noopener'>SEO documentation</a> is a useful baseline, but serious stores still need theme-level QA."),
            ("p", "WooCommerce gives more control because it sits on WordPress, but that control creates more variation. The theme, SEO plugin, schema plugin, product feed plugin, caching layer, and custom fields can all affect the final output. A WooCommerce store can be excellent for AI search if the data model is clean. It can also become chaotic if every plugin is trying to describe the product differently."),
            ("callout", "The platform is not the strategy. The strategy is a clean source of truth for product facts, then page, schema, and feed outputs that stay aligned."),
            ("h2", "A 30-day ecommerce GEO implementation plan"),
            ("p", "Do not start by rewriting the whole catalog. Start with the pages that already have impressions, sales, or strategic value. This keeps the project tied to revenue and gives you proof before scaling."),
            ("ol", [
                "<strong>Week 1: audit the top pages.</strong> Pull top product and category URLs from Search Console, analytics, Shopify or WooCommerce reports, and paid traffic data. Check indexing, titles, descriptions, schema validity, feed status, reviews, page speed, and mobile UX.",
                "<strong>Week 2: fix the product data model.</strong> Clean titles, attributes, variants, product type, identifiers, and internal categorization for the highest-value products first.",
                "<strong>Week 3: rebuild the page answer layer.</strong> Add decision-focused descriptions, FAQs, comparison guidance, care or compatibility details, trust blocks, and internal links from related guides.",
                "<strong>Week 4: validate schema, feeds, and conversion.</strong> Test Product schema, check Merchant Center feed issues, confirm canonical URLs, test mobile checkout, and monitor Search Console queries for new long-tail impressions.",
            ]),
            ("p", "That plan can be run inside a focused <a href='/services/technical-seo-audit.html'>technical SEO audit</a>, then turned into implementation work. If the store is on Shopify, pair it with the <a href='/blog/shopify-technical-seo-audit-checklist.html'>Shopify technical SEO audit checklist</a>. If the store is already thinking about AI shopping agents, read <a href='/blog/agentic-commerce-what-it-means-for-shopify.html'>agentic commerce for Shopify</a> as the next layer."),
            ("h2", "How to measure progress"),
            ("p", "Do not judge ecommerce GEO by one ranking screenshot. Use a cluster of signals. Search Console should show more impressions for attribute-heavy product queries and category-level comparison queries. Merchant Center should show fewer product data issues. Product pages should earn richer search appearances where eligible. Analytics should show better engagement from organic landing pages. Most importantly, the buying path should convert more confidently because the page answers better questions."),
            ("ul", [
                "Search Console impressions for product attributes and category modifiers",
                "Product rich result eligibility and structured data validation",
                "Merchant Center feed diagnostics and disapproval trends",
                "Organic revenue or qualified enquiries from product and category landing pages",
                "On-page engagement with FAQs, size guides, reviews, and comparison sections",
                "Mobile checkout completion and support-contact reduction",
            ]),
            ("h2", "Internal links and content cluster ideas"),
            ("p", "A single product page cannot carry the whole topic. Build a cluster around buying decisions. Product pages should link to size guides, material guides, care guides, comparison articles, and category explainers. Articles should link back to the relevant category and hero products. Case studies should show the business result when product data, UX, and search work together."),
            ("ul", [
                "<a href='/blog/ecommerce-conversion-audit.html'>Ecommerce conversion audit</a> for diagnosing PDP and checkout friction.",
                "<a href='/blog/shopify-custom-app-vs-public-app.html'>Shopify custom app vs public app</a> for stores with product-data or integration limits.",
                "<a href='/free-audit'>Free audit</a> for a first pass at technical, SEO, performance, design, and trust issues.",
            ]),
            ("h2", "Image and chart ideas for this post"),
            ("ul", [
                "<strong>Alt text:</strong> Diagram showing how product page content, Product schema, product feeds, reviews, and category pages support ecommerce GEO.",
                "<strong>Alt text:</strong> Table comparing traditional ecommerce SEO signals with AI product discovery signals.",
                "<strong>Alt text:</strong> Product page wireframe highlighting title, attributes, reviews, schema fields, FAQs, and shipping information.",
                "<strong>Alt text:</strong> 30-day ecommerce GEO implementation roadmap for Shopify and WooCommerce stores.",
            ]),
            ("h2", "Sources worth reading"),
            ("ul", [
                "<a href='https://developers.google.com/search/docs/appearance/ai-features' rel='noopener'>Google Search Central: AI features and your website</a>",
                "<a href='https://developers.google.com/search/docs/appearance/structured-data/product' rel='noopener'>Google Search Central: Product structured data</a>",
                "<a href='https://support.google.com/merchants/answer/7052112' rel='noopener'>Google Merchant Center: Product data specification</a>",
                "<a href='https://help.shopify.com/en/manual/promoting-marketing/seo' rel='noopener'>Shopify Help Center: Improving search engine optimization</a>",
                "<a href='https://schema.org/Product' rel='noopener'>Schema.org: Product</a>",
            ]),
            ("h2", "Frequently asked"),
            ("h3", "What is ecommerce GEO?"),
            ("p", "Ecommerce GEO is generative engine optimization for online stores. It makes product pages, category pages, feeds, schema, reviews, and brand signals clear enough for AI search and answer engines to understand and recommend."),
            ("h3", "Is ecommerce GEO different from ecommerce SEO?"),
            ("p", "The foundations overlap. Ecommerce GEO puts extra pressure on product data quality, extractable answers, entity clarity, and consistency between the visible page, structured data, and product feeds."),
            ("h3", "What should ecommerce brands fix first?"),
            ("p", "Fix the product data and page structure for the highest-value products first: titles, attributes, variants, availability, identifiers, Product schema, reviews, delivery information, internal links, and mobile checkout confidence."),
        ],
    },
    {
        "slug": "why-your-website-isnt-showing-up-on-google",
        "title": "Why Your Website Isn\u2019t Showing Up on Google \u2014 and How to Fix It",
        "excerpt": "Your site is live but invisible on Google. Here\u2019s the plain-English reason it happens, how to tell which problem you actually have, and the exact steps to fix it.",
        "meta": "Website not showing up on Google? Here\u2019s how to tell if it\u2019s an indexing problem or a ranking problem \u2014 and the exact steps to get found, for any business.",
        "category": "SEO",
        "date": "2026-06-15",
        "readingTime": "9 min",
        "primaryKeyword": "why isn\u2019t my website showing up on google",
        "secondaryKeyword": "website not showing up on google search",
        "funnelTo": "/services/technical-seo-audit.html",
        "funnelLabel": "Technical SEO Audit",
        "featured": True,
        "hook": "You built the website. You typed your business name into Google. Nothing \u2014 or worse, everyone but you. Before you blame the algorithm, know this: \u201Cnot showing up\u201D is almost always one of a handful of specific, fixable problems, and you can diagnose which one in about fifteen minutes.",
        "body": [
            ("p", "The first thing to get straight is that there are two completely different problems hiding behind \u201Cmy site isn\u2019t on Google,\u201D and the fix for one does nothing for the other. Sort out which you have first, or you\u2019ll waste weeks on the wrong thing."),
            ("h2", "Indexing vs. ranking: which problem do you actually have?"),
            ("p", "<strong>Indexing</strong> is whether Google knows your page exists at all. <strong>Ranking</strong> is where you sit once it does. A brand-new site that has never been crawled has an indexing problem. A two-year-old site sitting on page four has a ranking problem. They feel identical from the outside and they are not."),
            ("callout", "Quick test: search <code>site:yourdomain.com</code> on Google (swap in your real domain). If pages show up, you\u2019re indexed \u2014 your problem is ranking. If nothing shows up, you have an indexing problem. Start there."),
            ("h2", "Reason 1: Google hasn\u2019t indexed your site yet"),
            ("p", "New sites aren\u2019t indexed the moment they go live \u2014 Google has to discover and crawl them first, which can take days or a few weeks. If your <code>site:</code> search came up empty and the site is recent, this is usually it."),
            ("ul", [
                "Set up <strong>Google Search Console</strong> (free) and verify your domain \u2014 this is the single most useful thing you can do for visibility.",
                "Submit your XML sitemap (usually <code>/sitemap.xml</code>) in Search Console so Google has a map of every page.",
                "Use the URL Inspection tool to \u201CRequest indexing\u201D on your most important pages.",
                "Earn a couple of real links \u2014 a Google Business Profile, a social profile, a local directory \u2014 so Google has a path to find you.",
            ]),
            ("h2", "Reason 2: You\u2019re accidentally telling Google to stay away"),
            ("p", "This one catches almost everyone at least once. During a build it\u2019s normal to hide a site from search \u2014 and very easy to forget to switch it back on at launch. If you\u2019re not indexed and the site isn\u2019t brand new, check these in order:"),
            ("ul", [
                "A <code>noindex</code> tag left on the pages (on WordPress: Settings \u2192 Reading \u2192 uncheck \u201CDiscourage search engines\u201D).",
                "A <code>robots.txt</code> file blocking crawlers (<code>Disallow: /</code> blocks the whole site).",
                "A staging site still password-protected or pointed at the wrong domain.",
                "Pages canonicalised to a different URL, so Google indexes that one instead of yours.",
            ]),
            ("p", "Search Console\u2019s Pages report will tell you flatly why a page isn\u2019t indexed \u2014 \u201CExcluded by \u2018noindex\u2019,\u201D \u201CBlocked by robots.txt,\u201D and so on. Read it before guessing."),
            ("h2", "Reason 3: The site is too thin to rank"),
            ("p", "If you\u2019re indexed but invisible, the most common cause is simply that there isn\u2019t enough there. A three-page site with a hundred words total gives Google almost nothing to rank. Pages that actually answer what people search \u2014 clearly, in depth, in plain language \u2014 are what move you up. This is also exactly what AI search engines pull from now, so it does double duty."),
            ("h2", "Reason 4: You\u2019re ranking \u2014 just not on page one"),
            ("p", "Being on Google and being <em>found</em> on Google are different things \u2014 almost nobody clicks past the first page. If you rank but no one sees you, the usual culprits are:"),
            ("ul", [
                "<strong>Keyword mismatch</strong> \u2014 your pages target words you\u2019d use, not the words customers actually type.",
                "<strong>Search intent</strong> \u2014 the page doesn\u2019t match what someone wants when they search that term (buy vs. learn vs. compare).",
                "<strong>Competition</strong> \u2014 head terms are brutal; specific, longer phrases (\u201C[service] in [town]\u201D) are winnable.",
                "<strong>No authority</strong> \u2014 few or no other sites link to you, so Google has little reason to trust you yet.",
            ]),
            ("h2", "Reason 5: For a local business, it\u2019s usually the map, not the website"),
            ("p", "If you run a local business and you\u2019re not appearing for \u201C[what you do] near me,\u201D the issue often isn\u2019t your website at all \u2014 it\u2019s your <strong>Google Business Profile</strong>. The map pack (those top three map results) is ranked separately from the regular blue links, and for local searches it\u2019s where most of the clicks go."),
            ("ul", [
                "Claim and fully complete your Google Business Profile \u2014 category, hours, photos, service area.",
                "Keep your name, address and phone number identical everywhere they appear online.",
                "Ask happy customers for reviews, and reply to them \u2014 it genuinely moves local ranking.",
                "Make sure your website backs the profile up, with your location and services in the page content and structured data.",
            ]),
            ("p", "We build this in by default \u2014 see <a href=\"/websites/\">websites by industry</a> for how each type of local business should be set up to get found."),
            ("h2", "Reason 6: It\u2019s slow, broken, or not mobile-friendly"),
            ("p", "Google ranks the mobile version of your site and treats speed as a real factor. A site that takes five seconds to load on a phone, shifts around as it loads, or breaks on mobile will struggle to rank no matter how good the words are \u2014 and visitors leave before it even finishes. If the basics are shaky, that\u2019s the place to start; see <a href=\"/services/speed-optimization.html\">speed optimization</a>."),
            ("h2", "A 15-minute self-check"),
            ("ol", [
                "Search <code>site:yourdomain.com</code> \u2014 indexed, or not?",
                "If not indexed: check for <code>noindex</code> and <code>robots.txt</code> blocks, then set up Search Console and request indexing.",
                "If indexed: search the exact phrases a customer would use and see where you actually land.",
                "Run your homepage through Google\u2019s PageSpeed Insights \u2014 anything red on mobile is hurting you.",
                "If you\u2019re local, open Google Maps and search your service \u2014 are you in the map pack?",
            ]),
            ("h2", "Frequently asked"),
            ("h3", "How long until a new website shows up on Google?"),
            ("p", "Anywhere from a few days to a few weeks once Google can find it. Setting up Search Console, submitting a sitemap and earning a couple of links speeds it up considerably."),
            ("h3", "Why does my site show up for my business name but nothing else?"),
            ("p", "That\u2019s a ranking and content problem, not an indexing one. Ranking for your own name is easy; ranking for what you <em>do</em> takes pages that target those searches and enough trust signals to compete."),
            ("h3", "Do I need to pay Google to show up?"),
            ("p", "No. Ads buy the paid slots at the top; the organic results below them are earned, not bought \u2014 which is exactly what this article is about."),
        ],
    },
    {
        "slug": "ai-mode-seo-service-businesses",
        "title": "AI Mode SEO for Service Businesses: How to Win Answer-First Searches",
        "excerpt": "Google AI Mode and AI answers reward pages that are easy to understand, verify, and choose from. Here is the practical SEO plan for service businesses.",
        "meta": "AI Mode SEO guide for service businesses: structure pages for answer-first search, Google AI features, entity clarity, proof, schema, and lead capture.",
        "category": "SEO",
        "date": "2026-06-26",
        "readingTime": "11 min",
        "primaryKeyword": "AI Mode SEO for service businesses",
        "secondaryKeyword": "Google AI Mode SEO",
        "funnelTo": "/services/technical-seo-audit.html",
        "funnelLabel": "Technical SEO Audit",
        "featured": False,
        "hook": "AI Mode SEO is not a separate magic channel. It is what happens when search starts answering with synthesis instead of sending every visitor through a list of blue links. For service businesses, the opportunity is simple: become the page that is easiest to understand, verify, and choose when a buyer asks a long, commercial question.",
        "body": [
            ("p", "If your website only says who you are and asks people to book a call, it is thin for AI search. AI answers need facts, comparisons, constraints, examples, proof, and clean page structure. The same things help humans too. That is why the right AI Mode SEO strategy feels less like tricking Google and more like building a website that explains the business properly."),
            ("p", "For Lofts Studio, this matters because buyers are no longer searching only <em>web designer near me</em>. They are asking layered questions: who can redesign my service business website, improve lead quality, connect AI calling agents, fix speed, and explain the work without a giant agency process? A page built for old search may rank for a term. A page built for AI search has to survive follow-up questions."),
            ("callout", "The practical goal: every important service page should answer the question, prove the answer, explain who it is for, show what happens next, and link to the supporting evidence."),
            ("h2", "What AI Mode changes for SEO"),
            ("p", "Traditional SEO often rewarded the best page for a short keyword. AI Mode pushes the search experience toward longer prompts, follow-up questions, and summarized answers. A buyer might ask for the best website redesign approach for a local service business, then ask what it should cost, what to check before hiring, what mistakes to avoid, and which provider seems credible. Your content has to support that whole path."),
            ("p", "That does not mean every page needs to become a giant essay. It means the page needs to expose the useful parts clearly enough for search systems and humans to extract them. A buried claim in a vague paragraph is weak. A short answer, supported by proof, examples, schema, internal links, and a visible CTA is much stronger."),
            ("h2", "The AI Mode SEO stack"),
            ("p", "I would think of AI Mode SEO as six layers working together."),
            ("ol", [
                "<strong>Crawlability.</strong> The page has to be reachable, indexable, fast enough, and not blocked by robots, noindex, broken canonical tags, or heavy client rendering.",
                "<strong>Answer clarity.</strong> The page should define the problem, give a direct answer early, then expand with steps, examples, and caveats.",
                "<strong>Entity clarity.</strong> Search systems should understand the business, services, locations, founders, clients, offers, and proof points without guessing.",
                "<strong>Evidence.</strong> Claims should be supported by case studies, screenshots, reviews, process details, audits, before-and-after examples, and specific outcomes where available.",
                "<strong>Structured data.</strong> Schema should describe visible content accurately: organization, service, article, breadcrumb, FAQ, review, and local business details where appropriate.",
                "<strong>Conversion path.</strong> The answer should lead somewhere useful: audit, consultation, service page, case study, WhatsApp, form, or report download.",
            ]),
            ("p", "If one layer is missing, performance weakens. A beautifully written page that cannot be crawled will not help. A perfectly technical page with no proof will not persuade. A helpful guide with no CTA will educate the buyer and then lose them."),
            ("h2", "Start with the buyer question, not the keyword"),
            ("p", "Keywords still matter because they reveal demand. But AI Mode SEO starts with the full question behind the keyword. For example, <em>website design near me</em> is not just a phrase. The real buyer question might be: who can redesign my website, understand my service business, improve leads, prove they have done it before, and respond quickly?"),
            ("p", "That question needs a different page than a generic service page. It needs local relevance, proof, a clear service model, a low-friction first step, and enough plain-English explanation for the buyer to feel safe. That is why <a href='/blog/local-landing-page-seo.html'>local landing page SEO</a> and AI search optimization now overlap."),
            ("h2", "Build answer blocks into every commercial page"),
            ("p", "An answer block is a short, direct response near the top of the page. It should answer the main question in two to four sentences before the visitor scrolls. This helps both skimming humans and extraction systems. The block should not be fluffy. It should say what you do, who it is for, what outcome you improve, and what makes the approach different."),
            ("p", "For a service page, the first answer block could follow this pattern: <em>We help [audience] solve [problem] by doing [service] with [proof/process]. The right next step is [CTA].</em> That sounds simple because it is. Most websites lose because they hide this basic clarity behind design slogans."),
            ("h2", "Add proof where the claim happens"),
            ("p", "AI answers and buyers both struggle with unsupported claims. If a section says you improve conversions, place a case study, audit sample, before-and-after comparison, or concrete process detail nearby. If a section says you build fast websites, link to speed optimization and show how speed is measured. If a section says you understand AI calling agents, show the workflow: website form, lead routing, script, fallback, CRM, and reporting."),
            ("p", "This is where many agencies fall short. They put proof in a separate portfolio area and leave service pages thin. For AI Mode SEO, proof should be distributed. Each important claim needs enough evidence in its own section so the page can stand alone."),
            ("h2", "Use schema as a confirmation layer"),
            ("p", "Structured data should not invent facts. It should confirm facts already visible on the page. For service businesses, the useful schema usually includes Organization, WebSite, WebPage, BreadcrumbList, Service, Article, FAQPage where the FAQ is visible, and Review or AggregateRating only when review information is legitimate and shown to users."),
            ("p", "The mistake is treating schema like magic dust. Schema does not rescue weak content. It helps search systems understand strong content faster. If the page says one thing and the schema says another, that is not optimization. That is confusion."),
            ("h2", "Create follow-up content around the service"),
            ("p", "AI search is good at follow-up questions. Your site should be too. Around each important service page, publish supporting articles that answer what buyers ask before they convert. A technical SEO audit page can be supported by articles about AI visibility audits, Google AI Overviews, schema, Core Web Vitals, indexing, and local landing pages. A web design page can be supported by articles about redesign checklists, conversion-focused design, SaaS homepages, and service-area pages."),
            ("p", "This is not content for content's sake. It is a topical support system. The service page captures commercial intent. The articles answer objections and comparisons. The case studies prove the work. Internal links tie the whole thing together."),
            ("h2", "What to audit before chasing AI visibility"),
            ("ul", [
                "Can Google index the page, and is the canonical URL correct?",
                "Does the page answer the main buyer question in the first visible section?",
                "Are headings descriptive, or are they only brand phrases?",
                "Does the page define the audience, problem, service, outcome, and next step?",
                "Are important claims supported by nearby proof?",
                "Does schema match visible page content?",
                "Are service pages linked from the nav, footer, blog, and relevant case studies?",
                "Do images have useful context, not just decorative file names?",
                "Does the page load well on mobile and avoid layout shifts?",
                "Is there one obvious CTA for the visitor's current intent?",
            ]),
            ("p", "That audit is where most AI Mode SEO gains begin. Before adding more content, fix the clarity and technical foundations of the pages that already matter."),
            ("h2", "What not to do for AI Mode SEO"),
            ("p", "The fastest way to waste effort is to treat AI search like a loophole. Thin AI-written posts, fake FAQs, hidden schema, copied city pages, and generic expert roundups do not build authority. They make the site larger without making it more useful."),
            ("ul", [
                "Do not publish pages that say the same thing with a different keyword in the title.",
                "Do not add FAQ schema for questions that are not visible and useful on the page.",
                "Do not chase every AI platform with separate duplicate content. Build one strong answer and distribute it cleanly.",
                "Do not hide the actual service offer. AEO content still needs a business outcome and a next step.",
                "Do not let AI tools write claims you cannot prove with process, examples, screenshots, reviews, or case studies.",
            ]),
            ("p", "Good AI Mode SEO is boring in the best way: clear pages, accurate entities, visible proof, fast mobile experience, and useful internal links. It is harder to fake, which is exactly why it can become an advantage."),
            ("h2", "How Lofts Studio should use this"),
            ("p", "The strongest play is not to write one AI SEO article and wait. It is to build a clean cluster: service pages for technical SEO, AI calling agents, web design, CRO, speed, and custom app work; support articles for buyer questions; case studies that prove the work; and a free audit flow that turns curiosity into a useful report."),
            ("p", "The technical SEO audit should become the entry point for people who know something is wrong but do not know whether the issue is design, speed, indexing, AI visibility, or conversion. That is why this post links into <a href='/services/technical-seo-audit.html'>technical SEO audit</a>, <a href='/blog/ai-visibility-audit.html'>AI visibility audit</a>, and <a href='/blog/google-ai-overviews-seo-business-websites.html'>Google AI Overviews SEO</a>."),
            ("h2", "Frequently asked"),
            ("h3", "Is AI Mode SEO different from normal SEO?"),
            ("p", "The foundations are the same: useful content, crawlability, links, speed, structured data, and trust. The difference is the format. AI search rewards content that can answer layered questions and support a recommendation with evidence."),
            ("h3", "Can schema make a business appear in AI answers?"),
            ("p", "Schema helps search systems understand a page, but it does not guarantee inclusion. It works best when it describes visible, useful content that already answers the query well."),
            ("h3", "What is the first fix for a service business?"),
            ("p", "Rewrite the main service pages so each one gives a direct answer, clear audience, visible proof, internal links, schema, and a single next step. Then build supporting articles around the questions buyers ask before they enquire."),
        ],
    },
    {
        "slug": "answer-engine-optimization-checklist",
        "title": "Answer Engine Optimization Checklist for Business Websites",
        "excerpt": "A practical AEO checklist for making business websites easier for Google AI Overviews, AI Mode, ChatGPT, Perplexity, and real buyers to understand.",
        "meta": "Answer engine optimization checklist for business websites: content structure, schema, entity clarity, proof, FAQs, internal links, and conversion paths.",
        "category": "SEO",
        "date": "2026-06-26",
        "readingTime": "12 min",
        "primaryKeyword": "answer engine optimization checklist",
        "secondaryKeyword": "AEO checklist for business websites",
        "funnelTo": "/services/technical-seo-audit.html",
        "funnelLabel": "Technical SEO Audit",
        "featured": False,
        "hook": "Answer engine optimization is the discipline of making your website easy to quote, summarize, trust, and act on. This checklist is built for business websites that need leads, not vanity traffic.",
        "body": [
            ("p", "AEO is often described like a new replacement for SEO. That is the wrong frame. AEO is the stricter version of SEO. If your page is vague, slow, unsupported, hard to crawl, or full of claims with no evidence, answer engines have little reason to use it. If the page is clear, specific, structured, and useful, it becomes easier for both AI systems and buyers to trust."),
            ("p", "Use this checklist before publishing a new service page, city page, landing page, or long-form article. It is designed for founders, agencies, consultants, SaaS teams, ecommerce operators, and local service businesses that want organic leads from search and AI assistants."),
            ("callout", "AEO does not mean writing for robots. It means removing ambiguity so humans and machines can understand the same answer quickly."),
            ("h2", "1. Query and intent checks"),
            ("ul", [
                "Write the main query in plain English before writing the page. Example: <em>Who should I hire for a website redesign that improves leads?</em>",
                "Identify whether the searcher wants a definition, checklist, comparison, local provider, service quote, audit, or implementation partner.",
                "Map the page to one primary intent. Do not make one page serve every possible search.",
                "List five follow-up questions the buyer might ask after reading the first answer.",
                "Decide the right next action: read a service page, request an audit, download a report, call, WhatsApp, or view a case study.",
            ]),
            ("p", "This step prevents the most common AEO mistake: publishing content that is broad enough to mention a topic but too unfocused to answer a real buyer question."),
            ("h2", "2. First-screen clarity checks"),
            ("ul", [
                "The H1 should name the subject directly, not only use a clever slogan.",
                "The first paragraph should answer the main question in plain language.",
                "The page should state who the advice or service is for.",
                "The page should name the outcome: more leads, faster pages, better rankings, cleaner tracking, fewer missed calls, or safer launch.",
                "The first CTA should match the intent. A cold educational visitor may need an audit; a high-intent visitor may need a consultation.",
            ]),
            ("p", "For AI answers, the first screen is the extraction zone. For humans, it is the trust zone. If the top of the page is vague, the rest of the page has to work harder than it should."),
            ("h2", "3. Answer structure checks"),
            ("ul", [
                "Use descriptive H2s that can stand alone as questions or subtopics.",
                "Add short answer paragraphs before long explanations.",
                "Use ordered steps when the answer is sequential.",
                "Use bullets when the answer is a set of criteria, checks, examples, or red flags.",
                "Add comparison sections when buyers are likely choosing between options.",
                "Add caveats when the answer depends on business type, platform, location, budget, or risk.",
            ]),
            ("p", "AEO-friendly structure does not mean making every page look the same. It means choosing the format that makes the answer easiest to use. A comparison needs a comparison. A process needs steps. A service page needs proof and action."),
            ("h2", "4. Entity clarity checks"),
            ("ul", [
                "The business name, service names, founder names, location/service area, and primary industries should be visible on relevant pages.",
                "Use consistent service terminology across navigation, service pages, blog posts, schema, and case studies.",
                "Link from blog posts to the exact service page, not only to the homepage.",
                "Create author or about signals that explain who is behind the advice.",
                "Mention platforms, tools, and methods where they genuinely matter: Shopify, WooCommerce, WordPress, Webflow, Next.js, Core Web Vitals, schema, CRM, AI voice agents, and analytics.",
            ]),
            ("p", "Answer engines need to understand what the business is an entity for. If your site uses five different names for the same service, it becomes harder to connect the dots."),
            ("h2", "5. Proof and trust checks"),
            ("ul", [
                "Place proof near the claim it supports.",
                "Use case studies to show context, not just screenshots.",
                "Add before-and-after explanations where you can show the improvement without overpromising.",
                "Reference real processes: discovery, audit, design, implementation, QA, launch, handoff, reporting.",
                "Use testimonials or review snippets only when they are real and can be supported.",
                "Explain constraints honestly. Not every business needs the same SEO, AEO, AI agent, or rebuild strategy.",
            ]),
            ("p", "Trust is not a badge. Trust is the accumulation of specific details that make a buyer feel the page was written by someone who has actually done the work."),
            ("h2", "6. Schema and technical checks"),
            ("ul", [
                "Confirm the page is indexable and not blocked by robots.txt, noindex, or a wrong canonical URL.",
                "Use Article schema for articles and Service or WebPage schema for service pages where appropriate.",
                "Use FAQ schema only when the questions and answers are visible on the page.",
                "Use BreadcrumbList schema so the page hierarchy is clear.",
                "Use Organization or LocalBusiness schema accurately, with consistent name, URL, logo, and contact paths.",
                "Validate structured data after publishing and fix warnings that affect eligibility or clarity.",
                "Avoid schema that claims reviews, prices, locations, or services that are not visible and true on the page.",
            ]),
            ("p", "Technical AEO is mostly about reducing doubt. Search systems should not have to guess whether the page is an article, service, business profile, location page, or FAQ. The markup should confirm what the user can already see."),
            ("h2", "7. Internal linking checks"),
            ("ul", [
                "Every article should link to a relevant service page.",
                "Every service page should link to supporting guides and case studies.",
                "Every city or state page should link to the main service page and nearby/location-relevant pages.",
                "Use descriptive anchor text like <em>technical SEO audit</em>, not generic anchors like <em>click here</em>.",
                "Link from high-traffic educational posts into commercial pages before the reader reaches the footer.",
                "Create cluster links between related AI search, local SEO, schema, speed, CRO, and website redesign posts.",
            ]),
            ("p", "Internal links are how your site explains itself. They also turn educational traffic into commercial opportunity. This checklist pairs well with <a href='/blog/llm-seo-checklist-business-websites.html'>the LLM SEO checklist</a> and <a href='/blog/schema-markup-ai-search.html'>schema markup for AI search</a>."),
            ("h2", "8. Conversion checks"),
            ("ul", [
                "Add a CTA after the first complete answer, not only at the bottom.",
                "Match CTA language to the buyer stage: audit, compare, get in touch, see work, or request a plan.",
                "Use one primary CTA per page so the visitor is not forced to decide between too many actions.",
                "Make mobile CTAs easy to tap without covering content.",
                "Offer a diagnostic path for unsure visitors, such as a free audit or report download.",
                "Make the form ask only for what is needed to give a useful next response.",
            ]),
            ("p", "AEO content that does not convert is an expensive library. The page should answer the question and then offer the next logical step. For many business websites, that next step is a <a href='/services/technical-seo-audit.html'>technical SEO audit</a> or a focused website review."),
            ("h2", "9. Local and service-area checks"),
            ("ul", [
                "Do not copy the same city page and swap only the place name.",
                "Add local proof, service context, nearby industries, project examples, and unique FAQs.",
                "Make the business model clear if you serve clients remotely across many states or cities.",
                "Use location pages to help buyers understand availability, not to flood search with doorway pages.",
                "Link state pages, city pages, service pages, and case studies in a clean hierarchy.",
            ]),
            ("p", "This matters because local pages are one of the easiest places to create low-quality content at scale. If the page is not useful to a real buyer in that place, it is probably not useful to an answer engine either. Read <a href='/blog/service-area-pages-seo.html'>service area pages SEO</a> before scaling them."),
            ("h2", "10. Measurement checks"),
            ("ul", [
                "Track impressions and queries in Google Search Console after publishing.",
                "Watch which pages earn impressions but low CTR. Those pages may need better titles, descriptions, or opening answers.",
                "Track form submissions, calls, WhatsApp clicks, audit starts, and report downloads, not just pageviews.",
                "Review pages that get AI-search-adjacent impressions and build supporting content around those terms.",
                "Update content when search behavior changes, especially around AI Mode, AI Overviews, and industry-specific service terms.",
            ]),
            ("p", "AEO is not a one-time setup. It is a feedback loop. Search Console shows what Google is testing you for. Your audit data shows where visitors hesitate. Together, they tell you what to improve next."),
            ("h2", "A simple AEO publishing workflow"),
            ("ol", [
                "Pick one buyer question with commercial value.",
                "Write the short answer first.",
                "Add the criteria, steps, examples, proof, and caveats.",
                "Link to the relevant service page and supporting posts.",
                "Add schema that matches the visible content.",
                "Check mobile layout, speed, indexability, and CTA behavior.",
                "Publish, submit the URL in Search Console, and monitor impressions for four to eight weeks.",
            ]),
            ("p", "That workflow keeps the work grounded. The point is not to chase every AI platform separately. The point is to make your best answers findable, verifiable, and useful wherever buyers ask."),
            ("h2", "Frequently asked"),
            ("h3", "What is the difference between SEO and AEO?"),
            ("p", "SEO improves visibility in search results. AEO improves the chance that your content can be used as a direct answer, summary, recommendation, or cited source. The foundations overlap, but AEO requires tighter structure and clearer evidence."),
            ("h3", "Do I need FAQ schema for answer engine optimization?"),
            ("p", "FAQ schema can help when the questions are useful and visible on the page. It is not required for every page and should not be used to mark up hidden or low-value content."),
            ("h3", "How many AEO pages should a business create?"),
            ("p", "Start with the pages closest to revenue: core services, local/service-area pages, comparison posts, audit guides, and case studies. Add supporting posts only when they answer real buyer questions."),
        ],
    },
    {
        "slug": "shopify-developer-freelance-rates",
        "title": "Shopify Developer Freelance Rates: How to Compare Quotes Without Getting Burned",
        "excerpt": "Google is already testing Lofts Studio for Shopify developer rate searches. This guide captures that intent without turning the site into a public rate card.",
        "meta": "Shopify developer freelance rates guide: what changes a quote, how to compare junior, senior, and agency options, and what to ask before hiring.",
        "category": "Shopify",
        "date": "2026-06-23",
        "readingTime": "10 min",
        "primaryKeyword": "shopify developer freelance rates",
        "secondaryKeyword": "shopify developer rates 2024",
        "funnelTo": "/services/shopify-development.html",
        "funnelLabel": "Shopify Development",
        "featured": False,
        "hook": "If you searched for Shopify developer freelance rates, you are not really looking for a number. You are trying to understand whether the person you hire can protect the store, the launch, and the revenue behind it. A rate without scope is a trap; the right comparison starts with what the developer is being trusted to change.",
        "body": [
            ("p", "This article exists because Google is already testing Lofts Studio for rate-intent Shopify searches. That is useful data. It means buyers are not only searching for inspiration or a portfolio; they are comparing risk, seniority, and hiring models before they choose who touches their store."),
            ("p", "I am not going to publish a fixed rate card here. A serious Shopify project is not a menu item. The same phrase, <em>Shopify developer</em>, can mean a junior changing theme colors, a senior rebuilding checkout-adjacent flows, an app engineer integrating an ERP, or a team migrating a store before a peak trading period. Those are different jobs with different risk profiles."),
            ("callout", "Use this page as a buyer's filter: if two quotes look wildly different, the question is not which one is cheaper. The question is what responsibility, QA, handoff, and future maintenance each quote actually includes."),
            ("h2", "What people mean by Shopify developer rates"),
            ("p", "Most buyers use <strong>rates</strong> as a shortcut for three hidden questions: how senior is this person, how much risk is in my scope, and how likely is the store to still be easy to run six months after launch? If a proposal does not answer those three questions, the number attached to it is not very useful."),
            ("p", "Marketplaces make this more confusing because they put very different people under the same label. One profile may be a theme customizer. Another may be a Shopify Plus engineer. Another may be an agency salesperson using a freelancer profile as the front door. Public directories are useful for discovery, but the real comparison has to happen inside the scope."),
            ("h2", "The work type changes the quote more than the platform"),
            ("p", "Shopify itself is not the hard part. The hard part is what your store needs Shopify to do. Before you compare freelancers, sort the project into one of these buckets:"),
            ("ul", [
                "<strong>Theme cleanup.</strong> Existing theme, small visual edits, section ordering, content support, and light Liquid work.",
                "<strong>Conversion rebuild.</strong> Product pages, collection pages, cart UX, bundles, trust proof, analytics events, and mobile-first QA.",
                "<strong>Performance repair.</strong> App bloat, JavaScript cleanup, image strategy, Core Web Vitals, and measurement before/after.",
                "<strong>Migration.</strong> Moving products, customers, redirects, analytics, tracking, content, and SEO signals without breaking revenue.",
                "<strong>Custom app or integration.</strong> Inventory, ERP, subscriptions, wholesale logic, B2B workflows, dashboards, or internal operations.",
                "<strong>Shopify Plus or advanced operations.</strong> Multi-market, checkout extensibility, B2B catalogs, automation, permissions, and launch governance.",
            ]),
            ("p", "A low-risk theme cleanup can be handled by a capable junior. A migration, app integration, or conversion rebuild needs someone who understands the store as a system. That is why two Shopify developers can quote the same store and sound like they are describing different planets."),
            ("h2", "What changed since the 2024 rate searches"),
            ("p", "The screenshot keyword includes <strong>shopify developer rates 2024</strong>, which tells us people are still using older query wording. The market has shifted since then, but not in the way most buyers think. The biggest change is not that every developer suddenly became more expensive. The bigger change is that the scope is heavier."),
            ("ul", [
                "Stores rely on more apps, which means more conflicts, more script weight, and more QA.",
                "Shopify themes are more flexible, which is good, but flexible themes still need guardrails or the admin becomes messy fast.",
                "AI search and richer snippets make technical SEO, schema, and content structure part of the build conversation.",
                "Privacy, analytics, consent, and server-side tracking have become harder to ignore.",
                "Buyers expect faster mobile experiences, not just cleaner desktop screenshots.",
            ]),
            ("p", "So when you compare a current proposal against an old forum thread or an old marketplace rate, remember that the average Shopify scope now includes more moving parts. The better question is whether the developer has a process for those parts."),
            ("h2", "Freelancer, agency, or senior independent?"),
            ("p", "The hiring model matters because it changes who is accountable. A freelancer can be efficient when the person selling the work is the person doing the work. An agency can be right when the project needs strategy, copy, design, QA, and account management at the same time. A senior independent sits in the middle: fewer layers than an agency, more judgment than a task-taker."),
            ("p", "If you are comparing <a href='/blog/freelance-shopify-developer-vs-agency.html'>freelance Shopify developer vs agency</a>, do not only compare the headline figure. Compare the communication path, the QA process, the person reviewing code, and what happens after launch."),
            ("h2", "The quote should explain the risk"),
            ("p", "A serious Shopify quote should not be a one-line total. It should explain what is included, what is excluded, what assumptions the developer is making, and what could change after discovery. If a quote does not mention risk, it is usually hiding risk."),
            ("ul", [
                "Which templates, sections, or flows are included?",
                "Which apps are staying, being removed, or being replaced?",
                "Who owns design, copy, assets, and product data?",
                "How will redirects, SEO metadata, and analytics be handled?",
                "What does mobile QA include?",
                "What happens if the theme or app stack is worse than expected?",
                "What support window exists after launch?",
            ]),
            ("p", "That list is not bureaucracy. It is how you avoid the common pattern where the cheapest quote becomes the most expensive store to maintain."),
            ("h2", "How to turn a rate search into a useful first message"),
            ("p", "A good first message does not need to be long. It needs to give the developer enough context to stop guessing. When a buyer only asks for a rate, the developer has to either ask for discovery or invent assumptions. The better approach is to send a short brief that describes the store, the problem, the business risk, and the result you want after the work is done."),
            ("p", "That changes the conversation immediately. A junior task-taker will still try to quote from the surface. A senior developer will start identifying dependencies: theme quality, app conflicts, analytics gaps, content readiness, redirects, product data, search behavior, and the team's ability to maintain the store after launch."),
            ("ul", [
                "<strong>Store context.</strong> Share the URL, platform version, theme name if known, and whether the store is live or pre-launch.",
                "<strong>Commercial context.</strong> Explain what is hurting the business: low conversion, slow mobile pages, poor merchandising, broken tracking, weak SEO, or operational drag.",
                "<strong>Scope context.</strong> List the pages, templates, apps, integrations, or workflows you believe are involved, even if you are not sure.",
                "<strong>Risk context.</strong> Mention hard deadlines, active paid traffic, peak season, migration pressure, or anything that makes downtime expensive.",
                "<strong>Success context.</strong> Define what would make the project feel successful: easier admin work, higher conversion confidence, better speed, cleaner analytics, fewer apps, or a safer launch.",
            ]),
            ("p", "This is also how you protect yourself from vague proposals. When the brief is clear, the proposal should become clearer too. If the answer still feels generic after you provided context, that is a strong signal the person has not actually thought through the store."),
            ("h2", "What I would inspect before quoting a Shopify store"),
            ("p", "Before I treat any Shopify rate as real, I want to know what shape the store is in. A clean-looking storefront can hide a fragile backend. A plain-looking store can be technically healthy and easy to improve. The first inspection is not about judging the brand; it is about finding the risk that will affect the work."),
            ("ul", [
                "Theme architecture: whether sections, snippets, templates, and metafields are organized or patched together.",
                "App stack: which apps are essential, which duplicate each other, and which are slowing down key pages.",
                "Product and collection structure: whether filters, variants, bundles, subscriptions, or B2B logic are creating complexity.",
                "Analytics and SEO: whether tracking, redirects, schema, metadata, and search pages are reliable enough to preserve growth.",
                "Mobile buying path: whether the first screen, product detail page, cart, and trust proof work under real thumb-scrolling conditions.",
                "Admin maintainability: whether your team can update the store without breaking layouts or creating inconsistent pages.",
            ]),
            ("p", "Once those pieces are visible, a quote becomes more than a rate. It becomes a plan. That is the difference between hiring someone to change a Shopify theme and hiring someone to improve the store as a business asset."),
            ("h2", "Questions to send before asking for a rate"),
            ("p", "Before you ask for a number, send these questions. The answers will tell you whether the developer is thinking like a partner or like a task-taker."),
            ("ol", [
                "What would you inspect first if I gave you access to the current store?",
                "Which part of this scope has the most risk, and why?",
                "Can you show three live Shopify URLs where you handled a similar responsibility?",
                "What do you need from us before you can give a reliable scope?",
                "How do you handle QA across mobile, desktop, apps, analytics, and launch day?",
                "What will be documented so another developer can maintain the store later?",
            ]),
            ("p", "A senior developer will answer with specifics. A weak hire will answer with adjectives: clean, fast, modern, professional. Adjectives do not protect a store."),
            ("h2", "Red flags when comparing Shopify developer freelance rates"),
            ("ul", [
                "The developer gives a firm quote before asking about apps, theme, analytics, or product data.",
                "The portfolio is screenshots only, with no live URLs you can inspect.",
                "They promise speed without explaining what will be skipped.",
                "They recommend adding another app before auditing what is already installed.",
                "They cannot explain how their work will affect Core Web Vitals, SEO, or conversion tracking.",
                "They talk about design polish but never talk about handoff or maintainability.",
            ]),
            ("p", "These signs matter because Shopify stores rarely fail dramatically on launch day. They fail quietly after launch: slow pages, broken tracking, confusing product templates, duplicate apps, and a team that cannot safely update its own store."),
            ("h2", "A better way to compare two quotes"),
            ("p", "Make a simple comparison table with these columns: scope clarity, seniority, live proof, technical risk, communication, QA, handoff, and post-launch support. Put the rate last. If one quote wins on the first seven columns, the rate becomes easier to interpret. If it loses on the first seven, the rate is usually bait."),
            ("p", "For growth stores, I would rather see a smaller first scope with a senior developer than a bloated full-store rebuild with a weak process. A focused first sprint can repair the highest-risk parts of the store, prove communication, and give both sides better information before a larger engagement."),
            ("h2", "Where this fits inside Lofts Studio"),
            ("p", "If you want the practical next step, start with <a href='/services/shopify-development.html'>Shopify development</a> or a <a href='/services/technical-seo-audit.html'>technical SEO audit</a>. If speed is already hurting the store, look at <a href='/services/speed-optimization.html'>speed optimization</a>. If you are not sure whether the problem is design, performance, apps, or content, the audit route is usually cleaner than asking for a blind quote."),
            ("p", "The goal is not to make you choose the most expensive option. The goal is to make sure you compare the right things before a developer changes the part of your business that takes orders."),
            ("h2", "Frequently asked"),
            ("h3", "Should I choose the lowest Shopify developer freelance rate?"),
            ("p", "Only when the task is low-risk, clearly scoped, and easy to reverse. For revenue-critical templates, migrations, checkout-adjacent work, app integrations, or performance repairs, the lowest rate often skips the work that prevents expensive cleanup later."),
            ("h3", "Why not publish a fixed Shopify developer rate card?"),
            ("p", "Because a fixed public rate card encourages bad comparisons. The real scope depends on the theme, app stack, content, analytics, SEO risk, integrations, and launch timeline. A responsible quote starts with diagnosis."),
            ("h3", "What should I prepare before contacting a Shopify developer?"),
            ("p", "Send the store URL, the current pain points, the apps you rely on, examples of pages you like, analytics access if available, and the outcome you care about most: speed, conversion, migration, custom functionality, or maintainability."),
        ],
    },
    {
        "slug": "hire-shopify-developer-guide-2026",
        "title": "How to Hire a Shopify Developer in 2026 (Without Getting Burned)",
        "excerpt": "Ten red flags I've watched founders ignore, the questions that filter weak hires in one email, and how to judge Shopify scope before you sign.",
        "meta": "How to hire a Shopify developer without a bad engagement: red flags, screening questions, scope checks, and what senior Shopify process should include.",
        "category": "Shopify",
        "date": "2026-06-12",
        "readingTime": "11 min",
        "primaryKeyword": "hire shopify developer",
        "secondaryKeyword": "shopify developer hiring guide",
        "funnelTo": "/services/shopify-development.html",
        "funnelLabel": "Shopify Development",
        "featured": True,
        "hook": "If you're about to hire a Shopify developer for the first time, you are about to make the most expensive decision of the year — and you almost certainly don't have the vocabulary yet to make it well.",
        "body": [
            ("p", "I've spent almost 15 years inside this market — first as the developer being hired, then as the one cleaning up after the wrong ones. I've watched founders choose the cheapest path and rebuild months later, and I've watched careful scopes keep stores healthy for years. The headline number has almost nothing to do with which outcome they got."),
            ("p", "This post is the screening playbook I wish every client had used before they reached me. It will not flatter the industry. It will save you a six-figure mistake."),
            ("h2", "What a Shopify proposal should prove in 2026"),
            ("p", "If you are comparing Shopify partners, start with the work type. A serious proposal should make responsibility visible: what will be touched, what will be tested, what could break, and how the store will be handed back after launch."),
            ("ul", [
                "<strong>Theme task-takers.</strong> Good for content updates, simple section changes, and low-risk theme cleanup when the store is already stable.",
                "<strong>Mid-level builders.</strong> Useful for straightforward new stores, but risky when the brief touches migration, performance, analytics, or custom logic.",
                "<strong>Senior independents.</strong> Best when the store needs judgment: cleaner architecture, safer launch planning, fewer app conflicts, and a maintainable handoff.",
                "<strong>Agency teams.</strong> Right when the scope needs parallel design, copy, QA, strategy, and support capacity around the development work.",
            ]),
            ("p", "Anyone reducing a serious Shopify build to a quick fixed number before discovery is selling certainty they have not earned. The expensive part is rarely the first build; it is the cleanup when the first build was scoped badly."),
            ("h2", "The 10 red flags I'd run from"),
            ("h3", "1. They say yes to everything in the first email"),
            ("p", "A senior developer asks questions before quoting. A junior — or a sales-led shop — enquiries immediately because they don't yet know what they don't know. If your first reply contains a scope but zero clarifying questions, that's the entire signal you need."),
            ("h3", "2. No live URLs in the portfolio"),
            ("p", "Mockups and Behance shots don't count. You need three live URLs that you can open right now, click around, and verify still work. If the portfolio is screenshots only, the work either no longer exists or was never theirs to begin with."),
            ("h3", "3. They promise a launch date before scoping the work"),
            ("p", "Junior pattern: \"I can launch in 2 weeks.\" Senior pattern: \"Two weeks of discovery before I'll enquiry a date.\" Real builds have unknowns. Anyone who pretends they don't has either never built a real store or is about to skip the parts you need most."),
            ("h3", "4. They want full payment upfront"),
            ("p", "Industry standard is 30–50% deposit, milestones, balance on launch. Anyone asking for 100% upfront is either inexperienced or planning to disappear. Both end the same way."),
            ("h3", "5. \"I'll use a page builder\""),
            ("p", "If you ever plan to grow past early traction/month, page builders will slow your store down and lock you into the builder's scoping. PageFly and GemPages have their place — bare-bones stores that need to ship next week. They do not have a place in a build you'll run for years."),
            ("h3", "6. No code samples on request"),
            ("p", "Ask: \"Can you send me a section.liquid file from a past project?\" A senior developer will redact client identifiers and send it within 24 hours. A junior will dodge or send something that's obviously copy-pasted from Shopify's docs."),
            ("h3", "7. They don't ask about hosting plan or app stack"),
            ("p", "If they haven't asked which Shopify plan you're on, which apps you're committed to, or which analytics you run — they are not thinking about your store as a system. They are thinking about it as a screenshot."),
            ("h3", "8. No process documentation"),
            ("p", "Senior developers have a written process, sent unprompted. Discovery → design → build → QA → launch → 30-day support. If they can't articulate the phases without you asking, they don't have phases. They have improvisation."),
            ("h3", "9. They've never said \"no\""),
            ("p", "A senior developer will push back on requests that will hurt your store — adding a fifth pop-up, installing an app that breaks LCP, copying a competitor's checkout. If everything you suggest is met with \"sure, no problem,\" you don't have a developer. You have an order-taker."),
            ("h3", "10. The reviews don't read like real people wrote them"),
            ("p", "If every review is five sentences, five stars, and ends with \"highly recommend,\" they are either bought or written by the developer. Real client reviews mention specific deliverables, real timeline frustrations, and the actual revenue or speed impact. \"Adnan rebuilt our PDP and we saw a 17% conversion lift in 6 weeks\" is real. \"Great communication, highly recommend\" is filler."),
            ("h2", "The screening questions that filter 80% of bad hires in one email"),
            ("p", "Send these five questions in your first reply. Anyone who answers all five thoughtfully is in the top 10% of the market. Anyone who skips one or hand-waves their way through is filtered."),
            ("ol", [
                "<strong>Send me three live URLs of stores you've shipped in the last 12 months, with a sentence on what you actually built (theme, custom sections, app, full build).</strong>",
                "<strong>What was the most expensive mistake you made on a Shopify build, and how did you fix it?</strong> (Anyone who says they've never made a mistake has never shipped.)",
                "<strong>If I send you the URL of my current store, would you do a 10-minute audit before the call? What would you look at?</strong>",
                "<strong>Walk me through your process from contract signed to launch day. Phases, timelines, deliverables per phase.</strong>",
                "<strong>What's one piece of advice you'd give me before we start that I haven't asked about?</strong>",
            ]),
            ("p", "The last question is the diagnostic. A senior developer will use it to flag something specific to your store. A junior will give you a generic platitude about \"good communication.\""),
            ("h2", "What you should expect from the first paid week"),
            ("p", "You hired them. The deposit cleared. What does week one look like with a senior?"),
            ("ul", [
                "A kickoff call inside 48 hours with an agenda sent in advance.",
                "A shared document — Notion, Google Doc, anything — with scope, milestones, and a definition of done.",
                "Access requests with reasons attached. (\"I need staff access with these permissions because…\")",
                "A first deliverable inside 5–7 days — even if it's a design system, a sitemap, or a working section. Not three weeks of silence.",
                "An async update at least every 48 hours, even if it's two lines.",
            ]),
            ("p", "If you don't get those signals in the first week, address it directly. The pattern almost never improves on its own; it gets worse as the project gets harder."),
            ("h2", "When to fire fast"),
            ("p", "Three signs the relationship will not recover:"),
            ("ol", [
                "Deliverables ship late <em>and</em> the explanations rotate. Once is a circumstance. Three times is a pattern.",
                "Code quality is poor and they refuse to refactor when shown specifically what's wrong.",
                "Communication windows shrink. Two-hour replies became 24-hour replies became radio silence.",
            ]),
            ("p", "Eat the deposit. Hire someone else. The effort of staying in a bad engagement compounds — slower delivery, worse code, harder handoff. I have personally inherited 23 stores from developers a client should have fired in week two and didn't."),
            ("h2", "The honest summary"),
            ("p", "Hiring a Shopify developer well is a market-asymmetry problem. They've done 100 sales calls. You've done one. The five questions above and the ten red flags above flatten that asymmetry. Use them. If a developer is offended by the questions, that's the answer to every question you didn't ask."),
        ],
    },
    {
        "slug": "shopify-plus-vs-advanced-when-to-upgrade",
        "title": "Shopify Plus vs Advanced: When the Upgrade Makes Sense",
        "excerpt": "The honest math on when Shopify Plus earns its heavier platform commitment — and the four signs you should stay on Advanced and save the cash for engineering instead.",
        "meta": "Shopify Plus vs Advanced: when the Plus upgrade proves its value, and when it's a tax on founders who got over-sold by sales reps. Real math from 14 migrations.",
        "category": "Migration",
        "date": "2026-06-13",
        "readingTime": "9 min",
        "primaryKeyword": "shopify plus vs advanced",
        "secondaryKeyword": "when to upgrade to shopify plus",
        "funnelTo": "/services/shopify-plus-migration.html",
        "funnelLabel": "Shopify Plus Migration",
        "featured": False,
        "hook": "Shopify Plus sales reps will tell you the upgrade proves its value by $1M ARR. The math is more honest than that — and more nuanced.",
        "body": [
            ("p", "I've done 14 Shopify Plus migrations in the last five years. Some were obvious wins. Some, candidly, should never have happened — the founder upgraded because a rep said they should, and the only thing that changed was their monthly project record. This post is the framework I now run every client through before they sign the Plus contract."),
            ("h2", "What you're actually buying for $2,000/month"),
            ("p", "Plus is bundled. The headline features:"),
            ("ul", [
                "<strong>Higher capacity</strong> — 200 inventory locations, 99.99% uptime SLA, dedicated infrastructure during BFCM.",
                "<strong>B2B</strong> — Native B2B catalogs, tiered scoping, company accounts, draft orders at scale.",
                "<strong>Checkout extensibility</strong> — Custom checkout via Shopify Functions and checkout extensions (the only plan that allows real checkout customization in 2026).",
                "<strong>Multi-store / multi-region</strong> — Up to 10 expansion stores under one contract for international or multi-brand.",
                "<strong>Shopify Flow + Launchpad</strong> — Workflow automation and scheduled campaigns.",
                "<strong>Lower checkout overhead</strong> — Roughly 0.25% lower per transaction depending on payment method.",
                "<strong>Dedicated support</strong> — A Merchant Success Manager and faster ticket resolution.",
            ]),
            ("h2", "The actual break-even math"),
            ("p", "Most founders calculate Plus break-even on platform platform savings alone. That's the worst lens. The right lens is the <em>capability effort</em> — what would it effort you in engineering, lost revenue, or workarounds to do without each feature."),
            ("p", "Here's how I model it for clients:"),
            ("pre", "Plus commitment: meaningful recurring platform overhead\n\nTransaction platform savings (at scale revenue, 0.25%): meaningful annual overhead\nB2B without Plus: custom apps and manual workflows\nCheckout customization: value depends on conversion volume\nDedicated support during BFCM: risk reduction during peak traffic\nExpansion stores: simpler multi-market operations"),
            ("p", "If you tick three of those five rows, the upgrade is a no-brainer. If you tick one and you're using it to justify the upgrade, you are being sold."),
            ("h2", "The four signs you should upgrade"),
            ("h3", "1. You sell B2B or are planning to"),
            ("p", "Native Plus B2B is, candidly, the killer feature in 2026. Company accounts, tiered scoping per company, draft orders, account terms — all native, all free with the plan. The custom build equivalent on Advanced adds overhead a heavy engineering lift and never works as well."),
            ("h3", "2. You're hitting checkout customization limits"),
            ("p", "If your team has ever said \"can we add this field to checkout\" and the answer was \"no, that's Plus,\" and you've now hit that wall three times, the wall isn't moving. Plus is the move."),
            ("h3", "3. You're running 3+ stores under different brands or regions"),
            ("p", "Multiple regional stores can make Plus operationally cleaner because expansion stores are included. The logic is obvious once you map the architecture."),
            ("h3", "4. You are scaling hard and BFCM uptime matters"),
            ("p", "Plus dedicates infrastructure during BFCM. Advanced shares pooled resources. At smaller scale, pooled resources can be fine. At high scale, the dedicated SLA proves its value in a single near-miss."),
            ("h2", "The four signs you should stay on Advanced"),
            ("h3", "1. You don't sell B2B and don't plan to"),
            ("p", "If B2B isn't on the 12-month roadmap, you've removed the single highest-ROI Plus feature."),
            ("h3", "2. Your checkout is fine"),
            ("p", "If you've never wished you could customize checkout — congratulations. You're using the strongest part of native Shopify. Don't upgrade for capability you won't use."),
            ("h3", "3. You are not at serious scale yet"),
            ("p", "Before serious scale, the platform platform savings are too small to matter and the engineering you'd unlock could be paid for in cash with the a serious annual allocation you'd otherwise hand to Shopify. I'd rather see that money in a senior developer than a higher plan."),
            ("h3", "4. Your team isn't ready to use the features"),
            ("p", "Plus gives you Flow, Launchpad, B2B. If nobody on your team will operationalize them in the next 90 days, you are carrying a heavier platform setup for features that sit dormant."),
            ("h2", "The migration timeline (Advanced → Plus)"),
            ("p", "Real timelines from my last five migrations:"),
            ("ul", [
                "<strong>Contracting & onboarding</strong>: 1–2 weeks",
                "<strong>Plus store provisioning + theme cloning</strong>: 1 week",
                "<strong>Checkout extension rebuild (if applicable)</strong>: 2–4 weeks",
                "<strong>B2B setup (if applicable)</strong>: 2–3 weeks",
                "<strong>DNS cutover, payment provider migration, app reauth</strong>: 1 week",
                "<strong>Stabilization period</strong>: 2 weeks",
            ]),
            ("p", "Realistic total: 8–12 weeks. Anyone promising a 2-week Plus migration on a store with B2B or custom checkout is going to break something on launch day."),
            ("h2", "The honest conclusion"),
            ("p", "Plus is the right plan for fewer stores than Shopify's sales team would have you believe. It's the right plan for the stores that have already outgrown Advanced — not the stores that someone thinks <em>should</em> have outgrown Advanced. Run the framework above. If you tick three rows in the upgrade column, upgrade. If you tick one and the rep is pushing hard, that's a sales motion, not a fit."),
        ],
    },
    {
        "slug": "shopify-technical-seo-audit-checklist",
        "title": "Shopify Technical SEO Audit: The 32 Checks I Run Before Anything Else",
        "excerpt": "The full technical SEO audit I run on every new Shopify client. 32 checks across crawl, indexing, on-page, structured data, and Core Web Vitals — with the exact tools and target values.",
        "meta": "The 32-check technical SEO audit I run on every new Shopify client. Crawl, indexing, structured data, Core Web Vitals — with target values and tools.",
        "category": "SEO",
        "date": "2026-06-14",
        "readingTime": "13 min",
        "primaryKeyword": "shopify technical seo audit",
        "secondaryKeyword": "shopify seo checklist 2026",
        "funnelTo": "/services/technical-seo-audit.html",
        "funnelLabel": "Technical SEO Audit",
        "featured": False,
        "hook": "Most Shopify SEO advice you read online is content advice in a technical-SEO effortume. This is the actual technical pass — the 32 checks I run before I'll write a single piece of content for a client.",
        "body": [
            ("p", "Shopify is a particular SEO beast. It does some things very well (clean URLs, automatic XML sitemaps, native canonicals) and some things terribly (faceted nav indexing, pagination handling, duplicate content from collection sorts, search-engine-unfriendly variant URLs). A real technical audit accounts for both."),
            ("p", "I run this checklist on every new Shopify engagement before I'll commit to a content or CRO plan. It usually takes 6–8 hours and surfaces 12–20 issues on the average store. Here it is, with the tools and target values."),
            ("h2", "Part 1: Crawl & indexing (checks 1–9)"),
            ("ol", [
                "<strong>robots.txt audit.</strong> Confirm /admin, /cart, /checkouts/, /collections/all are noindexed correctly. Shopify auto-generates these but I've seen apps clobber them.",
                "<strong>XML sitemap reachability.</strong> /sitemap.xml should return 200, should be under 50MB, should be submitted to Search Console.",
                "<strong>Search Console coverage report.</strong> \"Excluded\" pages count vs total. If excluded > 30%, you have a structural problem.",
                "<strong>Indexed pages count via site: operator.</strong> Compare to product count. If indexed > products × 3, you have duplicate URL bloat from variants or filters.",
                "<strong>Canonical tag audit.</strong> Every PDP should canonical to itself, not to the default variant. /collections/all/products/x and /products/x should both canonical to /products/x.",
                "<strong>Pagination handling.</strong> ?page=2, ?page=3 should not self-canonical. Use rel=\"next\"/\"prev\" or noindex paginated pages.",
                "<strong>Faceted nav handling.</strong> /collections/x?filter.v.option.size=L type URLs should be noindexed. This is the single biggest Shopify SEO leak.",
                "<strong>Internal search pages.</strong> /search?q=… should be noindexed. Often these end up indexed by accident.",
                "<strong>404 audit.</strong> Run a Screaming Frog crawl. Internal links pointing to 404s lose ranking signal and waste crawl scope.",
            ]),
            ("h2", "Part 2: On-page SEO (checks 10–17)"),
            ("ol", [
                "<strong>Title tag uniqueness.</strong> Every page should have a unique title under 60 characters. Most Shopify themes default to \"Product Name — Store Name\" which is fine until you have 200 PDPs all trailing \"— Brand Co.\"",
                "<strong>Meta description coverage.</strong> Every page that gets organic traffic should have a custom meta description. Shopify defaults to the first 160 characters of body — that almost never makes sense.",
                "<strong>H1 uniqueness.</strong> One H1 per page, matches the primary keyword for that page.",
                "<strong>H2/H3 outline.</strong> No H4 without an H3, no H3 without an H2. Most themes break this.",
                "<strong>Image alt text coverage.</strong> Every content image should have descriptive alt text. Run a crawl and report missing alts.",
                "<strong>Internal linking depth.</strong> No important page should be more than 3 clicks from the homepage. Most Shopify stores have orphan collections and underlinked PDPs.",
                "<strong>Anchor text diversity.</strong> Audit anchor text patterns. \"Click here\" and \"learn more\" tell Google nothing.",
                "<strong>URL structure audit.</strong> /collections/category/products/product is the right pattern. Slug should match H1.",
            ]),
            ("h2", "Part 3: Structured data (checks 18–23)"),
            ("ol", [
                "<strong>Product schema.</strong> Every PDP needs Product schema with offers, scope, availability, brand, ratings. Most themes ship a broken version.",
                "<strong>Organization schema.</strong> Homepage needs Organization with logo, name, sameAs (social profiles).",
                "<strong>BreadcrumbList schema.</strong> Every page deeper than homepage needs breadcrumb schema.",
                "<strong>WebSite schema with SearchAction.</strong> Enables the sitelinks search box in SERPs.",
                "<strong>FAQ schema (where applicable).</strong> If your product has FAQs on the PDP, mark them up.",
                "<strong>Validate everything in Google's Rich Results Test.</strong> If it doesn't pass there, Google won't render rich results.",
            ]),
            ("h2", "Part 4: Performance (checks 24–28)"),
            ("ol", [
                "<strong>Core Web Vitals — field data via Search Console.</strong> LCP < 2.5s, CLS < 0.1, INP < 200ms.",
                "<strong>Mobile usability errors.</strong> Search Console → Mobile Usability. Should be zero.",
                "<strong>HTTPS everywhere.</strong> No mixed content warnings.",
                "<strong>Image optimization audit.</strong> No PDP image over 200KB. Use Shopify's image_url filter with explicit widths.",
                "<strong>Render-blocking resources.</strong> No render-blocking JS or CSS above the fold.",
            ]),
            ("h2", "Part 5: International & advanced (checks 29–32)"),
            ("ol", [
                "<strong>hreflang tags (if multi-region).</strong> Every region-specific URL should have hreflang to all other regions including x-default.",
                "<strong>Markets configuration audit.</strong> Shopify Markets should have correct domain or subfolder per region.",
                "<strong>Currency switching SEO.</strong> /en-us/, /en-gb/, /en-au/ folders should be properly hreflang'd, not just JS-switched.",
                "<strong>Server-side rendering check.</strong> Disable JavaScript in DevTools. Verify content still renders. Shopify themes that depend on JS for critical content lose ranking.",
            ]),
            ("h2", "The tools I actually use"),
            ("ul", [
                "<strong>Screaming Frog SEO Spider</strong> — full site crawl, every audit starts here",
                "<strong>Google Search Console</strong> — for real index data and Core Web Vitals field data",
                "<strong>Ahrefs / Semrush</strong> — backlink and competitor analysis",
                "<strong>Google Rich Results Test</strong> — structured data validation",
                "<strong>PageSpeed Insights + WebPageTest</strong> — performance",
                "<strong>Sitebulb</strong> — secondary crawler when Screaming Frog misses something",
            ]),
            ("h2", "What the audit deliverable looks like"),
            ("p", "When I run this for a client, the deliverable is a 12–20 page document organized by impact: 'do today,' 'do this month,' 'roadmap.' Every issue has the specific URL or page, the recommended fix, and an effort estimate. The fixes themselves are typically a 2–4 week engineering sprint after the audit lands."),
            ("p", "An audit without an implementation plan is just a list. The point of running these 32 checks is to know where to spend the next sprint, not to feel busy."),
        ],
    },
    {
        "slug": "freelance-shopify-developer-vs-agency",
        "title": "Freelance Shopify Developer vs Agency: What You Actually Pay For",
        "excerpt": "Agencies pitch process, project managers, and scale. Freelancers pitch hands-on senior work. Here's what each model actually adds overhead, when each one wins, and the hybrid most clients should consider.",
        "meta": "Freelance Shopify developer vs agency — what each model actually adds overhead, when each wins, and the hybrid most clients should consider before signing a contract.",
        "category": "Shopify",
        "date": "2026-06-15",
        "readingTime": "8 min",
        "primaryKeyword": "freelance shopify developer vs agency",
        "secondaryKeyword": "shopify agency comparison",
        "funnelTo": "/services/shopify-development.html",
        "funnelLabel": "Shopify Development",
        "featured": False,
        "hook": "Every founder who has hired both knows the secret: you are rarely paying for the developer. You are paying for the layer of people sitting between you and the developer.",
        "body": [
            ("p", "I've worked inside agencies, built solo for almost 15 years, and inherited dozens of stores from both kinds of teams. The right choice depends on which problem you actually have. Let me unpack the real difference."),
            ("h2", "What an agency adds overhead in 2026"),
            ("p", "A typical agency proposal includes more than engineering time. Some of that overhead is useful when the scope needs it. Some of it is simply the wrapper around the person doing the work. The extra layer usually includes:"),
            ("ul", [
                "Project manager hours (15–25% of total)",
                "Account manager hours (5–10%)",
                "Discovery / strategy phase (10–15%)",
                "QA + testing (5–10%)",
                "Overhead, sales, office (the rest)",
            ]),
            ("p", "You are paying for a system. The system has real value if your build needs it. If it doesn't, you're paying for capacity you'll never touch."),
            ("h2", "What a senior freelancer adds overhead in 2026"),
            ("p", "A senior independent Shopify developer can often deliver the same engineering responsibility with fewer layers. That is not because the work is smaller; it is because the communication path is shorter and the person scoping the work is usually the person building it."),
            ("p", "The trade-off: you are the project manager. You are the QA. If the freelancer gets sick, the project pauses. If you need 3 things at once, you have to sequence them."),
            ("h2", "When the agency model wins"),
            ("ul", [
                "<strong>You have zero technical staff on your side.</strong> You need someone to manage the project for you because you can't.",
                "<strong>The build is large and multi-disciplinary.</strong> Brand identity + photography + copy + dev + launch — you want one team accountable.",
                "<strong>You need scale guarantees.</strong> Plus migrations under tight BFCM deadlines, or builds with strict compliance (HIPAA, PCI).",
                "<strong>You'll have ongoing ongoing support needs.</strong> Continuous CRO, growth experiments, multi-store management — a bench helps.",
                "<strong>You're going to investor.</strong> \"We use [Agency]\" reads better in a deck than \"we use a freelancer.\" That's a real consideration whether you like it or not.",
            ]),
            ("h2", "When the senior freelancer model wins"),
            ("ul", [
                "<strong>You have a technical co-founder or in-house ops.</strong> You can manage scope and timeline without a PM layer.",
                "<strong>Your build is engineering-heavy, low ambiguity.</strong> The brand is decided. The IA is decided. You need execution.",
                "<strong>You want the actual developer accountable.</strong> No game of telephone through a PM. If something's wrong, you talk to the person fixing it.",
                "<strong>You care about effort-of-ownership.</strong> Cleaner code, fewer cooks, simpler handoff to your in-house team later.",
                "<strong>You want speed.</strong> Senior freelancers ship faster than agencies because there's no meeting tax.",
            ]),
            ("h2", "The hybrid most clients should consider"),
            ("p", "Most of my ongoing clients use this structure:"),
            ("ol", [
                "<strong>Senior freelancer (me) — fractional CTO + lead engineer.</strong> Architecture, build, code review, weekly priorities.",
                "<strong>One or two junior contractors I source for them.</strong> Content updates, theme tweaks, and low-stakes work. Managed by me.",
                "<strong>An agency on standby for surge capacity.</strong> Used 2–4 times a year for big launches.",
            ]),
            ("p", "This structure keeps senior accountability, avoids unnecessary layers, and lets you scale up and down without ending relationships."),
            ("h2", "Red flags in both models"),
            ("p", "Both agencies and freelancers can be the wrong hire. The red flags are different:"),
            ("p", "<strong>Agency red flags:</strong> The salesperson is brilliant and the people who actually do the work haven't been on a call. You'll meet them on day one of the engagement. By then it's too late."),
            ("p", "<strong>Freelancer red flags:</strong> One person can only do so much. If they pitch \"I'll do everything — brand, copy, dev, ads,\" they're either juniors or they're going to subcontract it to people you won't meet."),
            ("h2", "The honest framing"),
            ("p", "Pay for capability, not for the wrapper around the capability. If you need a project manager, hire an agency. If you don't, you're handing them margin you could be putting into the actual build. The freelancer-vs-agency question is really a question about how much project management you need — and most founders need less than the agency model is designed to deliver."),
        ],
    },
    {
        "slug": "shopify-custom-app-vs-public-app",
        "title": "Custom Shopify App vs Private App vs Public App",
        "excerpt": "Shopify has three app types and the terminology is genuinely confusing. Here's the decision tree I use with clients — what each one adds overhead, what each one limits, and which one wins for your situation.",
        "meta": "Custom Shopify app vs private app vs public app — what each one adds overhead, what each one limits, and which one is right for your situation, with examples.",
        "category": "Custom Apps",
        "date": "2026-06-16",
        "readingTime": "9 min",
        "primaryKeyword": "shopify custom app vs public app",
        "secondaryKeyword": "shopify private app development",
        "funnelTo": "/services/custom-app-development.html",
        "funnelLabel": "Custom App Development",
        "featured": False,
        "hook": "Shopify has three categories of apps. The terminology is, frankly, confusing — \"custom\" and \"private\" mean different things to Shopify than they do in English. The decision between them shapes the next two years of your store.",
        "body": [
            ("p", "I build Shopify apps for clients monthly. Roughly half the time, the first call is spent unwinding what Shopify, an agency, or a previous developer told them about which app type to use. Let me set the record straight."),
            ("h2", "The three app types in 2026"),
            ("h3", "Public app"),
            ("p", "Listed on the Shopify App Store. Anyone can install it. Submitted through Shopify's review process. Subject to Shopify's commerce model (Shopify takes a revenue share). What most people mean when they say \"Shopify app.\""),
            ("h3", "Custom app"),
            ("p", "Built for one specific merchant, distributed to that merchant only via an install link. No App Store listing. No Shopify revenue share. Most B2B internal tools and merchant-specific automations are custom apps."),
            ("h3", "Private app (deprecated, mostly)"),
            ("p", "Shopify deprecated private apps in 2022. They still technically exist for legacy stores, but new builds should not use them. If a developer tells you in 2026 they're going to build you a \"private app,\" they probably mean \"custom app\" and are using the old terminology."),
            ("p", "From here on, the real choice is custom vs public."),
            ("h2", "When you need a custom app"),
            ("ul", [
                "<strong>You need to automate internal ops.</strong> Order routing, inventory sync to external WMS, custom reporting, finance integrations.",
                "<strong>You need workflows the App Store doesn't cover.</strong> A B2B catalog logic specific to your industry, a custom scoping engine for one client tier, an internal portal.",
                "<strong>You don't want to share data with a third party.</strong> Public apps require you to grant access to a third-party developer's database. Custom apps live entirely under your control.",
                "<strong>You're already paying for 5+ apps that overlap.</strong> Often a single custom app replaces $300–$800/month of App Store subscriptions and pays itself back in 8–14 months.",
            ]),
            ("h2", "When you should build a public app"),
            ("ul", [
                "<strong>You want to commercialize it.</strong> If 100 other merchants would pay $20/month for it, build a public app.",
                "<strong>You need Shopify's distribution.</strong> The App Store is a real sales channel — millions of merchants browse it.",
                "<strong>You're OK with Shopify's revenue share.</strong> 0–15% depending on tier and revenue level.",
                "<strong>You're committed to ongoing maintenance.</strong> Public apps must keep up with Shopify API changes, security reviews, and support tickets.",
            ]),
            ("h2", "What custom apps actually effort"),
            ("p", "Here's a real range from the last two years of builds:"),
            ("ul", [
                "<strong>Simple custom app</strong> (privately scoped) — single integration, one or two endpoints. Example: sync new orders to a Slack channel, or push orders into Xero.",
                "<strong>Mid-complexity custom app</strong> (privately scoped) — multi-step workflow, admin UI inside Shopify, persistent data. Example: a B2B reorder portal with saved templates and tier scoping logic.",
                "<strong>Enterprise custom app</strong> (larger systems) — full internal system. Example: end-to-end OMS integration with custom shipping logic, supplier portal, and inventory orchestration across 12 locations.",
            ]),
            ("p", "Maintenance is real. Scope 15–25% of build effort annually for keeping it up to date with Shopify API changes, bug fixes, and small feature requests."),
            ("h2", "The decision tree I use with clients"),
            ("ol", [
                "<strong>Does the App Store already have something that solves 80% of your need?</strong> Install it. Don't build.",
                "<strong>Are you paying $300+/month across multiple overlapping apps?</strong> Build a custom app to consolidate.",
                "<strong>Are you doing something Shopify's APIs allow but no public app handles?</strong> Custom app.",
                "<strong>Do you want to sell this to other merchants?</strong> Public app — even if the first version is built for one merchant.",
                "<strong>Is the use case so specific that no one else would pay for it?</strong> Custom app. Always.",
            ]),
            ("h2", "Common mistakes I see"),
            ("p", "<strong>Building a public app for a one-merchant use case.</strong> You'll spend 30% more on the build to handle multi-tenancy you don't need, and you'll then maintain a billing/auth/support stack for one customer."),
            ("p", "<strong>Choosing public because \"it's safer.\"</strong> Custom apps are not less safe. They're often safer — your data doesn't leave your control."),
            ("p", "<strong>Trying to replicate an App Store app for $2K.</strong> If a public app does what you need and adds overhead lower-tier, install the public app. Building a worse version of it adds overhead more in dev time than three years of the subscription."),
            ("h2", "The honest summary"),
            ("p", "Custom is right for merchant-specific internal tools. Public is right for products you want to commercialize. If you're confused about which one fits, the question to ask is: \"would I pay for this every month if someone else built it?\" Yes → public. No → custom. That's the whole framework."),
        ],
    },
    {
        "slug": "speed-up-woocommerce-checklist",
        "title": "Why Your WooCommerce Store Is Slow: 5 Plugin Issues",
        "excerpt": "WooCommerce stores are slow for the same reasons over and over. The five plugins, the two server-side mistakes, and the fix that always works — from an engineer who's optimized 80+ WooCommerce stores.",
        "meta": "Why your WooCommerce store is slow — the 5 plugins causing most of it, the 2 server mistakes, and the fix that always works. Field-tested optimization from 80+ stores.",
        "category": "WooCommerce",
        "date": "2026-06-17",
        "readingTime": "10 min",
        "primaryKeyword": "speed up woocommerce",
        "secondaryKeyword": "why is woocommerce slow",
        "funnelTo": "/services/woocommerce-development.html",
        "funnelLabel": "WooCommerce Development",
        "featured": False,
        "hook": "WooCommerce is not inherently slow. It is, however, used by an ecosystem that builds plugins as if performance is something other people worry about. The result is what you're seeing in your Lighthouse score.",
        "body": [
            ("p", "I've optimized 80+ WooCommerce stores over almost 15 years. The diagnosis is almost always the same. This post is the playbook — the plugins, the server mistakes, and the order of operations that actually moves your LCP from 6 seconds to under 2.5."),
            ("h2", "The five plugins causing most WooCommerce slowdowns"),
            ("h3", "1. WooCommerce Subscriptions (when misconfigured)"),
            ("p", "Subscriptions is a great product, but it loads cart fragments via AJAX on every page load by default. On a homepage with no cart functionality, that's a 200–400ms request that does nothing. Fix: dequeue the cart fragments script on pages where it's not needed."),
            ("pre", "// In functions.php\nadd_action('wp_enqueue_scripts', function() {\n    if (!is_cart() && !is_checkout() && !is_account_page()) {\n        wp_dequeue_script('wc-cart-fragments');\n    }\n}, 11);"),
            ("h3", "2. Page builders (Elementor, Divi, WPBakery)"),
            ("p", "Page builders load their entire framework site-wide. Even on pages you didn't build with them. The framework alone adds 200–500KB to your bundle and 300–800ms to render."),
            ("p", "Fix: For builds where speed matters, replace page builder pages with a custom theme or block theme. For builds where you're committed to the builder, use a plugin like \"Asset CleanUp\" to dequeue builder assets on pages that don't need them."),
            ("h3", "3. WPML / Polylang (for multi-language)"),
            ("p", "Both load translation tables on every request. On stores with 5+ languages and many translatable strings, that's 100–300ms before WordPress can render anything. Fix: aggressive object caching (Redis), and consider whether you actually need 5 languages live or could ship just two."),
            ("h3", "4. Real-time tracking + analytics plugins"),
            ("p", "MonsterInsights, ExactMetrics, MetricsTracker, every \"connect WooCommerce to GA4\" plugin — they all add real-time hooks to order events that block the cart. Use Google Tag Manager + Server-Side Tag Manager instead. Almost always a 200–500ms saving."),
            ("h3", "5. Backup plugins that run during business hours"),
            ("p", "UpdraftPlus and BackupBuddy default to running backup processes that can spike CPU during traffic peaks. Schedule backups for 3 AM in your store's timezone, not \"continuous.\""),
            ("h2", "The two server-side mistakes"),
            ("h3", "1. Cheap shared hosting"),
            ("p", "If you're paying less than lower-tier for WooCommerce hosting, your store is shared with 200 other sites. There is no amount of plugin optimization that fixes this. The fix is to move to managed WooCommerce hosting — Kinsta, WP Engine, SiteGround Cloud, Rocket.net, or a properly-configured DigitalOcean droplet. Choose hosting that does not bottleneck you."),
            ("h3", "2. No object cache"),
            ("p", "WooCommerce queries the database aggressively. Redis or Memcached object caching keeps frequently-accessed data in memory and cuts database load by 60–80%. Most managed WooCommerce hosts include it. If yours doesn't, install it."),
            ("h2", "The fix that always works — the order of operations"),
            ("ol", [
                "<strong>Move to managed WooCommerce hosting.</strong> Single biggest lever. Skip this step and the rest barely matters.",
                "<strong>Install Redis object cache.</strong> Free, 10-minute install, 30–50% TTFB improvement instantly.",
                "<strong>Install a real caching plugin.</strong> WP Rocket or LiteSpeed Cache if you are on LiteSpeed servers. Page caching, browser caching, GZip compression.",
                "<strong>Audit plugin count.</strong> Healthy WooCommerce stores run 15–25 plugins. If yours is over 40, half are doing work for the other half. Deactivate, test, decide.",
                "<strong>Optimize images.</strong> Install ShortPixel or Imagify. Set up automatic WebP conversion. Resize uploads to a max width of 2000px on upload.",
                "<strong>Lazy load below-the-fold content.</strong> Native browser lazy loading works in modern browsers. Add <code>loading=\"lazy\"</code> to images below the fold.",
                "<strong>Defer non-critical JavaScript.</strong> Use the \"Delay JavaScript Execution\" feature in WP Rocket or equivalent.",
                "<strong>Audit your theme.</strong> If you're on a heavy multipurpose theme (Avada, Flatsome with everything enabled), consider migrating to a leaner option. This is the biggest lift but often the biggest win.",
            ]),
            ("h2", "The numbers you should target"),
            ("ul", [
                "<strong>TTFB</strong> — under 600ms (under 400ms is excellent)",
                "<strong>LCP</strong> — under 2.5s on mobile",
                "<strong>CLS</strong> — under 0.1",
                "<strong>INP</strong> — under 200ms",
                "<strong>Total page weight</strong> — under 2MB for a typical PDP",
                "<strong>Total HTTP requests</strong> — under 80",
            ]),
            ("p", "If you hit all of these, your Lighthouse mobile score will be 85+ and your conversion rate will measurably improve. I've watched it happen 80+ times in a row."),
            ("h2", "The honest summary"),
            ("p", "WooCommerce stores are slow because the ecosystem is permissive — anyone can ship a plugin that destroys your performance. The fix isn't WordPress's fault. It's the operator's responsibility to choose hosting that scales, plugins that respect performance, and a theme that doesn't load everything for everyone. Do those three things and your store will be in the top 10% of WooCommerce performance."),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  LOCATION SERVICE PAGES — country × service matrix
# ─────────────────────────────────────────────────────────────────────────────

LOCATIONS = [
    {
        "code": "us",
        "country": "United States",
        "demonym": "American",
        "currency": "USD",
        "timezone": "EST/PST overlap",
        "hours": "9am–5pm EST and PST callable",
        "tagline": "for US-based DTC and B2B brands",
        "marketNotes": "From Brooklyn coffee brands to Austin SaaS founders, the US market is where I do the majority of my work. Most of my ongoing clients are US-based. I work in your timezone, in your business language, and I am fluent in your platform stack.",
    },
    {
        "code": "uk",
        "country": "United Kingdom",
        "demonym": "British",
        "currency": "GBP",
        "timezone": "GMT/BST",
        "hours": "9am–6pm GMT/BST callable",
        "tagline": "for UK ecommerce and editorial brands",
        "marketNotes": "London editorial brands, Manchester DTC, Edinburgh B2B — I work weekly with UK clients across verticals. VAT-compliant account workflows, GDPR-aware data handling, and a familiarity with the cultural conventions of UK commerce.",
    },
    {
        "code": "au",
        "country": "Australia",
        "demonym": "Australian",
        "currency": "AUD",
        "timezone": "AEDT/AEST",
        "hours": "Reply window matches AEST business hours via async handoff",
        "tagline": "for Australian DTC and lifestyle brands",
        "marketNotes": "Australian founders get a senior dev who has shipped for the Australian market across DTC, hospitality, and luxury goods. Sydney and Melbourne–based clients are a meaningful share of my work.",
    },
    {
        "code": "ca",
        "country": "Canada",
        "demonym": "Canadian",
        "currency": "CAD",
        "timezone": "EST/PST",
        "hours": "Reply window matches Canadian business hours",
        "tagline": "for Canadian ecommerce founders",
        "marketNotes": "Toronto, Vancouver, Montreal — I work weekly with Canadian DTC and B2B brands. PIPEDA-aware, multi-currency setups, and clean USD/CAD billing.",
    },
    {
        "code": "uae",
        "country": "United Arab Emirates",
        "demonym": "Emirati",
        "currency": "AED",
        "timezone": "GST",
        "hours": "9am–6pm GST callable",
        "tagline": "for Dubai and Gulf-market brands",
        "marketNotes": "I've shipped Shopify and WordPress builds for the Dubai market — luxury retail, hospitality, B2B insurance. Comfortable with bilingual (English/Arabic) builds, AED checkout, and regional payment gateways like Telr and Tap.",
    },
]
HREFLANG_REGION_CODES = {"uk": "gb", "uae": "ae"}
SITEMAP_EXCLUDED_PATHS = {
    "/services/shopify-developer-ae.html",
    "/blog/shopify-developer-freelance-rates.html",
    "/blog/landing-page-design-cost.html",
    "/blog/pricing-page-design.html",
    "/blog/small-business-website-cost-2026.html",
    "/blog/post",
    "/unsubscribe",
}

# Service templates per location — currently we generate one master page per location
# that lists Shopify + WooCommerce + WordPress capability for that market.


def render_blog_post(p, nav, footer):
    """Render a single blog post HTML from a spec dict."""
    date_obj = datetime.strptime(p["date"], "%Y-%m-%d")
    date_readable = date_obj.strftime("%B %d, %Y")
    faq_schema = ""
    if p.get("faqs"):
        faq_data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq["answer"],
                    },
                }
                for faq in p["faqs"]
            ],
        }
        faq_schema = f'<script type="application/ld+json">\n{json.dumps(faq_data, ensure_ascii=False, indent=2)}\n</script>\n'

    # Body HTML from structured tuples
    body_parts = []
    for tag, content in p["body"]:
        if tag == "p":
            body_parts.append(f"<p>{content}</p>")
        elif tag == "h2":
            anchor = re.sub(r'[^a-z0-9]+', '-', content.lower()).strip('-')[:40]
            body_parts.append(f'<h2 id="{anchor}">{content}</h2>')
        elif tag == "h3":
            body_parts.append(f"<h3>{content}</h3>")
        elif tag == "ul":
            items = "\n".join(f"      <li>{li}</li>" for li in content)
            body_parts.append(f"<ul>\n{items}\n    </ul>")
        elif tag == "ol":
            items = "\n".join(f"      <li>{li}</li>" for li in content)
            body_parts.append(f"<ol>\n{items}\n    </ol>")
        elif tag == "pre":
            body_parts.append(f"<pre><code>{content}</code></pre>")
        elif tag == "callout":
            body_parts.append(f'<div class="post-callout"><p>{content}</p></div>')
        elif tag == "html":
            body_parts.append(content)
    body_html = "\n\n    ".join(body_parts)
    modified_date = p.get("modifiedDate", p["date"])
    intent_card_html = p.get("intentCardHtml", "")
    seo_title = p["title"] if len(p["title"]) > 51 else f'{p["title"]} | Lofts Studio'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>{seo_title}</title>
<meta name="description" content="{p["meta"]}" />
<link rel="canonical" href="{SITE}/blog/{p["slug"]}.html" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="author" content="Adnan K." />
<meta name="keywords" content="{p["primaryKeyword"]}, {p["secondaryKeyword"]}, website design, website development, technical SEO, AEO, conversion audit" />

<meta property="og:type" content="article" />
<meta property="og:url" content="{SITE}/blog/{p["slug"]}.html" />
<meta property="og:title" content="{p["title"]}" />
<meta property="og:description" content="{p["meta"]}" />
<meta property="og:image" content="{SITE}/assets/blog/{p["slug"]}.png?v={CACHE_VER}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="675" />
<meta property="og:image:alt" content="{p["title"]}" />
<meta property="article:published_time" content="{p["date"]}T09:00:00Z" />
<meta property="article:author" content="Adnan K." />
<meta property="article:section" content="{p["category"]}" />
<meta property="article:tag" content="{p["primaryKeyword"]}, {p["secondaryKeyword"]}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{SITE}/assets/blog/{p["slug"]}.png?v={CACHE_VER}" />

<link rel="icon" href="/favicon.ico" sizes="any" /><link rel="icon" href="/favicon.svg" type="image/svg+xml" /><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" /><link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />
<link rel="stylesheet" href="/assets/experience.css?v=20260801g" data-lofts-experience />

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{p["title"]}",
  "description": "{p["meta"]}",
  "image": "{SITE}/assets/blog/{p["slug"]}.png?v={CACHE_VER}",
  "datePublished": "{p["date"]}T09:00:00Z",
  "dateModified": "{modified_date}T09:00:00Z",
  "author": {{ "@type": "Person", "name": "Adnan K.", "url": "{SITE}/about.html" }},
  "publisher": {{ "@type": "Organization", "name": "Lofts Studio", "logo": {{ "@type": "ImageObject", "url": "{SITE}/favicon.svg" }} }},
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{SITE}/blog/{p["slug"]}.html" }},
  "keywords": "{p["primaryKeyword"]}, {p["secondaryKeyword"]}"
}}
</script>
<script type="application/ld+json">
{{ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [ {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}}, {{"@type":"ListItem","position":2,"name":"Blog","item":"{SITE}/blog/"}}, {{"@type":"ListItem","position":3,"name":"{p["title"]}","item":"{SITE}/blog/{p["slug"]}.html"}} ] }}
</script>
{faq_schema}

<style>
  .post-prose {{ max-width: 720px; margin: 0 auto; }}
  .post-prose h2 {{ font-family: var(--font-display); font-size: clamp(1.5rem, 2.4vw, 1.9rem); letter-spacing: -0.035em; font-weight: 600; margin: 3.5rem 0 1rem; line-height: 1.15; }}
  .post-prose h3 {{ font-family: var(--font-display); font-size: 1.25rem; letter-spacing: -0.025em; font-weight: 600; margin: 2.5rem 0 0.75rem; }}
  .post-prose p {{ color: var(--ink-soft); font-size: 1.075rem; line-height: 1.78; margin: 0 0 1.25rem; }}
  .post-prose p strong {{ color: var(--ink); }}
  .post-prose ul, .post-prose ol {{ padding-left: 1.5rem; margin: 0 0 1.5rem; color: var(--ink-soft); }}
  .post-prose li {{ margin-bottom: 0.55rem; font-size: 1.04rem; line-height: 1.7; }}
  .post-prose a {{ color: var(--accent); border-bottom: 1px solid rgba(0,64,255,0.3); }}
  .post-prose a:hover {{ border-bottom-color: var(--accent); }}
  .post-prose a.btn {{ border-bottom: 0; }}
  .post-prose a.btn-primary,
  .post-prose a.btn-accent,
  .post-prose a.btn-primary:hover,
  .post-prose a.btn-accent:hover {{ color: var(--bg); border-bottom: 0; }}
  .post-prose a.btn-ghost {{ color: var(--ink); border-bottom: 0; }}
  .post-prose a.btn-ghost:hover {{ color: var(--bg); border-bottom: 0; }}
  .post-prose code {{ font-family: var(--font-mono); font-size: 0.88em; background: var(--bg-soft); padding: 2px 6px; border-radius: 4px; color: var(--ink); }}
  .post-prose pre {{ background: var(--ink); color: #E8E8E8; padding: 1.25rem 1.5rem; border-radius: var(--r-md); overflow-x: auto; margin: 1.5rem 0; font-family: var(--font-mono); font-size: 0.86rem; line-height: 1.7; }}
  .post-prose pre code {{ background: transparent; padding: 0; color: inherit; font-size: inherit; }}
  .post-table-wrap {{ width: min(100vw - 2rem, 860px); margin: 2rem 0 2rem 50%; transform: translateX(-50%); overflow-x: auto; border: 1px solid var(--line); border-radius: var(--r-md); background: var(--surface); }}
  .post-prose table {{ width: 100%; border-collapse: collapse; min-width: 680px; font-family: var(--font-sans); font-size: 0.94rem; }}
  .post-prose th, .post-prose td {{ padding: 0.95rem 1rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--line); color: var(--ink-soft); }}
  .post-prose th {{ color: var(--ink); font-weight: 650; background: var(--bg-soft); }}
  .post-prose tr:last-child td {{ border-bottom: 0; }}
  .post-prose hr {{ border: 0; border-top: 1px solid var(--line); margin: 3rem 0; }}
  .post-callout {{ background: var(--accent-soft); border-left: 3px solid var(--accent); padding: 1.25rem 1.5rem; margin: 2rem 0; border-radius: 0 var(--r-md) var(--r-md) 0; }}
  .post-callout p {{ margin: 0; color: var(--ink); font-size: 1rem; }}
  .post-intent-card {{ margin: 2rem 0 0; padding: clamp(1.15rem, 2.8vw, 1.6rem); border: 1px solid var(--line); border-radius: 14px; background: linear-gradient(135deg, rgba(255,255,255,0.72), var(--bg-soft)); box-shadow: 0 18px 60px rgba(30,24,19,0.08); }}
  .post-intent-card h2 {{ font-family: var(--font-display); font-size: clamp(1.25rem, 2.3vw, 1.65rem); line-height: 1.12; letter-spacing: -0.035em; margin: 0; }}
  .post-intent-card p {{ margin: 0.75rem 0 0; color: var(--ink-soft); font-size: 0.98rem; line-height: 1.62; }}
  .post-audit-launcher {{ margin-top: 1.15rem; }}
  .post-audit-launcher label {{ display: block; margin-bottom: 0.45rem; color: var(--muted); font: 650 0.72rem/1.2 var(--font-mono); letter-spacing: 0.1em; text-transform: uppercase; }}
  .post-audit-row {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 0.65rem; align-items: stretch; }}
  .post-audit-row input {{ width: 100%; min-height: 48px; border: 1px solid var(--line); border-radius: var(--r-md); background: rgba(255,255,255,0.78); color: var(--ink); padding: 0 0.95rem; font: 500 0.95rem/1 var(--font-sans); outline: 0; }}
  .post-audit-row input:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(150,74,43,0.14); }}
  .post-audit-row button.btn {{ border: 0; cursor: pointer; color: var(--bg); white-space: nowrap; }}
  .post-intent-actions {{ display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1.2rem; }}
  .post-intent-actions .btn {{ min-height: 44px; }}
  .post-intent-note {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.65rem; margin-top: 1.1rem; }}
  .post-intent-note span {{ display: block; padding: 0.72rem 0.78rem; border: 1px solid var(--line); border-radius: 10px; background: rgba(255,255,255,0.52); color: var(--muted); font: 600 0.72rem/1.35 var(--font-mono); text-transform: uppercase; letter-spacing: 0.08em; }}
  @media (max-width: 620px) {{ .post-audit-row, .post-intent-actions {{ display: grid; grid-template-columns: 1fr; }} .post-audit-row .btn, .post-intent-actions .btn {{ width: 100%; justify-content: center; }} .post-intent-note {{ grid-template-columns: 1fr; }} }}
</style>
  <script>(function(){{try{{var m=localStorage.getItem('lofts-theme');document.documentElement.setAttribute('data-theme',m==='dark'?'dark':'light');}}catch(e){{}}}})();</script>
<link rel="stylesheet" href="/assets/typography.css" />
</head>
<body>

{nav}

<main id="main-content">
<article>
<section class="paper" style="padding: 5rem 0 3rem;">
  <div class="container post-prose" data-reveal>
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);">
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <a href="/blog" style="color: var(--muted);">Blog</a> <span style="margin: 0 8px;">/</span>
      <span style="color: var(--ink);">{p["title"][:60]}</span>
    </nav>

    <div style="display: flex; gap: 8px; margin-bottom: 1.25rem;">
      <span class="tag-pill">{p["category"]}</span>
    </div>

    <h1 class="h-display" style="font-size: clamp(2rem, 4.5vw, 3.6rem); line-height: 1.08;">{p["title"]}</h1>

    <div style="display: flex; align-items: center; gap: 1rem; margin-top: 2rem; padding: 1.25rem 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);">
      <div style="width: 44px; height: 44px; border-radius: 50%; background: var(--accent-soft); color: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: 700;">AK</div>
      <div>
        <div style="font-weight: 600;">Adnan K.</div>
        <div style="font-size: 0.85rem; color: var(--muted);"><time datetime="{p["date"]}">{date_readable}</time> · {p["readingTime"]} read</div>
      </div>
    </div>

    {intent_card_html}

    <img class="post-hero-img" src="/assets/blog/{p["slug"]}.png?v={CACHE_VER}" alt="{p["title"]}" width="1200" height="675" style="margin-top: 2rem;" />
  </div>
</section>

<section style="padding: 0 0 4rem;">
  <div class="container post-prose">
    <p style="font-size: 1.2rem; line-height: 1.65; color: var(--ink); font-family: var(--font-display); font-weight: 500; letter-spacing: -0.025em;">{p["hook"]}</p>

    {body_html}

    <hr/>

    <h2>If you'd rather not do this yourself</h2>
    <p>This is the work I do for clients. If you want it done properly, the relevant offer is <a href="{p["funnelTo"]}">{p["funnelLabel"]}</a>.</p>

    <p style="text-align: center; margin-top: 2.5rem;">
      <a href="{p["funnelTo"]}" class="btn btn-primary">Read about {p["funnelLabel"]} &nbsp;&rarr;</a>
    </p>

    <hr style="margin-top: 4rem;"/>

    <div style="display: grid; grid-template-columns: 64px 1fr; gap: 1.25rem; align-items: start; margin-top: 2rem;">
      <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--accent-soft); color: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.4rem;">AK</div>
      <div>
        <h3 style="font-family: var(--font-display); font-size: 1.25rem; font-weight: 600; margin: 0; letter-spacing: -0.025em;">Adnan K.</h3>
        <p style="color: var(--muted); margin: 0.25rem 0 0.75rem; font-size: 0.92rem;">Senior Shopify &amp; WooCommerce engineer. Top Rated Plus on Upwork. high-volume delivery, 100% Job Success.</p>
        <div style="display: flex; gap: 1rem; font-size: 0.88rem;">
          <a href="/about.html" style="color: var(--accent);">About</a>
          <a href="/portfolio" style="color: var(--accent);">Portfolio</a>
          <a href="/blog" style="color: var(--accent);">More posts</a>
        </div>
      </div>
    </div>
  </div>
</section>
</article>
</main>

{footer}

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="/assets/main.js?v={CACHE_VER}" defer></script>
<script src="/assets/widgets.js?v={CACHE_VER}" defer></script>
</body>
</html>
'''


def render_location_page(loc, nav, footer):
    """Render a country-specific service landing page."""
    title = f"Shopify & WooCommerce Developer {loc['country']} | Adnan K."
    meta = f"Hire a senior Shopify and WooCommerce developer {loc['tagline']}. Almost 15 years of custom store work shipped, 100% Job Success. Top Rated Plus on Upwork. {loc['hours']}."
    canonical = f"{SITE}/services/shopify-developer-{loc['code']}.html"

    hreflang_tags = "\n".join([
        f'<link rel="alternate" hreflang="en-{l["code"]}" href="{SITE}/services/shopify-developer-{l["code"]}.html" />'
        for l in LOCATIONS
    ]) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/" />'

    return f'''<!DOCTYPE html>
<html lang="en-{loc["code"]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>{title}</title>
<meta name="description" content="{meta}" />
<link rel="canonical" href="{canonical}" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="keywords" content="shopify developer {loc['country'].lower()}, hire shopify developer {loc['country'].lower()}, woocommerce developer {loc['country'].lower()}, wordpress developer {loc['country'].lower()}, ecommerce developer {loc['country'].lower()}" />

{hreflang_tags}

<meta property="og:type" content="website" />
<meta property="og:url" content="{canonical}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{meta}" />
<meta property="og:image" content="{SITE}/assets/og.jpg?v=2" />
<meta name="twitter:card" content="summary_large_image" />

<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<meta name="theme-color" content="#F4F0EA" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />
<link rel="stylesheet" href="/assets/experience.css?v=20260801g" data-lofts-experience />

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Adnan K. — Shopify & WooCommerce Developer for {loc['country']}",
  "description": "{meta}",
  "url": "{canonical}",
  "image": "{SITE}/assets/og.jpg?v=2",
  "areaServed": {{ "@type": "Country", "name": "{loc['country']}" }},
  "serviceType": ["Shopify Development", "WooCommerce Development", "WordPress Development", "Shopify Plus Migration", "Speed Optimization"],
  "provider": {{
    "@type": "Person",
    "name": "Adnan K.",
    "url": "{SITE}",
    "jobTitle": "Senior Shopify & WooCommerce Developer",
    "sameAs": ["https://www.upwork.com/freelancers/wordpressandshopifydeveloper"]
  }}
}}
</script>
<script type="application/ld+json">
{{ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [ {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}}, {{"@type":"ListItem","position":2,"name":"Services","item":"{SITE}/services/"}}, {{"@type":"ListItem","position":3,"name":"Shopify Developer {loc['country']}","item":"{canonical}"}} ] }}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Do you work with {loc['demonym']} clients?",
      "acceptedAnswer": {{ "@type": "Answer", "text": "Yes — a meaningful share of my launch and ongoing work is with {loc['country']}-based clients across DTC, B2B, and editorial verticals. {loc['hours']}." }}
    }},
    {{
      "@type": "Question",
      "name": "What does a Shopify build for a {loc['demonym']} brand effort?",
      "acceptedAnswer": {{ "@type": "Answer", "text": "A serious Shopify scope depends on theme condition, integrations, content, analytics, migration risk, and launch timing. The right next step is a short audit and written scope so the work is planned around the store's real constraints." }}
    }},
    {{
      "@type": "Question",
      "name": "Can you handle {loc['currency']} payment processing?",
      "acceptedAnswer": {{ "@type": "Answer", "text": "Yes. Shopify Payments, Stripe, and regional gateways are all covered. For {loc['country']}-specific regional payment methods, I work with the local provider that best fits the merchant." }}
    }},
    {{
      "@type": "Question",
      "name": "Do you offer ongoing support after launch?",
      "acceptedAnswer": {{ "@type": "Answer", "text": "Yes — many clients move into ongoing support after launch for continued CRO, speed, and feature work." }}
    }}
  ]
}}
</script>
<link rel="stylesheet" href="/assets/typography.css" />
</head>
<body>

{nav}

<section class="paper" style="padding: 7rem 0 4rem;">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);">
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <a href="/services" style="color: var(--muted);">Services</a> <span style="margin: 0 8px;">/</span>
      <span style="color: var(--ink);">Shopify Developer {loc['country']}</span>
    </nav>

    <div data-reveal style="max-width: 880px;">
      <span class="eyebrow">Senior Shopify, WooCommerce &amp; WordPress engineering · {loc['country']}</span>
      <h1 class="h-display" data-split="words" style="margin-top: 1.5rem;">
        Hire a senior Shopify developer <span class="italic-serif">in {loc['country']}.</span>
      </h1>
      <p class="lead" style="margin-top: 2rem;">
        Almost 15 years. Deep store delivery experience. Top Rated Plus on Upwork {loc['tagline']}.
        {loc['hours']}. Async-friendly, written-first, and senior-only — no junior team, no PM layer.
      </p>
      <div style="display: flex; gap: 1rem; margin-top: 2.5rem; flex-wrap: wrap;">
        <a href="/#contact" class="btn btn-primary">Get in touch &nbsp;&rarr;</a>
        <a href="/portfolio" class="btn btn-ghost">See 47 case studies</a>
      </div>
    </div>
  </div>
</section>

<section class="section-sm" style="border-top: 1px solid var(--line); padding: 4rem 0;">
  <div class="container">
    <div data-reveal style="max-width: 760px;">
      <span class="eyebrow">{loc['country']} market notes</span>
      <p style="font-family: var(--font-serif); font-size: 1.2rem; line-height: 1.65; color: var(--ink); margin-top: 1.5rem;">{loc['marketNotes']}</p>
    </div>
  </div>
</section>

<section class="section" style="border-top: 1px solid var(--line);">
  <div class="container">
    <div data-reveal style="max-width: 780px; margin-bottom: 4rem;">
      <span class="eyebrow">What I build for {loc['demonym']} brands</span>
      <h2 class="h-1" style="margin-top: 1.25rem;">Five capabilities. One operator. <span class="italic-serif">Senior-only delivery.</span></h2>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;">
      <a href='/services/shopify-development.html' class="card" data-reveal style="text-decoration: none;">
        <span class="eyebrow">Shopify Development</span>
        <h3 class="h-2" style="margin: 1rem 0 0.75rem;">Custom Shopify builds</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Themes, sections, conversion-tuned PDPs. From discovery to launch in 4–8 weeks.</p>
      </a>
      <a href="/services/shopify-plus-migration.html" class="card" data-reveal style="text-decoration: none;">
        <span class="eyebrow">Shopify Plus Migration</span>
        <h3 class="h-2" style="margin: 1rem 0 0.75rem;">Migrate to Plus</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">From Advanced or WooCommerce. B2B, checkout extensions, expansion stores.</p>
      </a>
      <a href="/services/woocommerce-development.html" class="card" data-reveal style="text-decoration: none;">
        <span class="eyebrow">WooCommerce Development</span>
        <h3 class="h-2" style="margin: 1rem 0 0.75rem;">WooCommerce that scales</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Custom themes, subscriptions, B2B tiers, performance work that survives traffic spikes.</p>
      </a>
      <a href='/services/speed-optimization.html' class="card" data-reveal style="text-decoration: none;">
        <span class="eyebrow">Speed Optimization</span>
        <h3 class="h-2" style="margin: 1rem 0 0.75rem;">Pass Core Web Vitals</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">LCP under 2.5s, CLS under 0.1, INP under 200ms. Field-data improvement guaranteed.</p>
      </a>
      <a href="/services/custom-app-development.html" class="card" data-reveal style="text-decoration: none;">
        <span class="eyebrow">Custom App Development</span>
        <h3 class="h-2" style="margin: 1rem 0 0.75rem;">Internal tools &amp; integrations</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Custom Shopify apps, WMS integrations, B2B portals, internal ops automation.</p>
      </a>
      <a href="/services/conversion-rate-optimization.html" class="card" data-reveal style="text-decoration: none;">
        <span class="eyebrow">CRO</span>
        <h3 class="h-2" style="margin: 1rem 0 0.75rem;">Conversion engineering</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">PDP tuning, checkout optimization, A/B testing infrastructure that compounds.</p>
      </a>
    </div>
  </div>
</section>

<section class="section-sm" style="background: var(--bg-soft); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 5rem 0;">
  <div class="container">
    <div data-reveal style="max-width: 780px; margin-bottom: 3rem;">
      <span class="eyebrow">FAQs · {loc['country']}</span>
      <h2 class="h-1" style="margin-top: 1.25rem;">Common questions from {loc['demonym']} founders.</h2>
    </div>

    <div style="display: grid; gap: 2rem; max-width: 780px;">
      <div data-reveal>
        <h3 class="h-2" style="margin: 0 0 0.5rem;">Do you work with {loc['demonym']} clients?</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Yes — a meaningful share of my launch and ongoing work is with {loc['country']}-based clients across DTC, B2B, and editorial verticals. {loc['hours']}.</p>
      </div>
      <div data-reveal>
        <h3 class="h-2" style="margin: 0 0 0.5rem;">What does a Shopify build for a {loc['demonym']} brand effort?</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">A serious Shopify scope depends on theme condition, integrations, content, analytics, migration risk, and launch timing. The right next step is a short audit and written scope so the work is planned around the store's real constraints.</p>
      </div>
      <div data-reveal>
        <h3 class="h-2" style="margin: 0 0 0.5rem;">Can you handle {loc['currency']} payment processing?</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Yes. Shopify Payments, Stripe, and regional gateways. For {loc['country']}-specific regional payment methods, I work with the provider that best fits the merchant.</p>
      </div>
      <div data-reveal>
        <h3 class="h-2" style="margin: 0 0 0.5rem;">Do you offer ongoing support after launch?</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Yes — many clients move into ongoing support after launch for continued CRO, speed, and feature work.</p>
      </div>
      <div data-reveal>
        <h3 class="h-2" style="margin: 0 0 0.5rem;">How do account workflows and contracts work for {loc['country']}?</h3>
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">Standard MSA + SOW structure. Engagement administration is agreed before work begins, with the working rhythm documented in plain English.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div data-reveal style="background: var(--ink); color: var(--bg); padding: 4rem 3rem; border-radius: var(--r-lg); text-align: center; max-width: 900px; margin: 0 auto;">
      <span style="font-family: var(--font-sans); font-size: 0.72rem; color: rgba(244,240,234,0.6); text-transform: uppercase; letter-spacing: 0.22em;">If you got this far</span>
      <h2 class="h-1" style="color: var(--bg); margin: 1.5rem 0;">Send your store URL.<br/><span class="italic-serif">I'll audit it before the call.</span></h2>
      <p style="font-family: var(--font-serif); font-size: 1.15rem; line-height: 1.6; color: rgba(244,240,234,0.85); max-width: 56ch; margin: 0 auto 2.5rem;">Three specific suggestions you can act on whether you hire me or not. Reply window: four hours, {loc['country']} business hours friendly.</p>
      <a href="/#contact" class="btn" style="background: var(--bg); color: var(--ink); padding: 1rem 2rem;">Get in touch &nbsp;&rarr;</a>
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


def update_posts_json():
    """Update posts.json with all POSTS (newest first)."""
    data = {
        "version": 2,
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "schema": "Source of truth for blog posts. Generated by scripts/seo_engine.py.",
        "categories": ["Speed", "CRO", "Shopify", "WooCommerce", "AI & Automation", "Custom Apps", "Design", "Migration", "SEO", "Process"],
        "posts": []
    }

    # Preserve any existing posts not in our spec
    existing = {}
    if POSTS_JSON.exists():
        old = json.loads(POSTS_JSON.read_text())
        for post in old.get("posts", []):
            existing[post["slug"]] = post

    new_slugs = set()
    for p in POSTS:
        if p["slug"] in EXCLUDED_PUBLIC_BLOG_SLUGS:
            continue
        entry = {
            "slug": p["slug"],
            "title": p["title"],
            "excerpt": p["excerpt"],
            "category": p["category"],
            "date": p["date"],
            "readingTime": p["readingTime"],
            "primaryKeyword": p["primaryKeyword"],
            "secondaryKeyword": p["secondaryKeyword"],
            "funnelTo": p["funnelTo"],
            "featured": p.get("featured", False),
            "published": True
        }
        data["posts"].append(entry)
        new_slugs.add(p["slug"])

    # Append legacy posts not in current specs
    for slug, post in existing.items():
        if slug not in new_slugs and slug not in EXCLUDED_PUBLIC_BLOG_SLUGS:
            data["posts"].append(post)

    # Sort by date desc
    data["posts"].sort(key=lambda x: x["date"], reverse=True)

    POSTS_JSON.write_text(json.dumps(data, indent=2))
    print(f"  ✓ posts.json updated ({len(data['posts'])} posts)")


def gen_covers():
    """Generate featured cover images for every published post.
    Reads posts.json (so run after update_posts_json). Soft-fails if Pillow
    or fonts are unavailable in the runtime — covers can be regenerated later."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generate_blog_covers", Path(__file__).resolve().parent / "generate_blog_covers.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    except Exception as e:
        print(f"  ! cover generation skipped ({type(e).__name__}: {e}) — regenerate with scripts/generate_blog_covers.py")


def gen_blog():
    """Generate all blog posts, their covers, and refresh posts.json."""
    nav, footer = load_nav_and_footer()
    for p in POSTS:
        if p["slug"] in EXCLUDED_PUBLIC_BLOG_SLUGS:
            continue
        html = render_blog_post(p, nav, footer)
        out = BLOG_DIR / f"{p['slug']}.html"
        out.write_text(html)
        print(f"  ✓ blog/{p['slug']}.html")
    update_posts_json()
    gen_covers()


def gen_locations():
    """Generate all country service pages."""
    nav, footer = load_nav_and_footer()
    for loc in LOCATIONS:
        html = render_location_page(loc, nav, footer)
        out = SERVICES_DIR / f"shopify-developer-{loc['code']}.html"
        out.write_text(html)
        print(f"  ✓ services/shopify-developer-{loc['code']}.html")


def gen_sitemap():
    """Crawl the filesystem for .html files and generate sitemap.xml."""
    today = datetime.now().strftime("%Y-%m-%d")
    urls = []
    seen = {}

    def add_url(path, freq, priority):
        if path == "/":
            canonical_path = "/"
        elif path.startswith("/notes/") or path == "/notes":
            return
        elif path.endswith("/index.html"):
            canonical_path = path[: -len("/index.html")] or "/"
        elif path.endswith("/"):
            canonical_path = path.rstrip("/")
        else:
            canonical_path = path
        if canonical_path in SITEMAP_EXCLUDED_PATHS:
            return
        url = f"{SITE}{canonical_path}"
        if url in seen:
            index = seen[url]
            existing = urls[index]
            if float(priority) > float(existing[3]):
                urls[index] = (url, today, freq, priority)
            return
        seen[url] = len(urls)
        urls.append((url, today, freq, priority))

    # Static top-level pages with priorities
    top = {
        "/": ("1.0", "weekly"),
        "/about.html": ("0.9", "monthly"),
        "/portfolio/": ("0.95", "weekly"),
        "/blog/": ("0.9", "weekly"),
        "/process/": ("0.7", "monthly"),
        "/tools/": ("0.7", "monthly"),
        "/now/": ("0.6", "weekly"),
        "/privacy.html": ("0.3", "yearly"),
        "/terms.html": ("0.3", "yearly"),
        "/cookie-policy.html": ("0.3", "yearly"),
    }
    for path, (priority, freq) in top.items():
        add_url(path, freq, priority)

    # All services
    for svc in sorted(SERVICES_DIR.glob("*.html")):
        add_url(f"/services/{svc.name}", "monthly", "0.85")

    # Vertical pillar pages — high priority commercial pages
    work_dir = ROOT / "work"
    if work_dir.exists():
        for pillar in sorted(work_dir.iterdir()):
            if pillar.is_dir() and (pillar / "index.html").exists():
                add_url(f"/work/{pillar.name}/", "weekly", "0.95")

    # Brand guide is publicly linked from the footer, so keep it indexable and discoverable.
    if (ROOT / "brand.html").exists():
        add_url("/brand.html", "monthly", "0.55")

    # All portfolio
    for pf in sorted(ROOT.glob("portfolio/*.html")):
        add_url(f"/portfolio/{pf.name}", "monthly", "0.75")

    # All blog posts
    for post in sorted(BLOG_DIR.glob("*.html")):
        if post.name.startswith("_"):
            continue
        if post.stem in EXCLUDED_PUBLIC_BLOG_SLUGS:
            continue
        add_url(f"/blog/{post.name}", "monthly", "0.8")

    # Tools and process directory pages. Notes are legacy URLs redirected to /blog.
    for d in ["tools", "process"]:
        sub = ROOT / d
        if sub.exists():
            for f in sorted(sub.glob("*.html")):
                if not f.name.startswith("_"):
                    add_url(f"/{d}/{f.name}", "monthly", "0.65")

    # Catch directory index pages and newer batch assets that live outside the
    # legacy explicit lists, while skipping private, API, noindex, and redirect-only paths.
    skipped_dirs = {".git", ".vercel", "admin", "api", "assets", "scripts", "tests"}
    skipped_files = {"404.html"}
    for page in sorted(ROOT.rglob("*.html")):
        rel = page.relative_to(ROOT)
        if any(part.startswith(".") or part in skipped_dirs for part in rel.parts[:-1]):
            continue
        if rel.parts[0] == "notes":
            continue
        if rel.name.startswith("_") or rel.name in skipped_files:
            continue
        add_url(f"/{rel.as_posix()}", "monthly", "0.65")

    # Build XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u, lastmod, freq, prio in urls:
        # Add hreflang for location pages
        if "shopify-developer-" in u and u.endswith(".html"):
            xml.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{lastmod}</lastmod>")
            for loc in LOCATIONS:
                region_code = HREFLANG_REGION_CODES.get(loc["code"], loc["code"])
                xml.append(f'    <xhtml:link rel="alternate" hreflang="en-{region_code}" href="{SITE}/services/shopify-developer-{loc["code"]}.html"/>')
            xml.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>')
            xml.append(f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>")
        else:
            xml.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>")
    xml.append("</urlset>")

    SITEMAP.write_text("\n".join(xml))
    print(f"  ✓ sitemap.xml regenerated ({len(urls)} URLs)")


def refresh_blog_index():
    """Refresh blog/index.html post grid from posts.json."""
    index_path = BLOG_DIR / "index.html"
    if not index_path.exists():
        return
    html = index_path.read_text()
    data = json.loads(POSTS_JSON.read_text())
    posts = [p for p in data["posts"] if p.get("published")]

    cards = []
    for i, p in enumerate(posts):
        cat = p["category"]
        date_fmt = datetime.strptime(p["date"], "%Y-%m-%d").strftime("%b %d, %Y")
        hidden = " hidden" if i >= 15 else ""
        cat_key = re.sub(r'[^a-z0-9]+', '-', cat.lower()).strip('-')
        cards.append(f'''      <article class="post-card" data-reveal data-blog-card data-blog-category="{cat_key}"{hidden}>
        <a href="/blog/{p["slug"]}.html" class="post-card-link">
          <img class="post-card-img" src="/assets/blog/{p["slug"]}.png?v={CACHE_VER}" alt="" width="1200" height="675" loading="lazy" />
          <div class="post-card-body">
            <div class="post-card-meta">
              <span class="tag-pill">{cat}</span>
              <time datetime="{p["date"]}">{date_fmt}</time>
              <span>·</span>
              <span>{p["readingTime"]}</span>
            </div>
            <h2 class="post-card-title">{p["title"]}</h2>
            <p class="post-card-excerpt">{p["excerpt"]}</p>
            <span class="post-card-cta">Read post &rarr;</span>
          </div>
        </a>
      </article>''')

    posts_html = "\n".join(cards)
    new_html = re.sub(
        r'<!-- POSTS_START -->.*?<!-- POSTS_END -->',
        f'<!-- POSTS_START -->\n{posts_html}\n      <!-- POSTS_END -->',
        html, flags=re.DOTALL
    )
    if new_html != html:
        index_path.write_text(new_html)
        print(f"  ✓ blog/index.html refreshed ({len(posts)} posts)")
    else:
        print(f"  · blog/index.html unchanged (no POSTS_START/END markers found)")


def main():
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("blog", "all"):
        print("→ Generating blog posts...")
        gen_blog()
        refresh_blog_index()
    if mode in ("locations", "all"):
        print("→ Generating location service pages...")
        gen_locations()
    if mode in ("sitemap", "all"):
        print("→ Regenerating sitemap...")
        gen_sitemap()
    print("\nDone.")


if __name__ == "__main__":
    main()
