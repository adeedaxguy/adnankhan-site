# Audit Route Inventory

Updated: 2026-09-04

This is the consolidation record for the audit/report, PDF, free-report, and checker families. The five routes in `audit-funnel-routes.json` are the indexable conversion path. Redirected and noindex routes stay useful only where their narrower visitor job differs from the primary route.

| Route | Decision | Searcher job or destination |
| --- | --- | --- |
| `/blog/website-structure-audit-report.html` | Retain | Primary educational guide for reading structure-audit findings and choosing a route. |
| `/free-audit` | Retain | Primary tool for a broader site audit report and downloadable PDF. |
| `/tools/seo-aeo-checker.html` | Retain | Primary one-page observable SEO/AEO diagnostic. |
| `/services/technical-seo-audit.html` | Retain | Developer-led implementation review for crawl, index, canonical, schema, and platform issues. |
| `/services/landing-page-sprint.html` | Retain | Focused page rebuild for message, proof, mobile, form, and CTA friction. |
| `/blog/free-seo-audit-report-pdf.html` | 301 to `/free-audit` | Same practical job: get a free audit report with PDF output. |
| `/blog/free-site-audit-report.html` | 301 to `/free-audit` | Same practical job: run a free site audit report. |
| `/blog/site-audit-report-pdf.html` | 301 to `/free-audit` | Same practical job: obtain a site audit PDF. |
| `/blog/site-audit-report-sample.html` | 301 to `/free-audit` | Same practical job: see the report outcome and generate one. |
| `/blog/website-audit-report-generator-free.html` | 301 to `/free-audit` | Same practical job: use the report generator. |
| `/blog/website-audit-report-sample-pdf.html` | 301 to `/free-audit` | Same practical job: obtain a report PDF. |
| `/blog/website-structure-audit-report-pdf.html` | 301 to `/free-audit` | Same practical job: receive a structure/site audit PDF. |
| `/blog/seo-compatibility-checker-free.html` | 301 to `/tools/seo-aeo-checker.html` | Same practical job: use the free page checker. |
| `/blog/seo-compatibility-checker-online-free.html` | 301 to `/tools/seo-aeo-checker.html` | Same practical job: use the online checker. |
| `/blog/seo-compatibility-checker-online.html` | 301 to `/tools/seo-aeo-checker.html` | Same practical job: use the online checker. |
| `/blog/website-technical-seo-checker.html` | 301 to `/tools/seo-aeo-checker.html` | Same practical job: check observable technical SEO signals. |
| `/blog/seo-audit-report-template-for-leads.html` | `noindex,follow` | Template is useful to an existing visitor but is not a primary audit-report landing page. |
| `/blog/website-audit-report-template-free-download.html` | `noindex,follow` | Template download is not a differentiated search route. |
| `/blog/website-structure-audit-report-template-excel.html` | `noindex,follow` | Spreadsheet template is a support asset, not a primary audit query destination. |
| `/blog/website-structure-audit-report-template.html` | `noindex,follow` | Template is a support asset, not a primary audit query destination. |
| `/blog/free-site-audit-report-vs-human-review.html` | Retain | Comparison for visitors deciding between tool output and manual review. |
| `/blog/site-audit-report-for-ai-search.html` | Retain | Distinct guide for AI-search audit considerations. |
| `/blog/site-audit-report-format-service-business.html` | Retain | Distinct format guidance for service-business owners. |
| `/blog/site-seo-audit-report-before-redesign.html` | Retain | Distinct pre-redesign decision job. |
| `/blog/website-audit-report-for-ai-search.html` | Retain | Distinct page-level AI-search audit explanation. |
| `/blog/website-audit-report-pdf-sample.html` | Retain | Representative PDF-format explainer that links to the working tool. |
| `/blog/website-audit-report-qa-before-launch.html` | Retain | Distinct pre-launch QA job. |
| `/blog/website-structure-audit-report-example.html` | Retain | Worked-example job that points to the primary guide and tool. |
| `/blog/website-structure-audit-report-sample.html` | Retain | Sample-reading job that points to the primary guide and tool. |
| `/blog/seo-compatibility-checker.html` | Retain | Explanatory guide for the checker, not the checker itself. |

Redirect destinations have no intermediate hop. Redirected and noindex routes are excluded from `sitemap.xml`; retained routes must carry a unique visitor job, evidence, and next step.
