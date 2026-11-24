"""Build-time renderer for the front page of THE WORLD TODAY,
Tuesday, 24 November 2026.

Draws a one-page broadsheet front page summing up the day's world
news and writes it to assets/final-page.png. The page is composed at
twice its final size with Pillow and then downscaled, which gives
the type and the press-style illustration panels a smoother, printed
finish. Pillow is used only here, on the build machine; the shipped
entry point (main.py) is pure standard library and simply copies the
committed image into place.

The day's running stories, as reported by Tuesday morning: three oil
tankers set ablaze by sea mines in the Strait of Hormuz; President
Zelenskyy's call for four-way talks after the Shenzhen trilateral
summit; Washington's blacklisting of Megaspeed in the Nvidia spy
scandal; the Banten candy-factory fire, whose toll rose to 24; and
Norway's supreme court voiding disputed oil licences as the fallout
from the COP31 collapse spread.

Layout, top to bottom: folio line and masthead, markets ticker,
"Inside today" strip, the Hormuz lead (one-line headline, deck, a
wide strait panel with caption and credit, two columns of report and
a pull-quote rail), a three-column row (Ukraine talks, the Nvidia
blacklist, the factory fire), a second row (Norway and the climate
fallout, the Pentagon's rebuke of Canada, a boxed Sport section), a
markets-at-a-glance and weather band, and a World in Brief strip.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersampling factor
W, H = 1024, 1024

PAPER = (243, 238, 226)
PAPER_DARK = (233, 226, 208)
INK = (26, 24, 20)
SOFT = (74, 69, 60)
FAINT = (120, 113, 99)
RED = (150, 30, 24)
NAVY = (30, 50, 74)
RULE = (43, 40, 35)

FONT_DIR = Path("/usr/share/fonts/truetype")
SERIF = str(FONT_DIR / "liberation" / "LiberationSerif-Regular.ttf")
SERIF_B = str(FONT_DIR / "liberation" / "LiberationSerif-Bold.ttf")
SERIF_I = str(FONT_DIR / "liberation" / "LiberationSerif-Italic.ttf")
SERIF_BI = str(FONT_DIR / "liberation" / "LiberationSerif-BoldItalic.ttf")
SANS = str(FONT_DIR / "liberation" / "LiberationSans-Regular.ttf")
SANS_B = str(FONT_DIR / "liberation" / "LiberationSans-Bold.ttf")
SANS_I = str(FONT_DIR / "liberation" / "LiberationSans-Italic.ttf")
DISPLAY = str(FONT_DIR / "noto" / "NotoSerifDisplay-Black.ttf")

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        try:
            _cache[key] = ImageFont.truetype(path, size * S)
        except OSError:
            _cache[key] = ImageFont.truetype(SERIF_B, size * S)
    return _cache[key]


img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img, "RGBA")


def X(v):
    return v * S


def rect(x, y, w, h, fill=None, outline=None, width=1):
    d.rectangle([X(x), X(y), X(x + w), X(y + h)],
                fill=fill, outline=outline, width=max(1, int(width * S)))


def line(x1, y1, x2, y2, fill=RULE, width=1):
    d.line([X(x1), X(y1), X(x2), X(y2)], fill=fill, width=max(1, int(width * S)))


def text(x, y, s, font, fill=INK, anchor="la"):
    d.text((X(x), X(y)), s, font=font, fill=fill, anchor=anchor)


def tw(s, font):
    return d.textlength(s, font=font) / S


def wrap(s, font, width):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(trial, font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def flow(x, y, s, font, width, lh, fill=INK, max_lines=None, align="left"):
    """Set a paragraph; return the y just below its last line."""
    lines = wrap(s, font, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        if align == "center":
            text(x + width / 2, y, ln, font, fill, anchor="ma")
        else:
            text(x, y, ln, font, fill)
        y += lh
    return y


def headline_fit(x_center, y, s, start_size, max_w):
    """Set a one-line headline, shrinking the face until it fits."""
    size = start_size
    while size > 12 and tw(s, F(SERIF_B, size)) > max_w:
        size -= 1
    text(x_center, y, s, F(SERIF_B, size), INK, anchor="ma")
    return size


def grain(x, y, w, h, seed, n=240, alpha=15):
    """A whisper of print grain over an illustration panel."""
    rng = random.Random(seed)
    for _ in range(n):
        px, py = x + rng.random() * w, y + rng.random() * h
        shade = rng.choice([(0, 0, 0), (255, 255, 255)])
        d.point((X(px), X(py)), fill=shade + (alpha,))


def panel(x, y, w, h):
    rect(x, y, w, h, fill=(210, 203, 186), outline=RULE, width=1)


def caption(x, y, w, s, credit):
    text(x, y, s, F(SANS_I, 9.5), SOFT)
    text(x + w, y, credit, F(SANS_I, 9.5), SOFT, anchor="ra")


def kicker(x, y, s, fill=RED):
    text(x, y, s, F(SANS_B, 10.5), fill)


# ---------------------------------------------------------------- panels

def tanker(x, base, scale, flame_h, smoke_seed):
    """One tanker silhouette riding at the waterline `base`: black
    hull, red deck line, a small superstructure, flames amidships and
    a drifting smoke plume."""
    w = 150 * scale
    d.polygon([(X(x), X(base)), (X(x + w * 0.92), X(base)),
               (X(x + w), X(base + 7 * scale)), (X(x + w * 0.86), X(base + 11 * scale)),
               (X(x + w * 0.10), X(base + 11 * scale))], fill=(28, 27, 29))
    rect(x + 2, base - 3.5 * scale, w * 0.90, 3.5 * scale, fill=(148, 50, 38))
    rect(x + w * 0.10, base - 12 * scale, 20 * scale, 8.5 * scale,
         fill=(224, 218, 204))
    rect(x + w * 0.14, base - 16 * scale, 4 * scale, 4 * scale, fill=(58, 56, 54))
    rng = random.Random(smoke_seed)
    for fx in (0.52, 0.60, 0.68):
        cx = x + w * fx
        fh = flame_h * (0.8 + 0.3 * rng.random())
        d.polygon([(X(cx - 4.5 * scale), X(base - 3 * scale)),
                   (X(cx), X(base - 3 * scale - fh)),
                   (X(cx + 4.5 * scale), X(base - 3 * scale))],
                  fill=(230, 116, 32))
        d.polygon([(X(cx - 2 * scale), X(base - 3 * scale)),
                   (X(cx), X(base - 3 * scale - fh * 0.55)),
                   (X(cx + 2 * scale), X(base - 3 * scale))],
                  fill=(246, 190, 70))
    for i in range(6):  # smoke, drifting right and thinning
        sx = x + w * 0.60 + i * 13 * scale
        sy = base - 16 * scale - flame_h - i * 3.5 * scale
        d.ellipse([X(sx), X(sy), X(sx + 26 * scale), X(sy + 11 * scale)],
                  fill=(88, 82, 76, 150 - i * 16))


def strait_panel(x, y, w, h):
    """The lead scene: three tankers ablaze in the strait at first
    light, a grey escort warship standing off to the right and the
    far shore a low line on the horizon."""
    panel(x, y, w, h)
    for i in range(6):  # dawn sky, smoke-grey paling to the horizon
        shade = (168 - i * 6, 156 - i * 5, 138 - i * 4)
        rect(x + 1, y + 1 + i * (h * 0.52) / 6, w - 2, (h * 0.52) / 6 + 1,
             fill=shade)
    rect(x + 1, y + h * 0.50, w - 2, 3, fill=(196, 188, 168))       # far shore
    rect(x + 1, y + h * 0.52, w - 2, h * 0.48 - 1, fill=(50, 72, 90))  # sea
    for i in range(9):  # broken light on the water
        lx = x + 24 + i * (w - 60) / 8
        line(lx, y + h * 0.86, lx + 26, y + h * 0.86,
             fill=(120, 142, 152, 120), width=1)
    tanker(x + w * 0.05, y + h * 0.60, 1.55, 30, 41)   # the big ship, near
    tanker(x + w * 0.52, y + h * 0.545, 0.78, 17, 42)  # second, further off
    tanker(x + w * 0.70, y + h * 0.565, 0.62, 13, 43)  # third, smaller still
    # the escort: a low grey warship at the right edge, bow to the scene
    wx, wy = x + w * 0.865, y + h * 0.60
    d.polygon([(X(wx), X(wy + 6)), (X(wx + w * 0.115), X(wy + 6)),
               (X(wx + w * 0.10), X(wy + 11)), (X(wx + 8), X(wy + 11))],
              fill=(96, 102, 110))
    rect(wx + 12, wy - 3, w * 0.055, 8, fill=(110, 116, 124))
    line(wx + 30, wy - 3, wx + 30, wy - 12, fill=(70, 76, 84), width=1.5)
    rect(wx + 24, wy - 14, 12, 3, fill=(70, 76, 84))
    text(x + 14, y + 8, "THE STRAIT OF HORMUZ", F(SANS_B, 12), (240, 234, 218))
    text(x + 14, y + 24, "Mine strikes reported Tuesday", F(SANS, 9.5),
         (214, 208, 192))
    grain(x, y, w, h, seed=97, n=320, alpha=11)
    rect(x, y, w, h, outline=RULE, width=1)


def chart_panel(x, y, w, h):
    """A dealing-room screen on a bad morning for chip shares."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 2, fill=(18, 26, 40))
    for gx in range(1, 6):
        line(x + gx * w / 6, y + 4, x + gx * w / 6, y + h - 4,
             fill=(52, 66, 88), width=1)
    for gy in range(1, 4):
        line(x + 4, y + gy * h / 4, x + w - 4, y + gy * h / 4,
             fill=(52, 66, 88), width=1)
    pts = [(0.04, 0.26), (0.20, 0.34), (0.36, 0.30), (0.52, 0.46),
           (0.68, 0.42), (0.84, 0.62), (0.97, 0.74)]
    xy = [(X(x + px * w), X(y + py * h)) for px, py in pts]
    d.line(xy, fill=(224, 84, 60), width=2 * S)
    for px, py in xy:
        d.ellipse([px - 2.5 * S, py - 2.5 * S, px + 2.5 * S, py + 2.5 * S],
                  fill=(240, 150, 60))
    text(x + 8, y + h - 19, "BRENT  $89.86  −2.9%", F(SANS_B, 12),
         (240, 190, 70))
    grain(x, y, w, h, seed=7, n=140, alpha=10)
    rect(x, y, w, h, outline=RULE, width=1)


def flags_panel(x, y, w, h):
    """The three flags at the Shenzhen trilateral summit."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 2, fill=(206, 198, 180))
    fw, fh, gap = (w - 32) / 3, h - 26, 8
    fx = x + 8
    for i in range(7):                                               # United States
        rect(fx, y + 6 + i * fh / 7, fw, fh / 7 + 1,
             fill=(168, 44, 48) if i % 2 == 0 else (238, 234, 224))
    rect(fx, y + 6, fw * 0.44, fh * 0.54, fill=(44, 54, 110))
    text(fx + fw / 2, y + h - 15, "USA", F(SANS_B, 9.5), INK, anchor="ma")
    fx += fw + gap
    for i, col in enumerate([(238, 234, 224), (52, 74, 140), (178, 40, 44)]):
        rect(fx, y + 6 + i * fh / 3, fw, fh / 3 + 1, fill=col)        # Russia
    text(fx + fw / 2, y + h - 15, "RUSSIA", F(SANS_B, 9.5), INK, anchor="ma")
    fx += fw + gap
    rect(fx, y + 6, fw, fh, fill=(186, 40, 40))                      # China
    for sx, sy, sr in ((9, 9, 3.5), (19, 6, 1.8), (22, 11, 1.8),
                       (19, 16, 1.8), (15, 19, 1.8)):
        d.ellipse([X(fx + sx - sr), X(y + 6 + sy - sr),
                   X(fx + sx + sr), X(y + 6 + sy + sr)], fill=(244, 200, 60))
    text(fx + fw / 2, y + h - 15, "CHINA", F(SANS_B, 9.5), INK, anchor="ma")
    grain(x, y, w, h, seed=3, n=120, alpha=10)
    rect(x, y, w, h, outline=RULE, width=1)


def factory_panel(x, y, w, h):
    """The gutted candy factory in Banten at night: a long shed with
    a collapsed roof section, fire crews' floodlights in front."""
    panel(x, y, w, h)
    rect(x + 1, y + 1, w - 2, h - 2, fill=(66, 66, 74))              # night
    rect(x + 1, y + h - 9, w - 2, 8, fill=(38, 38, 42))              # yard
    bx, by, bw, bh = x + w * 0.10, y + h * 0.30, w * 0.80, h * 0.52   # the shed
    rect(bx, by, bw, bh, fill=(52, 50, 54))
    d.polygon([(X(bx - 4), X(by)), (X(bx + bw * 0.45), X(by - 9)),
               (X(bx + bw + 4), X(by))], fill=(36, 35, 40))          # roofline
    d.polygon([(X(bx + bw * 0.52), X(by - 7)), (X(bx + bw * 0.80), X(by - 2)),
               (X(bx + bw * 0.80), X(by + 7)), (X(bx + bw * 0.52), X(by + 3))],
              fill=(66, 66, 74))                                     # caved-in section
    for c in range(6):                                               # window bays
        glow = (238, 176, 92) if c in (1, 4) else (26, 26, 30)
        rect(bx + 8 + c * (bw - 14) / 6, by + 7, 9, bh - 14, fill=glow)
    for i in range(4):                                               # smoke wisps
        d.ellipse([X(bx + bw * 0.58 + i * 10), X(by - 16 - i * 2),
                   X(bx + bw * 0.58 + i * 10 + 18), X(by - 8 - i * 2)],
                  fill=(120, 116, 110, 130))
    for tx in (x + w * 0.22, x + w * 0.66):                          # floodlights
        ly = y + h - 10
        d.polygon([(X(tx), X(ly - 20)), (X(tx - 13), X(ly + 1)),
                   (X(tx + 13), X(ly + 1))], fill=(250, 226, 150, 65))
        line(tx - 5, ly, tx, ly - 17, fill=(18, 18, 20), width=2)
        line(tx + 5, ly, tx, ly - 17, fill=(18, 18, 20), width=2)
        d.ellipse([X(tx - 3.5), X(ly - 23), X(tx + 3.5), X(ly - 17)],
                  fill=(250, 230, 160))
    grain(x, y, w, h, seed=53, n=150, alpha=12)
    rect(x, y, w, h, outline=RULE, width=1)


def plenary_panel(x, y, w, h):
    """The COP31 plenary hall in Antalya, emptied after the collapse:
    the summit screen over rows of delegates' desks."""
    panel(x, y, w, h)
    for i in range(8):
        shade = (44 + i * 2, 62 + i * 2, 84 + i)
        rect(x + 1, y + 1 + i * (h - 2) / 8, w - 2, (h - 2) / 8 + 1,
             fill=shade)
    rect(x + 1, y + h - 8, w - 2, 7, fill=(104, 88, 66))
    sw, sh = w * 0.52, h * 0.36
    sx0, sy0 = x + (w - sw) / 2, y + 4
    rect(sx0, sy0, sw, sh, fill=(24, 38, 56), outline=(220, 214, 198),
         width=1)
    text(sx0 + sw / 2, sy0 + 3, "COP31  ·  ANTALYA", F(SANS_B, 9),
         (236, 230, 212), anchor="ma")
    for row, (ty, span) in enumerate(((y + h - 15, w - 90), (y + h - 7, w - 40))):
        rect(x + (w - span) / 2, ty, span, 3, fill=(74, 56, 40))
        seats = 11 + row * 2
        for i in range(seats):
            cx = x + (w - span) / 2 + 16 + i * (span - 32) / (seats - 1)
            d.ellipse([X(cx - 2.5), X(ty - 7), X(cx + 2.5), X(ty - 2)],
                      fill=(16, 15, 14))
    grain(x, y, w, h, seed=31, n=140, alpha=12)
    rect(x, y, w, h, outline=RULE, width=1)


def capitol_panel(x, y, w, h):
    """The US Capitol at dusk: dome, colonnade and steps in silhouette."""
    panel(x, y, w, h)
    for i in range(6):
        shade = (96 + i * 9, 104 + i * 9, 122 + i * 8)
        rect(x + 1, y + 1 + i * (h - 2) / 6, w - 2, (h - 2) / 6 + 1,
             fill=shade)
    rect(x + 1, y + h - 6, w - 2, 5, fill=(52, 52, 58))
    cx = x + w / 2
    bw = w * 0.62
    bx = cx - bw / 2
    by = y + h - 12
    rect(bx, by - 13, bw, 13, fill=(38, 40, 48))
    for i in range(9):
        lx = bx + 8 + i * (bw - 16) / 8
        line(lx, by - 12, lx, by - 2, fill=(196, 198, 204), width=1)
    rect(bx - 6, by - 15, bw + 12, 2.5, fill=(30, 32, 40))
    d.pieslice([X(cx - 21), X(by - 40), X(cx + 21), X(by - 8)],
               180, 360, fill=(44, 47, 56))
    rect(cx - 21, by - 16, 42, 2, fill=(30, 32, 40))
    rect(cx - 4, by - 45, 8, 6, fill=(44, 47, 56))
    line(cx, by - 45, cx, by - 49, fill=(24, 25, 30), width=1.5)
    for sx in (x + w * 0.10, x + w * 0.86):
        rect(sx, by - 9, w * 0.13, 9, fill=(40, 42, 50))
    grain(x, y, w, h, seed=23, n=110, alpha=10)
    rect(x, y, w, h, outline=RULE, width=1)


# ---------------------------------------------------------------- page

M = 28                 # page margin
CW = W - 2 * M         # content width (968)
COLW = 309             # three-column width
GUT = 20.5             # gutter
COL2 = M + COLW + GUT  # 357.5
COL3 = M + 2 * (COLW + GUT)  # 687


def vrule(x, y1, y2):
    line(x, y1, x, y2, fill=FAINT, width=1)


def brief_flow(x, y, head, body):
    """One World in Brief item: a bold country head, then a two-line
    brief whose first line runs beside the head and second full width."""
    hf, bf = F(SANS_B, 9), F(SERIF, 9.5)
    text(x, y, head, hf, RED)
    hw = tw(head, hf) + 6
    words, first, rest = body.split(), "", ""
    for wd in words:
        trial = wd if not first else first + " " + wd
        if tw(trial, bf) <= COLW - hw or not first:
            first = trial
        else:
            rest = " ".join(words[len(first.split()):])
            break
    else:
        rest = ""
    text(x + hw, y, first, bf, INK)
    if rest:
        second = wrap(rest, bf, COLW)
        text(x, y + 10.5, second[0], bf, INK)


# --- folio + masthead -----------------------------------------------------
line(M, 16, W - M, 16, width=2.5)
text(M, 22, "Vol. XLI  ·  No. 328", F(SANS, 10.5), SOFT)
text(W / 2, 21, "TUESDAY, 24 NOVEMBER 2026", F(SANS_B, 12.5), RED, anchor="ma")
text(W - M, 22, "World Edition  ·  Price $2.00  ·  theworldtoday.news",
     F(SANS, 10.5), SOFT, anchor="ra")
text(W / 2, 38, "THE WORLD TODAY", F(DISPLAY, 45), INK, anchor="ma")
line(M, 94, W - M, 94, width=2.5)
line(M, 99, W - M, 99, width=1)

# --- markets ticker ---------------------------------------------------------
rect(M, 105, CW, 22, fill=INK)
text(W / 2, 109.5,
     "BRENT  $89.86    ·    WTI  $80.89    ·    GOLD  +2.7%    ·    "
     "VIX  35.89    ·    NIKKEI 225  −5.06%    ·    KOSPI  −4%    ·    US GAS  $3.56",
     F(SANS_B, 11.5), (240, 234, 218), anchor="ma")

# --- inside today -------------------------------------------------------------
text(M, 133, "INSIDE TODAY:", F(SANS_B, 10), RED)
text(M + 92, 133,
     "Hormuz crisis — full report p.2–3   ·   Ukraine talks p.6   ·   "
     "Nvidia blacklist p.14   ·   Antalya fallout p.9   ·   Factory fire p.7   ·   Sport p.24",
     F(SANS, 10), SOFT)
line(M, 148, W - M, 148, width=1)

# --- lead story -----------------------------------------------------------------
kicker(M, 156, "STRAIT OF HORMUZ  ·  SHIPPING CRISIS")
text(W - M, 156, "THIRD DAY OF ATTACKS ON GULF SHIPPING", F(SANS_B, 10.5),
     SOFT, anchor="ra")
headline_fit(W / 2, 168, "THREE TANKERS ABLAZE IN HORMUZ STRAIT", 39, CW - 8)
flow(M + 60, 222,
     "Iran's Revolutionary Guard says three oil tankers struck sea mines "
     "and caught fire in the strait, as a decoy tanker spoofing its own "
     "signals adds to the confusion and US warships move in to escort shipping",
     F(SERIF_I, 14), CW - 120, 18, SOFT, align="center")

strait_panel(M, 264, CW, 112)
caption(M, 380, CW,
        "Smoke rises over the Strait of Hormuz, where three tankers were reported ablaze on Tuesday.",
        "Illustration: Staff  ·  Reporting: Gulf Bureau")

text(M, 398, "By the Gulf Bureau", F(SERIF_BI, 11.5), INK)
LEAD_A = ("DUBAI — Three oil tankers hit sea mines and caught fire in "
          "the Strait of Hormuz, Iran's Revolutionary Guard said on "
          "Tuesday, in the most serious attack yet on shipping in the "
          "waterway that carries about a fifth of the world's oil. "
          "Crews were reported to be abandoning one of the vessels.")
LEAD_B = ("The US Navy said warships were moving to escort merchant "
          "shipping through the strait. Tracking firms also reported a "
          "decoy tanker — its name translates as “Line Breaker” — "
          "broadcasting false positions as if it had broken the US "
          "embargo, in an apparent effort to tie up traffic.")
flow(M, 416, LEAD_A, F(SERIF, 11.5), COLW, 14.5)
vrule(COL2 - GUT / 2, 416, 500)
flow(COL2, 416, LEAD_B, F(SERIF, 11.5), COLW, 14.5)
vrule(COL3 - GUT / 2, 416, 500)
rect(COL3, 416, COLW, 84, fill=PAPER_DARK, outline=RULE, width=1)
text(COL3 + 13, 423, "“", F(SERIF_B, 28), RED)
flow(COL3 + 33, 428,
     "An unwelcome addition to an already dangerous situation.",
     F(SERIF_BI, 12.5), COLW - 47, 15.5)
text(COL3 + 33, 480, "— Mark Douglas, Starboard Maritime Intelligence, "
     "on the decoy tanker", F(SANS_I, 9.5), SOFT)
line(M, 512, W - M, 512, width=1.5)

# --- row A: ukraine talks / nvidia blacklist / factory fire ---------------------
RA = 520
kicker(M, RA, "UKRAINE WAR  ·  SHENZHEN")
flags_panel(M, RA + 14, COLW, 44)
caption(M, RA + 61, COLW, "Flags of the three powers at Shenzhen.", "Staff")
y = flow(M, RA + 78, "ZELENSKYY URGES FOUR-WAY TALKS", F(SERIF_B, 18), COLW, 21)
flow(M, y + 2,
     "President Zelenskyy called for a four-party meeting with Russia, "
     "the United States and European leaders “as soon as possible”, "
     "saying Kyiv was ready to meet as early as Tuesday — a day after "
     "the Shenzhen trilateral summit. Brussels ruled out bilateral "
     "security talks with Moscow.",
     F(SERIF, 11), COLW, 13.5)

vrule(COL2 - GUT / 2, RA, RA + 180)
kicker(COL2, RA, "TECHNOLOGY  ·  MARKETS")
chart_panel(COL2, RA + 14, COLW, 44)
caption(COL2, RA + 61, COLW, "Screens in Tokyo as the tech rout ran on.", "Staff")
y = flow(COL2, RA + 78, "US BLACKLISTS MEGASPEED IN NVIDIA SPY SCANDAL",
         F(SERIF_B, 18), COLW, 21)
flow(COL2, y + 2,
     "Washington placed Singapore's Megaspeed International and six "
     "other Southeast Asian firms on its export blacklist, at the "
     "centre of an alleged Nvidia spy scandal. Nvidia reinstated its "
     "chief executive, Jensen Huang, after days of turmoil at the "
     "chipmaker, as the rout in technology shares ran into a second day.",
     F(SERIF, 11), COLW, 13.5)

vrule(COL3 - GUT / 2, RA, RA + 180)
kicker(COL3, RA, "INDONESIA")
factory_panel(COL3, RA + 14, COLW, 44)
caption(COL3, RA + 61, COLW, "Floodlights at the factory in Banten.", "Agencies")
y = flow(COL3, RA + 78, "FACTORY FIRE DEATH TOLL RISES TO 24",
         F(SERIF_B, 18), COLW, 21)
flow(COL3, y + 2,
     "The death toll from the fire at a candy factory in Banten rose "
     "to 24 as rescue teams searched the gutted plant for workers "
     "still missing. Emergency crews worked through the night while "
     "investigators sought the cause of the blaze.",
     F(SERIF, 11), COLW, 13.5)
line(M, RA + 188, W - M, RA + 188, width=1.5)

# --- row B: norway climate / pentagon canada / sport ------------------------------
RB = RA + 194  # 714
kicker(M, RB, "CLIMATE  ·  AFTER ANTALYA")
plenary_panel(M, RB + 14, COLW, 40)
caption(M, RB + 57, COLW, "The emptied plenary hall in Antalya.", "Staff")
y = flow(M, RB + 74, "NORWAY COURT VOIDS OIL LICENCES", F(SERIF_B, 17.5), COLW, 20)
flow(M, y + 2,
     "Norway's supreme court ruled its climate-disputed oil licences "
     "invalid, two days after the COP31 talks in Antalya ended without "
     "a deal. Experts met online on Tuesday to chart a way forward "
     "for climate action after the collapse.",
     F(SERIF, 11), COLW, 13.5)

vrule(COL2 - GUT / 2, RB, RB + 172)
kicker(COL2, RB, "UNITED STATES")
capitol_panel(COL2, RB + 14, COLW, 40)
caption(COL2, RB + 57, COLW, "The Capitol in Washington at dusk.", "Staff")
y = flow(COL2, RB + 74, "PENTAGON REBUKES CANADA OVER DEFENCE",
         F(SERIF_B, 17.5), COLW, 20)
flow(COL2, y + 2,
     "The Pentagon accused Canada of falling short as a credible "
     "partner in defending North America, citing defence-spending "
     "shortfalls and Ottawa's review of its planned purchase of "
     "American F-35 fighter jets.",
     F(SERIF, 11), COLW, 13.5)

rect(COL3, RB, COLW, 172, outline=RULE, width=1.2)                    # sport box
rect(COL3, RB, COLW, 20, fill=INK)
text(COL3 + 10, RB + 4, "SPORT", F(SANS_B, 11.5), (240, 234, 218))
text(COL3 + COLW - 10, RB + 5, "MILAN  ·  MELBOURNE", F(SANS, 9),
     (200, 194, 178), anchor="ra")
y = flow(COL3 + 10, RB + 27, "SEVEN-GOAL THRILLER STUNS INTER",
         F(SERIF_B, 14.5), COLW - 20, 18)
y = flow(COL3 + 10, y + 1,
         "Tresoldi's hat-trick condemned Inter to a historic defeat "
         "in a seven-goal thriller at San Siro.", F(SERIF, 10.5), COLW - 20, 13)
line(COL3 + 10, y + 4, COL3 + COLW - 10, y + 4, fill=FAINT, width=1)
y = flow(COL3 + 10, y + 9, "INGLIS, CAREY PUT AUSTRALIA ON TOP",
         F(SERIF_B, 14.5), COLW - 20, 18)
y = flow(COL3 + 10, y + 1,
         "Josh Inglis and Alex Carey put Australia in command of the "
         "deciding Test against South Africa.",
         F(SERIF, 10.5), COLW - 20, 13)
line(COL3 + 10, y + 4, COL3 + COLW - 10, y + 4, fill=FAINT, width=1)
flow(COL3 + 10, y + 9,
     "FIFA confirmed the US, Mexico, Costa Rica and Jamaica as hosts "
     "of the 2031 Women's World Cup, and the UK for 2035.",
     F(SANS, 9.5), COLW - 20, 12, SOFT)
line(M, RB + 180, W - M, RB + 180, width=1.5)

# --- markets at a glance + weather --------------------------------------------------
DB = RB + 186  # 916
rect(M, DB, 636, 38, fill=PAPER_DARK, outline=RULE, width=1)
text(M + 10, DB + 3, "MARKETS AT A GLANCE", F(SANS_B, 9), RED)
DATA = [("BRENT", "$89.86"), ("WTI", "$80.89"), ("GOLD", "+2.7%"),
        ("VIX", "35.89"), ("NIKKEI 225", "−5.06%"), ("KOSPI", "−4.0%"),
        ("S&P 500", "−3.7%"), ("NASDAQ", "−5.3%")]
for i, (name, val) in enumerate(DATA):
    cx = M + 10 + (i % 4) * 158
    cy = DB + 16 + (i // 4) * 12
    text(cx, cy, name, F(SANS_B, 8.5), SOFT)
    text(cx + 60, cy, val, F(SANS_B, 8.5),
         RED if val.startswith("−") else INK)
rect(M + 648, DB, 320, 38, outline=RULE, width=1)
text(M + 658, DB + 3, "WEATHER TODAY", F(SANS_B, 9), NAVY)
text(M + 658, DB + 16, "Antalya 17° clearing  ·  Kyiv 1° snow  ·  Tokyo 12° fair",
     F(SANS, 8.5), SOFT)
text(M + 658, DB + 28, "New York 7° clear  ·  London 8° rain  ·  Shenzhen 23° humid",
     F(SANS, 8.5), SOFT)

# --- world in brief ---------------------------------------------------------------------
WB = DB + 40  # 958
rect(M, WB, CW, 17, fill=NAVY)
text(M + 10, WB + 3.5, "WORLD IN BRIEF", F(SANS_B, 10), (240, 234, 218))
text(W / 2, WB + 3.5, "PAGE 1  ·  WORLD", F(SANS, 9.5), (205, 208, 216),
     anchor="ma")
text(W - M - 10, WB + 3.5, "TUESDAY, 24 NOVEMBER 2026", F(SANS_B, 10),
     (240, 234, 218), anchor="ra")
BRIEFS = [
    ("SOUTH KOREA", "Russian aircraft entered its air defence zone over "
                    "waters off Japan; Seoul corrected reports of a "
                    "territorial violation."),
    ("CHINA", "An official surnamed Ma was sentenced to death for "
              "spying for an unnamed foreign country."),
    ("SUDAN", "RSF drone attacks struck power stations and triggered "
              "mass blackouts across the country."),
    ("EBOLA", "Kenya discharged its last Ebola patient, even as the "
              "death toll in Congo passed 5,300."),
    ("RUSSIA", "Moscow told the UN Security Council it will not agree "
               "to any new grain deal with Ukraine."),
    ("SOUTH AFRICA", "Voters cast ballots as anger over power cuts and "
                     "failing services threatened the ANC."),
]
for i, (head, body) in enumerate(BRIEFS):
    bx = M + (i % 3) * (COLW + GUT)
    by = WB + 22 + (i // 3) * 22
    brief_flow(bx, by, head, body)

text(M, 1010, "Page 1  ·  WORLD  ·  Continued inside", F(SANS_B, 8.5), SOFT)
text(W - M, 1010, "Markets p.14  ·  Sport p.24  ·  theworldtoday.news",
     F(SANS, 8.5), SOFT, anchor="ra")

# ---------------------------------------------------------------- output

out = Path(__file__).resolve().parent.parent / "assets" / "final-page.png"
img.resize((W, H), Image.LANCZOS).save(out, optimize=True)
print("wrote", out)
