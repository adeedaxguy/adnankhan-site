import fs from "node:fs";

const DATE = "2026-08-08";
const MARKER = "data-dataforseo-audit-refresh=\"2026-08-08\"";

const pages = [
  {
    file: "blog/website-structure-audit-report.html",
    title: "Website Structure Audit Report + Free Tool | Lofts Studio",
    description:
      "Run a website structure audit report for crawl paths, page hierarchy, internal links, AI-search readiness, and lead-path fixes.",
    keyword: "website structure audit report",
    job: "show whether the site structure helps Google, AI answers, and buyers understand the offer",
    primary: "/free-audit",
    secondary: "/blog/website-structure-audit-report-template.html",
  },
  {
    file: "blog/website-audit-report-pdf-sample.html",
    title: "Website Audit Report PDF Sample | Lofts Studio",
    description:
      "Review a website audit report PDF sample with SEO, AEO, conversion, trust, evidence, and fix-priority sections before using a scanner.",
    keyword: "website audit report PDF sample",
    job: "show what a useful sample report should include before a business trusts a one-click score",
    primary: "/free-audit",
    secondary: "/blog/site-audit-report-pdf.html",
  },
  {
    file: "blog/free-seo-audit-report-pdf.html",
    title: "Free SEO Audit Report PDF: What to Include | Lofts Studio",
    description:
      "Use this free SEO audit report PDF guide to separate crawl, structure, AI-answer, content, trust, and lead-path fixes.",
    keyword: "free SEO audit report PDF",
    job: "turn a free PDF search into a prioritized fix list for visibility and enquiries",
    primary: "/free-audit",
    secondary: "/services/technical-seo-audit.html",
  },
  {
    file: "blog/site-audit-report-pdf.html",
    title: "Site Audit Report PDF: Format, Evidence, Fix Order | Lofts Studio",
    description:
      "Build a site audit report PDF that explains issue evidence, business impact, fix owner, priority, and the path from audit to implementation.",
    keyword: "site audit report PDF",
    job: "explain the report format, evidence fields, ownership, and next action",
    primary: "/free-audit",
    secondary: "/blog/website-audit-report-template-free-download.html",
  },
  {
    file: "blog/website-structure-audit-report-template.html",
    title: "Website Structure Audit Report Template | Lofts Studio",
    description:
      "Use a website structure audit report template for hierarchy, crawl depth, internal links, content gaps, schema, and conversion routes.",
    keyword: "website structure audit report template",
    job: "give teams a reusable section order instead of generic audit prose",
    primary: "/blog/website-structure-audit-report.html",
    secondary: "/free-audit",
  },
  {
    file: "blog/website-audit-report-template-free-download.html",
    title: "Website Audit Report Template Free Download | Lofts Studio",
    description:
      "Use a copyable website audit report template for access, structure, content, trust, conversion, ownership, and validation fields.",
    keyword: "website audit report template free download",
    job: "make the template printable, copyable, and practical before a full implementation sprint",
    primary: "/free-audit",
    secondary: "/blog/technical-seo-audit-report-template.html",
  },
  {
    file: "blog/website-structure-audit-report-example.html",
    title: "Website Structure Audit Report Example | Lofts Studio",
    description:
      "See a website structure audit report example that maps page hierarchy, internal links, search intent, proof, and fix priority.",
    keyword: "website structure audit report example",
    job: "show how findings move from issue evidence to fix mapping on a service website",
    primary: "/blog/website-structure-audit-report.html",
    secondary: "/free-audit",
  },
  {
    file: "blog/technical-seo-audit-report-template.html",
    title: "Technical SEO Audit Report Template | Lofts Studio",
    description:
      "Use a technical SEO audit report template with crawl, indexation, schema, redirects, Core Web Vitals, ownership, and validation fields.",
    keyword: "technical SEO audit report template",
    job: "turn technical findings into developer-ready fixes and validation criteria",
    primary: "/services/technical-seo-audit.html",
    secondary: "/blog/site-audit-report-pdf.html",
  },
  {
    file: "blog/service-website-audit-report-checklist.html",
    title: "Service Website Audit Report Checklist | Lofts Studio",
    description:
      "Use a service website audit report checklist for forms, phone paths, WhatsApp, proof, FAQs, speed, schema, and follow-up readiness.",
    keyword: "service website audit report checklist",
    job: "check whether a service website can turn search traffic into a serious enquiry",
    primary: "/free-audit",
    secondary: "/services/conversion-rate-optimization.html",
  },
  {
    file: "blog/website-conversion-path-audit.html",
    title: "Website Conversion Path Audit for Leads | Lofts Studio",
    description:
      "Run a website conversion path audit across first screen, proof, CTA, forms, tracking, internal links, and follow-up quality.",
    keyword: "website conversion audit",
    job: "trace the searcher from query to proof, action, form, and follow-up",
    primary: "/services/conversion-rate-optimization.html",
    secondary: "/free-audit",
  },
  {
    file: "blog/free-site-audit-report.html",
    title: "Free Site Audit Report: What to Expect | Lofts Studio",
    description:
      "Use a free site audit report to check access, structure, SEO/AEO readiness, trust, broken links, PDF output, and fix priority.",
    keyword: "free site audit report",
    job: "separate useful audit evidence from generic scanner warnings",
    primary: "/free-audit",
    secondary: "/blog/website-audit-report-pdf-sample.html",
  },
  {
    file: "blog/site-audit-report-sample.html",
    title: "Site Audit Report Sample for Service Websites | Lofts Studio",
    description:
      "Review a site audit report sample that connects SEO findings, AI-search clarity, proof, conversion paths, and prioritized fixes.",
    keyword: "site audit report sample",
    job: "show sample evidence and explain which fixes matter first",
    primary: "/free-audit",
    secondary: "/blog/site-audit-report-pdf.html",
  },
  {
    file: "blog/website-audit-report-generator-free.html",
    title: "Website Audit Report Generator Free: Judge the Output | Lofts Studio",
    description:
      "Use a free website audit report generator, then judge the output by evidence, fix priority, AI-readiness, trust, and lead path.",
    keyword: "website audit report generator free",
    job: "clarify what the live generator does and what still needs expert judgment",
    primary: "/free-audit",
    secondary: "/tools/seo-aeo-checker.html",
  },
  {
    file: "blog/website-audit-report-sample-pdf.html",
    title: "Website Audit Report Sample PDF | Lofts Studio",
    description:
      "Use this website audit report sample PDF guide to check issue evidence, screenshots, priorities, owners, and validation steps.",
    keyword: "website audit report sample PDF",
    job: "help searchers compare a sample PDF against a report they can actually act on",
    primary: "/free-audit",
    secondary: "/blog/website-audit-report-template-free-download.html",
  },
  {
    file: "blog/website-structure-audit-report-pdf.html",
    title: "Website Structure Audit Report PDF | Lofts Studio",
    description:
      "Create a website structure audit report PDF with hierarchy, crawl paths, internal links, schema, content gaps, and lead-path fixes.",
    keyword: "website structure audit report PDF",
    job: "turn structure findings into a report a founder and developer can both use",
    primary: "/blog/website-structure-audit-report.html",
    secondary: "/free-audit",
  },
];

const touchedUrls = new Set([
  "https://lofts.studio/free-audit",
  "https://lofts.studio/tools",
  "https://lofts.studio/tools/seo-aeo-checker.html",
  "https://lofts.studio/services/technical-seo-audit.html",
]);

for (const p of pages) {
  touchedUrls.add(`https://lofts.studio/${p.file}`);
}

function read(file) {
  return fs.readFileSync(file, "utf8");
}

function write(file, text) {
  fs.writeFileSync(file, text);
}

function replaceMetaDescription(html, description) {
  return html.replace(
    /<meta name="description" content="[^"]*" \/>/,
    `<meta name="description" content="${description}" />`
  );
}

function replaceTitle(html, title) {
  return html.replace(/<title>[\s\S]*?<\/title>/, `<title>${title}</title>`);
}

function refreshDates(html) {
  return html
    .replace(/<meta property="article:modified_time" content="[^"]*" \/>/, `<meta property="article:modified_time" content="${DATE}T00:00:00Z" />`)
    .replace(/"dateModified":\s*"[^"]*"/, `"dateModified": "${DATE}T00:00:00Z"`);
}

function auditBlock(p) {
  const id = `${p.file.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "")}-audit-action`;
  return `

    <div class="post-callout" ${MARKER}><p><strong>DataForSEO + GSC refresh:</strong> This page now maps the query <strong>${p.keyword}</strong> to one practical job: ${p.job}. The next step is not another score; it is a clear path from issue evidence to a prioritized fix.</p></div>

    <h2 id="${id}">What the report should decide first</h2>
    <p>A useful Lofts Studio audit report should make three things easy to see: whether the page can be crawled and understood, whether the first screen earns trust, and whether the visitor has a direct route to an enquiry, audit, or implementation conversation.</p>
    <ul>
      <li><strong>Evidence:</strong> list the affected URL, visible page section, source signal, and why it matters.</li>
      <li><strong>Fix order:</strong> separate access blockers, snippet/CTR fixes, answer clarity, proof gaps, and conversion friction.</li>
      <li><strong>Owner:</strong> mark whether the next action belongs to design, development, SEO content, analytics, or follow-up.</li>
      <li><strong>Lead path:</strong> connect the finding to <a href="${p.primary}">the primary next step</a>, <a href="${p.secondary}">the supporting resource</a>, or a technical implementation conversation.</li>
    </ul>`;
}

function injectAuditBlock(html, p) {
  if (html.includes(MARKER)) return html;
  const block = auditBlock(p);
  const leadMatch = /(<section style="padding: 0 0 4rem;">\s*<div class="container post-prose">\s*<p[^>]*>[\s\S]*?<\/p>)/;
  if (leadMatch.test(html)) return html.replace(leadMatch, `$1${block}`);
  const calloutMatch = /(<div class="post-callout">[\s\S]*?<\/div>)/;
  if (calloutMatch.test(html)) return html.replace(calloutMatch, `$1${block}`);
  return html;
}

for (const p of pages) {
  if (!fs.existsSync(p.file)) continue;
  let html = read(p.file);
  html = replaceTitle(html, p.title);
  html = replaceMetaDescription(html, p.description);
  html = refreshDates(html);
  html = injectAuditBlock(html, p);
  write(p.file, html);
}

{
  const file = "free-audit/index.html";
  let html = read(file);
  html = replaceTitle(html, "Free Site Audit Report + Website Audit PDF | Lofts Studio");
  html = replaceMetaDescription(
    html,
    "Run a free site audit report with PDF output, SEO/AEO checks, design friction, trust gaps, broken links, and prioritized fixes."
  );
  html = html
    .replace(
      /<meta property="og:title" content="[^"]*" \/>/,
      `<meta property="og:title" content="Free Site Audit Report + Website Audit PDF" />`
    )
    .replace(
      /<meta name="twitter:description" content="[^"]*" \/>/,
      `<meta name="twitter:description" content="Run a free site audit report with PDF output, SEO/AEO checks, design friction, trust gaps, broken links, and prioritized fixes." />`
    )
    .replace(
      `<p class="lead">Paste any URL and get a client-ready site audit report: design, SEO/AEO compatibility, performance, trust signals, broken links, and a plain-English before/after improvement plan you can discuss with a non-technical client or use before hiring a team.</p>`,
      `<p class="lead">Paste any URL and get a client-ready site audit report: design, SEO/AEO compatibility, performance, trust signals, broken links, PDF output, and a plain-English before/after improvement plan you can discuss with a non-technical client or use before hiring a team.</p>`
    )
    .replace(
      `<a href="/blog/website-audit-report-pdf-sample.html">What the PDF should include</a>
          <a href="/blog/website-structure-audit-report.html">Structure audit guide</a>
          <a href="/tools/seo-aeo-checker.html">SEO/AEO checker</a>`,
      `<a href="/blog/website-audit-report-pdf-sample.html">What the PDF should include</a>
          <a href="/blog/site-audit-report-pdf.html">Site audit PDF format</a>
          <a href="/blog/website-audit-report-generator-free.html">Generator output guide</a>
          <a href="/blog/website-structure-audit-report.html">Structure audit guide</a>
          <a href="/tools/seo-aeo-checker.html">SEO/AEO checker</a>`
    );
  if (!html.includes(MARKER)) {
    html = html.replace(
      `</div>
      <div class="diagnostic-panel" data-reveal>`,
      `<div class="audit-resource-links" ${MARKER} aria-label="Report decisions">
          <a href="/blog/free-site-audit-report.html">Free report expectations</a>
          <a href="/blog/website-conversion-path-audit.html">Conversion path audit</a>
          <a href="/services/technical-seo-audit.html">Implementation review</a>
        </div>
      </div>
      <div class="diagnostic-panel" data-reveal>`
    );
  }
  write(file, html);
}

{
  const file = "tools/seo-aeo-checker.html";
  let html = read(file);
  html = replaceTitle(html, "AEO Checker + SEO Compatibility Tool | Lofts Studio");
  html = replaceMetaDescription(
    html,
    "Run an AEO checker for one page: indexability, titles, schema, answer clarity, internal links, trust proof, mobile UX, and conversion path."
  );
  html = html.replace(
    `<p class="lead">Paste a page URL and see whether it has the signals Google and answer engines can actually work with: indexability, title and meta quality, schema, answer clarity, mobile setup, trust proof, internal links, and a clear next step.</p>`,
    `<p class="lead">Paste a page URL and see whether it has the signals Google and answer engines can actually work with: indexability, title and meta quality, schema, answer clarity, entity proof, mobile setup, internal links, and a clear next step.</p>`
  );
  if (!html.includes(MARKER)) {
    html = html.replace(
      `</form>
        </div>
      </div>
    </section>`,
      `</form>
          <div class="diagnostic-badges" ${MARKER} aria-label="AEO checker routes" style="margin-top: 1rem;">
            <a href="/blog/seo-compatibility-checker.html">SEO checker guide</a>
            <a href="/blog/website-audit-report-for-ai-search.html">AI-search audit</a>
            <a href="/free-audit">Full website report</a>
          </div>
        </div>
      </div>
    </section>`
    );
  }
  write(file, html);
}

{
  const file = "services/technical-seo-audit.html";
  let html = read(file);
  html = replaceMetaDescription(
    html,
    "Technical SEO audit service for crawl, indexation, schema, redirects, Core Web Vitals, search appearance, AEO readiness, and implementation."
  );
  if (!html.includes(MARKER)) {
    const section = `

<section class="section-sm" ${MARKER} aria-labelledby="audit-report-cluster">
  <div class="container">
    <div class="card" style="display:grid;gap:1rem;">
      <span class="eyebrow">Audit to implementation</span>
      <h2 class="h-2" id="audit-report-cluster">The report should end with fixes someone can ship.</h2>
      <p class="lead" style="margin:0;max-width:760px;">Lofts Studio connects technical SEO audit findings to crawl access, search appearance, AEO readiness, internal links, conversion paths, and the production work needed to make the report useful.</p>
      <div style="display:flex;flex-wrap:wrap;gap:.75rem;">
        <a class="btn btn-primary" href="/free-audit">Run the free audit</a>
        <a class="btn btn-ghost" href="/blog/technical-seo-audit-report-template.html">Technical report template</a>
        <a class="btn btn-ghost" href="/blog/site-audit-report-pdf.html">Site audit PDF format</a>
      </div>
    </div>
  </div>
</section>`;
    html = html.replace(`</main>`, `${section}\n</main>`);
  }
  write(file, html);
}

{
  const file = "tools/index.html";
  let html = read(file);
  if (!html.includes(MARKER)) {
    const cluster = `

<section class="section-sm" ${MARKER} aria-labelledby="audit-resource-hub" style="padding: 1rem 0 3rem;">
  <div class="container">
    <div data-reveal style="display:flex;align-items:flex-end;justify-content:space-between;gap:1.5rem;margin-bottom:1.4rem;flex-wrap:wrap;">
      <div>
        <span class="eyebrow">Audit resource hub</span>
        <h2 class="h-2" id="audit-resource-hub" style="margin:.4rem 0 0;">Choose the right report path.</h2>
      </div>
      <a class="btn btn-ghost" href="/free-audit">Start with the live audit</a>
    </div>
    <div class="work-grid" data-reveal>
      <article class="card"><span class="tag-pill">Run</span><h3>Free site audit report</h3><p>Use the live report when you need a current crawl, trust, broken-link, AEO, and conversion snapshot.</p><a class="btn-editorial" href="/free-audit">Open audit tool <span aria-hidden="true">&rarr;</span></a></article>
      <article class="card"><span class="tag-pill">Read</span><h3>Site audit PDF format</h3><p>Use the PDF guide when you need evidence fields, issue ownership, and a fix order.</p><a class="btn-editorial" href="/blog/site-audit-report-pdf.html">Read format guide <span aria-hidden="true">&rarr;</span></a></article>
      <article class="card"><span class="tag-pill">Check</span><h3>AEO readiness</h3><p>Use the focused checker when one page needs answer clarity, schema, entity proof, and internal links.</p><a class="btn-editorial" href="/tools/seo-aeo-checker.html">Run AEO checker <span aria-hidden="true">&rarr;</span></a></article>
    </div>
  </div>
</section>`;
    html = html.replace(`<!-- ── ROW 1: Field guides (mine) ── -->`, `${cluster}\n\n<!-- ── ROW 1: Field guides (mine) ── -->`);
  }
  write(file, html);
}

{
  const file = "blog/posts.json";
  const data = JSON.parse(read(file));
  data.lastUpdated = DATE;
  const updates = new Map(pages.map((p) => [
    p.file.replace(/^blog\//, "").replace(/\.html$/, ""),
    `Updated for DataForSEO and GSC audit-report intent: ${p.keyword}, answer clarity, internal links, report format, and audit-to-lead path.`,
  ]));
  for (const post of data.posts || []) {
    if (updates.has(post.slug)) {
      post.excerpt = updates.get(post.slug);
      post.funnelTo = post.funnelTo || "/free-audit/";
    }
  }
  write(file, `${JSON.stringify(data, null, 2)}\n`);
}

{
  const file = "llms.txt";
  let text = read(file);
  if (!text.includes("<!-- 2026-08-08-AUDIT-REPORT-CLUSTER:START -->")) {
    text += `

<!-- 2026-08-08-AUDIT-REPORT-CLUSTER:START -->
## August 8, 2026 audit report and AEO checker cluster
Lofts Studio connects site audit report, free website audit report, AEO checker, website conversion audit, and technical SEO audit intent to practical implementation paths for service businesses.
- [Free Website Audit Report](https://lofts.studio/free-audit) - live site audit report with PDF output, SEO/AEO checks, trust gaps, broken links, and prioritized fixes.
- [SEO and AEO Compatibility Checker](https://lofts.studio/tools/seo-aeo-checker.html) - one-page checker for indexability, answer clarity, schema, entity proof, internal links, mobile UX, and conversion path.
- [Website Structure Audit Report](https://lofts.studio/blog/website-structure-audit-report.html) - structure, crawl path, internal link, AI-search, and lead-path audit guide.
- [Site Audit Report PDF](https://lofts.studio/blog/site-audit-report-pdf.html) - PDF format, evidence fields, owners, fix priority, and validation criteria.
- [Website Conversion Path Audit](https://lofts.studio/blog/website-conversion-path-audit.html) - query-to-lead path review for first screen, proof, CTA, form, analytics, and follow-up.
- [Technical SEO Audit Service](https://lofts.studio/services/technical-seo-audit.html) - implementation-led crawl, indexation, schema, redirect, Core Web Vitals, search appearance, and AEO audit support.
<!-- 2026-08-08-AUDIT-REPORT-CLUSTER:END -->
`;
    write(file, text);
  }
}

{
  const file = "sitemap.xml";
  let xml = read(file);
  for (const url of touchedUrls) {
    const re = new RegExp(`(<loc>${url.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}</loc>\\s*<lastmod>)[^<]+(</lastmod>)`);
    xml = xml.replace(re, `$1${DATE}$2`);
  }
  write(file, xml);
}

console.log(`Updated ${pages.length} audit-cluster pages plus free audit, AEO checker, technical SEO service, tools hub, posts.json, llms.txt, and sitemap.`);
