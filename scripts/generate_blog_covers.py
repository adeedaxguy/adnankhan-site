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


CREAM_LT = (250, 247, 241)      # lighter cream for motif strokes on dark panel
ACCENT_LT = (216, 123, 85)      # warm accent that reads on the dark panel


def draw_motif(d, key, cx, cy):
    """Draw a bold, centred geometric motif on the dark right panel.
    Colours are bright (accent + cream) so they read on ink."""
    import math
    A  = ACCENT_LT
    C  = CREAM_LT
    DIM = (74, 62, 52)          # faint warm-grey for depth rings

    # depth rings behind everything
    for r in (190, 150):
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=DIM, width=2)

    if key == "ai":
        nodes = [(cx-70,cy-90),(cx+60,cy-110),(cx+105,cy+10),(cx-10,cy+30),
                 (cx+70,cy+115),(cx-95,cy+70),(cx+120,cy-70)]
        for i,(x,y) in enumerate(nodes):
            for x2,y2 in nodes[i+1:]:
                if abs(x-x2)+abs(y-y2) < 230:
                    d.line([(x,y),(x2,y2)], fill=DIM, width=2)
        for x,y in nodes:
            d.ellipse([x-15,y-15,x+15,y+15], fill=A)
            d.ellipse([x-22,y-22,x+22,y+22], outline=C, width=2)
    elif key == "seo":
        for i,bh in enumerate([70,120,175,235]):
            x = cx-110 + i*56
            d.rounded_rectangle([x, cy+80-bh, x+38, cy+80], radius=7, fill=DIM)
        r = 96
        mx, my = cx+10, cy-10
        d.ellipse([mx-r,my-r,mx+r,my+r], outline=A, width=11)
        d.line([(mx+r*0.7,my+r*0.7),(mx+r*1.5,my+r*1.5)], fill=A, width=13)
    elif key == "speed":
        bbox = [cx-130,cy-130,cx+130,cy+130]
        d.arc(bbox, start=140, end=400, fill=DIM, width=20)
        d.arc(bbox, start=140, end=255, fill=A, width=20)
        ang = math.radians(255)
        d.line([(cx,cy),(cx+105*math.cos(ang),cy+105*math.sin(ang))], fill=C, width=9)
        d.ellipse([cx-14,cy-14,cx+14,cy+14], fill=A)
    elif key in ("shopify","woo"):
        x0,y0,x1,y1 = cx-105, cy-80, cx+105, cy+120
        d.rounded_rectangle([x0,y0,x1,y1], radius=20, outline=A, width=9)
        d.arc([x0+58,y0-58,x1-58,y0+58], start=180, end=360, fill=A, width=9)
        d.ellipse([cx-7,cy+8,cx+7,cy+22], fill=C)
    elif key == "apps":
        d.rounded_rectangle([cx-115,cy-115,cx+115,cy+115], radius=18, outline=A, width=7)
        d.line([(cx-115,cy-68),(cx+115,cy-68)], fill=A, width=5)
        for i,xp in enumerate((-90,-74,-58)):
            d.ellipse([cx+xp-4,cy-96,cx+xp+4,cy-88], fill=C)
        bf = font(MONO_BOLD, 90)
        tw = d.textlength("</>", font=bf)
        d.text((cx-tw/2, cy-30), "</>", font=bf, fill=C)
    elif key == "migration":
        d.rounded_rectangle([cx-130,cy-90,cx-10,cy+60], radius=16, outline=A, width=7)
        d.rounded_rectangle([cx+10,cy-40,cx+130,cy+110], radius=16, fill=(58,39,27), outline=A, width=7)
        d.line([(cx-30,cy+10),(cx+40,cy+10)], fill=C, width=9)
        d.polygon([(cx+30,cy-4),(cx+58,cy+10),(cx+30,cy+24)], fill=C)
    else:
        for i,r in enumerate((50,95,140)):
            d.ellipse([cx-r,cy-r,cx+r,cy+r], outline=A if i==1 else DIM, width=5)


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
    for size in range(52, 30, -2):
        fnt = font(SERIF, size)
        lines = wrap_title(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size
    fnt = font(SERIF, 30)
    return fnt, wrap_title(draw, text, fnt, max_w)[:max_lines], 30


def render(post):
    slug, title, cat = post["slug"], post["title"], post["category"]
    key = cat_key(cat)

    PANEL_X = 750                # x where the dark panel begins

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # dark accent panel on the right
    d.rectangle([PANEL_X, 0, W, H], fill=INK)
    # thin accent seam between cream + panel
    d.rectangle([PANEL_X-4, 0, PANEL_X, H], fill=ACCENT)

    # bold centred motif on the panel
    draw_motif(d, key, cx=(PANEL_X + W)//2 + 6, cy=H//2)

    MX = 72                      # left text margin (cream side)

    # kicker: accent rule + category (mono, upper)
    ky = 96
    d.line([(MX, ky+11), (MX+40, ky+11)], fill=ACCENT, width=4)
    d.text((MX+54, ky), cat.upper(), font=font(MONO, 22), fill=ACCENT)

    # title (serif, ink), wrapped & auto-sized to the cream column
    col_w = PANEL_X - MX - 44
    fnt, lines, size = fit_title(d, title, max_w=col_w, max_lines=4)
    lh = int(size * 1.2)
    ty = 168
    for ln in lines:
        d.text((MX, ty), ln, font=fnt, fill=INK)
        ty += lh

    # wordmark bottom-left
    wm_y = H - 66
    d.line([(MX, wm_y-18), (MX+col_w, wm_y-18)], fill=LINE, width=1)
    d.text((MX, wm_y), "Lofts", font=font(SERIF, 26), fill=INK)
    lw = d.textlength("Lofts", font=font(SERIF, 26))
    d.text((MX+lw+7, wm_y+6), "studio", font=font(MONO, 19), fill=ACCENT)

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
