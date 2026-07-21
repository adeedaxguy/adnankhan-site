#!/usr/bin/env python3
"""
Publish the 2026-07-22 Lofts Studio audit-report SEO batch.

Research basis:
- GSC: real impressions for website structure audit report, site audit report,
  website audit report, SEO compatibility, and PDF/report variants.
- Ahrefs/RankyTools: reviewed with account session available; workspace showed
  intermittent inactive-banner limits, so public Google SERPs were used to
  validate page types and competitor patterns.
- Google SERPs: report templates, sample PDFs, free generators, compatibility
  checkers, and technical SEO audit service checklists dominate the cluster.
"""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog"

spec = importlib.util.spec_from_file_location("seo_engine", ROOT / "scripts" / "seo_engine.py")
seo_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo_engine)


TOPICS = [
    {
        "slug": "website-structure-audit-report-template",
        "title": "Website Structure Audit Report Template for Service Sites",
        "primary": "website structure audit report template",
        "secondary": "website audit report template",
        "excerpt": "A practical website structure audit report template for reviewing hierarchy, crawl paths, internal links, trust, UX, and lead paths before a redesign.",
        "meta": "Website structure audit report template for service sites: hierarchy, crawl paths, internal links, content gaps, UX, schema, and prioritized fixes.",
        "artifact": "template",
        "intent": "buyers who want a repeatable audit format before they rebuild pages or ask for a technical SEO quote",
        "competitors": "template and checklist pages from SEO tools, agency blogs, and audit PDF providers",
    },
    {
        "slug": "website-structure-audit-report-sample",
        "title": "Website Structure Audit Report Sample: What Good Looks Like",
        "primary": "website structure audit report sample",
        "secondary": "website audit report sample",
        "excerpt": "See what a useful structure audit report should include, how to prioritize findings, and how to turn the sample into action.",
        "meta": "Website structure audit report sample guide: sections, scoring, evidence, screenshots, internal links, conversion findings, and fix priorities.",
        "artifact": "sample",
        "intent": "founders comparing whether an audit deliverable is detailed enough to trust",
        "competitors": "PDF samples, agency report previews, and tool-generated audit examples",
    },
    {
        "slug": "website-structure-audit-report-pdf",
        "title": "Website Structure Audit Report PDF: Sections to Include",
        "primary": "website structure audit report PDF",
        "secondary": "website audit PDF",
        "excerpt": "A PDF-focused guide for building a website structure audit report that is readable, prioritized, and useful for non-technical owners.",
        "meta": "Website structure audit report PDF guide: what to include, how to order findings, and how to make the report useful after export.",
        "artifact": "PDF report",
        "intent": "teams who need a client-ready PDF after running site, SEO, and conversion checks",
        "competitors": "downloadable PDF audits, free report generators, and tool screenshots",
    },
    {
        "slug": "website-structure-audit-report-example",
        "title": "Website Structure Audit Report Example for Lead Websites",
        "primary": "website structure audit report example",
        "secondary": "website audit report example",
        "excerpt": "A plain-English example of how to structure a website audit around crawlability, page hierarchy, content depth, and conversion paths.",
        "meta": "Website structure audit report example for lead-generation websites, covering crawl checks, hierarchy, internal links, trust, UX, and fix order.",
        "artifact": "example",
        "intent": "service businesses deciding whether their site needs a cleanup, a content rebuild, or a full redesign",
        "competitors": "sample audit reports, SEO agency examples, and generic website grader pages",
    },
    {
        "slug": "website-structure-audit-report-template-excel",
        "title": "Website Structure Audit Report Template in Excel or Sheets",
        "primary": "website structure audit report template Excel",
        "secondary": "website audit report template spreadsheet",
        "excerpt": "How to build a spreadsheet-based website structure audit report that helps teams sort issues by URL, impact, owner, and next fix.",
        "meta": "Website structure audit report template for Excel or Google Sheets: columns, scoring, URL mapping, issue priority, owners, and next actions.",
        "artifact": "spreadsheet template",
        "intent": "operators who want a spreadsheet audit before turning findings into a PDF or implementation sprint",
        "competitors": "Excel checklist downloads, SEO audit spreadsheets, and agency reporting templates",
    },
    {
        "slug": "website-audit-report-sample-pdf",
        "title": "Website Audit Report Sample PDF: What to Review Before Sending",
        "primary": "website audit report sample PDF",
        "secondary": "website audit report sample",
        "excerpt": "Use this sample PDF checklist to decide whether a website audit report is clear enough, specific enough, and ready to act on.",
        "meta": "Website audit report sample PDF guide: sections, evidence, screenshots, priority scoring, executive summary, and next-step recommendations.",
        "artifact": "sample PDF",
        "intent": "consultants and business owners reviewing whether an audit PDF is complete before sharing it",
        "competitors": "free website audit PDF examples and automated report downloads",
    },
    {
        "slug": "site-audit-report-pdf",
        "title": "Site Audit Report PDF: Build One That Leads to Action",
        "primary": "site audit report PDF",
        "secondary": "SEO audit report PDF",
        "excerpt": "A guide to building a site audit report PDF that explains issues, impact, and fix order instead of dumping generic tool warnings.",
        "meta": "Site audit report PDF guide for service websites: technical findings, SEO/AEO checks, UX friction, conversion paths, and prioritized fixes.",
        "artifact": "site audit PDF",
        "intent": "buyers searching for an audit report they can download, share, and use to brief implementation work",
        "competitors": "SEOptimer, Semrush, Site Audit Pro, and PDF report generators",
    },
    {
        "slug": "site-audit-report-sample",
        "title": "Site Audit Report Sample for Small Business Websites",
        "primary": "site audit report sample",
        "secondary": "free site audit report",
        "excerpt": "A useful site audit report sample for small businesses that need plain priorities across technical SEO, structure, UX, and conversion.",
        "meta": "Site audit report sample for small business websites: crawl checks, page structure, SEO, content gaps, trust signals, and fix priorities.",
        "artifact": "sample report",
        "intent": "small businesses deciding what a practical website audit should actually show",
        "competitors": "free site audit tools, SEO checkers, and agency sample reports",
    },
    {
        "slug": "free-site-audit-report",
        "title": "Free Site Audit Report: What You Should Expect",
        "primary": "free site audit report",
        "secondary": "website audit report for free",
        "excerpt": "What a free site audit report can check, what it cannot prove by itself, and how to turn quick findings into a useful fix plan.",
        "meta": "Free site audit report guide: what automated checks can reveal, what needs human review, and how to prioritize fixes after the report.",
        "artifact": "free report",
        "intent": "visitors who want a low-friction audit before booking a deeper review",
        "competitors": "free website grader pages, automated scanners, and lightweight SEO reports",
    },
    {
        "slug": "free-seo-audit-report-pdf",
        "title": "Free SEO Audit Report PDF: Checks Worth Including",
        "primary": "free SEO audit report PDF",
        "secondary": "SEO audit PDF",
        "excerpt": "A practical guide to what a free SEO audit report PDF should include so the findings are useful, not just a branded export.",
        "meta": "Free SEO audit report PDF guide: titles, indexability, internal links, schema, page speed, content gaps, and prioritized SEO fixes.",
        "artifact": "SEO audit PDF",
        "intent": "searchers comparing free SEO report tools and wanting a readable deliverable",
        "competitors": "SEO checker PDFs, Semrush-style audit exports, and agency lead magnets",
    },
    {
        "slug": "website-audit-report-generator-free",
        "title": "Website Audit Report Generator Free: How to Judge the Output",
        "primary": "website audit report generator free",
        "secondary": "free website audit report generator",
        "excerpt": "A buyer-focused checklist for deciding whether a free website audit report generator gives you enough evidence to fix the site.",
        "meta": "Website audit report generator free guide: how to judge automated output, missing context, false positives, and next fixes.",
        "artifact": "free generator",
        "intent": "users trying automated report generators before choosing a technical SEO or redesign partner",
        "competitors": "free audit tools, online graders, and automated SEO report builders",
    },
    {
        "slug": "website-audit-checklist",
        "title": "Website Audit Checklist for Lead-Generation Sites",
        "primary": "website audit checklist",
        "secondary": "site audit checklist",
        "excerpt": "A practical website audit checklist for service businesses that need more leads, clearer pages, and fewer technical surprises.",
        "meta": "Website audit checklist for lead-generation sites: technical SEO, structure, content, UX, trust, analytics, schema, and conversion.",
        "artifact": "checklist",
        "intent": "teams who want a complete audit checklist before redesigning or commissioning SEO work",
        "competitors": "website audit checklists, SEO audit templates, and free grader pages",
    },
    {
        "slug": "seo-compatibility-checker-online",
        "title": "SEO Compatibility Checker Online: What to Test Before Launch",
        "primary": "SEO compatibility checker online",
        "secondary": "SEO compatibility checker",
        "excerpt": "Use this online SEO compatibility checklist to test whether a page is crawlable, understandable, useful, and ready for search.",
        "meta": "SEO compatibility checker online guide: crawlability, indexability, title tags, headings, schema, internal links, speed, and conversion checks.",
        "artifact": "online checker",
        "intent": "site owners validating important pages before publishing, redesigning, or asking for indexing",
        "competitors": "Seobility, HubSpot Website Grader, SEO checkers, and Google SEO tools",
    },
    {
        "slug": "seo-compatibility-checker-online-free",
        "title": "SEO Compatibility Checker Online Free: Practical Workflow",
        "primary": "SEO compatibility checker online free",
        "secondary": "free SEO compatibility checker",
        "excerpt": "A practical workflow for using a free online SEO compatibility checker without mistaking tool output for a full SEO strategy.",
        "meta": "Free online SEO compatibility checker workflow for crawlability, metadata, schema, content depth, internal links, and next-step SEO fixes.",
        "artifact": "free checker",
        "intent": "visitors who want a quick scan but need help interpreting which findings matter",
        "competitors": "free SEO checkers, website graders, and one-click audit tools",
    },
    {
        "slug": "seo-compatibility-checker-free",
        "title": "SEO Compatibility Checker Free: The Checks That Matter",
        "primary": "SEO compatibility checker free",
        "secondary": "free SEO checker",
        "excerpt": "What a free SEO compatibility checker should actually review before you trust a page to compete in Google and AI answers.",
        "meta": "Free SEO compatibility checker guide: indexability, titles, headings, schema, answer clarity, internal links, and conversion readiness.",
        "artifact": "free compatibility check",
        "intent": "small businesses validating pages without paying for a full crawler subscription",
        "competitors": "Seobility, HubSpot, Google SEO Checker pages, and browser-based graders",
    },
    {
        "slug": "google-seo-checker-free",
        "title": "Google SEO Checker Free: What It Can and Cannot Tell You",
        "primary": "Google SEO checker free",
        "secondary": "free Google SEO checker",
        "excerpt": "A realistic guide to using free Google SEO checker tools, Search Console data, and manual review together before making changes.",
        "meta": "Google SEO checker free guide: combine Search Console, page checks, schema validation, speed data, and manual review into a fix plan.",
        "artifact": "Google SEO check",
        "intent": "searchers looking for a free Google-oriented checker they can trust before hiring help",
        "competitors": "Google SEO checker pages, Search Console explainers, and SEO grader tools",
    },
    {
        "slug": "website-technical-seo-checker",
        "title": "Website Technical SEO Checker: What to Scan First",
        "primary": "website technical SEO checker",
        "secondary": "technical SEO checker",
        "excerpt": "A first-pass technical SEO checker workflow for finding crawl, index, canonical, speed, schema, and internal-link issues.",
        "meta": "Website technical SEO checker workflow: robots, indexability, canonicals, redirects, schema, Core Web Vitals, internal links, and fix order.",
        "artifact": "technical SEO scan",
        "intent": "teams checking technical issues before writing more content or starting a redesign",
        "competitors": "technical SEO checker tools, audit platforms, and agency service pages",
    },
    {
        "slug": "technical-seo-improvements",
        "title": "Technical SEO Improvements That Usually Move the Needle",
        "primary": "technical SEO improvements",
        "secondary": "technical SEO fixes",
        "excerpt": "A prioritized list of technical SEO improvements that help search engines crawl, understand, and trust a business website.",
        "meta": "Technical SEO improvements for business websites: crawlability, indexation, internal links, schema, speed, redirects, and content architecture.",
        "artifact": "fix list",
        "intent": "businesses that already have an audit report and need to decide what to implement first",
        "competitors": "technical SEO beginner guides, service pages, and improvement checklists",
    },
    {
        "slug": "technical-seo-for-beginners",
        "title": "Technical SEO for Beginners: A Plain-English Site Audit",
        "primary": "technical SEO for beginners",
        "secondary": "technical SEO audit for beginners",
        "excerpt": "A beginner-friendly explanation of technical SEO using the checks that actually affect crawling, indexing, page experience, and trust.",
        "meta": "Technical SEO for beginners: simple explanations of crawlability, indexability, canonicals, redirects, schema, speed, and internal links.",
        "artifact": "beginner guide",
        "intent": "owners who need to understand the audit before deciding whether to hire implementation help",
        "competitors": "beginner SEO guides, tool glossaries, and technical SEO tutorials",
    },
    {
        "slug": "technical-seo-audit-services-checklist",
        "title": "Technical SEO Audit Services Checklist Before You Hire",
        "primary": "technical SEO audit services checklist",
        "secondary": "technical SEO audit services",
        "excerpt": "Use this checklist to compare technical SEO audit services by evidence, implementation plan, reporting quality, and business impact.",
        "meta": "Technical SEO audit services checklist: what to ask before hiring, what the audit should include, and how to judge the fix plan.",
        "artifact": "hiring checklist",
        "intent": "buyers comparing technical SEO audit providers and wanting to avoid generic report-only deliverables",
        "competitors": "agency service pages from 1Digital, Logical Position, PageSpeed, Polaris, and SEO consultants",
    },
]


def sentence_case(keyword):
    text = keyword.replace("SEO", "seo").replace("PDF", "pdf")
    return text[:1].upper() + text[1:]


def intent_card(topic):
    form_id = topic["slug"][:32]
    return f"""<aside class="post-intent-card" aria-labelledby="{form_id}-audit">
      <h2 id="{form_id}-audit">Want the {topic['artifact']} applied to your site?</h2>
      <form class="post-audit-launcher" action="/free-audit/" method="get">
        <label for="{form_id}-url">Website URL to audit</label>
        <div class="post-audit-row">
          <input id="{form_id}-url" name="url" type="url" inputmode="url" placeholder="https://example.com" autocomplete="url" required />
          <button class="btn btn-primary" type="submit">Start audit <span aria-hidden="true">&rarr;</span></button>
        </div>
      </form>
      <p>Run the free Lofts Studio audit, then use this guide to decide which findings need a real implementation sprint.</p>
      <div class="post-intent-actions">
        <a href="/free-audit/" class="btn btn-primary">Open free audit</a>
        <a href="/services/technical-seo-audit.html" class="btn btn-ghost">Technical SEO service</a>
      </div>
      <div class="post-intent-note" aria-label="Audit report includes">
        <span>Search checks</span>
        <span>UX review</span>
        <span>Fix order</span>
      </div>
    </aside>"""


def comparison_table(topic):
    return f"""<div class="post-table-wrap"><table>
      <thead><tr><th>Section</th><th>What to check</th><th>Why it matters</th></tr></thead>
      <tbody>
        <tr><td><strong>Access</strong></td><td>Status code, HTTPS, robots, noindex, canonical, sitemap inclusion.</td><td>The page cannot earn visibility if Google cannot crawl and index it cleanly.</td></tr>
        <tr><td><strong>Structure</strong></td><td>Navigation, page hierarchy, breadcrumbs, internal links, and crawl depth.</td><td>A clean structure helps users, Google, and AI systems understand the role of each page.</td></tr>
        <tr><td><strong>Content</strong></td><td>Search intent, headings, short answers, FAQs, examples, and missing proof.</td><td>{sentence_case(topic['primary'])} needs useful detail, not only a title that matches the query.</td></tr>
        <tr><td><strong>Experience</strong></td><td>Mobile first screen, CTA visibility, form friction, page speed, and trust signals.</td><td>The report should connect SEO findings to the visitor journey and lead quality.</td></tr>
        <tr><td><strong>Priority</strong></td><td>Impact, effort, owner, evidence, and next action for each issue.</td><td>Prioritization turns a report into a plan instead of a long list of warnings.</td></tr>
      </tbody>
    </table></div>"""


def body_for(topic):
    primary = topic["primary"]
    artifact = topic["artifact"]
    return [
        ("p", f"Search Console is already testing Lofts Studio around audit-report and compatibility terms, which means the opportunity is not abstract. People are looking for a usable {artifact}: something that explains what is wrong, why it matters, and what to fix first. The page you are reading is built around that exact need."),
        ("p", f"The SERP pattern for <strong>{primary}</strong> is crowded with automated scanners, generic checklist posts, PDF samples, and large SEO platforms. Those can be useful, but they often stop at surface warnings. A better audit connects technical health, page structure, content intent, AI-search readability, and the path from visitor to lead."),
        ("callout", f"The goal of a {artifact} is not to prove the site has problems. Every site has problems. The goal is to separate small warnings from the few issues that are actually blocking search visibility, buyer trust, or enquiries."),
        ("h2", f"Short answer: what should a {artifact} include?"),
        ("p", f"A strong {artifact} should include crawl and index checks, page hierarchy, internal links, search intent, visible proof, schema, mobile UX, speed signals, conversion paths, and a prioritized fix order. It should show the URL affected, the evidence for the issue, the business impact, and the recommended next step."),
        ("p", f"For {topic['intent']}, that means the report should be readable by a non-technical decision maker and specific enough for a developer, SEO, or content lead to implement. Vague labels like <em>poor SEO</em> or <em>needs improvement</em> are not enough."),
        ("h2", "Use this audit structure"),
        ("html", comparison_table(topic)),
        ("h2", "Start with indexability and canonical clarity"),
        ("p", "The first section should confirm whether the important pages can be crawled and indexed. Check the HTTP status, HTTPS, robots rules, noindex tags, canonical URL, redirects, and sitemap inclusion. If this layer is wrong, content and design improvements sit on unstable ground."),
        ("p", "This is also the layer where automated tools help most. They are good at spotting a blocked page, redirect chain, missing title, duplicate canonical, or broken internal link. The judgment comes after the scan, when you decide whether the issue affects a revenue page, a support article, a tool page, or a page that should not be indexed anyway."),
        ("h2", "Map structure before judging content"),
        ("p", "A website can have good individual pages and still be hard to understand. Map the homepage, service pages, blog guides, tools, case studies, location pages, and contact routes. Then ask whether the structure tells a clear story about what the business does, who it helps, and what the visitor should do next."),
        ("ul", [
            "Important service pages should be linked from navigation, footer, and related articles.",
            "Educational posts should link to the commercial page they support.",
            "Audit and checker pages should link into the free audit flow and technical SEO service page.",
            "Similar posts should link to the main guide instead of competing silently.",
            "Pages with impressions and low CTR should have stronger titles, meta descriptions, and opening answers.",
        ]),
        ("h2", "Judge content by search intent, not word count"),
        ("p", f"A page targeting <strong>{primary}</strong> should answer the format-specific question first. If the visitor wants a template, show the template sections. If the visitor wants a PDF, explain what should survive export. If the visitor wants a checker, explain what the checker can and cannot verify."),
        ("p", "This is where many audit pages become thin even when they are long. They mention every possible SEO concept but do not help the reader make a decision. The better structure is answer, criteria, evidence, examples, fix order, and next step."),
        ("h2", "Add AI-search and AEO checks"),
        ("p", "Traditional SEO checks are not enough for modern search. The report should also ask whether the page can be summarized by answer engines without losing the point. Use direct headings, short answer blocks, visible FAQs, accurate schema, author signals, and enough original detail to make the page worth citing."),
        ("p", "The <a href='/tools/seo-aeo-checker.html'>SEO/AEO compatibility checker</a> is useful here because it reviews whether a page is readable, structured, and trustable. Pair that with Search Console data so you know which query families Google is already testing."),
        ("h2", "Prioritize by business impact"),
        ("p", "Not every issue deserves the same urgency. A missing alt attribute on a decorative image should not outrank a blocked service page, a broken form, a noindex tag on a commercial URL, or a weak first screen on a high-intent page."),
        ("ol", [
            "Fix pages that cannot be crawled, indexed, loaded, or used.",
            "Fix commercial pages with vague positioning, weak proof, or hidden CTAs.",
            "Fix internal links between audit guides, tool pages, service pages, and contact paths.",
            "Fix content gaps where Search Console shows impressions but visitors are not clicking.",
            "Fix schema only after the visible content and page role are accurate.",
        ]),
        ("h2", "How Lofts Studio uses this workflow"),
        ("p", "For Lofts Studio, this cluster supports the free audit tool, the SEO/AEO checker, and technical SEO audit services. The intent is practical: help a visitor understand what a useful report looks like, then give them a low-friction path to test their own site."),
        ("p", "The next step is simple. Run the <a href='/free-audit/'>free website audit report</a> for a real URL. Then compare the output against this guide. If the issue list is mostly warnings, keep the fixes small. If the same pages show crawl, structure, content, and conversion problems together, that is a stronger signal for a focused technical SEO or redesign sprint."),
    ]


def faqs_for(topic):
    primary = topic["primary"]
    artifact = topic["artifact"]
    return [
        {
            "question": f"What is a {primary}?",
            "answer": f"A {primary} is a practical audit resource that helps review whether a website is crawlable, structured clearly, useful to searchers, and ready to convert visitors. The best version includes evidence, affected URLs, priority, and next actions.",
        },
        {
            "question": f"What should a {artifact} include?",
            "answer": "It should include crawl and index checks, page hierarchy, internal links, headings, content gaps, schema, mobile UX, speed signals, trust signals, conversion paths, and a prioritized fix order.",
        },
        {
            "question": "Can an automated tool replace a human audit?",
            "answer": "No. Automated tools are useful for finding technical signals quickly, but a human audit is needed to judge search intent, business impact, conversion friction, content quality, and implementation priority.",
        },
        {
            "question": "What should I fix first after the audit?",
            "answer": "Fix anything that blocks crawling, indexing, page loading, forms, or core conversion paths first. Then improve high-intent pages with weak titles, thin answers, poor internal links, missing proof, or unclear CTAs.",
        },
    ]


def make_post(topic):
    return {
        "slug": topic["slug"],
        "title": topic["title"],
        "excerpt": topic["excerpt"],
        "meta": topic["meta"],
        "category": "SEO",
        "date": "2026-07-22",
        "modifiedDate": "2026-07-22",
        "readingTime": "9 min",
        "primaryKeyword": topic["primary"],
        "secondaryKeyword": topic["secondary"],
        "funnelTo": "/free-audit/",
        "funnelLabel": "Free Website Audit Report",
        "featured": False,
        "intentCardHtml": intent_card(topic),
        "hook": f"If you searched for {topic['primary']}, you probably do not need another generic SEO score. You need a clear way to understand whether the site can be crawled, understood, trusted, and turned into leads. This guide turns that search into a practical audit workflow.",
        "faqs": faqs_for(topic),
        "body": body_for(topic),
    }


BATCH_POSTS = [make_post(topic) for topic in TOPICS]


def update_sitemap_for_batch():
    sitemap = ROOT / "sitemap.xml"
    xml = sitemap.read_text()
    insertion = []
    for post in BATCH_POSTS:
        loc = f"https://lofts.studio/blog/{post['slug']}.html"
        if loc in xml:
            continue
        insertion.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            "    <lastmod>2026-07-22</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>0.8</priority>\n"
            "  </url>"
        )
    if not insertion:
        print("  . sitemap.xml already includes batch URLs")
        return
    xml = xml.replace("</urlset>", "\n".join(insertion) + "\n</urlset>")
    sitemap.write_text(xml)
    print(f"  + sitemap.xml appended ({len(insertion)} URLs)")


def main():
    nav, footer = seo_engine.load_nav_and_footer()
    for post in BATCH_POSTS:
        html = seo_engine.render_blog_post(post, nav, footer)
        out = BLOG_DIR / f"{post['slug']}.html"
        out.write_text(html)
        print(f"  + blog/{post['slug']}.html")

    batch_slugs = {post["slug"] for post in BATCH_POSTS}
    seo_engine.POSTS = BATCH_POSTS + [
        post for post in seo_engine.POSTS if post["slug"] not in batch_slugs
    ]
    seo_engine.update_posts_json()
    seo_engine.gen_covers()
    seo_engine.refresh_blog_index()
    update_sitemap_for_batch()

    print(f"  + published {len(BATCH_POSTS)} July 22 audit-guide posts")


if __name__ == "__main__":
    main()
