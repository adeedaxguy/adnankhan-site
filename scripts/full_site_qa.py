#!/usr/bin/env python3
"""Crawl the production sitemap and report technical, SEO, and HTML QA issues."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any


USER_AGENT = "LoftsStudio-QA/1.0 (+https://lofts.studio/)"
HTML_LIMIT = 8 * 1024 * 1024
DEFAULT_TIMEOUT = 25
INTERNAL_HOSTS = {"lofts.studio", "www.lofts.studio"}
SKIP_SCHEMES = {"mailto", "tel", "sms", "javascript", "data", "blob"}


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def comparable_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    host = (parsed.hostname or "").lower()
    if host == "www.lofts.studio":
        host = "lofts.studio"
    path = urllib.parse.unquote(parsed.path or "/")
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    if path != "/":
        path = path.rstrip("/")
    return urllib.parse.urlunsplit(("https", host, path or "/", "", ""))


def canonical_matches(final_url: str, canonical_url: str) -> bool:
    if comparable_url(final_url) == comparable_url(canonical_url):
        return True
    final = urllib.parse.urlsplit(final_url)
    canonical = urllib.parse.urlsplit(canonical_url)
    return bool(
        final.hostname in {"127.0.0.1", "localhost"}
        and canonical.hostname in INTERNAL_HOSTS
        and (final.path.rstrip("/") or "/") == (canonical.path.rstrip("/") or "/")
        and final.query == canonical.query
    )


def resolve_url(base: str, value: str) -> str | None:
    value = (value or "").strip()
    if not value or value == "#":
        return None
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme.lower() in SKIP_SCHEMES:
        return None
    resolved = urllib.parse.urljoin(base, value)
    parsed = urllib.parse.urlsplit(resolved)
    if parsed.scheme not in {"http", "https"}:
        return None
    return resolved


def srcset_urls(value: str) -> list[str]:
    urls = []
    for item in (value or "").split(","):
        candidate = item.strip().split(" ", 1)[0]
        if candidate:
            urls.append(candidate)
    return urls


class AuditHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang = ""
        self.title_parts: list[str] = []
        self.in_title = False
        self.heading_stack: list[tuple[str, list[str]]] = []
        self.headings: list[tuple[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.canonicals: list[str] = []
        self.links: list[dict[str, Any]] = []
        self.link_stack: list[int] = []
        self.assets: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.forms: list[dict[str, str]] = []
        self.fields: list[dict[str, str]] = []
        self.labels_for: set[str] = set()
        self.nested_label_depth = 0
        self.buttons: list[dict[str, Any]] = []
        self.button_stack: list[int] = []
        self.ids: list[str] = []
        self.main_count = 0
        self.jsonld_parts: list[str] = []
        self.jsonld_blocks: list[str] = []
        self.in_jsonld = False

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(key).lower(): value or "" for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = self.attrs_dict(attrs)
        element_id = data.get("id", "")
        if element_id:
            self.ids.append(element_id)

        if tag == "html":
            self.html_lang = data.get("lang", "")
        elif tag == "title":
            self.in_title = True
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_stack.append((tag, []))
        elif tag == "meta":
            self.meta.append(data)
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            href = data.get("href", "")
            if "canonical" in rel and href:
                self.canonicals.append(href)
            if href and rel.intersection({"stylesheet", "preload", "modulepreload", "icon"}):
                self.assets.append(("link", href))
        elif tag == "a":
            self.links.append(
                {
                    "href": data.get("href", ""),
                    "aria": data.get("aria-label", ""),
                    "title": data.get("title", ""),
                    "text": [],
                }
            )
            self.link_stack.append(len(self.links) - 1)
        elif tag == "img":
            self.images.append(data)
            src = data.get("src", "")
            if src:
                self.assets.append(("img", src))
            for candidate in srcset_urls(data.get("srcset", "")):
                self.assets.append(("img-srcset", candidate))
            if self.link_stack and data.get("alt"):
                self.links[self.link_stack[-1]]["text"].append(data["alt"])
        elif tag in {"script", "iframe", "source", "video", "audio"}:
            src = data.get("src", "")
            if src:
                self.assets.append((tag, src))
            for candidate in srcset_urls(data.get("srcset", "")):
                self.assets.append((f"{tag}-srcset", candidate))
            if tag == "script" and data.get("type", "").lower() == "application/ld+json":
                self.in_jsonld = True
                self.jsonld_parts = []
        elif tag == "form":
            self.forms.append(data)
        elif tag == "label":
            label_for = data.get("for", "")
            if label_for:
                self.labels_for.add(label_for)
            self.nested_label_depth += 1
        elif tag in {"input", "select", "textarea"}:
            field_data = dict(data)
            field_data["tag"] = tag
            if self.nested_label_depth:
                field_data["nested_label"] = "true"
            self.fields.append(field_data)
        elif tag == "button":
            self.buttons.append(
                {
                    "aria": data.get("aria-label", ""),
                    "title": data.get("title", ""),
                    "text": [],
                }
            )
            self.button_stack.append(len(self.buttons) - 1)
        elif tag == "main":
            self.main_count += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            for index in range(len(self.heading_stack) - 1, -1, -1):
                if self.heading_stack[index][0] == tag:
                    heading_tag, parts = self.heading_stack.pop(index)
                    self.headings.append((heading_tag, compact("".join(parts))))
                    break
        elif tag == "a" and self.link_stack:
            self.link_stack.pop()
        elif tag == "button" and self.button_stack:
            self.button_stack.pop()
        elif tag == "label" and self.nested_label_depth:
            self.nested_label_depth -= 1
        elif tag == "script" and self.in_jsonld:
            self.jsonld_blocks.append("".join(self.jsonld_parts).strip())
            self.in_jsonld = False
            self.jsonld_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.heading_stack:
            self.heading_stack[-1][1].append(data)
        if self.link_stack:
            self.links[self.link_stack[-1]]["text"].append(data)
        if self.button_stack:
            self.buttons[self.button_stack[-1]]["text"].append(data)
        if self.in_jsonld:
            self.jsonld_parts.append(data)


@dataclass
class PageResult:
    requested_url: str
    final_url: str = ""
    status: int = 0
    content_type: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_ms: int = 0
    title: str = ""
    description: str = ""
    canonical: str = ""
    robots: str = ""
    h1: list[str] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)
    links: list[dict[str, Any]] = field(default_factory=list)
    assets: list[tuple[str, str]] = field(default_factory=list)
    issues: list[dict[str, str]] = field(default_factory=list)

    def add(self, severity: str, code: str, detail: str) -> None:
        self.issues.append({"severity": severity, "code": code, "detail": detail})


def request(url: str, method: str = "GET", timeout: int = DEFAULT_TIMEOUT) -> tuple[int, str, dict[str, str], bytes, int, str]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "identity",
    }
    started = time.monotonic()
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(HTML_LIMIT) if method != "HEAD" else b""
            elapsed = round((time.monotonic() - started) * 1000)
            return response.status, response.geturl(), dict(response.headers.items()), body, elapsed, ""
    except urllib.error.HTTPError as exc:
        body = exc.read(HTML_LIMIT) if method != "HEAD" else b""
        elapsed = round((time.monotonic() - started) * 1000)
        return exc.code, exc.geturl(), dict(exc.headers.items()), body, elapsed, str(exc)
    except Exception as exc:
        elapsed = round((time.monotonic() - started) * 1000)
        return 0, url, {}, b"", elapsed, f"{type(exc).__name__}: {exc}"


def meta_value(parser: AuditHTMLParser, key: str, value: str) -> str:
    key = key.lower()
    value = value.lower()
    for item in parser.meta:
        if item.get(key, "").lower() == value:
            return compact(item.get("content", ""))
    return ""


def audit_page(url: str) -> PageResult:
    status, final_url, headers, body, elapsed, fetch_error = request(url)
    content_type = next((value for key, value in headers.items() if key.lower() == "content-type"), "")
    result = PageResult(
        requested_url=url,
        final_url=final_url,
        status=status,
        content_type=content_type,
        headers={key.lower(): value for key, value in headers.items()},
        elapsed_ms=elapsed,
    )
    if fetch_error and status == 0:
        result.add("error", "fetch_failed", fetch_error)
        return result
    if status != 200:
        result.add("error", "http_status", f"Expected 200, received {status}")
        return result
    if comparable_url(url) != comparable_url(final_url):
        result.add("warning", "sitemap_redirect", f"Redirected to {final_url}")
    if "text/html" not in result.content_type.lower():
        result.add("error", "content_type", f"Expected HTML, received {result.content_type or 'unknown'}")
        return result

    charset_match = re.search(r"charset=([^;\s]+)", result.content_type, re.I)
    encoding = charset_match.group(1).strip('"\'') if charset_match else "utf-8"
    try:
        html = body.decode(encoding, errors="replace")
    except LookupError:
        html = body.decode("utf-8", errors="replace")

    parser = AuditHTMLParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:
        result.add("error", "html_parse", f"{type(exc).__name__}: {exc}")

    result.title = compact("".join(parser.title_parts))
    result.description = meta_value(parser, "name", "description")
    result.canonical = parser.canonicals[0] if parser.canonicals else ""
    result.robots = meta_value(parser, "name", "robots").lower()
    result.h1 = [text for tag, text in parser.headings if tag == "h1"]
    result.ids = parser.ids
    result.links = parser.links
    result.assets = parser.assets

    if not result.title:
        result.add("error", "missing_title", "No title element found")
    elif len(result.title) < 20 or len(result.title) > 70:
        result.add("warning", "title_length", f"{len(result.title)} characters")
    if not result.description:
        result.add("error", "missing_description", "No meta description found")
    elif len(result.description) < 80 or len(result.description) > 170:
        result.add("warning", "description_length", f"{len(result.description)} characters")
    if len(parser.canonicals) != 1:
        result.add("error", "canonical_count", f"Found {len(parser.canonicals)} canonical links")
    elif not canonical_matches(final_url, result.canonical):
        result.add("error", "canonical_mismatch", f"Canonical is {result.canonical}")
    if "noindex" in result.robots:
        result.add("error", "sitemap_noindex", f"Robots meta is {result.robots}")
    if len(result.h1) != 1:
        result.add("error", "h1_count", f"Found {len(result.h1)} H1 elements")
    if not parser.html_lang:
        result.add("warning", "missing_lang", "The html element has no lang attribute")
    if not meta_value(parser, "name", "viewport"):
        result.add("error", "missing_viewport", "No viewport meta tag found")
    if parser.main_count != 1:
        result.add("warning", "main_count", f"Found {parser.main_count} main elements")

    duplicate_ids = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    if duplicate_ids:
        result.add("error", "duplicate_ids", ", ".join(duplicate_ids[:12]))

    missing_alt = [img.get("src", "<inline>") for img in parser.images if "alt" not in img]
    if missing_alt:
        result.add("error", "images_missing_alt", f"{len(missing_alt)} images; first: {missing_alt[0]}")
    missing_dimensions = [
        img.get("src", "<inline>")
        for img in parser.images
        if img.get("src") and not (img.get("width") and img.get("height"))
    ]
    if missing_dimensions:
        result.add("warning", "images_missing_dimensions", f"{len(missing_dimensions)} images; first: {missing_dimensions[0]}")

    inaccessible_links = []
    for link in parser.links:
        text = compact("".join(link["text"]))
        if link.get("href") and not (text or link.get("aria") or link.get("title")):
            inaccessible_links.append(link.get("href", ""))
    if inaccessible_links:
        result.add("error", "links_without_name", f"{len(inaccessible_links)} links; first: {inaccessible_links[0]}")

    inaccessible_buttons = []
    for button in parser.buttons:
        text = compact("".join(button["text"]))
        if not (text or button.get("aria") or button.get("title")):
            inaccessible_buttons.append("button")
    if inaccessible_buttons:
        result.add("error", "buttons_without_name", f"{len(inaccessible_buttons)} buttons")

    unlabeled_fields = []
    ignored_types = {"hidden", "submit", "button", "reset", "image"}
    for field_item in parser.fields:
        if field_item.get("type", "text").lower() in ignored_types:
            continue
        field_id = field_item.get("id", "")
        labeled = bool(
            field_item.get("nested_label")
            or (field_id and field_id in parser.labels_for)
            or field_item.get("aria-label")
            or field_item.get("aria-labelledby")
        )
        if not labeled:
            unlabeled_fields.append(field_item.get("name") or field_id or field_item.get("tag", "field"))
    if unlabeled_fields:
        result.add("error", "unlabeled_form_fields", f"{len(unlabeled_fields)} fields; first: {unlabeled_fields[0]}")

    if not meta_value(parser, "property", "og:title"):
        result.add("warning", "missing_og_title", "No og:title found")
    if not meta_value(parser, "property", "og:description"):
        result.add("warning", "missing_og_description", "No og:description found")
    if not meta_value(parser, "property", "og:image"):
        result.add("warning", "missing_og_image", "No og:image found")

    for index, block in enumerate(parser.jsonld_blocks, start=1):
        if not block:
            result.add("error", "empty_jsonld", f"JSON-LD block {index} is empty")
            continue
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            result.add("error", "invalid_jsonld", f"Block {index}: line {exc.lineno}, column {exc.colno}: {exc.msg}")

    if elapsed > 2500:
        result.add("warning", "slow_html_response", f"HTML response took {elapsed} ms")
    return result


def fetch_sitemap(sitemap_url: str) -> tuple[list[str], list[str]]:
    status, _, _, body, _, error = request(sitemap_url)
    if status != 200:
        raise RuntimeError(f"Sitemap returned {status}: {error}")
    root = ET.fromstring(body)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = [compact(node.text or "") for node in root.findall(f".//{namespace}loc")]
    duplicates = sorted(key for key, count in Counter(urls).items() if count > 1)
    return urls, duplicates


def resource_status(url: str) -> dict[str, Any]:
    status, final_url, headers, _, elapsed, error = request(url, method="HEAD")
    if status in {0, 405, 501}:
        status, final_url, headers, _, elapsed, error = request(url, method="GET")
    return {
        "url": url,
        "status": status,
        "final_url": final_url,
        "content_type": headers.get("Content-Type", ""),
        "elapsed_ms": elapsed,
        "error": error,
    }


def add_cross_page_checks(pages: list[PageResult]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for field_name, code in (("title", "duplicate_title"), ("description", "duplicate_description"), ("canonical", "duplicate_canonical")):
        grouped: dict[str, list[str]] = defaultdict(list)
        for page in pages:
            value = compact(getattr(page, field_name, ""))
            if value:
                grouped[value].append(page.requested_url)
        for value, urls in grouped.items():
            if len(urls) > 1:
                issues.append(
                    {
                        "severity": "error" if field_name in {"title", "canonical"} else "warning",
                        "code": code,
                        "detail": f"{len(urls)} pages share {value[:110]}",
                        "urls": urls,
                    }
                )
    return issues


def run(args: argparse.Namespace) -> dict[str, Any]:
    urls, sitemap_duplicates = fetch_sitemap(args.sitemap)
    started = time.monotonic()
    pages: list[PageResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {pool.submit(audit_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_map):
            try:
                pages.append(future.result())
            except Exception as exc:
                failed = PageResult(requested_url=future_map[future])
                failed.add("error", "audit_crash", f"{type(exc).__name__}: {exc}")
                pages.append(failed)
    pages.sort(key=lambda item: item.requested_url)

    known_pages = {comparable_url(page.final_url or page.requested_url): page for page in pages if page.status == 200}
    internal_targets: dict[str, set[str]] = defaultdict(set)
    asset_targets: dict[str, set[str]] = defaultdict(set)
    fragment_refs: set[tuple[str, str, str]] = set()
    mixed_content: list[dict[str, str]] = []

    for page in pages:
        base = page.final_url or page.requested_url
        for link in page.links:
            resolved = resolve_url(base, link.get("href", ""))
            if not resolved:
                continue
            parsed = urllib.parse.urlsplit(resolved)
            if parsed.scheme == "http" and parsed.hostname in INTERNAL_HOSTS:
                mixed_content.append({"source": page.requested_url, "target": resolved})
            if parsed.hostname in INTERNAL_HOSTS:
                target = urllib.parse.urlunsplit(("https", "lofts.studio", parsed.path or "/", parsed.query, ""))
                internal_targets[target].add(page.requested_url)
                if parsed.fragment:
                    fragment_refs.add((page.requested_url, target, urllib.parse.unquote(parsed.fragment)))
        for _, value in page.assets:
            resolved = resolve_url(base, value)
            if not resolved:
                continue
            parsed = urllib.parse.urlsplit(resolved)
            if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost"}:
                mixed_content.append({"source": page.requested_url, "target": resolved})
            if parsed.hostname in INTERNAL_HOSTS:
                target = urllib.parse.urlunsplit(("https", "lofts.studio", parsed.path or "/", parsed.query, ""))
                asset_targets[target].add(page.requested_url)

    checks: dict[str, dict[str, Any]] = {}
    resources_to_check = sorted(set(internal_targets).union(asset_targets))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {pool.submit(resource_status, url): url for url in resources_to_check}
        for future in concurrent.futures.as_completed(future_map):
            checks[future_map[future]] = future.result()

    broken_links = []
    redirected_links = []
    for url, sources in internal_targets.items():
        checked = checks[url]
        if checked["status"] >= 400 or checked["status"] == 0:
            broken_links.append({"target": url, "status": checked["status"], "sources": sorted(sources)})
        elif comparable_url(url) != comparable_url(checked["final_url"]):
            redirected_links.append({"target": url, "final_url": checked["final_url"], "sources": sorted(sources)})

    broken_assets = []
    for url, sources in asset_targets.items():
        checked = checks[url]
        if checked["status"] >= 400 or checked["status"] == 0:
            broken_assets.append({"target": url, "status": checked["status"], "sources": sorted(sources)})

    broken_fragments = []
    for source, target, fragment in fragment_refs:
        page = known_pages.get(comparable_url(target))
        if page and fragment not in page.ids:
            broken_fragments.append({"source": source, "target": target, "fragment": fragment})

    security_headers = {}
    root_page = known_pages.get("https://lofts.studio/")
    expected_headers = [
        "strict-transport-security",
        "x-content-type-options",
        "referrer-policy",
        "permissions-policy",
        "x-frame-options",
    ]
    if root_page:
        security_headers = {key: root_page.headers.get(key, "") for key in expected_headers}

    page_issues = [dict(issue, url=page.requested_url) for page in pages for issue in page.issues]
    cross_page = add_cross_page_checks(pages)
    all_issue_codes = Counter(issue["code"] for issue in page_issues)
    all_severities = Counter(issue["severity"] for issue in page_issues)
    all_severities["error"] += len(broken_links) + len(broken_assets) + len(broken_fragments) + len(sitemap_duplicates)
    all_severities["warning"] += len(redirected_links) + len(mixed_content) + len(cross_page)

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sitemap": args.sitemap,
        "duration_seconds": round(time.monotonic() - started, 2),
        "summary": {
            "sitemap_urls": len(urls),
            "pages_200": sum(page.status == 200 for page in pages),
            "page_errors": all_severities["error"],
            "page_warnings": all_severities["warning"],
            "broken_internal_links": len(broken_links),
            "redirected_internal_links": len(redirected_links),
            "broken_assets": len(broken_assets),
            "broken_fragments": len(broken_fragments),
            "mixed_content": len(mixed_content),
            "sitemap_duplicates": len(sitemap_duplicates),
        },
        "issue_counts": dict(all_issue_codes.most_common()),
        "sitemap_duplicates": sitemap_duplicates,
        "page_issues": page_issues,
        "cross_page_issues": cross_page,
        "broken_internal_links": broken_links,
        "redirected_internal_links": redirected_links,
        "broken_assets": broken_assets,
        "broken_fragments": broken_fragments,
        "mixed_content": mixed_content,
        "security_headers": security_headers,
        "pages": [
            {
                "requested_url": page.requested_url,
                "final_url": page.final_url,
                "status": page.status,
                "elapsed_ms": page.elapsed_ms,
                "title": page.title,
                "description": page.description,
                "canonical": page.canonical,
                "h1": page.h1,
            }
            for page in pages
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sitemap", default="https://lofts.studio/sitemap.xml")
    parser.add_argument("--output", default="qa-report.json")
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()
    report = run(args)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
    print(json.dumps(report["summary"], indent=2))
    print("Issue counts:")
    for code, count in report["issue_counts"].items():
        print(f"  {code}: {count}")
    print(f"Report: {args.output}")
    return 1 if report["summary"]["page_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
