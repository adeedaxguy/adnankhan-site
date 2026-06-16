#!/usr/bin/env python3
"""
Generate on-brand featured/cover images for every blog post.

Reads the post list straight from seo_engine.POSTS (single source of truth) and
renders a 1200x675 PNG per post into assets/blog/<slug>.png.

Design: Quiet-Luxury brand system — warm cream paper, ink serif headline, a
mono category kicker, a short accent rule, a category-specific geometric motif,
and the Lofts Studio wordmark. No hype, lots of air.

Run:  python3 scripts/generate_blog_covers.py
"""
import importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "blog"
W, H = 1200, 675

# ── Brand palette (light) ─────────────────────────────────────────────
CREAM       = (244, 240, 234)
INK         = (26, 22, 18)
MUTED       = (108, 98, 88)
LINE        = (217, 210, 196)
ACCENT      = (139, 58, 31)

# ── Fonts (system fonts on macOS) ─────────────────────────────────────
_SYSFONT = Path("/System/Library/Fonts/Supplemental")
_LIBFONT = Path("/Library/Fonts")

SERIF      = str(_SYSFONT / "Georgia Bold.ttf")
SERIF_REG  = str(_SYSFONT / "Georgia.ttf")
MONO       = str(_SYSFONT / "Courier New.ttf")
MONO_BOLD  = str(_SYSFONT / "Courier New Bold.ttf")

def font(name, size):
    return ImageFont.truetype(name, size)


# ── Category → accent tint + motif ────────────────────────────────────
def cat_key(cat):
    c = cat.lower()
    if "ai" in c or "automation" in c: return "ai"
    if "seo" in c: return "seo"
    if "speed" in c or "performance" in c: return "speed"
    if "woo" in c: return "woo"
    if "custom" in c or "app" in c: return "apps"
    if "migration" in c: return "migration"
    if "shopify" in c: return "shopify"
    return "default"


def rgba(c, a):
    return (c[0], c[1], c[2], a)


def draw_motif(ov, key):
    """Draw a large, low-opacity geometric motif on the right side (RGBA overlay)."""
    d = ImageDraw.Draw(ov)
    cx, cy = 970, 300          # motif centre, upper-right
    A   = rgba(ACCENT, 38)
    AS  = rgba(ACCENT, 22)
    LN  = rgba(ACCENT, 60)
    INKL = rgba(INK, 16)

    if key == "ai":
        # Neural / agent network: nodes connected by thin lines
        nodes = [(880,150),(1010,120),(1090,250),(960,300),(1040,400),(870,330),(1110,160)]
        for i,(x,y) in enumerate(nodes):
            for x2,y2 in nodes[i+1:]:
                if abs(x-x2)+abs(y-y2) < 230:
                    d.line([(x,y),(x2,y2)], fill=LN, width=2)
        for x,y in nodes:
            r = 16
            d.ellipse([x-r,y-r,x+r,y+r], fill=rgba(ACCENT,55))
            d.ellipse([x-r-7,y-r-7,x+r+7,y+r+7], outline=AS, width=2)
    elif key == "seo":
        # Magnifier over rising bars
        for i,bh in enumerate([60,110,160,220]):
            x = 880 + i*52
            d.rounded_rectangle([x, 360-bh, x+34, 360], radius=6, fill=rgba(ACCENT,28))
        r = 92
        d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=rgba(ACCENT,70), width=10)
        d.line([(cx+r*0.7,cy+r*0.7),(cx+r*1.5,cy+r*1.5)], fill=rgba(ACCENT,70), width=12)
    elif key == "speed":
        # Speed gauge arc + needle
        bbox = [cx-120,cy-120,cx+120,cy+120]
        d.arc(bbox, start=140, end=400, fill=rgba(ACCENT,30), width=18)
        d.arc(bbox, start=140, end=250, fill=rgba(ACCENT,75), width=18)
        import math
        ang = math.radians(250)
        d.line([(cx,cy),(cx+95*math.cos(ang),cy+95*math.sin(ang))], fill=rgba(ACCENT,80), width=8)
        d.ellipse([cx-12,cy-12,cx+12,cy+12], fill=rgba(ACCENT,80))
    elif key in ("shopify","woo"):
        # Shopping bag outline
        x0,y0,x1,y1 = 875, 215, 1075, 415
        d.rounded_rectangle([x0,y0,x1,y1], radius=18, outline=rgba(ACCENT,65), width=8)
        d.arc([x0+55,y0-55,x1-55,y0+55], start=180, end=360, fill=rgba(ACCENT,65), width=8)
        d.line([(x0+45,y0+5),(x0+45,y0-5)], fill=rgba(ACCENT,65), width=8)
        d.ellipse([cx-6,cy+5,cx+6,cy+17], fill=rgba(ACCENT,55))
    elif key == "apps":
        # Code brackets + window
        d.rounded_rectangle([885,190,1085,410], radius=16, outline=rgba(ACCENT,45), width=6)
        d.line([(885,235),(1085,235)], fill=rgba(ACCENT,45), width=4)
        for cxp in (915,927,939):
            d.ellipse([cxp-4,208,cxp+4,216], fill=rgba(ACCENT,55))
        d.text((930,270), "</>", font=font(MONO_BOLD,72), fill=rgba(ACCENT,70))
    elif key == "migration":
        # Two offset panels + arrow
        d.rounded_rectangle([860,210,1000,360], radius=14, outline=rgba(ACCENT,40), width=6)
        d.rounded_rectangle([965,250,1105,400], radius=14, fill=rgba(ACCENT,18), outline=rgba(ACCENT,55), width=6)
        d.line([(940,300),(1010,300)], fill=rgba(ACCENT,75), width=8)
        d.polygon([(1005,288),(1030,300),(1005,312)], fill=rgba(ACCENT,75))
    else:
        for i,r in enumerate((40,80,120,160)):
            d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=rgba(ACCENT, 60-i*10), width=4)

    # faint large ink ring behind, for depth
    d.ellipse([cx-205,cy-205,cx+205,cy+205], outline=INKL, width=2)


def wrap_title(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def fit_title(draw, text, max_w, max_lines):
    """Pick the largest serif size whose wrapped title fits within max_lines."""
    for size in range(74, 40, -2):
        fnt = font(SERIF, size)
        lines = wrap_title(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size
    fnt = font(SERIF, 42)
    return fnt, wrap_title(draw, text, fnt, max_w)[:max_lines], 42


def render(post):
    slug, title, cat = post["slug"], post["title"], post["category"]
    key = cat_key(cat)

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # subtle paper panel + frame
    d.rectangle([0, 0, W, H], fill=CREAM)
    d.rectangle([24, 24, W-24, H-24], outline=LINE, width=2)

    # motif (separate RGBA overlay so it sits softly under text)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_motif(ov, key)
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)

    MX = 80                      # left margin for text

    # category kicker: accent rule + label (mono, upper) — centred vertically
    kick_y = H // 2 - 20
    d.line([(MX, kick_y), (MX+40, kick_y)], fill=ACCENT, width=3)
    d.text((MX+56, kick_y - 11), cat.upper(), font=font(MONO, 22), fill=ACCENT)

    # footer rule
    fy = H - 80
    d.line([(MX, fy), (W-MX, fy)], fill=LINE, width=1)

    # wordmark bottom-left
    wm_y = H - 58
    d.text((MX, wm_y), "Lofts", font=font(SERIF, 26), fill=INK)
    lw = d.textlength("Lofts", font=font(SERIF, 26))
    d.text((MX+lw+7, wm_y+6), "studio", font=font(MONO, 19), fill=ACCENT)

    # bottom-right: domain (mono, muted)
    url = "lofts.studio"
    uw = d.textlength(url, font=font(MONO, 18))
    d.text((W-MX-uw, wm_y+5), url, font=font(MONO, 18), fill=MUTED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{slug}.png"
    img.save(out, "PNG", optimize=True)
    return out


def load_posts():
    """Read every published post from blog/posts.json (the single source of truth,
    which includes posts not authored through seo_engine.POSTS)."""
    import json
    data = json.loads((ROOT / "blog" / "posts.json").read_text())
    return [p for p in data["posts"] if p.get("published", True)]


def main():
    posts = load_posts()
    print(f"Rendering {len(posts)} blog covers → assets/blog/")
    for p in posts:
        out = render(p)
        print(f"  ✓ {out.relative_to(ROOT)}  ({p['category']})")
    print("Done.")


if __name__ == "__main__":
    main()
