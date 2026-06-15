#!/usr/bin/env python3
"""
make_og.py — generates the social share image (Open Graph / Twitter card).
1200x630 JPG/PNG, brand-styled. Rasterised with Pillow so Slack/Twitter/
Facebook/LinkedIn actually render it (they don't support SVG og:images).

Run: python3 scripts/make_og.py
Writes: assets/og.jpg  and  assets/og.png
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = 2                      # supersample for crisp text
W, H = 1200 * S, 630 * S

# Brand palette
INK      = (20, 18, 14)    # near-black warm
INK_SOFT = (30, 26, 21)
CREAM    = (244, 240, 234)
CREAM_MUTED = (181, 173, 159)
ACCENT   = (197, 96, 60)   # warm terracotta (slightly brightened for dark bg)
LINE     = (58, 50, 41)

def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

SERIF_IT = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
SANS = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
SANS_BOLD = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]

f_word   = font(SERIF_IT, 150 * S)
f_studio = font(SANS_BOLD, 40 * S)
f_tag    = font(SANS, 42 * S)
f_foot   = font(SANS, 23 * S)

img = Image.new("RGB", (W, H), INK)
d = ImageDraw.Draw(img)

# Subtle top-down gradient for depth
for y in range(H):
    t = y / H
    r = int(INK_SOFT[0] + (INK[0] - INK_SOFT[0]) * t)
    g = int(INK_SOFT[1] + (INK[1] - INK_SOFT[1]) * t)
    b = int(INK_SOFT[2] + (INK[2] - INK_SOFT[2]) * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# Thin inset frame
m = 40 * S
d.rectangle([m, m, W - m, H - m], outline=LINE, width=2 * S)

def text_w(s, fnt, tracking=0):
    w = d.textlength(s, font=fnt)
    if tracking:
        w += tracking * (len(s) - 1)
    return w

def draw_tracked(cx, y, s, fnt, fill, tracking):
    total = text_w(s, fnt, tracking)
    x = cx - total / 2
    for ch in s:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking

cx = W // 2

# 1) Wordmark "Lofts" (serif italic) + accent dot
word = "Lofts"
ww = d.textlength(word, font=f_word)
dot_r = 11 * S
gap = 26 * S
block_w = ww + gap + dot_r * 2
wx = cx - block_w / 2
wy = 150 * S
# ascent box for vertical metrics
bbox = d.textbbox((0, 0), word, font=f_word)
d.text((wx, wy), word, font=f_word, fill=CREAM)
# accent dot near baseline of the wordmark
dot_cx = wx + ww + gap + dot_r
dot_cy = wy + (bbox[3] - bbox[1]) * 0.86
d.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=ACCENT)

# 2) STUDIO (letterspaced caps)
sy = wy + (bbox[3] - bbox[1]) + 30 * S
draw_tracked(cx, sy, "S T U D I O", f_studio, CREAM_MUTED, 6 * S)

# 3) Tagline
ty = sy + 96 * S
tag = "Senior Web Engineering  ·  1,000+ Builds"
d.text((cx - d.textlength(tag, font=f_tag) / 2, ty), tag, font=f_tag, fill=CREAM)

# 4) Short accent rule
ry = ty + 86 * S
d.line([(cx - 46 * S, ry), (cx + 46 * S, ry)], fill=ACCENT, width=3 * S)

# 5) Footer credentials
fy = ry + 40 * S
draw_tracked(cx, fy, "MULTAN · DUBAI    —    TOP RATED ON UPWORK · 100% JSS",
             f_foot, CREAM_MUTED, 3 * S)

# Downscale for anti-aliasing
img = img.resize((1200, 630), Image.LANCZOS)
img.save(ROOT / "assets" / "og.jpg", "JPEG", quality=88, optimize=True)
img.save(ROOT / "assets" / "og.png", "PNG", optimize=True)
print("Wrote assets/og.jpg and assets/og.png (1200x630)")
