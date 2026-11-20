#!/usr/bin/env python3
"""draw.py -- build-time renderer for the news-image-20261120 entry.

Draws a one-page newspaper front page, "The World Today", dated
FRIDAY, 20 NOVEMBER 2026, on a 1024x1024 canvas with Pillow and
saves it as preview.png beside this file. Every story on the page
comes from the verified headlines recorded in NOTES.md; nothing
is fetched at draw time and the output is deterministic.

Layout discipline: each text block is measured in pixels before it
is drawn and asserted to fit inside the page margins, so a wording
change that would overflow fails loudly here instead of silently
clipping on the printed page.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "preview.png")

PAGE = 1024
MARGIN = 36
CONTENT_W = PAGE - 2 * MARGIN
BOTTOM_LIMIT = PAGE - MARGIN

PAPER = (250, 247, 239)
INK = (24, 21, 17)
FADED = (96, 88, 74)
ACCENT = (146, 32, 24)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap, measured in pixels. Returns a list of lines,
    each guaranteed no wider than max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            assert cur, "single word wider than %d px: %r" % (max_w, word)
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, fill, leading, max_w):
    """Wrap and draw a paragraph at (x, y); return the y just below it."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, y, text, fnt, fill):
    """Draw one centered line; return the y just below it."""
    w = draw.textlength(text, font=fnt)
    assert w <= CONTENT_W, "centered line too wide: %r" % text
    draw.text(((PAGE - w) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size + 4


def rule(draw, y, weight=2):
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=weight)
    return y + weight


def burst(draw, cx, cy, r, seed):
    """One explosion: layered fireball discs, a hot core, and sparks."""
    for frac, col in ((1.0, (203, 78, 28)), (0.66, (242, 141, 42)),
                      (0.38, (255, 209, 110))):
        rad = max(3, int(r * frac))
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 246, 208))
    rng = random.Random(seed)
    for k in range(12):
        ang = 2 * math.pi * k / 12 + rng.uniform(-0.15, 0.15)
        ln = r * rng.uniform(1.2, 1.7)
        draw.line([(cx, cy), (cx + ln * math.cos(ang),
                              cy + ln * math.sin(ang))],
                  fill=(242, 141, 42), width=2)


def draw_kyiv_panel(draw, x0, y0, w, h):
    """Night skyline under fire, drawn inside the box (x0, y0, w, h):
    gradient sky, stars, a crescent moon, silhouetted apartment
    blocks with lit windows, missile streaks and three bursts."""
    sky_top, sky_bot = (14, 20, 44), (56, 41, 57)
    for i in range(h):
        t = i / max(h - 1, 1)
        col = tuple(int(sky_top[c] + (sky_bot[c] - sky_top[c]) * t)
                    for c in range(3))
        draw.line([(x0, y0 + i), (x0 + w, y0 + i)], fill=col)

    rng = random.Random(20261120)
    for _ in range(70):
        sx = x0 + rng.randrange(4, w - 4)
        sy = y0 + rng.randrange(4, int(h * 0.45))
        draw.point((sx, sy), fill=(208, 214, 234))

    mx, my, mr = x0 + w - 84, y0 + 32, 16
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(228, 226, 206))
    draw.ellipse([mx - mr + 12, my - mr - 5, mx + mr + 12, my + mr - 5],
                 fill=sky_top)

    ground = y0 + h
    bx = x0 + 6
    while bx < x0 + w - 30:
        bw = rng.randrange(38, 74)
        bh = rng.randrange(int(h * 0.30), int(h * 0.60))
        draw.rectangle([bx, ground - bh, bx + bw, ground], fill=(9, 10, 17))
        for wy in range(ground - bh + 8, ground - 10, 13):
            for wx in range(bx + 6, bx + bw - 6, 11):
                if rng.random() < 0.42:
                    draw.rectangle([wx, wy, wx + 4, wy + 6],
                                   fill=(240, 190, 92))
        bx += bw + rng.randrange(4, 14)

    for sx, sy, ex, ey in ((110, 18, 292, 64), (420, 6, 552, 52),
                           (688, 30, 788, 60)):
        draw.line([(x0 + sx, y0 + sy), (x0 + ex, y0 + ey)],
                  fill=(255, 214, 140), width=3)
        draw.ellipse([x0 + ex - 4, y0 + ey - 4, x0 + ex + 4, y0 + ey + 4],
                     fill=(255, 238, 196))

    burst(draw, x0 + 300, y0 + 70, 22, seed=11)
    burst(draw, x0 + 560, y0 + 58, 18, seed=23)
    burst(draw, x0 + 796, y0 + 66, 20, seed=37)

    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=INK, width=2)


LEAD_HEADLINE = "Russia Fires Ballistic Missiles at Kyiv in Overnight Barrage"
LEAD_BODY = (
    "Russian ballistic missiles slammed into the capital overnight, "
    "explosions rolling across the city from about 1:25 a.m. and fires "
    "breaking out in several districts. A residential building burned "
    "in Obolonskyi; officials reported no casualties in the first hours."
)

SECONDARY = [
    ("Houthis Claim Strikes on Saudi Targets; Riyadh Tower Damaged",
     "Houthi forces said they struck four Saudi targets, Riyadh airport "
     "among them. The PIF Tower, the capital's tallest building, lost "
     "windows across seven floors on Thursday; no injuries were reported."),
    ("Anthropic's Record IPO Closes Up 17% at $97.17",
     "The listing raised $81.3 billion, the largest IPO on record, as "
     "the first standalone AI lab reached the market. Shares priced at "
     "$83 opened up 34% before settling 17% higher at the close."),
    ("White House Fires Cyber Chief After Week of Outages",
     "National Cyber Director Sean Cairncross was dismissed after a "
     "week of technology failures across federal systems. Pentagon CIO "
     "Kirsten Davies takes over in an acting capacity."),
    ("Europe Says It Is Ready for Talks With Russia",
     "European allies presented a united position and said they are "
     "ready to negotiate with Moscow. President Putin answered by "
     "inviting European leaders to talks in the Russian capital."),
]

ALSO_TODAY = (
    "Genoa airport halts flights after drones spotted overhead  \u2022  "
    "Two tankers hit naval mines in the Strait of Hormuz  \u2022  "
    "COP31 draft text drops fossil-fuel phase-out"
)


def draw_front_page():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    y = MARGIN

    y = centered(draw, y, "GLOBAL NEWS, DRAWN FRESH EVERY MORNING",
                 font(SANS_BOLD, 15), FADED)
    y = centered(draw, y + 2, "The World Today", font(SERIF_BOLD, 78), INK)

    date_f = font(SANS_BOLD, 16)
    draw.text((MARGIN, y + 6), "FRIDAY, 20 NOVEMBER 2026", font=date_f,
              fill=INK)
    tag = "ONE PAGE \u2014 EVERY STORY THAT MATTERS"
    draw.text((PAGE - MARGIN - draw.textlength(tag, font=date_f), y + 6),
              tag, font=date_f, fill=INK)
    y = rule(draw, y + 28, weight=3)
    y = rule(draw, y + 3, weight=1)

    y += 10
    draw.text((MARGIN, y), "KYIV \u2014 OVERNIGHT ATTACK",
              font=font(SANS_BOLD, 17), fill=ACCENT)
    y += 22
    y = block(draw, MARGIN, y, LEAD_HEADLINE, font(SERIF_BOLD, 44), INK,
              leading=52, max_w=CONTENT_W)
    y = block(draw, MARGIN, y + 4, LEAD_BODY, font(SANS, 19), INK,
              leading=24, max_w=CONTENT_W)

    y += 10
    panel_h = 128
    draw_kyiv_panel(draw, MARGIN, y, CONTENT_W, panel_h)
    y += panel_h + 5
    draw.text((MARGIN, y), "Kyiv, Ukraine \u2014 the capital's skyline "
              "during the overnight barrage.",
              font=font(SERIF_ITALIC, 15), fill=FADED)
    y += 21
    assert y < 640, "top half overran: y=%d" % y

    y = rule(draw, y + 4, weight=2) + 8
    cell_w = (CONTENT_W - 24) // 2
    head_f, body_f = font(SERIF_BOLD, 23), font(SANS, 17)
    for row in range(2):
        heights = []
        for col in range(2):
            headline, body = SECONDARY[row * 2 + col]
            x = MARGIN + col * (cell_w + 24)
            hy = block(draw, x, y, headline, head_f, INK, leading=27,
                       max_w=cell_w)
            by = block(draw, x, hy + 3, body, body_f, INK, leading=21,
                       max_w=cell_w)
            heights.append(by - y)
        y += max(heights) + 8
    assert y < 890, "story grid overran: y=%d" % y

    draw.text((MARGIN, y), "ALSO TODAY", font=font(SANS_BOLD, 15),
              fill=ACCENT)
    y += 21
    band_f = font(SANS_BOLD, 15)
    band_lines = wrap(draw, ALSO_TODAY, band_f, CONTENT_W - 28)
    band_h = len(band_lines) * 20 + 12
    draw.rectangle([MARGIN, y, PAGE - MARGIN, y + band_h], fill=INK)
    for i, line in enumerate(band_lines):
        lw = draw.textlength(line, font=band_f)
        draw.text(((PAGE - lw) / 2, y + 6 + i * 20), line, font=band_f,
                  fill=PAPER)
    y += band_h + 10

    y = rule(draw, y, weight=1) + 6
    y = centered(draw, y, "Sources: Reuters \u2022 WSJ \u2022 Le Monde "
                 "\u2022 CNN \u2022 wire reports \u2014 compiled "
                 "20 November 2026", font(SANS, 13), FADED)
    assert y <= BOTTOM_LIMIT, "page overran: y=%d > %d" % (y, BOTTOM_LIMIT)
    return img


def main():
    img = draw_front_page()
    img.save(OUT_PATH, format="PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    assert size <= 1_048_576, "preview.png too large: %d bytes" % size
    print("wrote %s (%d bytes)" % (OUT_PATH, size))


if __name__ == "__main__":
    main()
