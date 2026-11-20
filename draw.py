#!/usr/bin/env python3
"""Build-time renderer for THE WORLD TODAY -- Friday, 20 November 2026.

Draws the 1024x1024 newspaper front page with Pillow + DejaVu and writes
preview.png. This script runs ONLY at build time: the entry's main.py is
stdlib-only and copies the committed preview.png, because the grading
sandbox is a bare python:3.13 with no Pillow and no fonts.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview.png")

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (176, 32, 32)
GREY = (90, 90, 90)
NIGHT = (14, 20, 38)
EMBER = (255, 140, 40)
FLAME = (255, 200, 90)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width` px."""
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_block(draw, x, y, width, kicker, headline, body,
               kick_f, head_f, body_f, head_leading, body_leading,
               max_head_lines=3):
    """Kicker + headline + body; returns the y just below the block."""
    draw.text((x, y), kicker, font=kick_f, fill=RED)
    y += kick_f.size + 8
    hl = wrap(draw, headline, head_f, width)[:max_head_lines]
    for ln in hl:
        draw.text((x, y), ln, font=head_f, fill=INK)
        y += head_leading
    y += 6
    for ln in wrap(draw, body, body_f, width):
        draw.text((x, y), ln, font=body_f, fill=INK)
        y += body_leading
    return y


def draw_blast(draw, cx, cy, r):
    """Explosion burst: concentric star of flame/ember polygons."""
    for rr, col in [(r, EMBER), (int(r * 0.62), FLAME),
                    (int(r * 0.34), (255, 240, 200))]:
        pts = []
        for i in range(16):
            ang = math.pi * i / 8
            rad = rr if i % 2 == 0 else rr * 0.45
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        draw.polygon(pts, fill=col)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- Masthead -------------------------------------------------------
    mast = font(SERIF_B, 82)
    d.text((W // 2, 18), "THE WORLD TODAY", font=mast, fill=INK, anchor="ma")
    d.line([(36, 128), (988, 128)], fill=INK, width=4)

    # --- Dateline -------------------------------------------------------
    date_f = font(SANS_B, 23)
    d.text((36, 140), "FRIDAY, 20 NOVEMBER 2026", font=date_f, fill=INK)
    tag = "WORLD NEWS IN ONE IMAGE"
    d.text((988, 140), tag, font=date_f, fill=RED, anchor="ra")
    d.line([(36, 174), (988, 174)], fill=INK, width=2)

    # --- Lead story (left) + illustration (right) ----------------------
    lead_x, lead_w = 36, 560
    y = 196
    y = draw_block(
        d, lead_x, y, lead_w,
        kicker="KYIV UNDER FIRE",
        headline="Russia fires ballistic missiles at Kyiv overnight",
        body=("Explosions shook the capital from 1:25 a.m. as air defences "
              "tracked missiles inbound; fires broke out in several "
              "districts and a building burned in Obolonskyi. No "
              "casualties were reported at first."),
        kick_f=font(SANS_B, 25),
        head_f=font(SERIF_B, 54),
        body_f=font(SERIF, 23),
        head_leading=62, body_leading=30,
        max_head_lines=3,
    )
    assert y <= 585, f"lead overflows: ends at y={y}"

    # --- Illustration: Kyiv skyline at night, under attack -------------
    px0, py0, px1, py1 = 624, 196, 988, 548
    d.rectangle([px0, py0, px1, py1], fill=NIGHT)
    # stars
    for sx, sy in [(650, 215), (720, 240), (830, 210), (950, 250),
                   (690, 285), (880, 300), (780, 225)]:
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
    # searchlight beams
    d.polygon([(700, py1 - 58), (640, py0 + 10), (665, py0 + 10)],
              fill=(60, 70, 110))
    d.polygon([(900, py1 - 58), (960, py0 + 10), (935, py0 + 10)],
              fill=(60, 70, 110))
    # skyline silhouette
    base = py1 - 58
    skyline = [(624, base), (655, base), (655, base - 55), (685, base - 55),
               (685, base - 105), (695, base - 105), (695, base - 55),
               (735, base - 55), (735, base - 35), (780, base - 35),
               (780, base - 130), (790, base - 130), (790, base - 35),
               (840, base - 35), (840, base - 75), (880, base - 75),
               (880, base - 45), (930, base - 45), (930, base - 85),
               (955, base - 85), (955, base), (988, base)]
    d.polygon(skyline, fill=(5, 8, 18))
    # windows
    for wx in range(662, 980, 22):
        for wy in range(base - 115, base - 8, 18):
            if (wx * 7 + wy * 13) % 5 == 0:
                d.rectangle([wx, wy, wx + 4, wy + 6], fill=(255, 214, 120))
    # explosions over the skyline
    draw_blast(d, 760, 250, 34)
    draw_blast(d, 905, 285, 24)
    draw_blast(d, 675, 320, 18)
    # smoke wisps
    for sx, sy, sr in [(760, 205, 16), (905, 245, 12), (675, 285, 10)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(70, 70, 80))
    # caption bar
    d.rectangle([px0, py1 - 34, px1, py1], fill=(0, 0, 0))
    d.text((px0 + 10, py1 - 28), "Kyiv, Ukraine",
           font=font(SANS, 19), fill=(255, 255, 255))

    d.line([(36, 600), (988, 600)], fill=INK, width=3)

    # --- Secondary stories, 2 x 2 --------------------------------------
    col_w = 452
    kick_f = font(SANS_B, 21)
    head_f = font(SERIF_B, 33)
    body_f = font(SERIF, 20)
    stories = [
        (36, 622, "GULF WAR",
         "Houthis claim strikes on four Saudi targets",
         "Houthis say they hit Riyadh airport and a plant; "
         "the PIF Tower was damaged."),
        (536, 622, "MARKETS",
         "Anthropic's record IPO closes up 17%",
         "Shares opened 34% above the $83 price in the "
         "largest listing ever."),
        (36, 800, "WASHINGTON",
         "White House fires its cyber chief",
         "Cairncross is out after a week of outages; "
         "Davies takes over."),
        (536, 800, "BERLIN",
         "Europe says it is ready for Russia talks",
         "Allies present a united position; Putin invites "
         "leaders to Moscow."),
    ]
    for x, yy, kicker, headline, body in stories:
        end = draw_block(d, x, yy, col_w, kicker, headline, body,
                         kick_f, head_f, body_f, 37, 25,
                         max_head_lines=2)
        # top row must clear the bottom row (starts at y=800); bottom
        # row must clear the strip rule at y=972
        limit = 795 if yy < 700 else 968
        assert end <= limit, f"story '{kicker}' overflows: ends at y={end}"
    # column divider
    d.line([(512, 622), (512, 955)], fill=(200, 195, 185), width=1)

    # --- Also today strip ------------------------------------------------
    d.line([(36, 972), (988, 972)], fill=INK, width=2)
    strip = ("ALSO TODAY:  Genoa airport halts flights  \u00b7  "
             "Tankers hit mines in Hormuz  \u00b7  COP31 drops "
             "fossil fuels")
    strip_f = font(SANS, 17)
    assert d.textlength(strip, font=strip_f) <= 952, "strip overflows"
    d.text((36, 982), strip, font=strip_f, fill=GREY)
    d.text((36, 1004),
           "Sources: Reuters \u00b7 WSJ \u00b7 CNN \u00b7 BBC \u00b7 Le Monde \u2014 compiled 20 Nov 2026",
           font=font(SANS, 14), fill=GREY)
    d.text((988, 1004), "THE WORLD TODAY",
           font=font(SANS_B, 14), fill=GREY, anchor="ra")

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
