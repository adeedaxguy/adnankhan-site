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
CACHE_VER = "20260622j"
BRAND_NAME = "Lofts Studio"
BRAND_TAGLINE = "Senior web engineering for founders."
FOUNDERS = "Adnan & Irfan Khan"

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

POSTS = [
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
        "secondaryKeyword": "shopify developer rates 2026",
        "funnelTo": "/services/shopify-development.html",
        "funnelLabel": "Shopify Development",
        "featured": True,
        "hook": "If you're about to hire a Shopify developer for the first time, you are about to make the most expensive decision of the year — and you almost certainly don't have the vocabulary yet to make it well.",
        "body": [
            ("p", "I've spent almost 15 years inside this market — first as the developer being hired, then as the one cleaning up after the wrong ones. I've watched founders choose the cheapest path and rebuild months later, and I've watched careful scopes keep stores healthy for years. The headline number has almost nothing to do with which outcome they got."),
            ("p", "This post is the screening playbook I wish every client had used before they reached me. It will not flatter the industry. It will save you a six-figure mistake."),
            ("h2", "What Shopify developer rates actually signal in 2026"),
            ("p", "If you are comparing rates, start with the work type. I wrote a dedicated guide to <a href='/blog/shopify-developer-freelance-rates.html'>Shopify developer freelance rates</a>, but the short version is this: the quote only makes sense once you know what responsibility the developer is carrying."),
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
        "title": "Shopify Plus vs Shopify Advanced: When the Plus Jump Actually Makes Sense",
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
        "title": "Custom Shopify App vs Private App vs Public App: Which One You Actually Need",
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
        "title": "Why Your WooCommerce Store Is Slow — and the 5 Plugins Causing 80% of It",
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

# Service templates per location — currently we generate one master page per location
# that lists Shopify + WooCommerce + WordPress capability for that market.


def render_blog_post(p, nav, footer):
    """Render a single blog post HTML from a spec dict."""
    date_obj = datetime.strptime(p["date"], "%Y-%m-%d")
    date_readable = date_obj.strftime("%B %d, %Y")

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
    body_html = "\n\n    ".join(body_parts)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<title>{p["title"]} | Adnan K.</title>
<meta name="description" content="{p["meta"]}" />
<link rel="canonical" href="{SITE}/blog/{p["slug"]}.html" />
<meta name="robots" content="index,follow,max-image-preview:large" />
<meta name="author" content="Adnan K." />
<meta name="keywords" content="{p["primaryKeyword"]}, {p["secondaryKeyword"]}, shopify developer, woocommerce developer, hire shopify developer" />

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
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{p["title"]}",
  "description": "{p["meta"]}",
  "image": "{SITE}/assets/blog/{p["slug"]}.png?v={CACHE_VER}",
  "datePublished": "{p["date"]}T09:00:00Z",
  "dateModified": "{p["date"]}T09:00:00Z",
  "author": {{ "@type": "Person", "name": "Adnan K.", "url": "{SITE}/about.html" }},
  "publisher": {{ "@type": "Organization", "name": "Lofts Studio", "logo": {{ "@type": "ImageObject", "url": "{SITE}/favicon.svg" }} }},
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{SITE}/blog/{p["slug"]}.html" }},
  "keywords": "{p["primaryKeyword"]}, {p["secondaryKeyword"]}"
}}
</script>
<script type="application/ld+json">
{{ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [ {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}}, {{"@type":"ListItem","position":2,"name":"Blog","item":"{SITE}/blog/"}}, {{"@type":"ListItem","position":3,"name":"{p["title"]}","item":"{SITE}/blog/{p["slug"]}.html"}} ] }}
</script>

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
  .post-prose a.btn {{ color: var(--bg); border-bottom: 0; }}
  .post-prose a.btn:hover {{ color: var(--bg); border-bottom: 0; }}
  .post-prose code {{ font-family: var(--font-mono); font-size: 0.88em; background: var(--bg-soft); padding: 2px 6px; border-radius: 4px; color: var(--ink); }}
  .post-prose pre {{ background: var(--ink); color: #E8E8E8; padding: 1.25rem 1.5rem; border-radius: var(--r-md); overflow-x: auto; margin: 1.5rem 0; font-family: var(--font-mono); font-size: 0.86rem; line-height: 1.7; }}
  .post-prose pre code {{ background: transparent; padding: 0; color: inherit; font-size: inherit; }}
  .post-prose hr {{ border: 0; border-top: 1px solid var(--line); margin: 3rem 0; }}
  .post-callout {{ background: var(--accent-soft); border-left: 3px solid var(--accent); padding: 1.25rem 1.5rem; margin: 2rem 0; border-radius: 0 var(--r-md) var(--r-md) 0; }}
  .post-callout p {{ margin: 0; color: var(--ink); font-size: 1rem; }}
</style>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1KT1MFDY8R"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-1KT1MFDY8R');</script>
  <script>(function(){{try{{var m=localStorage.getItem('lofts-theme');document.documentElement.setAttribute('data-theme',m==='dark'?'dark':'light');}}catch(e){{}}}})();</script>
</head>
<body>

{nav}

<article>
<section class="paper" style="padding: 5rem 0 3rem;">
  <div class="container post-prose" data-reveal>
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);">
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <a href="/blog/" style="color: var(--muted);">Blog</a> <span style="margin: 0 8px;">/</span>
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
          <a href="/portfolio/" style="color: var(--accent);">Portfolio</a>
          <a href="/blog/" style="color: var(--accent);">More posts</a>
        </div>
      </div>
    </div>
  </div>
</section>
</article>

<section class="comments" aria-labelledby="comments-title">
  <div class="container container-narrow">
    <div id="comments" data-slug="{p['slug']}">
      <div class="comments-head">
        <h2 id="comments-title">Comments <span class="comments-count" data-count></span></h2>
        <p class="comments-sub">Have a question, or a better way to do this? Add it below — real replies, no sign-up.</p>
      </div>
      <ol class="comments-list" data-list></ol>
      <p class="comments-empty" data-empty hidden>Be the first to comment.</p>
      <form class="comment-form" data-form novalidate>
        <div class="cf-row">
          <input class="cf-input" type="text" name="name" maxlength="60" placeholder="Your name" required aria-label="Your name" autocomplete="name" />
          <input class="cf-input" type="email" name="email" maxlength="120" placeholder="Email (optional, never shown)" aria-label="Email (optional)" autocomplete="email" />
        </div>
        <textarea class="cf-input cf-text" name="body" maxlength="3000" rows="4" placeholder="Add to the conversation…" required aria-label="Your comment"></textarea>
        <div class="cf-hp"><label>Leave this field empty<input type="text" name="hp_url" tabindex="-1" autocomplete="off" /></label></div>
        <div class="cf-foot">
          <span class="cf-note" data-status>Be kind and constructive. Links are limited to keep spam out.</span>
          <button class="btn btn-primary cf-submit" type="submit">Post comment</button>
        </div>
      </form>
    </div>
  </div>
</section>
<script src="/assets/comments.js?v={CACHE_VER}" defer></script>

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
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,400..600;1,400..500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..600;1,8..60,400..500&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/assets/styles.css?v={CACHE_VER}" />

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
      "acceptedAnswer": {{ "@type": "Answer", "text": "A serious Shopify scope depends on theme condition, integrations, content, analytics, migration risk, and launch timing. I do not publish a fixed public rate card; the right next step is a short audit and written scope." }}
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
</head>
<body>

{nav}

<section class="paper" style="padding: 7rem 0 4rem;">
  <div class="container">
    <nav aria-label="Breadcrumb" style="margin-bottom: 1.5rem; font-size: 0.82rem; color: var(--muted);">
      <a href="/" style="color: var(--muted);">Home</a> <span style="margin: 0 8px;">/</span>
      <a href="/services/" style="color: var(--muted);">Services</a> <span style="margin: 0 8px;">/</span>
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
        <a href="/portfolio/" class="btn btn-ghost">See 47 case studies</a>
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
        <p style="font-family: var(--font-serif); color: var(--ink-soft); margin: 0;">A serious Shopify scope depends on theme condition, integrations, content, analytics, migration risk, and launch timing. I do not publish a fixed public rate card; the right next step is a short audit and written scope.</p>
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
        if slug not in new_slugs:
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

    # Static top-level pages with priorities
    top = {
        "/": ("1.0", "weekly"),
        "/about.html": ("0.9", "monthly"),
        "/portfolio/": ("0.95", "weekly"),
        "/blog/": ("0.9", "weekly"),
        "/process/": ("0.7", "monthly"),
        "/notes/": ("0.7", "weekly"),
        "/tools/": ("0.7", "monthly"),
        "/now/": ("0.6", "weekly"),
        "/privacy.html": ("0.3", "yearly"),
        "/terms.html": ("0.3", "yearly"),
        "/cookie-policy.html": ("0.3", "yearly"),
    }
    for path, (priority, freq) in top.items():
        urls.append((f"{SITE}{path}", today, freq, priority))

    # All services
    for svc in sorted(SERVICES_DIR.glob("*.html")):
        urls.append((f"{SITE}/services/{svc.name}", today, "monthly", "0.85"))

    # Vertical pillar pages — high priority commercial pages
    work_dir = ROOT / "work"
    if work_dir.exists():
        for pillar in sorted(work_dir.iterdir()):
            if pillar.is_dir() and (pillar / "index.html").exists():
                urls.append((f"{SITE}/work/{pillar.name}/", today, "weekly", "0.95"))

    # Brand guide (noindex but included for completeness)
    if (ROOT / "brand.html").exists():
        pass  # Skipped — has noindex meta

    # All portfolio
    for pf in sorted(ROOT.glob("portfolio/*.html")):
        urls.append((f"{SITE}/portfolio/{pf.name}", today, "monthly", "0.75"))

    # All blog posts
    for post in sorted(BLOG_DIR.glob("*.html")):
        if post.name.startswith("_"):
            continue
        urls.append((f"{SITE}/blog/{post.name}", today, "monthly", "0.8"))

    # Notes, tools, process
    for d in ["notes", "tools", "process"]:
        sub = ROOT / d
        if sub.exists():
            for f in sorted(sub.glob("*.html")):
                if not f.name.startswith("_"):
                    urls.append((f"{SITE}/{d}/{f.name}", today, "monthly", "0.65"))

    # Build XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u, lastmod, freq, prio in urls:
        # Add hreflang for location pages
        if "shopify-developer-" in u and u.endswith(".html"):
            xml.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{lastmod}</lastmod>")
            for loc in LOCATIONS:
                xml.append(f'    <xhtml:link rel="alternate" hreflang="en-{loc["code"]}" href="{SITE}/services/shopify-developer-{loc["code"]}.html"/>')
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
