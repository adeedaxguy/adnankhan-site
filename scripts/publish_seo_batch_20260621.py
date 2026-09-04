#!/usr/bin/env python3
"""
Publish the 2026-06-21 SEO content batch.

This keeps the long-form posts generated through the same renderer as the
existing hand-authored blog, then updates posts.json, the blog index, covers,
and sitemap.
"""

import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog"
POSTS_JSON = BLOG_DIR / "posts.json"

spec = importlib.util.spec_from_file_location("seo_engine", ROOT / "scripts" / "seo_engine.py")
seo_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo_engine)


TOPICS = [
    {
        "slug": "ai-search-optimization-service-businesses",
        "title": "AI Search Optimization for Service Businesses in 2026",
        "excerpt": "A practical guide to making a service business easier to cite, trust, and choose across Google AI Overviews, ChatGPT, Perplexity, and traditional search.",
        "meta": "AI search optimization for service businesses: how to structure pages, proof, schema, FAQs, and internal links so buyers and answer engines can trust you.",
        "category": "SEO",
        "primary": "ai search optimization for service businesses",
        "secondary": "AI SEO for local service businesses",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "service business owners who rely on enquiries, calls, and booked consultations",
        "surface": "AI answers and traditional local search results",
        "intent": "prove that the business is real, specific, experienced, and safe to contact",
        "problem": "the site says what the business does, but it does not give search systems enough structured evidence to cite it confidently",
        "asset": "service pages, proof blocks, FAQs, case studies, local signals, and a clean technical foundation",
        "proof": "named services, visible process, case-study links, location context, team details, reviews, and clear next steps",
        "link": "/websites",
    },
    {
        "slug": "google-ai-overviews-seo-business-websites",
        "title": "Google AI Overviews SEO for Business Websites",
        "excerpt": "Google AI Overviews changed how buyers discover answers. This is how a business website should structure pages for citation, trust, and conversion.",
        "meta": "Google AI Overviews SEO guide for business websites: direct answers, entity clarity, structured data, proof, and pages that still convert human buyers.",
        "category": "SEO",
        "primary": "Google AI Overviews SEO",
        "secondary": "optimize website for AI Overviews",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "founders, marketers, and service teams that cannot afford to disappear inside answer-first search",
        "surface": "Google AI Overviews, organic results, and the source panels attached to AI answers",
        "intent": "make the page easy to summarize without removing the reason to click",
        "problem": "many pages hide the actual answer below brand copy, vague sections, and thin proof",
        "asset": "answer-led page sections, structured data, original examples, FAQs, and useful next-step CTAs",
        "proof": "specific claims, screenshots, process notes, named services, and internal links to deeper evidence",
        "link": "/services/technical-seo-audit.html",
    },
    {
        "slug": "chatgpt-seo-small-business",
        "title": "ChatGPT SEO for Small Business Websites",
        "excerpt": "People now ask AI tools who to hire, what to fix, and which provider to trust. Here is how small business websites should prepare.",
        "meta": "ChatGPT SEO for small business: build clear entity signals, trustworthy service pages, helpful FAQs, and proof that AI tools can understand.",
        "category": "AI & Automation",
        "primary": "ChatGPT SEO for small business",
        "secondary": "optimize small business website for ChatGPT",
        "funnel": "/services/ai-chatbot-automation.html",
        "label": "AI Chatbot & Automation",
        "audience": "small business owners who want organic leads without depending only on ads",
        "surface": "ChatGPT, AI assistants, classic search, and referral journeys from AI-generated answers",
        "intent": "make the business recognizable as a strong answer to a specific buyer problem",
        "problem": "the website has pages, but the business entity, service fit, and proof are scattered",
        "asset": "a consistent entity footprint, service pages, comparison answers, FAQs, and review-aware proof",
        "proof": "clear services, named industries, owner details, service area, case studies, and plain-language promises",
        "link": "/about.html",
    },
    {
        "slug": "llm-seo-checklist-business-websites",
        "title": "LLM SEO Checklist for Business Websites",
        "excerpt": "A hands-on checklist for making a business website easier for large language models, search engines, and buyers to parse.",
        "meta": "LLM SEO checklist for business websites: entity clarity, crawlability, headings, schema, citations, proof, internal links, and conversion paths.",
        "category": "SEO",
        "primary": "LLM SEO checklist",
        "secondary": "large language model SEO",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "teams that want AI search visibility without turning the website into thin SEO copy",
        "surface": "large language model answer engines, AI search, and normal organic discovery",
        "intent": "make the site understandable, extractable, and credible at the same time",
        "problem": "LLMs can only summarize what the page makes clear; vague positioning becomes vague answers",
        "asset": "semantic headings, structured pages, schema, source-like explanations, and linked proof",
        "proof": "case studies, original diagrams, service definitions, implementation notes, and transparent limitations",
        "link": "/portfolio/",
    },
    {
        "slug": "ai-visibility-audit",
        "title": "AI Visibility Audit: What to Check Before Competitors Own the Answer",
        "excerpt": "An AI visibility audit shows whether your website, schema, reviews, and proof are strong enough to be used in AI-generated answers.",
        "meta": "AI visibility audit guide: check entity clarity, service pages, reviews, structured data, technical health, and conversion paths before competitors get cited.",
        "category": "SEO",
        "primary": "AI visibility audit",
        "secondary": "AI search visibility audit",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "businesses that already have a website but are unsure whether AI search can understand and trust it",
        "surface": "AI answer engines, Google AI surfaces, local search, and comparison-style buyer journeys",
        "intent": "find the missing evidence before traffic and leads start shifting elsewhere",
        "problem": "the brand may be technically indexed but still invisible in answer-led discovery",
        "asset": "a page-by-page audit of entity signals, content depth, technical health, local proof, and conversion flow",
        "proof": "query checks, page screenshots, schema validation, internal link maps, and before-after recommendations",
        "link": "/tools/",
    },
    {
        "slug": "ai-voice-agent-appointment-booking",
        "title": "AI Voice Agent for Appointment Booking: Website and Workflow Guide",
        "excerpt": "AI voice agents book more appointments when the website, offer, script, CRM, and human handoff are designed as one system.",
        "meta": "AI voice agent appointment booking guide: website flow, lead qualification, call scripts, CRM handoff, compliance, and measurement for service businesses.",
        "category": "AI & Automation",
        "primary": "AI voice agent for appointment booking",
        "secondary": "AI appointment booking agent",
        "funnel": "/services/ai-calling-agents.html",
        "label": "AI Calling Agents",
        "audience": "clinics, consultants, agencies, trades, and service teams that lose leads when nobody replies quickly",
        "surface": "website forms, phone enquiries, missed calls, CRM queues, and automated follow-up flows",
        "intent": "turn intent into a booked next step without making the buyer feel processed",
        "problem": "the agent can call, but the website and CRM often fail to give it enough context to qualify properly",
        "asset": "offer pages, intake forms, call scripts, qualification rules, calendar logic, and human escalation paths",
        "proof": "call outcomes, appointment status, reason codes, transcript review, and clear consent language",
        "link": "/services/ai-calling-agents.html",
    },
    {
        "slug": "ai-receptionist-small-business",
        "title": "AI Receptionist for Small Business: What Your Website Must Support",
        "excerpt": "An AI receptionist is only as good as the information, routing, and escalation rules around it. Here is the website setup that makes it useful.",
        "meta": "AI receptionist for small business: how to structure website content, FAQs, forms, call routing, CRM fields, and handoff rules before launch.",
        "category": "AI & Automation",
        "primary": "AI receptionist for small business",
        "secondary": "AI phone receptionist for business",
        "funnel": "/services/ai-calling-agents.html",
        "label": "AI Calling Agents",
        "audience": "small service businesses that want faster response without losing the human feel",
        "surface": "phone calls, web enquiries, booking forms, service pages, and follow-up messages",
        "intent": "answer common questions, collect the right details, and route real opportunities quickly",
        "problem": "most websites do not contain the operational answers an AI receptionist needs",
        "asset": "a structured knowledge base, service-specific FAQs, form logic, call routing, and CRM notes",
        "proof": "fewer missed calls, cleaner intake data, faster replies, and visible handoff rules",
        "link": "/services/ai-calling-agents.html",
    },
    {
        "slug": "ai-lead-follow-up-automation",
        "title": "AI Lead Follow-Up Automation for Service Businesses",
        "excerpt": "Most leads are not lost because the offer is weak. They are lost because follow-up is late, vague, or disconnected from the website.",
        "meta": "AI lead follow-up automation for service businesses: form routing, email and SMS sequences, AI calling, CRM stages, and human handoff.",
        "category": "AI & Automation",
        "primary": "AI lead follow-up automation",
        "secondary": "automated lead follow up system",
        "funnel": "/services/ai-chatbot-automation.html",
        "label": "AI Chatbot & Automation",
        "audience": "teams that receive enquiries but do not always respond while buyer intent is still high",
        "surface": "website forms, chat, email, SMS, AI calls, CRM tasks, and calendar booking",
        "intent": "move a fresh enquiry to the right next step before attention fades",
        "problem": "forms collect information, but the business does not have a reliable path from enquiry to conversation",
        "asset": "routing rules, qualification fields, message templates, CRM stages, and AI-assisted follow-up",
        "proof": "response time, booked calls, disqualified leads, unanswered leads, and follow-up completion",
        "link": "/services/ai-chatbot-automation.html",
    },
    {
        "slug": "local-landing-page-seo",
        "title": "Local Landing Page SEO: Build City Pages That Actually Rank",
        "excerpt": "City landing pages can bring qualified leads, but only when they are useful local pages rather than copied doorway pages.",
        "meta": "Local landing page SEO guide: build city pages with real local proof, service intent, FAQs, internal links, schema, and conversion paths.",
        "category": "SEO",
        "primary": "local landing page SEO",
        "secondary": "city landing pages SEO",
        "funnel": "/websites",
        "label": "Websites by Industry",
        "audience": "businesses planning state, city, or service-area pages for organic lead generation",
        "surface": "Google local organic results, map-adjacent searches, AI summaries, and service comparison searches",
        "intent": "match location intent without creating thin copy that search engines and buyers ignore",
        "problem": "many location pages swap the city name and call it SEO, which creates weak pages with no real reason to rank",
        "asset": "city-specific service framing, local proof, FAQs, nearby internal links, and conversion-focused page design",
        "proof": "service area clarity, project examples, local search language, reviews, and contact paths",
        "link": "/locations/usa/",
    },
    {
        "slug": "service-area-pages-seo",
        "title": "Service Area Pages SEO Without Doorway Page Risk",
        "excerpt": "Service area pages should help buyers in a real location make a decision. This guide shows how to scale them without thin content.",
        "meta": "Service area pages SEO guide: avoid doorway pages by adding real service detail, local proof, FAQs, internal links, schema, and helpful CTAs.",
        "category": "SEO",
        "primary": "service area pages SEO",
        "secondary": "service location pages SEO",
        "funnel": "/websites",
        "label": "Websites by Industry",
        "audience": "service businesses expanding across cities, suburbs, states, or regions",
        "surface": "local organic results, AI answer snippets, service pages, and comparison queries",
        "intent": "show that the business genuinely serves the area and understands the buyer context",
        "problem": "scaled pages often become repetitive, and repetition gives people no reason to trust the result",
        "asset": "a reusable page system with unique local proof, service-specific detail, FAQs, and internal linking",
        "proof": "named areas, nearby examples, service constraints, review snippets, process detail, and clear contact routes",
        "link": "/locations/usa/",
    },
    {
        "slug": "website-design-near-me-seo",
        "title": "Website Design Near Me SEO: How Local Brands Win the Search",
        "excerpt": "Near-me searches are not won by repeating a phrase. They are won by matching local intent, trust, proof, and speed.",
        "meta": "Website design near me SEO guide: local intent, service pages, Google Business Profile signals, city pages, schema, proof, and conversion flow.",
        "category": "Websites",
        "primary": "website design near me SEO",
        "secondary": "web design near me search optimization",
        "funnel": "/websites",
        "label": "Websites by Industry",
        "audience": "local brands, service providers, and studios competing for high-intent local searches",
        "surface": "near-me searches, local organic pages, Google Business Profile, and AI-assisted recommendations",
        "intent": "prove local fit and service credibility before the visitor opens three competitor tabs",
        "problem": "businesses chase the phrase but ignore the signals that make a local result believable",
        "asset": "local page structure, business profile alignment, service proof, reviews, schema, and enquiry design",
        "proof": "location clarity, local project examples, review language, fast mobile pages, and easy contact",
        "link": "/websites",
    },
    {
        "slug": "programmatic-seo-local-business",
        "title": "Programmatic SEO for Local Business: Scale Without Thin Pages",
        "excerpt": "Programmatic SEO can work for local businesses if the page system adds real utility, local proof, and a better decision path.",
        "meta": "Programmatic SEO for local business: build scalable location and service pages without thin content, duplicate copy, or weak conversion flow.",
        "category": "SEO",
        "primary": "programmatic SEO for local business",
        "secondary": "scalable local SEO pages",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "businesses with many services, cities, industries, or buyer types to cover",
        "surface": "state pages, city pages, service pages, industry pages, and AI-generated answer sources",
        "intent": "scale useful pages while keeping every page worthy of indexation",
        "problem": "programmatic pages become risky when the template is stronger than the content",
        "asset": "a page database, unique local/service fields, editorial rules, internal links, and quality checks",
        "proof": "unique examples, FAQs, constraints, page-specific CTAs, and measurable search intent coverage",
        "link": "/locations/usa/",
    },
    {
        "slug": "conversion-focused-web-design",
        "title": "Conversion-Focused Web Design: The Page System Behind More Leads",
        "excerpt": "A conversion-focused website is not louder. It is clearer. Here is the page system that helps visitors understand, trust, and enquire.",
        "meta": "Conversion-focused web design guide: first screen clarity, proof, navigation, CTAs, trust signals, page speed, forms, and measurement.",
        "category": "CRO",
        "primary": "conversion-focused web design",
        "secondary": "website design for lead generation",
        "funnel": "/services/conversion-rate-optimization.html",
        "label": "Conversion Rate Optimization",
        "audience": "businesses that already get visitors but do not receive enough qualified enquiries",
        "surface": "homepages, service pages, landing pages, forms, portfolio sections, and follow-up flows",
        "intent": "make the next step feel obvious, safe, and worth taking",
        "problem": "the site may look polished while still leaving the visitor unsure what to do",
        "asset": "message hierarchy, proof placement, friction-light forms, fast mobile pages, and analytics",
        "proof": "before-after page maps, lead quality, form completion, CTA clicks, scroll depth, and booked calls",
        "link": "/services/conversion-rate-optimization.html",
    },
    {
        "slug": "website-redesign-lead-generation",
        "title": "Website Redesign for Lead Generation: Fix the Path Before the Paint",
        "excerpt": "A lead-generation redesign should fix message, proof, routing, speed, and forms before visual polish takes over the project.",
        "meta": "Website redesign for lead generation: improve message clarity, proof, page flow, forms, technical SEO, speed, and measurement before launch.",
        "category": "Websites",
        "primary": "website redesign for lead generation",
        "secondary": "lead generation website redesign",
        "funnel": "/services/design-and-branding.html",
        "label": "Design & Branding",
        "audience": "founders and service teams planning a redesign because the current site is not producing enough opportunities",
        "surface": "homepage, service pages, case studies, forms, thank-you pages, analytics, and follow-up sequences",
        "intent": "turn the redesign into a stronger sales path rather than a visual refresh",
        "problem": "redesigns often change the look while preserving the same weak page logic",
        "asset": "a conversion map, updated messaging, proof-led sections, faster templates, and better measurement",
        "proof": "clearer first screen, stronger case studies, improved form paths, and tracked lead quality",
        "link": "/portfolio/",
    },
    {
        "slug": "homepage-ux-audit-checklist",
        "title": "Homepage UX Audit Checklist for Higher-Intent Visitors",
        "excerpt": "Your homepage has seconds to prove relevance. This UX audit checklist shows what to fix before a visitor leaves or chooses a competitor.",
        "meta": "Homepage UX audit checklist: first screen clarity, navigation, proof, CTA focus, mobile layout, page speed, accessibility, and trust signals.",
        "category": "CRO",
        "primary": "homepage UX audit checklist",
        "secondary": "homepage conversion checklist",
        "funnel": "/services/conversion-rate-optimization.html",
        "label": "Conversion Rate Optimization",
        "audience": "business owners and marketing teams who suspect the homepage is leaking qualified visitors",
        "surface": "first screen, navigation, trust strip, service preview, portfolio proof, forms, and mobile layout",
        "intent": "make relevance and next step obvious before the visitor has to work",
        "problem": "homepages often open with brand language that sounds good internally but answers too little for a new visitor",
        "asset": "a structured UX audit, page hierarchy, proof map, CTA review, and mobile scan",
        "proof": "visitor paths, CTA clicks, scroll behavior, form starts, and plain-language first-screen testing",
        "link": "/tools/",
    },
    {
        "slug": "technical-seo-service-business-websites",
        "title": "Technical SEO for Service Business Websites",
        "excerpt": "Technical SEO for service businesses should make every important page crawlable, fast, structured, and connected to commercial intent.",
        "meta": "Technical SEO for service business websites: crawlability, indexation, page speed, schema, internal links, duplicate pages, and lead paths.",
        "category": "SEO",
        "primary": "technical SEO for service business websites",
        "secondary": "service business technical SEO",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "service businesses with useful pages that still struggle to turn search visibility into enquiries",
        "surface": "service pages, location pages, blog posts, case studies, sitemap, schema, and forms",
        "intent": "remove technical ambiguity so search engines can crawl and buyers can move easily",
        "problem": "the site may have good content, but crawl errors, weak links, slow pages, or missing schema reduce its reach",
        "asset": "a technical SEO audit, crawl map, speed review, schema plan, internal link improvements, and indexation checks",
        "proof": "clean sitemap, fewer errors, stronger internal links, passing structured data, and better mobile performance",
        "link": "/services/technical-seo-audit.html",
    },
    {
        "slug": "core-web-vitals-business-websites",
        "title": "Core Web Vitals for Business Websites: A Plain-English Guide",
        "excerpt": "Core Web Vitals matter because slow, unstable pages lose visitors before your offer gets a fair chance.",
        "meta": "Core Web Vitals for business websites: plain-English guide to LCP, INP, CLS, image weight, scripts, mobile speed, and conversion impact.",
        "category": "Speed",
        "primary": "Core Web Vitals for business websites",
        "secondary": "business website speed optimization",
        "funnel": "/services/speed-optimization.html",
        "label": "Speed Optimization",
        "audience": "non-technical founders who need a faster website but do not want a wall of jargon",
        "surface": "mobile pages, hero images, scripts, forms, portfolios, landing pages, and PageSpeed reports",
        "intent": "understand which speed issues actually affect leads and which ones are noise",
        "problem": "reports show scores and acronyms, but the business needs an ordered fix list",
        "asset": "a Core Web Vitals review, image cleanup, script control, layout stability, and mobile testing",
        "proof": "field data, Lighthouse checks, faster first screen, stable layout, and fewer blocked interactions",
        "link": "/services/speed-optimization.html",
    },
    {
        "slug": "schema-markup-ai-search",
        "title": "Schema Markup for AI Search: Entities, Services, FAQs, and Case Studies",
        "excerpt": "Schema does not magically rank a page, but it does help search systems understand what the page is, who it serves, and what it proves.",
        "meta": "Schema markup for AI search: use Organization, LocalBusiness, Service, Article, FAQ, Breadcrumb, and case-study schema to clarify your entity.",
        "category": "SEO",
        "primary": "schema markup for AI search",
        "secondary": "structured data for AI SEO",
        "funnel": "/services/technical-seo-audit.html",
        "label": "Technical SEO Audit",
        "audience": "businesses that want cleaner search context, richer SERP eligibility, and better AI understanding",
        "surface": "service pages, articles, case studies, location pages, FAQs, and organization-level entity signals",
        "intent": "make the relationship between brand, service, proof, and page type machine-readable",
        "problem": "many sites have visible content but no structured context for search systems to connect the dots",
        "asset": "a schema map, JSON-LD implementation, validation, and page-type rules",
        "proof": "valid structured data, consistent entity naming, clear service markup, and linked case studies",
        "link": "/portfolio/",
    },
    {
        "slug": "b2b-saas-homepage-design",
        "title": "B2B SaaS Homepage Design: Explain Product Fit Before the Demo",
        "excerpt": "A B2B SaaS homepage should help the right buyer recognize fit, see proof, and know whether a demo is worth their time.",
        "meta": "B2B SaaS homepage design guide: positioning, product proof, use cases, integrations, screenshots, demo CTAs, and conversion measurement.",
        "category": "SaaS",
        "primary": "B2B SaaS homepage design",
        "secondary": "SaaS homepage conversion",
        "funnel": "/services/webflow-development.html",
        "label": "Webflow Development",
        "audience": "SaaS founders and marketing teams that need the homepage to support demos, trials, and sales conversations",
        "surface": "homepage hero, product sections, use-case blocks, integrations, customer proof, demo paths, and analytics",
        "intent": "help the buyer decide whether the product solves their specific problem before asking for time",
        "problem": "many SaaS homepages describe the company but do not explain the product decision clearly enough",
        "asset": "positioning, product screenshots, proof hierarchy, use-case routing, and measured CTAs",
        "proof": "demo intent, feature engagement, use-case clicks, trial starts, and sales feedback",
        "link": "/services/webflow-development.html",
    },
    {
        "slug": "ecommerce-conversion-audit",
        "title": "Ecommerce Conversion Audit: Find Revenue Leaks Before Buying More Traffic",
        "excerpt": "An ecommerce conversion audit shows where buyers lose trust, get confused, or leave before checkout.",
        "meta": "Ecommerce conversion audit guide: product pages, collection pages, trust signals, site speed, checkout friction, mobile UX, and measurement.",
        "category": "CRO",
        "primary": "ecommerce conversion audit",
        "secondary": "online store conversion audit",
        "funnel": "/services/conversion-rate-optimization.html",
        "label": "Conversion Rate Optimization",
        "audience": "store owners who want more value from existing traffic before increasing acquisition",
        "surface": "homepage, collection pages, product pages, cart, checkout, reviews, speed, and analytics",
        "intent": "find the friction that stops a motivated shopper from becoming a customer",
        "problem": "traffic can look healthy while product discovery, trust, and checkout confidence are quietly leaking sales",
        "asset": "a page-by-page conversion audit with screenshots, severity, fix order, and measurement notes",
        "proof": "product-page clarity, collection filters, mobile performance, cart behavior, and checkout completion",
        "link": "/services/conversion-rate-optimization.html",
    },
]

BATCH_SLUGS = {topic["slug"] for topic in TOPICS}


def h2(title):
    return ("h2", title)


def p(text):
    return ("p", text)


def ul(items):
    return ("ul", items)


def ol(items):
    return ("ol", items)


def callout(text):
    return ("callout", text)


def words_in(parts, hook):
    raw = hook + " " + " ".join(
        item if isinstance(item, str) else " ".join(item)
        for _, item in parts
    )
    raw = re.sub(r"<[^>]+>", " ", raw)
    return len(re.findall(r"[A-Za-z0-9']+", raw))


def make_body(t):
    primary = t["primary"]
    secondary = t["secondary"]
    body = [
        p(f"If you are searching for <strong>{primary}</strong>, the real question is not whether another page should exist. The real question is whether the page gives a buyer, a search engine, and an AI answer system enough evidence to understand the offer and trust the next step."),
        p(f"This guide is written for {t['audience']}. It avoids tricks and thin keyword repetition. The goal is to build a page system that earns visibility because it is useful, specific, and easier to act on than the competing result."),
        h2(f"What people really mean by {primary}"),
        p(f"Searches around <strong>{primary}</strong> usually hide a practical business problem: {t['problem']}. Someone is not looking for theory; they are looking for the shortest reliable path from uncertainty to decision."),
        p(f"That path has to work across {t['surface']}. A human visitor wants clarity and proof. A crawler wants structure. An AI answer system wants extractable statements that can be supported by the page. A strong page serves all three without sounding mechanical."),
        callout(f"Build the page around this job: {t['intent']}. The keyword matters, but the decision behind the keyword matters more."),
        h2("Why this is moving faster in 2026"),
        p("Search behavior has become more answer-led. Buyers still use Google, but they also ask AI tools for shortlists, explanations, comparisons, and next steps. That means a business website has to do two jobs at once: rank for the query and become a trustworthy source that can be summarized accurately."),
        p("The strongest sites now behave more like organized knowledge bases than brochures. They define the service, show who it is for, answer objections, connect to proof, and make the next action obvious. The design can still be beautiful, but the structure underneath has to be precise."),
        p(f"For <strong>{secondary}</strong>, this matters because vague pages create vague answers. If your site says the same broad lines as everyone else, search systems have no reason to treat it as the better source. Specificity becomes the advantage."),
        h2("The search intent map"),
        p("Before writing or redesigning the page, map the search intent. This keeps the page from becoming a pile of keywords and helps every section earn its place."),
        ul([
            f"<strong>Problem-aware searches:</strong> people know something is broken and are trying to name it. These sections should describe the symptoms in plain language.",
            f"<strong>Solution-aware searches:</strong> people know they need {primary} or a close variant. These sections should explain the method and the expected outcome.",
            "<strong>Comparison searches:</strong> people are choosing between providers, tools, or approaches. These sections should show trade-offs without attacking alternatives.",
            "<strong>Action searches:</strong> people are close to enquiring. These sections need proof, next steps, and a low-friction contact path.",
        ]),
        h2("The page structure I would use"),
        p(f"The page should open with a direct statement of the outcome, not a poetic slogan. For this topic, the first screen has to tell the visitor what {primary} means, who it is for, and why the business is credible enough to help."),
        ol([
            "<strong>Hero:</strong> one clear promise, one supporting proof line, one primary CTA, and one secondary path for people who need more context.",
            "<strong>Problem section:</strong> name the friction the buyer already feels, using their language rather than internal terminology.",
            f"<strong>Method section:</strong> explain the working system: {t['asset']}.",
            f"<strong>Proof section:</strong> show {t['proof']}.",
            "<strong>FAQ section:</strong> answer the questions a serious buyer asks before starting a conversation.",
            "<strong>Final CTA:</strong> repeat the next step with less pressure and more context than the hero.",
        ]),
        p("This is also the structure that helps AI systems summarize the page. Direct headings, compact definitions, and evidence close to claims make the content easier to extract without flattening the human experience."),
        h2("Design details that change conversion"),
        p("Good UX here is quiet. It does not need more animation, more blocks, or more decoration. It needs less ambiguity. A visitor should know where they are, what the page is about, whether the offer fits them, and what to do next."),
        ul([
            "<strong>Use descriptive section headings.</strong> Search systems and rushed visitors both rely on headings to understand the page.",
            "<strong>Keep proof near claims.</strong> If you say the work is strategic, show the process. If you say the work improves leads, show the lead path.",
            "<strong>Make mobile the default review.</strong> Most local and service searches involve a phone-sized screen, even when the final decision happens later.",
            "<strong>Do not hide the CTA.</strong> A page can be calm and still make the next step obvious.",
        ]),
        h2("Technical foundations that support rankings"),
        p("Technical SEO is not glamorous, but it decides whether the content has a fair chance. A strong page needs crawlable HTML, fast loading, stable layout, descriptive metadata, clean internal links, and schema that matches the page type."),
        p("For this topic, I would check title tags, meta descriptions, canonical tags, image sizes, heading order, structured data, sitemap inclusion, mobile usability, and whether the page is linked from the right parent pages. If the page is hard to find internally, it is harder to justify externally."),
        p(f"The related internal link should not be random. A page about {primary} should connect to the most relevant service page, supporting blog posts, and proof pages. For this site, a natural commercial path is <a href=\"{t['funnel']}\">{t['label']}</a>, with proof coming from <a href=\"/portfolio/\">case studies</a> and broader service context from <a href=\"{t['link']}\">the related hub</a>."),
        h2("Content depth without keyword stuffing"),
        p("Long content only helps when the extra words remove uncertainty. Do not add paragraphs to satisfy a word count. Add sections because the buyer needs a clearer explanation, a stronger example, a better checklist, or a more honest comparison."),
        p(f"A strong <strong>{primary}</strong> page should use the primary phrase naturally, then cover the topic with related language: the problem, the audience, the workflow, the risks, the proof, the next step, and the measurement plan. That creates semantic coverage without turning the page into spam."),
        ul([
            "Define the term in the first third of the page.",
            "Use short paragraphs that answer one idea at a time.",
            "Add examples that sound like real operational situations.",
            "Include limitations so the page feels trustworthy rather than overpromised.",
            "Link to deeper pages instead of trying to explain everything in one place.",
        ]),
        h2("A practical implementation plan"),
        p("Start by auditing the current page or creating a simple content brief. The brief should list the target query, secondary phrases, audience, intent, proof needed, internal links, schema type, CTA, and measurement events. If any of those fields are blank, the page is not ready to build."),
        ol([
            "<strong>Day one:</strong> collect the real questions buyers ask on calls, in forms, in chat, and in email. Those questions become headings.",
            "<strong>Day two:</strong> map the page structure and decide where proof belongs. Do not leave proof until the bottom.",
            "<strong>Day three:</strong> write the first draft in plain language, then trim anything that sounds like filler.",
            "<strong>Day four:</strong> add internal links, schema, metadata, image alt text, and conversion tracking.",
            "<strong>Day five:</strong> test on mobile, run a crawl, check speed, and ask whether a first-time visitor can explain the offer back in one sentence.",
        ]),
        h2("What to measure after launch"),
        p("Rankings are only one signal. For lead generation, the better question is whether the page attracts the right visitors and moves them to the right action. Measure visibility, engagement, form starts, booked calls, qualified enquiries, and the paths people take before they enquire."),
        ul([
            "Search Console impressions and clicks for the primary and secondary query group.",
            "Engagement on the sections that explain the method and proof.",
            "CTA clicks from hero, mid-page, and final sections separately.",
            "Form completion and reply quality, not just form volume.",
            "AI and referral traffic where analytics can identify it.",
        ]),
        p("Review the page after thirty days, then again after ninety. The first pass catches technical and message issues. The second pass shows whether the page is attracting the right search terms or needs a stronger supporting cluster."),
        h2("Common mistakes"),
        ul([
            "Writing for the keyword but not the buyer decision behind it.",
            "Publishing a page with no proof, examples, or internal links.",
            "Using the same copy structure across many pages with only the label changed.",
            "Treating schema as decoration instead of matching it to visible content.",
            "Adding a form without a follow-up process behind it.",
            "Letting design polish hide unclear positioning.",
        ]),
        h2("FAQ"),
        ("h3", f"How long should a page about {primary} be?"),
        p("Long enough to answer the decision fully. For competitive service topics, that usually means a deep page with clear sections, examples, FAQs, proof, and internal links. The page should feel complete, not padded."),
        ("h3", f"Should I build one page or a cluster for {secondary}?"),
        p("If the topic has several buyer intents, build a cluster. Use one main page for the broad topic, then support it with focused pages for examples, checklists, use cases, locations, and comparisons."),
        ("h3", "Does AI search replace normal SEO?"),
        p("No. AI search extends the work. The same foundations still matter: crawlable pages, helpful content, credible proof, fast performance, and clean internal links. The difference is that pages also need to be easier to summarize and cite."),
        ("h3", "What should I fix first?"),
        p("Fix clarity first. If the first screen does not explain who the page is for, what problem it solves, and what to do next, technical tweaks will not save the page. After clarity, fix proof, speed, schema, and follow-up."),
    ]

    supplemental_checks = [
        (
            "Validate the buyer path before publishing",
            f"Read the page as a buyer comparing three options. Confirm that the approach to {primary}, the evidence behind it, and the next step are all obvious without decoding agency language.",
            "Follow every CTA from mobile and desktop. The destination should continue the same promise, preserve context, and ask only for information the team will actually use.",
        ),
        (
            "Check the page as a search system",
            "Make the topic, entity, service, audience, and next step explicit in the HTML. Use descriptive headings, useful internal links, accurate metadata, and schema that matches visible content.",
            "Inspect the rendered page as well as the source. Important answers cannot depend on an animation, tab, or script that prevents crawlers and assistive technology from reaching them.",
        ),
        (
            "Pressure-test the proof",
            "Replace generic claims with bounded examples, screenshots, methodology, or a clear explanation of how the work is done. Remove any statement the business could not defend in a sales call.",
            "Proof should sit beside the decision it supports. Do not hide all credibility in a testimonial strip at the end while the service sections ask readers to trust unsupported promises.",
        ),
        (
            "Run the final mobile and conversion review",
            "Test the first screen, navigation, forms, links, tap targets, typography, and performance on a real narrow viewport. A page that works only on a large monitor is not ready to attract leads.",
            "Finally, confirm that analytics can distinguish page views, meaningful CTA clicks, form starts, successful submissions, and qualified follow-up without collecting more data than the visitor agreed to share.",
        ),
    ]
    for heading, first_paragraph, second_paragraph in supplemental_checks:
        if words_in(body, "") >= 2050:
            break
        body.extend([
            h2(heading),
            p(first_paragraph),
            p(second_paragraph),
        ])
    return body


def make_post(t):
    hook = (
        f"{t['primary']} is not a trick phrase to sprinkle into a page. It is a signal that buyers are changing how they discover, compare, and choose providers. The businesses that win will be the ones whose websites are easier to understand, easier to trust, and easier to act on."
    )
    body = make_body(t)
    count = words_in(body, hook)
    minutes = max(10, round(count / 210))
    return {
        "slug": t["slug"],
        "title": t["title"],
        "excerpt": t["excerpt"],
        "meta": t["meta"],
        "category": t["category"],
        "date": "2026-06-21",
        "readingTime": f"{minutes} min",
        "primaryKeyword": t["primary"],
        "secondaryKeyword": t["secondary"],
        "funnelTo": t["funnel"],
        "funnelLabel": t["label"],
        "featured": False,
        "hook": hook,
        "body": body,
        "wordCount": count,
    }


def update_posts_json(posts):
    data = json.loads(POSTS_JSON.read_text())
    existing = {p["slug"]: p for p in data.get("posts", [])}
    new_entries = []
    for post in posts:
        new_entries.append({
            "slug": post["slug"],
            "title": post["title"],
            "excerpt": post["excerpt"],
            "category": post["category"],
            "date": post["date"],
            "readingTime": post["readingTime"],
            "primaryKeyword": post["primaryKeyword"],
            "secondaryKeyword": post["secondaryKeyword"],
            "funnelTo": post["funnelTo"],
            "featured": post.get("featured", False),
            "published": True,
        })
    new_slugs = {p["slug"] for p in new_entries}
    merged = new_entries + [p for slug, p in existing.items() if slug not in BATCH_SLUGS]
    merged.sort(key=lambda p: p["date"], reverse=True)
    data["lastUpdated"] = "2026-06-21"
    for category in ["Websites", "SaaS", "AI & Automation", "SEO", "CRO", "Speed"]:
        if category not in data["categories"]:
            data["categories"].append(category)
    data["posts"] = merged
    POSTS_JSON.write_text(json.dumps(data, indent=2) + "\n")


def main():
    posts = [make_post(t) for t in TOPICS]
    too_short = [p for p in posts if p["wordCount"] < 2000]
    if too_short:
        raise SystemExit(f"Posts under 2000 words: {', '.join(p['slug'] for p in too_short)}")

    nav, footer = seo_engine.load_nav_and_footer()
    stale_slugs = BATCH_SLUGS - {post["slug"] for post in posts}
    for slug in stale_slugs:
        for path in (BLOG_DIR / f"{slug}.html", ROOT / "assets" / "blog" / f"{slug}.png"):
            if path.exists():
                path.unlink()
                print(f"  - removed stale {path.relative_to(ROOT)}")

    for post in posts:
        (BLOG_DIR / f"{post['slug']}.html").write_text(seo_engine.render_blog_post(post, nav, footer))
        print(f"  + blog/{post['slug']}.html ({post['wordCount']} words)")

    update_posts_json(posts)
    seo_engine.refresh_blog_index()
    seo_engine.gen_covers()
    seo_engine.gen_sitemap()
    print(f"Published {len(posts)} posts.")


if __name__ == "__main__":
    main()
