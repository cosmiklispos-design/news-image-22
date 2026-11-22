#!/usr/bin/env python3
"""Draw the news-image-20261122 front page: a newspaper-style summary of
Sunday 22 November 2026, rendered to entry.png (1024x1024) with PIL only.
Run:  python3 build/draw_poster.py
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 30  # margin
BG = (248, 244, 233)
INK = (20, 20, 20)
GREY = (90, 86, 76)
RED = (163, 22, 33)
TEAL = (15, 94, 110)
BLUE = (28, 78, 128)
PANEL = (220, 235, 242)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill=INK, leading=None, max_lines=None):
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    f_mast = font(SERIF, 56)
    title = "THE DAILY GLOBE"
    d.text(((W - d.textlength(title, font=f_mast)) / 2, 22), title,
           font=f_mast, fill=INK)
    f_date = font(SANS_B, 16)
    date = "SUNDAY, 22 NOVEMBER 2026  ·  THE WORLD'S NEWS IN ONE PAGE"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 96), date,
           font=f_date, fill=RED)
    d.rectangle([M, 122, W - M, 125], fill=INK)
    d.rectangle([M, 129, W - M, 130], fill=INK)

    # ---- lead story: COP31 ----
    y = 144
    f_kick = font(SANS_B, 15)
    d.text((M, y), "CLIMATE  ·  ANTALYA", font=f_kick, fill=RED)
    y += 26
    f_lead = font(SERIF, 30)
    y = draw_wrapped(d, M, y, "COP31 nears a deal after two days of overtime",
                     f_lead, 620, leading=36, max_lines=2)
    y += 6
    f_deck = font(SANS, 17)
    y = draw_wrapped(
        d, M, y,
        "A new package was put to nearly 200 nations in the early hours "
        "of Sunday; delegates reconvene in the morning to approve it. "
        "Fossil-fuel wording and aid for poorer nations were the last "
        "sticking points.",
        f_deck, 620, leading=22, max_lines=5)

    # lead illustration: globe panel
    px0, py0, px1, py1 = 682, 144, W - M, 372
    d.rectangle([px0, py0, px1, py1], fill=PANEL, outline=TEAL, width=2)
    cx, cy, r = (px0 + px1) // 2, 232, 68
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(58, 140, 190),
              outline=INK, width=2)
    # land, clipped to the globe disc
    land = Image.new("L", (2 * r, 2 * r), 0)
    dl = ImageDraw.Draw(land)
    dl.ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    layer = Image.new("RGB", (2 * r, 2 * r), (58, 140, 190))
    dg = ImageDraw.Draw(layer)
    dg.ellipse([16, 14, 62, 48], fill=(96, 176, 96))
    dg.ellipse([70, 60, 118, 100], fill=(96, 176, 96))
    dg.ellipse([86, 10, 122, 40], fill=(96, 176, 96))
    img.paste(layer, (cx - r, cy - r), land)
    for k in (-34, 0, 34):  # meridians
        d.arc([cx - r + abs(k), cy - r, cx + r - abs(k), cy + r],
              90, 270, fill=(255, 255, 255), width=2)
        d.arc([cx - r + abs(k), cy - r, cx + r - abs(k), cy + r],
              270, 90, fill=(255, 255, 255), width=2)
    d.arc([cx - r, cy - 26, cx + r, cy + 26], 0, 360,
          fill=(255, 255, 255), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    f_cap = font(SANS_B, 16)
    cap = "COP31  ·  ANTALYA"
    d.text(((px0 + px1 - d.textlength(cap, font=f_cap)) / 2, 312), cap,
           font=f_cap, fill=TEAL)
    f_cap2 = font(SANS, 13)
    cap2 = "Nearly 200 nations weigh a final text"
    d.text(((px0 + px1 - d.textlength(cap2, font=f_cap2)) / 2, 338), cap2,
           font=f_cap2, fill=GREY)

    d.rectangle([M, 384, W - M, 385], fill=INK)

    # ---- 8 more stories, 2 columns x 4 rows ----
    stories = [
        ("THE GULF", RED,
         "Iran strikes Bahrain; two tankers hit in Hormuz",
         "Bahrain says an Iranian attack set a civilian industrial site "
         "ablaze on Saturday; two tankers were hit in the Strait of "
         "Hormuz. Tehran said it struck US bases."),
        ("MEXICO", RED,
         "\u2018El Chapo Isidro\u2019 captured; 11 killed in Sinaloa raid",
         "Troops seized FBI most-wanted cartel boss Fausto Isidro Meza "
         "Flores in Guasave on Friday night; four soldiers and seven "
         "gunmen died."),
        ("UKRAINE", RED,
         "Russian \u2018triple-tap\u2019 strike kills boy, 7, and paramedic",
         "Missiles hit Kryvyi Rih, Zelenskyy\u2019s hometown, on Friday "
         "night, then struck rescuers; 60 wounded, six of them children."),
        ("RIYADH", RED,
         "Three Houthi missiles at Riyadh intercepted",
         "The Saudi-led coalition shot down three ballistic missiles "
         "early on Saturday, days after a strike damaged Riyadh\u2019s "
         "tallest tower."),
        ("MARKETS", BLUE,
         "Wall Street slides into correction in AI sell-off",
         "The S&P 500 fell 3.7% and the Nasdaq 5.3% on Friday; Nvidia "
         "sank 14% as AI shares led the worst week since 2020."),
        ("TRADE", BLUE,
         "EU and Indonesia sign deal after 10 years of talks",
         "The pact, signed in Brussels on Saturday, scraps duties on "
         "about 98% of tariff lines; it takes effect in early 2027."),
        ("INDONESIA", BLUE,
         "Candy factory fire kills 3; 36 missing in Banten",
         "The blaze swept PT Fonusa Agung Mulia in Cikande on Saturday "
         "evening; rescuers searched the ruins on Sunday."),
        ("NIGERIA", BLUE,
         "Funeral boat capsizes; 24 dead in Bayelsa",
         "A crowded boat carrying mourners sank on Friday; 24 bodies "
         "were recovered and 24 people rescued."),
    ]
    col_w = 470
    xs = [M, M + col_w + 24]
    ys = [398, 546, 694, 842]
    f_ck = font(SANS_B, 13)
    f_h = font(SERIF, 19)
    f_b = font(SANS, 14)
    for i, (kick, color, head, deck) in enumerate(stories):
        x, y = xs[i % 2], ys[i // 2]
        d.rectangle([x, y, x + col_w, y + 1], fill=GREY)
        d.rectangle([x, y + 8, x + 10, y + 18], fill=color)
        d.text((x + 16, y + 6), kick, font=f_ck, fill=color)
        y += 28
        y = draw_wrapped(d, x, y, head, f_h, col_w, leading=23, max_lines=2)
        y += 3
        draw_wrapped(d, x, y, deck, f_b, col_w, leading=18, max_lines=3)

    # ---- footer ----
    f_f = font(SANS, 12)
    foot = ("Sources: Reuters  ·  Associated Press  ·  AFP  ·  Al Jazeera  —  "
            "Events of 20\u201322 Nov 2026, as reported on Sunday 22 November 2026")
    d.text(((W - d.textlength(foot, font=f_f)) / 2, 1002), foot,
           font=f_f, fill=GREY)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
