#!/usr/bin/env python3
"""Apply deterministic, idempotent repairs found by full_site_qa.py."""

from __future__ import annotations

import html
import re
import struct
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
RELEASE = "20260731d"

LEGACY_POSTS_WITHOUT_H1 = {
    "blog/checkout-friction-audit.html",
    "blog/core-web-vitals-shopify.html",
    "blog/migration-without-downtime.html",
    "blog/the-handoff-problem.html",
    "blog/the-pdp-question.html",
    "blog/the-quiet-conversion-killers.html",
    "blog/why-i-stopped-using-themes.html",
    "blog/woocommerce-still-makes-sense.html",
}

TITLE_OVERRIDES = {
    "blog/ecommerce-conversion-audit.html": "Ecommerce Conversion Audit: Find Leaks Before More Traffic",
    "blog/schema-markup-ai-search.html": "Schema Markup for AI Search: Entities, Services and FAQs",
    "blog/seo-audit-report-template-for-leads.html": "SEO Audit Report Template for Leads: What Websites Should Show",
    "blog/shopify-custom-app-vs-public-app.html": "Shopify App Types: Custom vs Private vs Public",
    "blog/shopify-plus-vs-advanced-when-to-upgrade.html": "Shopify Plus vs Advanced: When to Upgrade",
    "blog/speed-up-woocommerce-checklist.html": "Why Your WooCommerce Store Is Slow: 5 Common Causes",
    "process/index.html": "Process | Lofts Studio Web Design & Development",
}

DESCRIPTION_REPLACEMENTS = {
    "Agentic commerce, explained for Shopify merchants: what “your store is now in ChatGPT” really means in 2026, what changed, what’s hype, and the product-data work that decides whether AI shopping agents recommend you.": "A practical guide to agentic commerce for Shopify: what changed, what is hype, and how product data helps AI shopping agents understand a store.",
    "A practical guide to passing Core Web Vitals on Shopify in 2026. The four metrics that matter, the apps that quietly tank LCP, and the four-hour audit any operator can run today.": "A practical Shopify Core Web Vitals guide covering the metrics, common app bottlenecks, and a focused audit merchants can run before making changes.",
    "What this site stores in your browser, what it doesn't, and how to clear it.": "See what Lofts Studio stores in your browser, when optional analytics loads, how consent works, and how to clear local preferences and measurement cookies.",
    "Senior remote website design, local SEO structure, and AI calling agents for US service businesses. Start with priority state and city pages built for qualified enquiries.": "Senior remote web design, development, local SEO structure, and AI calling agents for US businesses, with truthful regional service and qualified enquiry paths.",
    "A curated public archive from Lofts Studio: selected shipped work across Shopify, WooCommerce, WordPress, custom apps, B2B platforms, marketplaces, and performance rebuilds.": "Explore selected Lofts Studio work across Shopify, WooCommerce, WordPress, Webflow, SaaS, custom apps, marketplaces, and performance-focused rebuilds.",
    "A five-phase, six-week template for how every project here ships — Discovery, Audit, Build, Launch, Iterate. Written for founders who have been burned by agencies and want to see the work before they sign.": "See how Lofts Studio moves from discovery and audit through build, launch, and iteration, with visible senior ownership and clear decisions at every stage.",
}

NOTE_REDIRECTS = {
    "/notes/why-i-stopped-using-themes.html": "/blog/why-i-stopped-using-themes.html",
    "/notes/migration-without-downtime.html": "/blog/migration-without-downtime.html",
    "/notes/checkout-friction-audit.html": "/blog/checkout-friction-audit.html",
    "/notes/core-web-vitals-shopify.html": "/blog/core-web-vitals-shopify.html",
    "/notes/the-pdp-question.html": "/blog/the-pdp-question.html",
    "/notes/woocommerce-still-makes-sense.html": "/blog/woocommerce-still-makes-sense.html",
    "/notes/the-quiet-conversion-killers.html": "/blog/the-quiet-conversion-killers.html",
}

GTM_HEAD_RE = re.compile(
    r"\s*<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->\s*",
    re.DOTALL,
)
GTM_NOSCRIPT_RE = re.compile(
    r"\s*<!-- Google Tag Manager \(noscript\) -->.*?<!-- End Google Tag Manager \(noscript\) -->\s*",
    re.DOTALL,
)
GTAG_RE = re.compile(
    r"\s*(?:<!-- Google tag \(gtag\.js\) -->\s*)?"
    r"<script\b[^>]*src=[\"']https://www\.googletagmanager\.com/gtag/js\?id=[^\"']+[\"'][^>]*></script>\s*"
    r"<script>\s*window\.dataLayer=.*?gtag\(['\"]config['\"],\s*['\"]G-[^'\"]+['\"]\);\s*</script>\s*",
    re.DOTALL,
)
GOOGLE_FONT_LINK_RE = re.compile(
    r"\s*<link\b[^>]*(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*?/?>\s*",
    re.IGNORECASE,
)
COMMENT_RE = re.compile(
    r"\s*<section class=[\"']comments[\"'][^>]*>.*?</section>\s*"
    r"(?:<script\b[^>]*src=[\"']/assets/comments\.js[^\"']*[\"'][^>]*></script>)?\s*",
    re.DOTALL,
)
QUALITY_BLOCK_RE = re.compile(
    r"\s*<h2 id=[\"']one-more-quality-check-before-publishing[\"']>"
    r"One more quality check before publishing</h2>\s*"
    r"<p>Read the page.*?</p>\s*"
    r"<p>Then read it.*?</p>",
    re.DOTALL,
)
IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", re.DOTALL)


def attributes(tag: str) -> dict[str, str]:
    return {name.lower(): html.unescape(value) for name, _, value in ATTR_RE.findall(tag)}


def first_meta(text: str, key: str, value: str) -> str:
    for tag in re.findall(r"<meta\b[^>]*>", text, flags=re.IGNORECASE):
        attrs = attributes(tag)
        if attrs.get(key) == value:
            return attrs.get("content", "")
    return ""


def first_canonical(text: str) -> str:
    for tag in re.findall(r"<link\b[^>]*>", text, flags=re.IGNORECASE):
        attrs = attributes(tag)
        if "canonical" in attrs.get("rel", "").lower().split():
            return attrs.get("href", "")
    return ""


def page_title(text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip()) if match else ""


def update_title(text: str, relative: str) -> str:
    current = page_title(text)
    if not current:
        return text
    replacement = TITLE_OVERRIDES.get(relative)
    if replacement is None and len(current) > 65:
        replacement = current
        for suffix in (" | Adnan K.", " · Lofts Studio Blog", " | Lofts Studio"):
            if replacement.endswith(suffix):
                replacement = replacement[: -len(suffix)]
                break
    if not replacement or replacement == current:
        return text
    escaped = html.escape(replacement, quote=False)
    return re.sub(r"(<title>).*?(</title>)", rf"\1{escaped}\2", text, count=1, flags=re.IGNORECASE | re.DOTALL)


def add_social_metadata(text: str, path: Path) -> str:
    if "noindex" in first_meta(text, "name", "robots").lower():
        return text
    title = page_title(text)
    description = first_meta(text, "name", "description")
    canonical = first_canonical(text)
    if not title or not description or not canonical:
        return text

    social_tags: list[str] = []
    if not first_meta(text, "property", "og:type"):
        social_tags.append(f'<meta property="og:type" content="{"article" if path.parent.name == "blog" else "website"}" />')
    if not first_meta(text, "property", "og:url"):
        social_tags.append(f'<meta property="og:url" content="{html.escape(canonical, quote=True)}" />')
    if not first_meta(text, "property", "og:title"):
        social_tags.append(f'<meta property="og:title" content="{html.escape(title, quote=True)}" />')
    if not first_meta(text, "property", "og:description"):
        social_tags.append(f'<meta property="og:description" content="{html.escape(description, quote=True)}" />')

    image_url = "https://lofts.studio/assets/og.jpg?v=2"
    if path.parent.name == "blog":
        for suffix in (".png", ".svg", ".jpg", ".webp"):
            candidate = ROOT / "assets" / "blog" / f"{path.stem}{suffix}"
            if candidate.exists():
                image_url = f"https://lofts.studio/assets/blog/{candidate.name}"
                break
    if not first_meta(text, "property", "og:image"):
        social_tags.extend(
            [
                f'<meta property="og:image" content="{image_url}" />',
                '<meta property="og:image:width" content="1200" />',
                f'<meta property="og:image:height" content="{"675" if "/assets/blog/" in image_url else "630"}" />',
                f'<meta property="og:image:alt" content="{html.escape(title, quote=True)}" />',
            ]
        )
    if not first_meta(text, "name", "twitter:card"):
        social_tags.extend(
            [
                '<meta name="twitter:card" content="summary_large_image" />',
                f'<meta name="twitter:title" content="{html.escape(title, quote=True)}" />',
                f'<meta name="twitter:description" content="{html.escape(description, quote=True)}" />',
                f'<meta name="twitter:image" content="{image_url}" />',
            ]
        )
    if not social_tags:
        return text
    return text.replace("</head>", "\n" + "\n".join(social_tags) + "\n</head>", 1)


def svg_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        start = path.read_text(encoding="utf-8", errors="ignore")[:4096]
    except OSError:
        return None
    tag_match = re.search(r"<svg\b[^>]*>", start, flags=re.IGNORECASE)
    if not tag_match:
        return None
    attrs = attributes(tag_match.group(0))
    try:
        if attrs.get("width") and attrs.get("height"):
            return int(float(re.sub(r"[^\d.]", "", attrs["width"]))), int(float(re.sub(r"[^\d.]", "", attrs["height"])))
        viewbox = [float(value) for value in re.split(r"[\s,]+", attrs.get("viewbox", "")) if value]
        if len(viewbox) == 4:
            return round(viewbox[2]), round(viewbox[3])
    except ValueError:
        return None
    return None


def raster_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 9 < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            offset += 2
            if marker in (0xD8, 0xD9):
                continue
            if offset + 2 > len(data):
                break
            length = struct.unpack(">H", data[offset : offset + 2])[0]
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                if offset + 7 <= len(data):
                    height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
                    return width, height
                break
            offset += max(length, 2)
    return None


def local_image_dimensions(src: str, html_path: Path) -> tuple[int, int] | None:
    parsed = urlsplit(src)
    if parsed.scheme or parsed.netloc or src.startswith("data:"):
        return None
    clean = unquote(parsed.path)
    path = ROOT / clean.lstrip("/") if clean.startswith("/") else html_path.parent / clean
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        return None
    if not path.exists():
        return None
    return svg_dimensions(path) if path.suffix.lower() == ".svg" else raster_dimensions(path)


def add_image_dimensions(text: str, html_path: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        attrs = attributes(tag)
        if not attrs.get("src") or ("width" in attrs and "height" in attrs):
            return tag
        dimensions = local_image_dimensions(attrs["src"], html_path)
        if not dimensions:
            return tag
        width, height = dimensions
        additions = ""
        if "width" not in attrs:
            additions += f' width="{width}"'
        if "height" not in attrs:
            additions += f' height="{height}"'
        closing = "/>" if tag.endswith("/>") else ">"
        return tag[: -len(closing)].rstrip() + additions + " " + closing

    return IMG_RE.sub(replace, text)


def add_legacy_h1(text: str, relative: str) -> str:
    if relative not in LEGACY_POSTS_WITHOUT_H1 or re.search(r"<h1\b", text, flags=re.IGNORECASE):
        return text
    title = page_title(text)
    for suffix in (" · Lofts Studio Blog", " | Adnan K.", " | Lofts Studio"):
        if title.endswith(suffix):
            title = title[: -len(suffix)]
    description = first_meta(text, "name", "description")
    section = f'''
<section class="paper" style="padding: 5rem 0 3rem;">
  <div class="container post-prose">
    <span class="eyebrow">Field note</span>
    <h1 class="h-1" style="margin-top: 1.25rem;">{html.escape(title, quote=False)}</h1>
    <p class="lead" style="margin-top: 1.5rem;">{html.escape(description, quote=False)}</p>
  </div>
</section>
'''
    return text.replace("</header>", "</header>\n" + section, 1)


def ensure_main_and_skip_link(text: str) -> str:
    main_match = re.search(r"<main\b[^>]*>", text, flags=re.IGNORECASE)
    if main_match:
        tag = main_match.group(0)
        attrs = attributes(tag)
        additions = ""
        if "id" not in attrs:
            additions += ' id="main-content"'
        if "tabindex" not in attrs:
            additions += ' tabindex="-1"'
        if additions:
            replacement = tag[:-1].rstrip() + additions + ">"
            text = text[: main_match.start()] + replacement + text[main_match.end() :]
    else:
        header_end = text.find("</header>")
        footer_start = text.rfind('<footer class="site-footer')
        if header_end >= 0:
            insert_at = header_end + len("</header>")
            close_at = footer_start
            if close_at <= header_end:
                main_script = re.search(
                    r"\n<script\b[^>]*src=[\"'][^\"']*assets/main\.js",
                    text[insert_at:],
                    flags=re.IGNORECASE,
                )
                close_at = insert_at + main_script.start() if main_script else text.rfind("</body>")
            if close_at > header_end:
                text = text[:insert_at] + '\n<main id="main-content" tabindex="-1">' + text[insert_at:]
                close_at += len('\n<main id="main-content" tabindex="-1">')
                text = text[:close_at] + "</main>\n\n" + text[close_at:]
    if 'id="main-content"' in text and 'class="skip-link"' not in text:
        text = re.sub(
            r"(<body\b[^>]*>)",
            r'\1\n<a class="skip-link" href="#main-content">Skip to main content</a>',
            text,
            count=1,
            flags=re.IGNORECASE,
        )
    return text


def normalize_asset_versions(text: str) -> str:
    names = ("styles.css", "home-critical.css", "experience.css", "main.js", "widgets.js")
    for name in names:
        text = re.sub(rf"({re.escape(name)}\?v=)[A-Za-z0-9._-]+", rf"\g<1>{RELEASE}", text)
    return text


def repair_html(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="strict")
    original = text

    text = GTM_HEAD_RE.sub("\n", text)
    text = GTM_NOSCRIPT_RE.sub("\n", text)
    text = GTAG_RE.sub("\n", text)
    text = GOOGLE_FONT_LINK_RE.sub("\n", text)
    text = COMMENT_RE.sub("\n", text)
    text = text.replace('href="#contact"', 'href="/#contact"')
    text = text.replace("href='#contact'", "href='/#contact'")
    text = text.replace('href="/#services"', 'href="/services"')
    text = text.replace("href='/#services'", "href='/services'")
    for source, destination in NOTE_REDIRECTS.items():
        text = text.replace(f'href="{source}"', f'href="{destination}"')
        text = text.replace(f"href='{source}'", f"href='{destination}'")
    text = re.sub(r'href=(["\'])/notes/?\1', r'href=\1/blog/\1', text)

    if 'href="#faq"' in text:
        text = re.sub(
            r"<h2(?![^>]*\bid=)([^>]*)>\s*FAQ\s*</h2>",
            r'<h2 id="faq"\1>FAQ</h2>',
            text,
            count=1,
            flags=re.IGNORECASE,
        )

    quality_count = 0

    def deduplicate_quality_block(match: re.Match[str]) -> str:
        nonlocal quality_count
        quality_count += 1
        return match.group(0) if quality_count == 1 else ""

    text = QUALITY_BLOCK_RE.sub(deduplicate_quality_block, text)
    for old, new in DESCRIPTION_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = update_title(text, relative)
    text = add_legacy_h1(text, relative)
    text = ensure_main_and_skip_link(text)
    text = add_social_metadata(text, path)
    text = add_image_dimensions(text, path)
    text = normalize_asset_versions(text)

    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(part.startswith(".") for part in relative.parts) or relative.parts[0] in {"admin", "node_modules"}:
            continue
        if repair_html(path):
            changed.append(relative.as_posix())
    print(f"Repaired {len(changed)} HTML files.")
    for item in changed[:20]:
        print(f"  {item}")
    if len(changed) > 20:
        print(f"  ... and {len(changed) - 20} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
