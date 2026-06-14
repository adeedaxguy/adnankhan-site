#!/usr/bin/env python3
"""
fetch_thumbnails.py — run this ON YOUR MAC (it needs internet; the cloud
build environment is firewalled so it can't fetch external sites).

For every published portfolio item that has no image, it:
  1. Verifies the site is actually LIVE and not a parked / expired / registrar
     placeholder (skips it with a warning if so — matching the "only live
     sites" rule).
  2. Downloads a real screenshot to assets/work/<slug>.jpg (permanent local
     file — no hot-linking, no spinner services).
  3. Sets the item's "image" path in portfolio/portfolio.json.

Then it reminds you to regenerate the detail pages.

Usage:
    python3 scripts/fetch_thumbnails.py            # only items missing a thumb
    python3 scripts/fetch_thumbnails.py --all      # refresh every item
    python3 scripts/fetch_thumbnails.py expedited ireliants   # specific slugs

After it runs:
    python3 scripts/generate_portfolio_pages.py
    git add -A && git commit -m "Portfolio thumbnails" && git push origin main
"""
import json, sys, time, subprocess, tempfile, os, pathlib, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "portfolio" / "portfolio.json"
WORK = ROOT / "assets" / "work"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

PARK_MARKERS = [
    "domain is for sale", "buy this domain", "is for sale", "parked free",
    "sedoparking", "hugedomains", "this domain may be for sale", "domain parking",
    "godaddy.com/forsale", "afternic", "future home of something quite cool",
    "account suspended", "default web page", "website coming soon", "under construction",
]


def curl(url, extra=None):
    cmd = ["curl", "-sL", "--max-time", "25", "-A", UA]
    if extra:
        cmd += extra
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True)


def is_live(url):
    """Return (ok, reason). ok=False means skip (dead/parked)."""
    head = subprocess.run(
        ["curl", "-sIL", "--max-time", "25", "-A", UA, "-o", "/dev/null",
         "-w", "%{http_code} %{url_effective}", url],
        capture_output=True, text=True,
    )
    parts = head.stdout.split()
    code = parts[0] if parts else "000"
    if code in ("000",):
        return False, "no response / DNS failure (likely expired)"
    if code.startswith("4") or code.startswith("5"):
        # some sites 403 bots but are live; fall through to body check
        pass
    body = curl(url).stdout.decode("utf-8", "ignore").lower()
    if not body.strip():
        return False, f"empty body (HTTP {code})"
    for m in PARK_MARKERS:
        if m in body:
            return False, f"parking/placeholder marker: '{m}'"
    # Shopify "opening soon" / password page
    if "shopify" in body and ("opening soon" in body or "this store is unavailable" in body):
        return False, "Shopify store locked / opening soon"
    return True, f"live (HTTP {code})"


def grab_screenshot(url, dest):
    """WordPress mShots, polled until a real (non-placeholder) image arrives."""
    shot = "https://s.wordpress.com/mshots/v1/" + urllib.parse.quote(url, safe="") + "?w=1280&h=960"
    for attempt in range(1, 15):
        r = curl(shot)
        data = r.stdout
        # mShots returns a tiny grey placeholder while generating; real shots are larger
        if data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n":
            if len(data) > 28000:  # bytes — real screenshot, not the spinner
                dest.write_bytes(data)
                return True
        time.sleep(4)
    return False


def main():
    args = [a for a in sys.argv[1:]]
    do_all = "--all" in args
    slugs = [a for a in args if not a.startswith("--")]
    d = json.loads(DATA.read_text())
    WORK.mkdir(parents=True, exist_ok=True)
    changed = 0
<<<<<<< ours
<<<<<<< ours
=======
    demoted = 0
>>>>>>> theirs
=======
    demoted = 0
>>>>>>> theirs
    for it in d["items"]:
        if not it.get("published"):
            continue
        if slugs and it["slug"] not in slugs:
            continue
        if it.get("image") and not do_all:
            continue
        url = it.get("url", "").strip()
        if not url:
            print(f"  ⊘ {it['slug']}: no URL, skipped")
            continue
        ok, reason = is_live(url)
        if not ok:
<<<<<<< ours
<<<<<<< ours
            print(f"  ✗ {it['slug']}: NOT live — {reason} (left without thumbnail)")
=======
=======
>>>>>>> theirs
            # Safety net: never leave a dead/parked project published & visible.
            it["published"] = False
            demoted += 1
            print(f"  ✗ {it['slug']}: NOT live — {reason} → set published=false")
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs
            continue
        dest = WORK / f"{it['slug']}.jpg"
        print(f"  … {it['slug']}: {reason} — capturing screenshot")
        if grab_screenshot(url, dest):
            it["image"] = f"/assets/work/{it['slug']}.jpg"
            changed += 1
            print(f"  ✓ {it['slug']}: saved {dest.relative_to(ROOT)}")
        else:
            print(f"  ! {it['slug']}: screenshot service didn't return a real image — retry later")
<<<<<<< ours
<<<<<<< ours
    if changed:
        d["lastUpdated"] = time.strftime("%Y-%m-%d")
        DATA.write_text(json.dumps(d, indent=2, ensure_ascii=True) + "\n")
        print(f"\nUpdated {changed} thumbnail(s) in portfolio.json.")
        print("Next: python3 scripts/generate_portfolio_pages.py")
    else:
        print("\nNo thumbnails changed.")
=======
=======
>>>>>>> theirs
    if changed or demoted:
        d["lastUpdated"] = time.strftime("%Y-%m-%d")
        DATA.write_text(json.dumps(d, indent=2, ensure_ascii=True) + "\n")
        print(f"\nUpdated {changed} thumbnail(s); demoted {demoted} dead/parked project(s).")
        print("Next: python3 scripts/generate_portfolio_pages.py")
    else:
        print("\nNo changes.")
<<<<<<< ours
>>>>>>> theirs
=======
>>>>>>> theirs


if __name__ == "__main__":
    main()
